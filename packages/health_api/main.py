from threading import Thread
from dt_class_utils import DTProcess, AppStatus
from dt_robot_utils import get_robot_type, RobotType

from health_api.api import HealthAPI
from health_api.constants import HEALTH_API_PORT
from health_api.watchdog import health_watchdog
from health_api.knowledge_base import KnowledgeBase

from battery_drivers import Battery


ROBOTS_WITH_BATTERY = [
    RobotType.DUCKIEBOT,
]


class HealthAPIApp(DTProcess):
    
    def __init__(self):
        super(HealthAPIApp, self).__init__('HealthAPI')
        self.status = AppStatus.RUNNING
        # spin a health watchdog thread
        self.watchdog = Thread(target=health_watchdog)
        self.watchdog.start()
        # spin the battery drivers
        cback = lambda d: KnowledgeBase.set('battery', {'battery': {'present': True, **d}}, -1)
        self.battery = None
        robot_type = get_robot_type()
        if robot_type in ROBOTS_WITH_BATTERY:
            self.battery = Battery(cback, self.logger)
            self.register_shutdown_callback(self.battery.shutdown)
            self.battery.start()
        # register shutdown callback
        self.register_shutdown_callback(self._terminate)
        # serve HTTP requests over the REST API
        self._api = HealthAPI(self)
        self._api.run(host='0.0.0.0', port=HEALTH_API_PORT)

    def _terminate(self):
        self.watchdog.join()
        if self.battery is not None:
            self.battery.join()
        exit(0)


if __name__ == '__main__':
    app = HealthAPIApp()
