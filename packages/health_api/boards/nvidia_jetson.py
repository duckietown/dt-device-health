import os
import subprocess
from datetime import datetime
from typing import Optional, List

import jtop

from health_api.constants import GB, GHz
from health_api.knowledge_base import KnowledgeBase
from health_api.machine import GenericMachine, I2CBusDescriptor
from health_api.memory_util import poll_meminfo


class NvidiaJetson(GenericMachine):
    # NOTE: strings taken from here:
    # https://docs.nvidia.com/jetson/l4t/index.html#page/Tegra%2520Linux%2520Driver%2520Package%2520Development%2520Guide%2Fhw_setup_jetson_io.html%23wwpID0E0TB0HA
    MODELS = {
        "nvidia,p3542-0000+p3448-0003nvidia": {
            "release_date": "Q4 2020",
            "model": "Nano 2GB",
            "revision": "",
            "memory": 2 * GB,
            "frequency": 1.4 * GHz,
            "gpu": True,
            "notes": ""
        },
        "nvidia,p3449-0000-a02+p3448-0000-a02": {
            "release_date": "Q2 2019",
            "model": "Nano",
            "revision": "A02",
            "memory": 4 * GB,
            "frequency": 1.4 * GHz,
            "gpu": True,
            "notes": ""
        },
        "nvidia,p3449-0000-b00+p3448-0000-b00": {
            "release_date": "Q2 2019",
            "model": "Nano",
            "revision": "B01",
            "memory": 4 * GB,
            "frequency": 1.4 * GHz,
            "gpu": True,
            "notes": ""
        },
        "nvidia,p2597-0000+p3310-1000": {
            "release_date": "Q2 2017",
            "model": "TX2",
            "revision": "",
            "memory": 8 * GB,
            "frequency": 2.0 * GHz,
            "gpu": True,
            "notes": ""
        },
        "nvidia,p2822-0000+p2888-0001": {
            "release_date": "Q4 2018",
            "model": "AGX Xavier",
            "revision": "",
            "memory": 32 * GB,
            "frequency": 2.2 * GHz,
            "gpu": True,
            "notes": ""
        },
        "nvidia,p2597-0000+p2180-1000": {
            "release_date": "Q4 2015",
            "model": "TX1",
            "revision": "",
            "memory": 4 * GB,
            "frequency": 1.7 * GHz,
            "gpu": True,
            "notes": ""
        }
    }

    def get_voltage(self):
        return {
            "volts": {
                "core": 0.0,
                "ram": 0.0,
            }
        }

    def get_cpu_thermal_zone_name(self) -> str:
        return 'thermal-fan-est'

    def get_firmware(self):
        # get JetPack date
        day, month, year = 0, 0, 0
        # noinspection PyBroadException
        try:
            with open('/etc/nv_tegra_release', 'rt') as fin:
                datestr = fin.read().strip().split(',')[-1].strip().split(':', 1)[-1].strip()
                date = datetime.strptime(datestr, '%a %b %d %H:%M:%S UTC %Y')
                day, month, year = date.strftime("%d"), date.strftime("%-m"), date.strftime("%Y")
        except BaseException:
            pass
        # get JetPack version
        jtop_dir = jtop.__path__[0]
        jtop_vars = os.path.join(jtop_dir, 'jetson_variables')
        cmd = f'. "{jtop_vars}" && env'
        # noinspection PyBroadException
        try:
            env = subprocess.check_output(cmd, shell=True, stderr=subprocess.PIPE).decode('utf-8')
            env = {k[0]: k[1]
                   for k in map(lambda p: tuple(p.split('=', 1)), env.strip().split('\n'))}
        except BaseException:
            env = {}
        version = env.get('JETSON_JETPACK', "ND")
        # assemble response
        return {
            'firmware': {
                'date': {
                    'day': int(day),
                    'month': int(month),
                    'year': int(year)
                },
                'version': version
            }
        }

    @classmethod
    def is_instance_of(cls):
        compatible = cls.get_compatible()
        return compatible.startswith('nvidia,')

    @classmethod
    def is_4gb(cls):
        board = cls.get_hardware()
        return cls.is_instance_of() and board["hardware"]["model"] == "Nano"

    @classmethod
    def is_2gb(cls):
        board = cls.get_hardware()
        return cls.is_instance_of() and board["hardware"]["model"] == "Nano 2GB"

    @classmethod
    def is_A02(cls):
        carrier_board: str = cls._get_carrier_board()
        return cls.is_instance_of() and cls.is_4gb() and carrier_board == "A02"

    @classmethod
    def is_B01(cls):
        carrier_board: str = cls._get_carrier_board()
        return cls.is_instance_of() and cls.is_4gb() and carrier_board == "B01"

    @classmethod
    def get_hardware(cls):
        # get defaults
        res = {'hardware': cls._default_hardware_info()}
        # get Jetson board model
        compatible = cls.get_compatible()
        res['hardware']['board'] = 'Nvidia Jetson'
        for model in cls.MODELS:
            if model in compatible:
                info = cls.MODELS[model]
                res['hardware'].update(info)
                break
        # ---
        return res

    def get_throttled(self):
        return {
            'throttling': {
                'under-voltage-now': False,
                'freq-capped-now': False,
                'throttling-now': False,
                'under-voltage-occurred': False,
                'freq-capped-occurred': False,
                'throttling-occurred': False
            },
            'status': 'ok',
            'status_msgs': []
        }

    def get_gpu(self):
        """
        Returns:
        {
            "gpu": {
                "percentage": <int, percentage(used)>
                "temperature": <float, celsius>
                "power": <float, watt>
                "memory": {
                    "total": <int, bytes>,
                    "used": <int, bytes>,
                    "free": <int, bytes>,
                    "percentage": <int, percentage(used)>
                }
            }
        }
        """
        mem_info = poll_meminfo()  # Value in kB
        mem_used = mem_info.get("NvMapMemUsed", {}).get('val', 0) * 1024
        mem_free = mem_info.get("NvMapMemFree", {}).get('val', 0) * 1024
        mem_total = mem_free + mem_used
        mem_percentage = round(mem_used / mem_total * 100, 2)
        res = {
            "gpu": {
                "percentage": KnowledgeBase.get("GPU_USAGE", 0),
                "temperature": KnowledgeBase.get("GPU_TEMP", 0),
                "power": KnowledgeBase.get("GPU_POWER", 0),
                "memory": {
                    "total": mem_total,
                    "used": mem_used,
                    "free": mem_free,
                    "percentage": mem_percentage
                }
            }
        }
        return res

    @classmethod
    def _get_carrier_board(cls) -> Optional[str]:
        i2cbuses: List[I2CBusDescriptor] = NvidiaJetson.get_i2c_buses()
        # find all i2c buses with "i2c-6-mux" in the name
        mux6: int = len(list(filter(lambda b: b.name.startswith("i2c-6-mux"), i2cbuses)))
        # the carrier board B01 has 2 of such buses, while A02 has none
        if mux6 == 0:
            return "A02"
        elif mux6 == 2:
            return "B01"
        else:
            raise ValueError(f"Carrier board has {mux6} 'i2c-6-mux' buses, unknown board.")


__all__ = [
    'NvidiaJetson'
]
