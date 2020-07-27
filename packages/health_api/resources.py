import re
import psutil
import subprocess

from health_api import logger
from health_api.utils import command_output
from health_api.hardware import get_hardware_info
from health_api.knowledge_base import KnowledgeBase

VC = "vcgencmd"


def get_voltage():
    # get Voltage
    res = {
        'volts': {}
    }
    for dev in ["core", "sdram_i"]:
        cmd = [VC, "measure_volts", dev]
        volt = command_output(cmd, 'volt')
        if volt['volt'] != 'ND':
            vals = list(volt.values())
            res['volts'][dev] = float(vals[0][:-1]) if vals else 'ND'
        else:
            res['volts'][dev] = 'ND'
    return res


def get_temperature():
    # get Temperature
    cmd = [VC, "measure_temp"]
    res = command_output(cmd, 'temp')
    if res['temp'] != 'ND':
        res['temp'] = float(res['temp'][:-2])
    return res


def get_frequency():
    # get CPU frequency
    cmd = [VC, "measure_clock", "arm"]
    res = command_output(cmd, 'frequency')
    if res['frequency'] != 'ND':
        res['frequency'] = float(res['frequency'])
    return res


def get_memory():
    # get Memory stats
    mem_stats = psutil.virtual_memory()
    return {
        'mem': {
            'pmem': mem_stats.percent,
            'total': mem_stats.total,
            'used': mem_stats.used,
            'free': mem_stats.available
        }
    }


def get_swap():
    # get Swap stats
    swap_stats = psutil.swap_memory()
    return {
        'swap': {
            'pswap': swap_stats.percent,
            'total': swap_stats.total,
            'used': swap_stats.used,
            'free': swap_stats.free
        }
    }


def get_pcpu():
    # get CPU usage
    return {
        'pcpu': psutil.cpu_percent()
    }


def get_disk():
    # get Disk usage
    disk_stats = psutil.disk_usage('/')
    return {
        'disk': {
            'pdisk': disk_stats.percent,
            'total': disk_stats.total,
            'used': disk_stats.used,
            'free': disk_stats.free
        }
    }


def get_firmware():
    cmd = ' '.join([VC, 'version', '2>/dev/null', '||', 'echo', 'ND'])
    res = subprocess.check_output(cmd, shell=True)
    lines = res.decode('utf-8').split('\n')
    res = {
        'date': {
            'year': -1,
            'day': -1,
            'month': "ND"
        },
        'version': "ND"
    }
    # try parsing
    try:
        date_str, _, version_str, _ = lines
        month, day, year, _ = re.sub('\s+', ' ', date_str.strip()).split(' ')
        res['date']['year'] = int(year)
        res['date']['month'] = month
        res['date']['day'] = int(day)
        _, version, *_ = version_str.split(' ')
        res['version'] = version
    finally:
        return {
            'firmware': res
        }


def get_hardware():
    # get defaults
    res = {'hardware': get_hardware_info(None)}
    # get Raspberry Pi board model
    cpuinfo = command_output(['cat', '/proc/cpuinfo'], 'Revision', None)
    if cpuinfo['Revision'] is not None:
        res['hardware'] = get_hardware_info(cpuinfo['Revision'])
    return res


def get_throttled():
    res = {
        'throttled': "ND",
        'throttled_humans': {
            'under-voltage-now': False,
            'freq-capped-now': False,
            'throttling-now': False,
            'under-voltage-occurred': False,
            'freq-capped-occurred': False,
            'throttling-occurred': False
        },
        'status': 'ND',
        'status_msgs': []
    }
    # get throttled
    res.update(command_output([VC, 'get_throttled'], 'throttled'))
    if res['throttled'] != 'ND':
        # expand throttled
        tint = int(res['throttled'], 0)
        bits = {
            'under-voltage-now': 0,
            'freq-capped-now': 1,
            'throttling-now': 2,
            'under-voltage-occurred': 16,
            'freq-capped-occurred': 17,
            'throttling-occurred': 18
        }
        res['throttled_humans'] = {}
        for k, n in bits.items():
            a = tint & (1 << n)
            res['throttled_humans'][k] = a > 0
        # get throttled
        error = False
        warning = False
        msgs = []
        # define human-readable status
        if res['throttled_humans']['throttling-now']:
            msgs.append('Error: PI is throttled')
            error = True
        if res['throttled_humans']['freq-capped-now']:
            msgs.append('Error: Frequency is capped')
            error = True
        if res['throttled_humans']['under-voltage-now']:
            msgs.append('Error: Under-voltage')
            error = True
        if res['throttled_humans']['throttling-occurred']:
            msgs.append('Warning: PI throttling occurred in the past.')
            warning = True
        if res['throttled_humans']['freq-capped-occurred']:
            msgs.append('Warning: Frequency is capped occurred in the past.')
            warning = True
        if res['throttled_humans']['under-voltage-occurred']:
            msgs.append('Warning: Under-voltage occurred in the past.')
            warning = True
        # define overall status
        res['status'] = 'error' if error else 'warning' if warning else 'ok'
        res['status_msgs'] = msgs
    else:
        res['status'] = 'error'
        res['status_msgs'] = [
            'Error fetching data from the VCHI device.'
        ]
    # ---
    return res


resources = {
    'volts': get_voltage,
    'temp': get_temperature,
    'frequency': get_frequency,
    'mem': get_memory,
    'swap': get_swap,
    'pcpu': get_pcpu,
    'disk': get_disk,
    'firmware': get_firmware,
    'hardware': get_hardware,
    'status': get_throttled
}

resource_ttl = {
    'volts': 1,
    'temp': 1,
    'frequency': 1,
    'mem': 2,
    'swap': 5,
    'pcpu': 1,
    'disk': 10,
    'firmware': -1,
    'hardware': -1,
    'status': 1
}

all_resources = resource_ttl.keys()


def cached_resource(resource):
    if resource not in resources:
        raise KeyError(resource)
    try:
        res = KnowledgeBase.get(resource)
        logger.debug("Resource '{}':{}Using cached data.".format(
            resource, ' ' * (12 - len(resource))
        ))
        return res
    except KeyError:
        fcn = resources[resource]
        res = fcn()
        logger.debug("Resource '{}':{}Fetching new data.".format(
            resource, ' ' * (12 - len(resource))
        ))
        KnowledgeBase.set(resource, res, resource_ttl[resource])
        return res


__all__ = [
    'cached_resource',
    'all_resources'
]
