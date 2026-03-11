import abc
import dataclasses
import datetime
import glob
import json
import os
import re
import subprocess
from typing import List, Optional

import psutil

from dt_robot_utils import get_robot_hardware, RobotHardware
from health_api.constants import MHz, DISK_IMAGE_STATS_FILE
from health_api import logger


@dataclasses.dataclass
class I2CBusDescriptor:
    number: int
    name: str
    description: str


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

    # Fallback thermal zone names to try if the primary one is not found
    THERMAL_ZONE_FALLBACKS = ['cpu-thermal', 'cpu_thermal', 'thermal-fan-est', 'coretemp', 'soc-thermal']

    @staticmethod
    def _read_thermal_zone_sysfs(zone_type: str) -> Optional[float]:
        """Read temperature directly from sysfs for a given thermal zone type.

        This bypasses psutil, which crashes on boards where some thermal zones
        return 'Resource temporarily unavailable' (e.g., Orin Nano cv0/cv1/cv2).

        Args:
            zone_type: The thermal zone type name (e.g., 'cpu-thermal').

        Returns:
            Temperature in Celsius, or None if the zone is not found or unreadable.
        """
        for zone_dir in sorted(glob.glob('/sys/class/thermal/thermal_zone*')):
            try:
                with open(os.path.join(zone_dir, 'type'), 'r') as f:
                    if f.read().strip() != zone_type:
                        continue
                with open(os.path.join(zone_dir, 'temp'), 'r') as f:
                    return int(f.read().strip()) / 1000.0
            except (IOError, OSError, ValueError):
                continue
        return None

    def get_temperature(self):
        """
        Returns:

            {
                "temperature": <float, celsius>
            }
        """
        # First, try psutil (works on Jetson Nano, Raspberry Pi, etc.)
        try:
            thermal_zones = psutil.sensors_temperatures()
            if thermal_zones:
                # try the board-specific thermal zone first
                zone_name = self.get_cpu_thermal_zone_name()
                temp = thermal_zones.get(zone_name, None)
                # if not found, try common fallback zone names
                if temp is None or len(temp) <= 0:
                    for fallback in self.THERMAL_ZONE_FALLBACKS:
                        temp = thermal_zones.get(fallback, None)
                        if temp is not None and len(temp) > 0:
                            break
                if temp is not None and len(temp) > 0:
                    current = temp[0].current
                    if current is not None:
                        return {"temperature": current}
        except (TypeError, ValueError, AttributeError):
            # psutil crashes on some boards (e.g., Orin Nano) where thermal zone
            # files exist but some return 'Resource temporarily unavailable',
            # causing float(None) inside psutil
            pass

        # Fallback: read directly from sysfs, trying primary zone then fallbacks
        for zone_type in [self.get_cpu_thermal_zone_name()] + self.THERMAL_ZONE_FALLBACKS:
            temp_c = self._read_thermal_zone_sysfs(zone_type)
            if temp_c is not None:
                return {"temperature": temp_c}

        logger.warning("No readable thermal zone found")
        return {"temperature": 0.0}

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
        robot_hw = get_robot_hardware()
        # get device tree base compatible
        if robot_hw not in [RobotHardware.VIRTUAL]:
            with open('/sys/firmware/devicetree/base/compatible', 'rt') as fin:
                compatible = fin.read().replace('\x00', '')
        else:
            compatible = "duckietown,virtual"
        return compatible

    @staticmethod
    def get_i2c_buses() -> List[I2CBusDescriptor]:
        buses: List[I2CBusDescriptor] = []
        cmdout = subprocess.check_output(['i2cdetect', '-l']).decode("utf8")
        pattern = re.compile(r'^i2c-([0-9]+)\s*\t(i2c)\s*\t([^t]+)\s*\t(.*)$', re.MULTILINE)
        for i2cbus in pattern.finditer(cmdout):
            buses.append(I2CBusDescriptor(
                number=int(i2cbus.group(1)),
                name=i2cbus.group(3),
                description=i2cbus.group(4)
            ))
        return buses

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
        pass

    @classmethod
    @abc.abstractmethod
    def is_instance_of(cls) -> bool:
        pass
