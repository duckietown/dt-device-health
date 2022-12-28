import abc
import datetime
import json

import psutil

from health_api.constants import MHz, DISK_IMAGE_STATS_FILE
from health_api import logger


class GenericMachine(abc.ABC):

    @staticmethod
    def get_memory():
        """
        Returns:

            {
                "memory": {
                    "total": <int, bytes>,
                    "used": <int, bytes>,
                    "free": <int, bytes>,
                    "percentage": <int, percentage(used)>
                }
            }
        """
        # get Memory stats
        mem_stats = psutil.virtual_memory()
        return {
            'memory': {
                'total': mem_stats.total,
                'used': mem_stats.used,
                'free': mem_stats.available,
                'percentage': mem_stats.percent,
            }
        }

    @staticmethod
    def get_swap():
        """
        Returns:

            {
                "swap": {
                    "total": <int, bytes>,
                    "used": <int, bytes>,
                    "free": <int, bytes>,
                    "percentage": <int, percentage(used)>
                }
            }
        """
        # get Swap stats
        swap_stats = psutil.swap_memory()
        return {
            'swap': {
                'total': swap_stats.total,
                'used': swap_stats.used,
                'free': swap_stats.free,
                'percentage': swap_stats.percent,
            }
        }

    @staticmethod
    def get_cpu():
        """
        Returns:

            {
                "cpu": {
                    "cores": <int>,
                    "frequency": {
                        "min": <int, Hz>,
                        "max": <int, Hz>,
                        "current": <int, Hz>
                    },
                    "percentage": <int, percentage(used)>
                }
            }
        """
        freq = psutil.cpu_freq()
        # get CPU usage
        return {
            'cpu': {
                'cores': psutil.cpu_count(),
                'frequency': {
                    'min': int(freq.min * MHz),
                    'max': int(freq.max * MHz),
                    'current': int(freq.current * MHz),
                },
                'percentage': psutil.cpu_percent()
            }
        }

    @staticmethod
    def get_disk():
        """
        Returns:

            {
                "disk": {
                    "total": <int, bytes>,
                    "used": <int, bytes>,
                    "free": <int, bytes>,
                    "percentage": <int, percentage(used)>
                }
            }
        """
        # get Disk usage
        disk_stats = psutil.disk_usage('/')
        return {
            'disk': {
                'total': disk_stats.total,
                'used': disk_stats.used,
                'free': disk_stats.free,
                'percentage': disk_stats.percent,
            }
        }

    @staticmethod
    def get_battery():
        """
        Returns:
            {
                "battery": {
                    "present": <bool>,
                    "charging": <bool>,
                    "temperature": <float, celsius>,
                    "cell_voltage": <float, volt>,
                    "input_voltage": <float, volt>,
                    "current": <float, ampere>,
                    "cycle_count": <int>,
                    "percentage": <int, charge left>,
                    "time_to_empty": <int, minutes>,
                    "usb_out_1_voltage": <float, volt>,
                    "usb_out_2_voltage": <float, volt>
                }
            }
        """
        # this is a fake resource provider, the battery drivers will write to the Knowledge Base
        return {
            'battery': {
                'present': False,
                'charging': False,
                'temperature': 0.0,
                'cell_voltage': 0.0,
                'input_voltage': 0.0,
                'current': 0.0,
                'cycle_count': 0,
                'percentage': 0,
                'time_to_empty': 0,
                'usb_out_1_voltage': 0.0,
                'usb_out_2_voltage': 0.0
            }
        }

    @staticmethod
    def get_battery_info():
        """
        Returns:
            {
                "boot": {
                    "version": <str,numeric>,
                    "date": <str,mm/dd/yy>,
                    "pcb_version": <str,numeric>
                },
                "version": <str,semantic_version>,
                "serial_number": <str>
            }
        """
        # this is a fake resource provider, the battery drivers will write to the Knowledge Base
        return {
            "version": "ND",
            "boot": {
                "version": "ND",
                "pcb_version": "ND",
                "date": "ND"
            },
            "serial_number": "ND"
        }

    def get_temperature(self):
        """
        Returns:

            {
                "temperature": <float, celsius>
            }
        """
        themal_zones = psutil.sensors_temperatures()
        temp = themal_zones.get(self.get_cpu_thermal_zone_name(), None)
        if temp is None or len(temp) <= 0:
            return 0.0
        return {
            "temperature": temp[0].current
        }

    @staticmethod
    def get_software():
        """
        Returns:

            {
                "software": {
                    "base": {
                        "type": <str, {"Nvidia Jetpack", "HypriotOS"}>,
                        "version": <str, semantic_version>
                    },
                    "date": {
                        "day": <int, 1-31>,
                        "month": <int, 1-12>,
                        "year": <int>,
                    },
                    "version": <str, semantic_version>
                }
            }
        """
        try:
            with open(DISK_IMAGE_STATS_FILE, 'rt') as fin:
                stats = json.load(fin)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(str(e))
            return GenericMachine._default_software_info()
        # parse stats
        date = datetime.datetime.fromtimestamp(stats['stamp'])
        # compile output
        return {
            "software": {
                "base": {
                    "type": stats['base_type'],
                    "version": stats['base_version'],
                },
                "date": {
                    "day": date.day,
                    "month": date.month,
                    "year": date.year,
                },
                "version": stats['version']
            }
        }

    @staticmethod
    def get_compatible():
        # get device tree base compatible
        with open('/sys/firmware/devicetree/base/compatible', 'rt') as fin:
            compatible = fin.read().replace('\x00', '')
        return compatible

    @staticmethod
    def _default_software_info():
        return {
            "software": {
                "base": {
                    "type": "ND",
                    "version": "ND"
                },
                "date": {
                    "day": 0,
                    "month": 0,
                    "year": 0,
                },
                "version": "ND"
            }
        }

    @staticmethod
    def _default_hardware_info():
        return {
            "release_date": "ND",
            "model": "ND",
            "revision": "ND",
            "memory": 0.0,
            "frequency": 0.0,
            "gpu": False,
            "notes": "ND"
        }

    @abc.abstractmethod
    def get_voltage(self):
        """
        Returns:

            {
                "volts": {
                    "core": <float, volt>,
                    "ram": <float, volt>,
                }
            }
        """
        pass

    @abc.abstractmethod
    def get_cpu_thermal_zone_name(self) -> str:
        """
        Returns the key to be used in the output of `psutil.sensors_temperatures()` to identify
        the CPU thermal zone.
        """
        pass

    @abc.abstractmethod
    def get_firmware(self):
        """
        Returns:

            {
                "firmware": {
                    "date": {
                        "day": <int, 1-31>,
                        "month": <int, 1-12>,
                        "year": <int>,
                    },
                    "version": <str, free-form>
                }
            }
        """
        pass

    @abc.abstractmethod
    def get_hardware(self):
        pass

    @abc.abstractmethod
    def get_throttled(self):
        pass

    @abc.abstractmethod
    def get_gpu(self):
        """
        Returns:

            {
                "gpu": {
                    "percentage": <int, percentage(used)>
                    "temperature": <float, celsius>
                    "power": <int, milliwatt>
                }
            }
        """
        pass

    @classmethod
    @abc.abstractmethod
    def is_instance_of(cls) -> bool:
        pass
