#!/usr/bin/env python3

import sys
import json
import subprocess
import psutil
from .raspberry_pi import get_raspberrypi_info
from http.server import BaseHTTPRequestHandler, HTTPServer


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
                res[line[:i].strip()] = line[i + 1:].strip()
                break
    return res


def go():
    health = {
        'throttled': '0',
        'volts': {},
        'mem': {},
        'swap': {},
        'disk': {},
        'hardware': {}
    }
    vc = "vcgencmd"
    # get Voltage
    for a in ["core", "sdram_i"]:
        cmd = [vc, "measure_volts", a]
        res = command_output(cmd)
        vals = list(res.values())
        health['volts'][a] = vals[0] if vals else 'ND'
    # get Temperature
    cmd = [vc, "measure_temp"]
    health.update(command_output(cmd))
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
    # add (unknown) to hardware fields (will be replaced later)
    health['hardware'] = get_raspberrypi_info(None)
    # get Raspberry Pi board model
    cpuinfo = command_output(['cat', '/proc/cpuinfo'])
    if 'Revision' in cpuinfo:
        health['hardware'] = get_raspberrypi_info(cpuinfo['Revision'])
    # get Throttled
    health.update(command_output([vc, 'get_throttled']))
    # expand Throttled
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
    # define human-readable status
    error = False
    warning = False
    msgs = []
    if throttled['throttling-now']:
        msgs.append('Error: PI is throttled')
        error = True
    if throttled['freq-capped-now']:
        msgs.append('Error: Frequency is capped')
        error = True
    if throttled['under-voltage-now']:
        msgs.append('Error: Under-voltage')
        error = True
    if throttled['throttling-occurred']:
        msgs.append('Warning: PI throttling occurred in the past.')
        warning = True
    if throttled['freq-capped-occurred']:
        msgs.append('Warning: Frequency is capped occurred in the past.')
        warning = True
    if throttled['under-voltage-occurred']:
        msgs.append('Warning: Under-voltage occurred in the past.')
        warning = True
    # define overall status
    health['status'] = 'error' if error else 'warning' if warning else "ok"
    health['status_msgs'] = msgs
    # ---
    return health


class HealthAPI(BaseHTTPRequestHandler):
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


def run(server_class=HTTPServer, handler_class=HealthAPI, port=80):
    health = go()
    res = json.dumps(health, indent=4)
    print(res)
    print('')
    sys.stdout.flush()
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
