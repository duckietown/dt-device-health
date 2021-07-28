from typing import Union

from dt_robot_utils import get_robot_configuration
from robot.types import Robot


def get_robot(configuration: Union[None, str] = None) -> Robot:
    from .duckiebot.db21m import DB21M

    known_robots = {
        'DB21M': DB21M,
    }

    if configuration is None:
        configuration = get_robot_configuration().name
        print(f"Robot configuration not given. Using '{configuration}' from robot.")

    robot = known_robots.get(configuration, Robot)
    return robot()
