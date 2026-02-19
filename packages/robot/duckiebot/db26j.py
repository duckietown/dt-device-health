from typing import List
from robot.types import HardwareComponent, ComponentType, I2CBus, I2CBusAnyAddress, BusType
from .db21m import DB21M


class DB26J(DB21M):
    """
    DB26J - Duckiebot 2026 Jetson Orin Nano

    Similar hardware to DB21M (Jetson Nano) but without battery support.
    Front bumper and ToF sensors are optional hardware (not included by default).

    I2C bus differences from DB21M:
    - HAT/Motors: Bus 1 (same as DB21M)
    - Screen/IMU: Bus 7 (was bus 1 on DB21M)
    - Camera: Bus 2 (was bus 6 on DB21M)
    """

    # Bus 1: HAT and motors (inherited from DB21M)
    # I2C_HW_BUS_1 = I2CBus(BusType.I2C, 1) - inherited from parent

    # Bus 7: Screen, IMU, and sensors
    I2C_HW_BUS_7 = I2CBus(BusType.I2C, 7)
    # IMU can appear at 0x68 (MPU-6050) or 0x71 (knockoff variant) — mirrors imu_driver config
    I2C_HW_BUS_7_IMU = I2CBusAnyAddress(BusType.I2C, 7, candidate_addresses=["0x68", "0x71"])

    # Camera is on bus 2 (instead of bus 6 on DB21M)
    I2C_SW_TEGRA_ADAPTER_BUS = I2CBus(BusType.I2C, 2)

    # Front bumper mux would be on bus 2 if present, creating software buses 9 and 10
    # These bus definitions are kept for compatibility but not scanned (front bumper is optional)
    I2C_SW_FRONT_BUMPER_MUX_BUS_0 = I2CBus(BusType.I2C, 10, I2C_SW_TEGRA_ADAPTER_BUS)
    I2C_SW_FRONT_BUMPER_MUX_BUS_1 = I2CBus(BusType.I2C, 9, I2C_SW_TEGRA_ADAPTER_BUS)
    I2C_SW_FRONT_BUMPER_MUX_BUS_2 = I2CBus(BusType.I2C, 10, I2C_SW_TEGRA_ADAPTER_BUS)  # Reuse bus 10
    I2C_SW_FRONT_BUMPER_MUX_BUS_3 = I2CBus(BusType.I2C, 10, I2C_SW_TEGRA_ADAPTER_BUS)  # Reuse bus 10
    I2C_SW_FRONT_BUMPER_MUX_BUS_4 = I2CBus(BusType.I2C, 10, I2C_SW_TEGRA_ADAPTER_BUS)  # Reuse bus 10
    I2C_SW_FRONT_BUMPER_MUX_BUS_5 = I2CBus(BusType.I2C, 10, I2C_SW_TEGRA_ADAPTER_BUS)  # Reuse bus 10
    I2C_SW_FRONT_BUMPER_MUX_BUS_6 = I2CBus(BusType.I2C, 10, I2C_SW_TEGRA_ADAPTER_BUS)  # Reuse bus 10
    I2C_SW_FRONT_BUMPER_MUX_BUS_7 = I2CBus(BusType.I2C, 10, I2C_SW_TEGRA_ADAPTER_BUS)  # Reuse bus 10

    @staticmethod
    def get_i2c_buses() -> List[int]:
        """Get I2C buses for Jetson Orin Nano"""
        # Hardware buses: 0, 1 (HAT/motors), 2 (camera), 4, 5, 7 (screen/IMU)
        # Note: Mux buses 9, 10 only exist if optional front bumper is present
        return [0, 1, 2, 4, 5, 7]

    def _get_components(self) -> List[HardwareComponent]:
        """Get all DB21M components with corrected bus assignments, no battery, and optional front bumper"""
        components = super()._get_components()

        # Filter out battery (not present on DB26J)
        components = [c for c in components if c.type != ComponentType.BATTERY]

        # Update bus assignments and support status for components
        for component in components:
            # Screen moved from bus 1 to bus 7
            if component.key == 'screen':
                component.bus = self.I2C_HW_BUS_7
            # IMU moved from bus 1 to bus 7; can be at 0x68 (MPU-6050) or 0x71 (knockoff)
            elif component.key == 'imu':
                component.bus = self.I2C_HW_BUS_7_IMU
            # Front bumper mux is optional hardware - mark as not supported
            elif component.key == 'front-bumper':
                component.bus = self.I2C_SW_TEGRA_ADAPTER_BUS
                component.supported = False
            # Front-center ToF is connected directly to bus 7 (not via mux) - keep supported
            elif component.key == 'tof/front-center':
                component.bus = self.I2C_HW_BUS_7
                component.parent = None  # Not connected via mux
                component.supported = True
            # Other ToF sensors are on optional front bumper mux - mark as not supported
            elif component.type == ComponentType.TOF:
                component.supported = False

        return components


__all__ = ['DB26J']
