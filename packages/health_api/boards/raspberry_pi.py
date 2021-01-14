import re
import subprocess

from typing import Dict, Optional, Union

from health_api.constants import MB, GB, MHz, GHz
from health_api.machine import GenericMachine


class RaspberryPi(GenericMachine):
    VC = "vcgencmd"
    MODELS = {
        "900021": {
            "release_date": "Q3 2016",
            "model": "A+",
            "revision": "1.1",
            "memory": 512 * MB,
            "frequency": 700 * MHz,
            "gpu": False,
            "notes": "(Mfg by Sony)"
        },
        "900032": {
            "release_date": "Q2 2016?",
            "model": "B+",
            "revision": "1.2",
            "memory": 512 * MB,
            "frequency": 700 * MHz,
            "gpu": False,
            "notes": "(Mfg by Sony)"
        },
        "900092": {
            "release_date": "Q4 2015",
            "model": "Zero",
            "revision": "1.2",
            "memory": 512 * MB,
            "frequency": 1 * GHz,
            "gpu": False,
            "notes": "(Mfg by Sony)"
        },
        "900093": {
            "release_date": "Q2 2016",
            "model": "Zero",
            "revision": "1.3",
            "memory": 512 * MB,
            "frequency": 1 * GHz,
            "gpu": False,
            "notes": "(Mfg by Sony)"
        },
        "920093": {
            "release_date": "Q4 2016?",
            "model": "Zero",
            "revision": "1.3",
            "memory": 512 * MB,
            "frequency": 1 * GHz,
            "gpu": False,
            "notes": "(Mfg by Embest)"
        },
        "Beta": {
            "release_date": "Q1 2012",
            "model": "B (Beta)",
            "revision": "?",
            "memory": "256 MB",
            "frequency": 700 * MHz,
            "gpu": False,
            "notes": "Beta Board"
        },
        "0002": {
            "release_date": "Q1 2012",
            "model": "B",
            "revision": "1.0",
            "memory": "256 MB",
            "frequency": 700 * MHz,
            "gpu": False,
            "notes": ""
        },
        "0003": {
            "release_date": "Q3 2012",
            "model": "B (ECN0001)",
            "revision": "1.0",
            "memory": "256 MB",
            "frequency": 700 * MHz,
            "gpu": False,
            "notes": "Fuses mod and D14 removed"
        },
        "0004": {
            "release_date": "Q3 2012",
            "model": "B",
            "revision": "2.0",
            "memory": "256 MB",
            "frequency": 700 * MHz,
            "gpu": False,
            "notes": "(Mfg by Sony)"
        },
        "0005": {
            "release_date": "Q4 2012",
            "model": "B",
            "revision": "2.0",
            "memory": "256 MB",
            "frequency": 700 * MHz,
            "gpu": False,
            "notes": "(Mfg by Qisda)"
        },
        "0006": {
            "release_date": "Q4 2012",
            "model": "B",
            "revision": "2.0",
            "memory": "256 MB",
            "frequency": 700 * MHz,
            "gpu": False,
            "notes": "(Mfg by Egoman)"
        },
        "0007": {
            "release_date": "Q1 2013",
            "model": "A",
            "revision": "2.0",
            "memory": "256 MB",
            "frequency": 700 * MHz,
            "gpu": False,
            "notes": "(Mfg by Egoman)"
        },
        "0008": {
            "release_date": "Q1 2013",
            "model": "A",
            "revision": "2.0",
            "memory": "256 MB",
            "frequency": 700 * MHz,
            "gpu": False,
            "notes": "(Mfg by Sony)"
        },
        "0009": {
            "release_date": "Q1 2013",
            "model": "A",
            "revision": "2.0",
            "memory": "256 MB",
            "frequency": 700 * MHz,
            "gpu": False,
            "notes": "(Mfg by Qisda)"
        },
        "000d": {
            "release_date": "Q4 2012",
            "model": "B",
            "revision": "2.0",
            "memory": 512 * MB,
            "frequency": 700 * MHz,
            "gpu": False,
            "notes": "(Mfg by Egoman)"
        },
        "000e": {
            "release_date": "Q4 2012",
            "model": "B",
            "revision": "2.0",
            "memory": 512 * MB,
            "frequency": 700 * MHz,
            "gpu": False,
            "notes": "(Mfg by Sony)"
        },
        "000f": {
            "release_date": "Q4 2012",
            "model": "B",
            "revision": "2.0",
            "memory": 512 * MB,
            "frequency": 700 * MHz,
            "gpu": False,
            "notes": "(Mfg by Qisda)"
        },
        "0010": {
            "release_date": "Q3 2014",
            "model": "B+",
            "revision": "1.0",
            "memory": 512 * MB,
            "frequency": 700 * MHz,
            "gpu": False,
            "notes": "(Mfg by Sony)"
        },
        "0011": {
            "release_date": "Q2 2014",
            "model": "Compute Module 1",
            "revision": "1.0",
            "memory": 512 * MB,
            "frequency": 700 * MHz,
            "gpu": False,
            "notes": "(Mfg by Sony)"
        },
        "0012": {
            "release_date": "Q4 2014",
            "model": "A+",
            "revision": "1.1",
            "memory": "256 MB",
            "frequency": 700 * MHz,
            "gpu": False,
            "notes": "(Mfg by Sony)"
        },
        "0013": {
            "release_date": "Q1 2015",
            "model": "B+",
            "revision": "1.2",
            "memory": 512 * MB,
            "frequency": 700 * MHz,
            "gpu": False,
            "notes": "(Mfg by Embest)"
        },
        "0014": {
            "release_date": "Q2 2014",
            "model": "Compute Module 1",
            "revision": "1.0",
            "memory": 512 * MB,
            "frequency": 700 * MHz,
            "gpu": False,
            "notes": "(Mfg by Embest)"
        },
        "0015": {
            "release_date": "?",
            "model": "A+",
            "revision": "1.1",
            "memory": "256 MB / 512 MB",
            "frequency": 700 * MHz,
            "gpu": False,
            "notes": "(Mfg by Embest)"
        },
        "a01040": {
            "release_date": "Unknown",
            "model": "2 model B",
            "revision": "1.0",
            "memory": 1 * GB,
            "frequency": 900 * MHz,
            "gpu": False,
            "notes": "(Mfg by Sony)"
        },
        "a01041": {
            "release_date": "Q1 2015",
            "model": "2 model B",
            "revision": "1.1",
            "memory": 1 * GB,
            "frequency": 900 * MHz,
            "gpu": False,
            "notes": "(Mfg by Sony)"
        },
        "a21041": {
            "release_date": "Q1 2015",
            "model": "2 model B",
            "revision": "1.1",
            "memory": 1 * GB,
            "frequency": 900 * MHz,
            "gpu": False,
            "notes": "(Mfg by Embest)"
        },
        "a22042": {
            "release_date": "Q3 2016",
            "model": "2 model B (with BCM2837)",
            "revision": "1.2",
            "memory": 1 * GB,
            "frequency": 900 * MHz,
            "gpu": False,
            "notes": "(Mfg by Embest)"
        },
        "9000c1": {
            "release_date": "Q1 2017",
            "model": "Zero W",
            "revision": "1.1",
            "memory": 512 * MB,
            "frequency": 1 * GHz,
            "gpu": False,
            "notes": "(Mfg by Sony)"
        },
        "a02082": {
            "release_date": "Q1 2016",
            "model": "3 model B",
            "revision": "1.2",
            "memory": 1 * GB,
            "frequency": 1.2 * GHz,
            "gpu": False,
            "notes": "(Mfg by Sony)"
        },
        "a020a0": {
            "release_date": "Q1 2017",
            "model": "Compute Module 3 (and CM3 Lite)",
            "revision": "1.0",
            "memory": 1 * GB,
            "frequency": 1.2 * GHz,
            "gpu": False,
            "notes": "(Mfg by Sony)"
        },
        "a22082": {
            "release_date": "Q1 2016",
            "model": "3 model B",
            "revision": "1.2",
            "memory": 1 * GB,
            "frequency": 1.2 * GHz,
            "gpu": False,
            "notes": "(Mfg by Embest)"
        },
        "a32082": {
            "release_date": "Q4 2016",
            "model": "3 model B",
            "revision": "1.2",
            "memory": 1 * GB,
            "frequency": 1.2 * GHz,
            "gpu": False,
            "notes": "(Mfg by Sony Japan)"
        },
        "a020d3": {
            "release_date": "Q1 2018",
            "model": "3 model B+",
            "revision": "1.3",
            "memory": 1 * GB,
            "frequency": 1.4 * GHz,
            "gpu": False,
            "notes": "(Mfg by Sony)"
        },
        "9020e0": {
            "release_date": "Q4 2018",
            "model": "3 model A+",
            "revision": "1.0",
            "memory": 512 * MB,
            "frequency": 1.4 * GHz,
            "gpu": False,
            "notes": "(Mfg by Sony)"
        },
        "a02100": {
            "release_date": "Q1 2019",
            "model": "Compute Module 3+",
            "revision": "1.0",
            "memory": 1 * GB,
            "frequency": 1.2 * GHz,
            "gpu": False,
            "notes": "(Mfg by Sony)"
        },
        "a03111": {
            "release_date": "Q2 2019",
            "model": "4 model B",
            "revision": "1.1",
            "memory": 1 * GB,
            "frequency": 2.0 * GHz,
            "gpu": False,
            "notes": "(Mfg by Sony)"
        },
        "b03111": {
            "release_date": "Q2 2019",
            "model": "4 model B",
            "revision": "1.1",
            "memory": 2 * GB,
            "frequency": 2.0 * GHz,
            "gpu": False,
            "notes": "(Mfg by Sony)"
        },
        "b03112": {
            "release_date": "Q2 2019",
            "model": "4 model B",
            "revision": "1.2",
            "memory": 2 * GB,
            "frequency": 2.0 * GHz,
            "gpu": False,
            "notes": "(Mfg by Sony)"
        },
        "c03111": {
            "release_date": "Q2 2019",
            "model": "4 model B",
            "revision": "1.1",
            "memory": 4 * GB,
            "frequency": 2.0 * GHz,
            "gpu": False,
            "notes": "(Mfg by Sony)"
        },
        "c03112": {
            "release_date": "Q2 2019",
            "model": "4 model B",
            "revision": "1.2",
            "memory": 4 * GB,
            "frequency": 2.0 * GHz,
            "gpu": False,
            "notes": "(Mfg by Sony)"
        },
        "d03114": {
            "release_date": "Q2 2020",
            "model": "4 model B",
            "revision": "1.4",
            "memory": 8 * GB,
            "frequency": 2.0 * GHz,
            "gpu": False,
            "notes": "(Mfg by Sony)"
        }
    }
    MONTHS = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12
    }

    def get_voltage(self):
        # get Voltage
        res = {
            'volts': {}
        }
        for dev, key in {"core": "core", "sdram_i": "ram"}.items():
            cmd = [self.VC, "measure_volts", dev]
            volt = self._command_output(cmd, 'volt')
            if volt['volt'] != 'ND':
                vals = list(volt.values())
                res['volts'][key] = float(vals[0][:-1]) if vals else 'ND'
            else:
                res['volts'][key] = 'ND'
        return res

    def get_cpu_thermal_zone_name(self) -> str:
        return 'cpu_thermal'

    def get_firmware(self):
        cmd = ' '.join([self.VC, 'version', '2>/dev/null', '||', 'echo', 'ND'])
        res = subprocess.check_output(cmd, shell=True)
        lines = res.decode('utf-8').split('\n')
        res = {
            'date': {
                'day': 0,
                'month': 0,
                'year': 0
            },
            'version': "ND"
        }
        # try parsing
        try:
            date_str, _, version_str, _ = lines
            month, day, year, _ = re.sub(r'\s+', ' ', date_str.strip()).split(' ')
            res['date']['year'] = int(year)
            res['date']['month'] = self.MONTHS[month]
            res['date']['day'] = int(day)
            _, version, *_ = version_str.split(' ')
            res['version'] = version
        finally:
            return {
                'firmware': res
            }

    def get_hardware(self):
        # get defaults
        res = {'hardware': self._default_hardware_info()}
        # get Raspberry Pi board model
        cpuinfo = self._command_output(['cat', '/proc/cpuinfo'], 'Revision')
        revision = cpuinfo['Revision']
        if revision in self.MODELS:
            info = self.MODELS[revision]
            info['board'] = 'Raspberry Pi'
            res['hardware'] = info
        # ---
        return res

    def get_throttled(self):
        res = {
            'throttling': {
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
        throttled = self._command_output([self.VC, 'get_throttled'], 'throttled')['throttled']
        if throttled != 'ND':
            # expand throttled
            tint = int(throttled, 0)
            bits = {
                'under-voltage-now': 0,
                'freq-capped-now': 1,
                'throttling-now': 2,
                'under-voltage-occurred': 16,
                'freq-capped-occurred': 17,
                'throttling-occurred': 18
            }
            res['throttling'] = {}
            for k, n in bits.items():
                a = tint & (1 << n)
                res['throttling'][k] = a > 0
            # get throttled
            error = False
            warning = False
            msgs = []
            # define human-readable status
            if res['throttling']['throttling-now']:
                msgs.append('Error: PI is throttled')
                error = True
            if res['throttling']['freq-capped-now']:
                msgs.append('Error: Frequency is capped')
                error = True
            if res['throttling']['under-voltage-now']:
                msgs.append('Error: Under-voltage')
                error = True
            if res['throttling']['throttling-occurred']:
                msgs.append('Warning: PI throttling occurred in the past.')
                warning = True
            if res['throttling']['freq-capped-occurred']:
                msgs.append('Warning: Frequency is capped occurred in the past.')
                warning = True
            if res['throttling']['under-voltage-occurred']:
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

    @classmethod
    def is_instance_of(cls):
        cpuinfo = cls._command_output(['cat', '/proc/cpuinfo'], 'Revision')
        revision = cpuinfo['Revision']
        return revision in cls.MODELS

    @classmethod
    def _command_output(cls, cmd, key, default='ND') -> Dict[str, Optional[str]]:
        cmd = ' '.join(cmd + ['2>/dev/null', '||', 'echo', 'ND'])
        res = subprocess.check_output(cmd, shell=True)
        lines = res.decode('utf-8').split('\n')
        res = {
            key: default
        }
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


__all__ = [
    'RaspberryPi'
]
