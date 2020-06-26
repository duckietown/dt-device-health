#!/usr/bin/env python3

import sys
import json
import subprocess
import psutil
import re
import time
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

from dt_class_utils import DTProcess
from dt_module_utils import set_module_healthy, set_module_unhealthy

from .hardware import get_hardware_info

VC = "vcgencmd"
HEALTH_CHECKER_FREQUENCY_HZ = 1.0 / 5.0  # once every 5 seconds


def command_output(cmd):
    cmd = ' '.join(cmd + [' 2>/dev/null ||', 'echo', 'ND'])
    res = subprocess.check_output(cmd, shell=True)
    lines = res.decode('utf-8').split('\n')
    res = {}
    for line in lines:
        if not line:
            continue
        for c in ['=', ':']:
            if c in line:
                i = line.index(c)
                j = i if '(' not in line else line.index('(')
                res[line[:j].strip()] = line[i + 1:].strip()
                break
    return res


def get_firmware_info(cmd):
    cmd = ' '.join(cmd + [' 2>/dev/null ||', 'echo', 'ND'])
    res = subprocess.check_output(cmd, shell=True)
    lines = res.decode('utf-8').split('\n')
    data = {
        'date': {
            'year': -1,
            'day': -1,
            'month': "ND"
        },
        'version': "ND"
    }
    # ---
    try:
        date_str, _, version_str, _ = lines
        month, day, year, _ = re.sub('\s+', ' ', date_str.strip()).split(' ')
        data['date']['year'] = int(year)
        data['date']['month'] = month
        data['date']['day'] = int(day)
        _, version, *_ = version_str.split(' ')
        data['version'] = version
    finally:
        return data


def get_throttled():
    # get throttled
    health = dict()
    health.update(command_output([VC, 'get_throttled']))
    # expand throttled
    tint = int(health['throttled'], 0)
    bits = {
        'under-voltage-now': 0,
        'freq-capped-now': 1,
        'throttling-now': 2,
        'under-voltage-occurred': 16,
        'freq-capped-occurred': 17,
        'throttling-occurred': 18
    }
    throttled = health['throttled_humans'] = {}
    for k, n in bits.items():
        a = tint & (1 << n)
        throttled[k] = a > 0
    # ---
    return health


STATIC_FIRMWARE_INFO = get_firmware_info([VC, 'version'])


def go():
    health = {
        'throttled': '0',
        'frequency': '0',
        'volts': {},
        'mem': {},
        'swap': {},
        'disk': {},
        'firmware': {},
        'hardware': {}
    }
    # get Voltage
    for a in ["core", "sdram_i"]:
        cmd = [VC, "measure_volts", a]
        res = command_output(cmd)
        vals = list(res.values())
        health['volts'][a] = float(vals[0][:-1]) if vals else 'ND'
    # get Temperature
    cmd = [VC, "measure_temp"]
    health.update(command_output(cmd))
    if health['temp'] != 'ND':
        health['temp'] = float(health['temp'][:-2])
    # get CPU frequency
    cmd = [VC, "measure_clock", "arm"]
    health.update(command_output(cmd))
    if health['frequency'] != 'ND':
        health['frequency'] = float(health['frequency'])
    # get Memory stats
    mem_stats = psutil.virtual_memory()
    health['mem'].update({
        'pmem': mem_stats.percent,
        'total': mem_stats.total,
        'used': mem_stats.used,
        'free': mem_stats.available
    })
    # get Swap stats
    swap_stats = psutil.swap_memory()
    health['swap'].update({
        'pswap': swap_stats.percent,
        'total': swap_stats.total,
        'used': swap_stats.used,
        'free': swap_stats.free
    })
    # get CPU usage
    health['pcpu'] = psutil.cpu_percent()
    # get Disk usage
    disk_stats = psutil.disk_usage('/')
    health['disk'].update({
        'pdisk': disk_stats.percent,
        'total': disk_stats.total,
        'used': disk_stats.used,
        'free': disk_stats.free
    })
    # get firmware info
    health['firmware'] = STATIC_FIRMWARE_INFO
    # add (unknown) to hardware fields (will be replaced later)
    health['hardware'] = get_hardware_info(None)
    # get Raspberry Pi board model
    cpuinfo = command_output(['cat', '/proc/cpuinfo'])
    if 'Revision' in cpuinfo:
        health['hardware'] = get_hardware_info(cpuinfo['Revision'])
    # get throttled
    health.update(get_throttled())
    # define human-readable status
    error = False
    warning = False
    msgs = []
    if health['throttled_humans']['throttling-now']:
        msgs.append('Error: PI is throttled')
        error = True
    if health['throttled_humans']['freq-capped-now']:
        msgs.append('Error: Frequency is capped')
        error = True
    if health['throttled_humans']['under-voltage-now']:
        msgs.append('Error: Under-voltage')
        error = True
    if health['throttled_humans']['throttling-occurred']:
        msgs.append('Warning: PI throttling occurred in the past.')
        warning = True
    if health['throttled_humans']['freq-capped-occurred']:
        msgs.append('Warning: Frequency is capped occurred in the past.')
        warning = True
    if health['throttled_humans']['under-voltage-occurred']:
        msgs.append('Warning: Under-voltage occurred in the past.')
        warning = True
    # define overall status
    health['status'] = 'error' if error else 'warning' if warning else "ok"
    health['status_msgs'] = msgs
    # ---
    return health


class HealthAPIRequestHandler(BaseHTTPRequestHandler):

    def _set_headers(self):
        # open headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        # support CORS
        origin = self.headers.get('Origin', None)
        if origin:
            self.send_header('Access-Control-Allow-Origin', origin)
        # close headers
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        health = go()
        res = json.dumps(health, indent=4).encode()
        self.wfile.write(res)

    def do_HEAD(self):
        self._set_headers()


class HealthAPIServer(HTTPServer, DTProcess):

    def __init__(self, *args, **kwargs):
        HTTPServer.__init__(self, *args, **kwargs)
        DTProcess.__init__(self, name='health-api')
        self._last_time_checked = 0
        self._health_checker = Thread(target=self._health_check)
        self._health_checker.start()

    def _health_check(self):
        while not self.is_shutdown():
            if (time.time() - self._last_time_checked) > (1.0 / HEALTH_CHECKER_FREQUENCY_HZ):
                t = get_throttled()['throttled_humans']
                if t['throttling-now'] or t['freq-capped-now'] or t['under-voltage-now']:
                    set_module_unhealthy()
                else:
                    set_module_healthy()
                # ---
                self._last_time_checked = time.time()
            time.sleep(1.0)


def run(server_class=HealthAPIServer, handler_class=HealthAPIRequestHandler, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    sys.stderr.write('\n\nListening on port %s...\n' % port)
    httpd.serve_forever()


def just_check():
    health = go()
    if health['status'] == 'error':
        msg = "\n".join(health['status_msgs'])
        sys.stderr.write('Status = error\n')
        sys.stderr.write(msg + '\n')
        sys.stderr.flush()
        sys.exit(1)
    else:
        sys.exit(0)
