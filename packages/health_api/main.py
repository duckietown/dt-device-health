import sys
from dt_class_utils import DTProcess, AppStatus

from health_api.api import HealthAPI
from health_api.constants import HEALTH_API_PORT


class HealthAPIApp(DTProcess):
    
    def __init__(self):
        super(HealthAPIApp, self).__init__('HealthAPI')
        self._api = HealthAPI()
        self.status = AppStatus.RUNNING
        # register shutdown callback
        self.register_shutdown_callback(_kill)
        # serve HTTP requests over the REST API
        self._api.run(host='0.0.0.0', port=HEALTH_API_PORT)


def _kill():
    sys.exit(0)


if __name__ == '__main__':
    app = HealthAPIApp()
