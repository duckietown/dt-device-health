from typing import List
from robot.types import HardwareComponent, ComponentType
from .db21m import DB21M


class DB26J(DB21M):
    """
    DB26J - Duckiebot 2026 Jetson Orin Nano

    Similar hardware to DB21M (Jetson Nano) but without battery support.
    The Orin Nano does not include the USB battery controller found on DB21M/DB21J.
    """

    def _get_components(self) -> List[HardwareComponent]:
        """Get all DB21M components except battery"""
        components = super()._get_components()
        return [c for c in components if c.type != ComponentType.BATTERY]


__all__ = ['DB26J']
