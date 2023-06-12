import dataclasses
import os
from datetime import datetime
from enum import IntEnum, Enum
from typing import Dict, Union, List, Set, Callable, Optional

import smbus


class BusType(IntEnum):
    UNKNOWN = 0
    I2C = 1
    SPI = 2
    USB = 3
    GPIO = 4

    def as_dict(self) -> Dict:
        return {
            "type": self.value,
            "description": self.name,
        }


class ComponentType(Enum):
    UNKNOWN = "UNKNOWN"
    IMU = "IMU - Inertial Measurement Unit"
    TOF = "ToF - Time-of-Flight sensor"
    SCREEN = "OLED Screen"
    CAMERA = "CSI Camera"
    BUS_MULTIPLEXER = "Bus Multiplexer"
    HAT = "Duckietown HAT"
    MOTOR = "Motor Driver"
    BATTERY = "Battery"
    WHEEL_ENCODER = "Wheel Encoder"
    BUTTON = "Button"
    LED_GROUP = "LED Group"


@dataclasses.dataclass
class Bus:
    type: BusType

    def detect(self):
        pass

    def has(self, address: Union[str, int]) -> bool:
        return False

    def as_dict(self) -> Dict:
        return self.type.as_dict()


@dataclasses.dataclass
class I2CBus(Bus):
    number: int
    parent: Union['I2CBus', None] = None
    _detections: Union[Set[str], None] = None

    def detect(self):
        if self._detections is not None:
            return
        try:
            _i2c_bus = smbus.SMBus(self.number)
        except FileNotFoundError:
            self._detections = set()
            raise RuntimeError(
                "I2C Bus #%d not found, check if enabled in config!" % self.number
            )
        # scan the bus
        found = set()
        for addr in range(0, 0x80):
            try:
                _i2c_bus.read_byte(addr)
            except OSError as e:
                if e.errno == 16:
                    found.add(hex(addr))
                continue
            found.add(hex(addr))
        # ---
        self._detections = found

    def has(self, address: Union[str, int]) -> bool:
        # run the detection step if we have not done it yet
        if self._detections is None:
            self.detect()
        # sanitize address
        address = hex(address) if isinstance(address, int) else address
        # we don't count those devices that we see because connected to the parent
        if self.parent and self.parent.has(address):
            return False
        # finally, we check for detections
        return address in self._detections

    def as_dict(self) -> Dict:
        return {
            "number": self.number,
            "parent": self.parent.as_dict() if self.parent else None,
            **self.type.as_dict()
        }


@dataclasses.dataclass
class I2CBusAnyOf(Bus):
    """
    Impersonated the I2C Bus hosting the given address
    """
    buses: List[I2CBus]
    address: Union[str, int]
    _matched: Optional[I2CBus] = None

    @property
    def number(self) -> int:
        if not self._matched:
            return self.buses[0].number
        return self._matched.number

    @property
    def parent(self) -> Optional[I2CBus]:
        if not self._matched:
            return self.buses[0].parent
        return self._matched.parent

    def detect(self):
        for bus in self.buses:
            try:
                if bus.has(self.address):
                    self._matched = bus
                    return
            except RuntimeError as e:
                print("WARNING", str(e))

    def has(self, address: Union[str, int]) -> bool:
        return self._matched is not None

    def as_dict(self) -> Dict:
        return {
            "number": self.number,
            "parent": self.parent.as_dict() if self.parent else None,
            **self.type.as_dict()
        }


@dataclasses.dataclass
class USBBus(Bus):
    number: int

    def as_dict(self) -> Dict:
        return {
            "number": self.number,
            **self.type.as_dict()
        }

    def has(self, address: Union[str, int]) -> bool:
        return os.path.exists(f"/dev/ttyACM{address}")


class GPIO(Bus):
    pass


Buses: Dict[str, Dict[int, Bus]]


@dataclasses.dataclass
class Calibration:
    needed: bool = False
    completed: bool = False
    time: Optional[datetime] = None

    def as_dict(self) -> Dict:
        return {
            "needed": self.needed,
            "completed": self.completed,
            "time": self.time.isoformat() if self.time else None
        }


@dataclasses.dataclass
class HardwareComponent:
    bus: Union[Bus, None]
    type: ComponentType
    name: str
    instance: int
    address: Union[str, int]
    parent: Union['HardwareComponent', None] = None
    supported: bool = False
    detected: bool = False
    calibration: Calibration = dataclasses.field(default_factory=Calibration)
    detection_tests: Optional[List[Callable]] = None
    detectable: bool = True

    def as_dict(self, compact: bool = False):
        return {
            "type": self.type.name,
            "instance": self.instance,
            "address": self.address
        } if compact else {
            "bus": self.bus.as_dict(),
            "type": self.type.name,
            "description": self.type.value,
            "name": self.name,
            "instance": self.instance,
            "address": self.address,
            "parent": self.parent.as_dict(compact=True) if self.parent else None,
            "supported": self.supported,
            "detected": self.detected,
            "detectable": self.detectable,
            "calibration": self.calibration.as_dict()
        }


class Robot:

    @staticmethod
    def get_i2c_buses() -> List[int]:
        return [1]

    def get_components(self) -> List[HardwareComponent]:
        return self._detect_components(self._get_components())

    def _get_components(self) -> List[HardwareComponent]:
        return []

    @staticmethod
    def _detect_components(components: List[HardwareComponent]) -> List[HardwareComponent]:
        # detect hardware
        for component in components:
            if component.bus:
                try:
                    component.bus.detect()
                except RuntimeError as e:
                    print("WARNING", str(e))
                component.detected = component.bus.has(component.address)
            if component.detection_tests:
                for test in component.detection_tests:
                    component.detected = component.detected and test()
        # ---
        return components

    def serialize_components(self) -> List[Dict]:
        components = self.get_components()
        return [component.as_dict() for component in components]
