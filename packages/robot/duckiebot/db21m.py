from typing import List

from robot.types import Robot, HardwareComponent, I2CBus, BusType, ComponentType


class DB21M(Robot):

    I2C_HW_BUS_1 = I2CBus(BusType.I2C, 1)
    I2C_HW_BUS_2 = I2CBus(BusType.I2C, 2)
    I2C_SW_TEGRA_ADAPTER_BUS = I2CBus(BusType.I2C, 6)
    I2C_SW_FRONT_BUMPER_MUX_BUS_0 = I2CBus(BusType.I2C, 7, I2C_HW_BUS_1)
    I2C_SW_FRONT_BUMPER_MUX_BUS_1 = I2CBus(BusType.I2C, 8, I2C_HW_BUS_1)
    I2C_SW_FRONT_BUMPER_MUX_BUS_2 = I2CBus(BusType.I2C, 9, I2C_HW_BUS_1)
    I2C_SW_FRONT_BUMPER_MUX_BUS_3 = I2CBus(BusType.I2C, 10, I2C_HW_BUS_1)
    I2C_SW_FRONT_BUMPER_MUX_BUS_4 = I2CBus(BusType.I2C, 11, I2C_HW_BUS_1)
    I2C_SW_FRONT_BUMPER_MUX_BUS_5 = I2CBus(BusType.I2C, 12, I2C_HW_BUS_1)
    I2C_SW_FRONT_BUMPER_MUX_BUS_6 = I2CBus(BusType.I2C, 13, I2C_HW_BUS_1)
    I2C_SW_FRONT_BUMPER_MUX_BUS_7 = I2CBus(BusType.I2C, 14, I2C_HW_BUS_1)

    @staticmethod
    def get_i2c_buses() -> List[int]:
        # Jetson HW i2c buses + fron bumper mux software i2c buses
        return [1, 2] + list(range(7, 15, 1))

    def _get_components(self) -> List[HardwareComponent]:
        i2c_mux = HardwareComponent(
            bus=DB21M.I2C_HW_BUS_1,
            type=ComponentType.BUS_MULTIPLEXER,
            name="I2C Multiplexer",
            instance=0,
            address="0x70",
            supported=True
        )
        # ---
        return [
            HardwareComponent(
                bus=DB21M.I2C_HW_BUS_1,
                type=ComponentType.HAT,
                name="Duckietown Hat",
                instance=0,
                address="0x40",
                supported=True
            ),
            HardwareComponent(
                bus=DB21M.I2C_SW_TEGRA_ADAPTER_BUS,
                type=ComponentType.CAMERA,
                name="IMX219 Camera Module",
                instance=0,
                address="0x10",
                supported=True
            ),
            HardwareComponent(
                bus=DB21M.I2C_HW_BUS_1,
                type=ComponentType.SCREEN,
                name="Screen",
                instance=0,
                address="0x3c",
                supported=True
            ),
            HardwareComponent(
                bus=DB21M.I2C_HW_BUS_1,
                type=ComponentType.IMU,
                name="IMU",
                instance=0,
                address="0x68",
                supported=True
            ),
            i2c_mux,
            HardwareComponent(
                bus=DB21M.I2C_SW_FRONT_BUMPER_MUX_BUS_0,
                type=ComponentType.TOF,
                name="ToF",
                instance=0,
                address="0x29",
                parent=i2c_mux,
                supported=False
            ),
            HardwareComponent(
                bus=DB21M.I2C_SW_FRONT_BUMPER_MUX_BUS_1,
                type=ComponentType.TOF,
                name="ToF",
                instance=1,
                address="0x29",
                parent=i2c_mux,
                supported=False
            ),
            HardwareComponent(
                bus=DB21M.I2C_SW_FRONT_BUMPER_MUX_BUS_2,
                type=ComponentType.TOF,
                name="ToF",
                instance=2,
                address="0x29",
                parent=i2c_mux,
                supported=False
            ),
            HardwareComponent(
                bus=DB21M.I2C_SW_FRONT_BUMPER_MUX_BUS_3,
                type=ComponentType.TOF,
                name="ToF",
                instance=3,
                address="0x29",
                parent=i2c_mux,
                supported=False
            ),
            HardwareComponent(
                bus=DB21M.I2C_SW_FRONT_BUMPER_MUX_BUS_4,
                type=ComponentType.TOF,
                name="ToF",
                instance=4,
                address="0x29",
                parent=i2c_mux,
                supported=False
            ),
            HardwareComponent(
                bus=DB21M.I2C_SW_FRONT_BUMPER_MUX_BUS_5,
                type=ComponentType.TOF,
                name="ToF",
                instance=5,
                address="0x29",
                parent=i2c_mux,
                supported=False
            ),
            HardwareComponent(
                bus=DB21M.I2C_SW_FRONT_BUMPER_MUX_BUS_6,
                type=ComponentType.TOF,
                name="ToF",
                instance=6,
                address="0x29",
                parent=i2c_mux,
                supported=True
            ),
            HardwareComponent(
                bus=DB21M.I2C_SW_FRONT_BUMPER_MUX_BUS_7,
                type=ComponentType.TOF,
                name="ToF",
                instance=7,
                address="0x29",
                parent=i2c_mux,
                supported=False
            )
        ]