#!/usr/bin/env python2
import json
import subprocess


def command_output(cmd):
    cmd = ' '.join(cmd + [' 2>/dev/null ||', 'echo', 'ND'])
    res = subprocess.check_output(cmd, shell=True)
    lines = res.decode('utf-8').split('\n')
    res = {}
    for l in lines:
        if not l:
            continue
        if '=' in l:
            i = l.index('=')
            res[l[:i]] = l[i + 1:]
    return res


def go():
    health = {
        'throttled': '0',
        'clock': {},
        'volts': {},
        'mem': {}
    }
    VC = "vcgencmd"
    for src in "arm core h264 isp v3d uart pwm emmc pixel vec hdmi dpi".split():
        cmd = [VC, "measure_clock", src]
        res = command_output(cmd)
        vals = list(res.values())
        health['clock'][src] = vals[0] if vals else 'ND'

    for a in "core sdram_c sdram_i sdram_p".split():
        cmd = [VC, "measure_volts", a]
        res = command_output(cmd)
        vals = list(res.values())
        health['volts'][a] = vals[0] if vals else 'ND'

    cmd = [VC, "measure_temp"]
    health.update(command_output(cmd))

    for a in "arm gpu".split():
        cmd = [VC, 'get_mem', a]
        health['mem'].update(command_output(cmd))

    health.update(command_output([VC, 'get_throttled']))

    tint = int(health['throttled'], 0)
    # tbin = "{0:b}".format(tint)

    # 0: under-voltage
    # 1: arm frequency capped
    # 2: currently throttled
    # 16: under-voltage has occurred
    # 17: arm frequency capped has occurred
    # 18: throttling has occurred

    bits = {'under-voltage-now': 0,
            'freq-capped-now': 1,
            'throttling-now': 2,
            'under-voltage-occurred': 16,
            'freq-capped-occurred': 17,
            'throttling-occurred': 18}

    T = health['throttled_humans'] = {}
    for k, n in bits.items():
        a = tint & (1 << n)
        T[k] = a > 0

    error = False
    warning = False
    msgs = []

    if T['throttling-now']:
        msgs.append('Error: PI is throttled')
        error = True
    if T['freq-capped-now']:
        msgs.append('Error: Frequency is capped')
        error = True
    if T['under-voltage-now']:
        msgs.append('Error: Under-voltage')
        error = True
    if T['throttling-occurred']:
        msgs.append('Warning: PI throttling occurred in the past.')
        warning = True
    if T['freq-capped-occurred']:
        msgs.append('Warning: Frequency is capped occurred in the past.')
        warning = True
    if T['under-voltage-occurred']:
        msgs.append('Warning: Under-voltage occurred in the past.')
        warning = True

    health['status'] = 'error' if error else 'warning' if warning else "ok"
    health['status_msgs'] = msgs

    return health


from http.server import BaseHTTPRequestHandler, HTTPServer


class S(BaseHTTPRequestHandler):
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


import sys


def run(server_class=HTTPServer, handler_class=S, port=80):
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
        sys.stderr.write(msg+'\n')
        sys.stderr.flush()
        sys.exit(1)
    else:
        sys.exit(0)
