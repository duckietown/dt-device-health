import os
from datetime import datetime
from functools import partial
from os.path import isfile
from pathlib import Path
from typing import List, Optional

from dt_robot_utils import get_robot_name
from robot.types import Robot, HardwareComponent, I2CBus, BusType, ComponentType, Calibration, \
    USBBus, GPIO

CALIBRATIONS_DIR = "/data/config/calibrations/"

CAM_INT_CALIB_FILE = os.path.join(CALIBRATIONS_DIR, "camera_intrinsic", f"{get_robot_name()}.yaml")
CAM_EXT_CALIB_FILE = os.path.join(CALIBRATIONS_DIR, "camera_extrinsic", f"{get_robot_name()}.yaml")
KINEM_CALIB_FILE = os.path.join(CALIBRATIONS_DIR, "kinematics", f"{get_robot_name()}.yaml")


class DB21M(Robot):
    GPIO = GPIO(BusType.GPIO)
    # buses
    I2C_HW_BUS_1 = I2CBus(BusType.I2C, 1)
    I2C_HW_BUS_2 = I2CBus(BusType.I2C, 2)
    USB_BUS_1 = USBBus(BusType.USB, 1)
    I2C_SW_TEGRA_ADAPTER_BUS = I2CBus(BusType.I2C, 6)
    I2C_SW_FRONT_BUMPER_MUX_BUS_0 = I2CBus(BusType.I2C, 7, I2C_HW_BUS_1)
    I2C_SW_FRONT_BUMPER_MUX_BUS_1 = I2CBus(BusType.I2C, 8, I2C_HW_BUS_1)
    I2C_SW_FRONT_BUMPER_MUX_BUS_2 = I2CBus(BusType.I2C, 9, I2C_HW_BUS_1)
    I2C_SW_FRONT_BUMPER_MUX_BUS_3 = I2CBus(BusType.I2C, 10, I2C_HW_BUS_1)
    I2C_SW_FRONT_BUMPER_MUX_BUS_4 = I2CBus(BusType.I2C, 11, I2C_HW_BUS_1)
    I2C_SW_FRONT_BUMPER_MUX_BUS_5 = I2CBus(BusType.I2C, 12, I2C_HW_BUS_1)
    I2C_SW_FRONT_BUMPER_MUX_BUS_6 = I2CBus(BusType.I2C, 13, I2C_HW_BUS_1)
    I2C_SW_FRONT_BUMPER_MUX_BUS_7 = I2CBus(BusType.I2C, 14, I2C_HW_BUS_1)
    # components
    FRONT_BUMPER_I2C_MUX = HardwareComponent(
        bus=I2C_HW_BUS_1,
        type=ComponentType.BUS_MULTIPLEXER,
        key="front-bumper",
        name="Front Bumper",
        description="The front bumper hosting the I2C multiplexer",
        instance=0,
        address="0x70",
        supported=True
    )
    HAT = HardwareComponent(
        bus=I2C_HW_BUS_1,
        type=ComponentType.HAT,
        key="hat",
        name="Duckietown HAT",
        description="The Duckietown HAT connected to the GPIO header",
        instance=0,
        address="0x40",
        supported=True
    )

    @staticmethod
    def get_i2c_buses() -> List[int]:
        # Jetson HW i2c buses + fron bumper mux software i2c buses
        return [1, 2] + list(range(7, 15, 1))

    @staticmethod
    def get_file_mtime(filepath: str) -> Optional[datetime]:
        if os.path.exists(filepath):
            return datetime.fromtimestamp(Path(filepath).stat().st_mtime)

    def _get_components(self) -> List[HardwareComponent]:
        return [
            self.HAT,
            HardwareComponent(
                bus=self.USB_BUS_1,
                type=ComponentType.BATTERY,
                key="battery",
                name="DuckieBattery",
                description="",
                instance=0,
                # this will check for /dev/ttyACM[0]
                address=0,
                supported=True,
                test_service_name="robot_http_api_node/tests/battery",
            ),
            HardwareComponent(
                bus=self.I2C_SW_TEGRA_ADAPTER_BUS,
                type=ComponentType.CAMERA,
                key="camera",
                name="IMX219 Camera Module",
                description="Robot's camera",
                instance=0,
                address="0x10",
                supported=True,
                calibration=Calibration(
                    needed=True,
                    completed=isfile(CAM_INT_CALIB_FILE) and isfile(CAM_EXT_CALIB_FILE),
                    time=self.get_file_mtime(CAM_EXT_CALIB_FILE)
                ),
                detection_tests=[
                    partial(os.path.exists, "/dev/video0")
                ],
                test_service_name="camera_node/test",
            ),
            HardwareComponent(
                bus=self.I2C_HW_BUS_1,
                type=ComponentType.MOTOR,
                key="motor/left",
                name="Left Motor Driver",
                description="Motor controlling the left wheel",
                instance=0,
                address="0x40",
                supported=True,
                calibration=Calibration(
                    needed=True,
                    completed=isfile(KINEM_CALIB_FILE),
                    time=self.get_file_mtime(KINEM_CALIB_FILE)
                ),
                test_service_name="wheels_driver_node/tests/left",
            ),
            HardwareComponent(
                bus=self.I2C_HW_BUS_1,
                type=ComponentType.MOTOR,
                key="motor/right",
                name="Right Motor Driver",
                description="Motor controlling the right wheel",
                instance=0,
                address="0x40",
                supported=True,
                calibration=Calibration(
                    needed=True,
                    completed=isfile(KINEM_CALIB_FILE),
                    time=self.get_file_mtime(KINEM_CALIB_FILE)
                ),
                test_service_name="wheels_driver_node/tests/right",
            ),
            HardwareComponent(
                bus=self.GPIO,
                type=ComponentType.WHEEL_ENCODER,
                key="encoder/left",
                name="Left Wheel Encoder",
                description="Left wheel encoder measuring how much the wheel rotates",
                instance=0,
                address=18,
                supported=True,
                detectable=False,
                test_service_name="left_wheel_encoder_node/test",
            ),
            HardwareComponent(
                bus=self.GPIO,
                type=ComponentType.WHEEL_ENCODER,
                key="encoder/right",
                name="Right Wheel Encoder",
                description="Right wheel encoder measuring how much the wheel rotates",
                instance=0,
                address=19,
                supported=True,
                detectable=False,
                test_service_name="right_wheel_encoder_node/test",
            ),
            HardwareComponent(
                bus=self.I2C_HW_BUS_1,
                type=ComponentType.SCREEN,
                key="screen",
                name="Screen",
                description="OLED screen on the top plate of the robot",
                instance=0,
                address="0x3c",
                supported=True,
                test_service_name="display_driver_node/test",
            ),
            HardwareComponent(
                bus=self.I2C_HW_BUS_1,
                type=ComponentType.IMU,
                key="imu",
                name="IMU",
                description="IMU - Inertial Measurement Unit",
                instance=0,
                address="0x68",
                supported=True,
                test_service_name="imu_node/test",
            ),
            HardwareComponent(
                bus=self.GPIO,
                type=ComponentType.BUTTON,
                key="power-button",
                name="Power Button",
                description="The power button on the top plate of the robot",
                instance=0,
                address=40,
                supported=True,
                detectable=False,
                test_service_name="button_driver_node/test",
            ),
            HardwareComponent(
                bus=self.USB_BUS_1,
                type=ComponentType.USB_WIFI_DONGLE,
                key="wifi",
                name="Wifi Adapter",
                description="USB Wifi Dongle",
                instance=0,
                address="0",
                supported=True,
                detectable=False,
                test_service_name="robot_http_api_node/tests/wifi",
            ),
            HardwareComponent(
                bus=self.HAT.bus,
                type=ComponentType.LED_GROUP,
                key="leds/front",
                name="Front LEDs",
                description="LEDs on the front of the vehicle",
                instance=0,
                address="0x40",
                parent=self.HAT,
                supported=True,
                detectable=False,
                test_service_name="led_driver_node/tests/front",
            ),
            HardwareComponent(
                bus=self.HAT.bus,
                type=ComponentType.LED_GROUP,
                key="leds/back",
                name="Back LEDs",
                description="LEDs on the back of the vehicle",
                instance=0,
                address="0x40",
                parent=self.HAT,
                supported=True,
                detectable=False,
                test_service_name="led_driver_node/tests/back",
            ),
            self.FRONT_BUMPER_I2C_MUX,
            HardwareComponent(
                bus=self.I2C_SW_FRONT_BUMPER_MUX_BUS_0,
                type=ComponentType.TOF,
                key="tof/0",
                name="ToF",
                description="ToF - Time-of-Flight sensor",
                instance=0,
                address="0x29",
                parent=self.FRONT_BUMPER_I2C_MUX,
                supported=False
            ),
            HardwareComponent(
                bus=self.I2C_SW_FRONT_BUMPER_MUX_BUS_1,
                type=ComponentType.TOF,
                key="tof/1",
                name="ToF",
                description="ToF - Time-of-Flight sensor",
                instance=1,
                address="0x29",
                parent=self.FRONT_BUMPER_I2C_MUX,
                supported=False
            ),
            HardwareComponent(
                bus=self.I2C_SW_FRONT_BUMPER_MUX_BUS_2,
                type=ComponentType.TOF,
                key="tof/2",
                name="ToF",
                description="ToF - Time-of-Flight sensor",
                instance=2,
                address="0x29",
                parent=self.FRONT_BUMPER_I2C_MUX,
                supported=False
            ),
            HardwareComponent(
                bus=self.I2C_SW_FRONT_BUMPER_MUX_BUS_3,
                type=ComponentType.TOF,
                key="tof/3",
                name="ToF",
                description="ToF - Time-of-Flight sensor",
                instance=3,
                address="0x29",
                parent=self.FRONT_BUMPER_I2C_MUX,
                supported=False
            ),
            HardwareComponent(
                bus=self.I2C_SW_FRONT_BUMPER_MUX_BUS_4,
                type=ComponentType.TOF,
                key="tof/4",
                name="ToF",
                description="ToF - Time-of-Flight sensor",
                instance=4,
                address="0x29",
                parent=self.FRONT_BUMPER_I2C_MUX,
                supported=False
            ),
            HardwareComponent(
                bus=self.I2C_SW_FRONT_BUMPER_MUX_BUS_5,
                type=ComponentType.TOF,
                key="tof/5",
                name="ToF",
                description="ToF - Time-of-Flight sensor",
                instance=5,
                address="0x29",
                parent=self.FRONT_BUMPER_I2C_MUX,
                supported=False
            ),
            HardwareComponent(
                bus=self.I2C_SW_FRONT_BUMPER_MUX_BUS_6,
                type=ComponentType.TOF,
                key="tof/front-center",
                name="ToF",
                description="ToF - Time-of-Flight sensor",
                instance=6,
                address="0x29",
                parent=self.FRONT_BUMPER_I2C_MUX,
                supported=True,
                test_service_name="front_center_tof_driver_node/test",
            ),
            HardwareComponent(
                bus=self.I2C_SW_FRONT_BUMPER_MUX_BUS_7,
                type=ComponentType.TOF,
                key="tof/7",
                name="ToF",
                description="ToF - Time-of-Flight sensor",
                instance=7,
                address="0x29",
                parent=self.FRONT_BUMPER_I2C_MUX,
                supported=False
            )
        ]
