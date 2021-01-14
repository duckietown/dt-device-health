from health_api import logger
from health_api.knowledge_base import KnowledgeBase
from health_api.boards import get_board


machine = get_board()

resources = {
    'volts': machine.get_voltage,
    'temperature': machine.get_temperature,
    'memory': machine.get_memory,
    'swap': machine.get_swap,
    'cpu': machine.get_cpu,
    'disk': machine.get_disk,
    'firmware': machine.get_firmware,
    'hardware': machine.get_hardware,
    'status': machine.get_throttled,
    'battery': machine.get_battery
}

resource_ttl = {
    'volts': 1,
    'temperature': 1,
    'memory': 2,
    'swap': 5,
    'cpu': 1,
    'disk': 10,
    'firmware': -1,
    'hardware': -1,
    'status': 1,
    'battery': -1
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
