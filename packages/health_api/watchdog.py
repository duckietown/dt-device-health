import time

from dt_class_utils import DTProcess
from dt_module_utils import set_module_healthy, set_module_unhealthy

from health_api.resources import cached_resource
from health_api.constants import HEALTH_WATCHDOG_FREQUENZY_HZ


def health_watchdog():
    sleep_time = 1.0 / HEALTH_WATCHDOG_FREQUENZY_HZ
    process = DTProcess.get_instance()
    while not process.is_shutdown():
        res = cached_resource('status')
        if res['status'] == 'error':
            set_module_unhealthy()
        else:
            set_module_healthy()
        time.sleep(sleep_time)
