import os

from health_api.machine import GenericMachine


class Virtual(GenericMachine):

    def get_voltage(self):
        # get Voltage
        res = {
            'volts': 0
        }
        return res

    def get_cpu_thermal_zone_name(self) -> str:
        return 'none'

    def get_firmware(self):
        res = {
            'date': {
                'day': 0,
                'month': 0,
                'year': 0
            },
            'version': "ND"
        }
        return {
            'firmware': res
        }

    def get_hardware(self):
        # get defaults
        res = {
            'hardware': {
                **self._default_hardware_info(),
                "board": "Virtual"
            }
        }
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
        return res

    @classmethod
    def is_instance_of(cls):
        return os.environ.get("ROBOT_HARDWARE", None) == "virtual"

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
        return {
            "gpu": {
                "percentage": 0,
                "temperature": 0,
                "power": 0,
                "memory": {
                    "total": 0,
                    "used": 0,
                    "free": 0,
                    "percentage": 0
                }
            }
        }

    @staticmethod
    def get_software():
        return {
            "software": {
                "base": {
                    "type": "virtual",
                    "version": "",
                },
                "date": {
                    "day": 0,
                    "month": 0,
                    "year": 0,
                },
                "version": "v0"
            }
        }


__all__ = [
    'Virtual'
]
