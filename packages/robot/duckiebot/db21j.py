from typing import List, Optional
from typing import Type

from health_api.boards import NvidiaJetson
from robot.types import Robot, HardwareComponent, I2CBus, BusType, ComponentType, I2CBusAnyOf
from .db21m import DB21M


class _DB21J_Base(DB21M):

    def _get_components(self) -> List[HardwareComponent]:
        components: List[HardwareComponent] = super()._get_components()
        # make front bumper optional
        self.FRONT_BUMPER_I2C_MUX.supported = False
        # on the DB21J we support a ToF connected both to the front bumper or the main i2c bus
        for i in range(len(components)):
            component = components[i]
            # ToF #6 is the front-center
            if component.type == ComponentType.TOF and component.instance == 6:
                components[i].bus = I2CBusAnyOf(
                    BusType.I2C,
                    [self.I2C_SW_FRONT_BUMPER_MUX_BUS_6, self.I2C_HW_BUS_1],
                    "0x29"
                )
        # ---
        return components


class _DB21J_NanoA02(_DB21J_Base):
    pass


class _DB21J_NanoB01(_DB21J_Base):
    # The B01-based DB21J has a different mapping on the i2c bus due to an extra i2c-mux on the carrier board
    I2C_SW_FRONT_BUMPER_MUX_BUS_0 = I2CBus(BusType.I2C, 9, _DB21J_Base.I2C_HW_BUS_1)
    I2C_SW_FRONT_BUMPER_MUX_BUS_1 = I2CBus(BusType.I2C, 10, _DB21J_Base.I2C_HW_BUS_1)
    I2C_SW_FRONT_BUMPER_MUX_BUS_2 = I2CBus(BusType.I2C, 11, _DB21J_Base.I2C_HW_BUS_1)
    I2C_SW_FRONT_BUMPER_MUX_BUS_3 = I2CBus(BusType.I2C, 12, _DB21J_Base.I2C_HW_BUS_1)
    I2C_SW_FRONT_BUMPER_MUX_BUS_4 = I2CBus(BusType.I2C, 13, _DB21J_Base.I2C_HW_BUS_1)
    I2C_SW_FRONT_BUMPER_MUX_BUS_5 = I2CBus(BusType.I2C, 14, _DB21J_Base.I2C_HW_BUS_1)
    I2C_SW_FRONT_BUMPER_MUX_BUS_6 = I2CBus(BusType.I2C, 15, _DB21J_Base.I2C_HW_BUS_1)
    I2C_SW_FRONT_BUMPER_MUX_BUS_7 = I2CBus(BusType.I2C, 16, _DB21J_Base.I2C_HW_BUS_1)

    @staticmethod
    def get_i2c_buses() -> List[int]:
        # Jetson HW i2c buses + front bumper mux software i2c buses
        return [1, 2] + list(range(9, 17, 1))


DB21J: Type[Robot] = Robot


if NvidiaJetson.is_instance_of():
    if NvidiaJetson.is_A02():
        print("Detected Jetson Nano 4GB (Carrier Board: A02).")
        DB21J = _DB21J_NanoA02
    elif NvidiaJetson.is_B01():
        print("Detected Jetson Nano 4GB (Carrier Board: B01).")
        DB21J = _DB21J_NanoB01
    else:
        nano = NvidiaJetson()
        board = nano.get_hardware()
        hardware = board["hardware"]
        raise ValueError(f"Board {hardware} not supported!")


__all__ = [
    "DB21J"
]
