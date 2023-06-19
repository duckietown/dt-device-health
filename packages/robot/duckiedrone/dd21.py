import os
import subprocess
from datetime import datetime
from functools import partial
from os.path import isfile
from pathlib import Path
from typing import List, Optional

from dt_robot_utils import get_robot_name
from robot.types import \
    Robot, \
    HardwareComponent, \
    I2CBus, \
    BusType, \
    ComponentType, \
    Calibration, \
    USBBus

CALIBRATIONS_DIR = "/data/config/calibrations/"

CAM_INT_CALIB_FILE = os.path.join(CALIBRATIONS_DIR, "camera_intrinsic", f"{get_robot_name()}.yaml")
ACCEL_CALIB_FILE = os.path.join(CALIBRATIONS_DIR, "accelerometer", f"{get_robot_name()}.yaml")


class DD21(Robot):

    I2C_HW_BUS_1 = I2CBus(BusType.I2C, 1)
    USB_BUS_1 = USBBus(BusType.USB, 1)
    CSI_BUS_1 = USBBus(BusType.CSI, 1)

    @staticmethod
    def get_i2c_buses() -> List[int]:
        # Jetson HW i2c buses + fron bumper mux software i2c buses
        return [1]

    @staticmethod
    def get_file_mtime(filepath: str) -> Optional[datetime]:
        if os.path.exists(filepath):
            return datetime.fromtimestamp(Path(filepath).stat().st_mtime)

    def _get_components(self) -> List[HardwareComponent]:
        return [
            HardwareComponent(
                bus=DD21.I2C_HW_BUS_1,
                type=ComponentType.TOF,
                key="tof/height",
                name="ToF",
                description="ToF - Time-of-Flight sensor",
                instance=0,
                address="0x29",
                supported=True
            ),
            HardwareComponent(
                bus=DD21.USB_BUS_1,
                type=ComponentType.FLIGHT_CONTROLLER,
                key="flight-controller",
                name="Flight Controller",
                description="Flight Controller PCB",
                instance=0,
                address=0,
                supported=True,
                calibration=Calibration(
                    needed=True,
                    completed=isfile(ACCEL_CALIB_FILE),
                    time=self.get_file_mtime(ACCEL_CALIB_FILE)
                ),
                detection_tests=[
                    partial(os.path.exists, "/dev/ttyUSB0")
                ]
            ),
            HardwareComponent(
                bus=DD21.CSI_BUS_1,
                type=ComponentType.CAMERA,
                key="camera",
                name="IMX219 Camera Module",
                description="Robot's camera",
                instance=0,
                address=0,
                supported=True,
                calibration=Calibration(
                    needed=True,
                    completed=isfile(CAM_INT_CALIB_FILE),
                    time=self.get_file_mtime(CAM_INT_CALIB_FILE)
                ),
                detection_tests=[
                    lambda: "detected=1" in
                            subprocess.check_output(["vcgencmd", "get_camera"]).decode("utf-8")
                ]
            )
        ]
