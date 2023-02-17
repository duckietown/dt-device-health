from typing import Union

from dt_robot_utils import get_robot_configuration
from robot.types import Robot


def get_robot(configuration: Union[None, str] = None) -> Robot:
    # TODO: add DBR4
    from .duckiebot.db21m import DB21M
    from .duckiebot.db21j import DB21J

    known_robots = {
        'DB21M': DB21M,
        'DB21J': DB21J,
    }

    if configuration is None:
        configuration = get_robot_configuration().name
        print(f"Robot configuration not given. Using '{configuration}' from robot.")

    robot = known_robots.get(configuration, Robot)
    return robot()
