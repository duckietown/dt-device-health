import re
import time
import traceback
from logging import Logger
from threading import Thread

import serial
import yaml
from serial.tools.list_ports import grep as serial_grep

from dt_class_utils import DTReminder
from .constants import BATTERY_PCB16_READY_VID, BATTERY_PCB16_READY_PID, BATTERY_PCB16_BAUD_RATE
from .history import BatteryHistory

KELVIN_TO_CELSIUS = lambda k: k - 273.15


#
# This is a driver for the Duckietown Battery v1.
# The data passed to the given callback function is stored in a dictionary with the
# following structure.
#
#   {
#       "temperature": <float>,
#       "cell_voltage": <float>,
#       "input_voltage": <float>,
#       "current": <float>,
#       "cycle_count": <int>,
#       "percentage": <int>,
#       "time_to_empty": <int>,
#       "usb_out_1_voltage": <float>,
#       "usb_out_2_voltage": <float>
#   }
#
class Battery:

    def __init__(self, callback, logger: Logger = None):
        self._devices = []
        self._info = None
        self._data = None
        self._device = None
        self._command = None
        self._is_shutdown = False
        self._logger = logger
        if not callable(callback):
            raise ValueError('Callback must be a callable object.')
        self._callback = callback
        self._reset_reminder = DTReminder(period=5)
        self._worker = Thread(target=self._work)
        self._history = BatteryHistory()

    def start(self, block: bool = False, quiet: bool = True):
        if block:
            return self._work(quiet=quiet)
        else:
            self._worker.start()

    def join(self):
        if self._worker.is_alive():
            self._worker.join()

    def is_shutdown(self):
        return self._is_shutdown

    def shutdown(self):
        #   This is NOT a battery shutdown, it simply shuts down the drivers
        self._is_shutdown = True
        self.join()

    def turn_off(self, timeout: int = 20):
        #   This is a battery shutdown, the power will be cut off after `timeout` seconds
        timeout = f'{timeout}'.zfill(2)
        self._command = f'Q{timeout}'.encode('utf-8')

    @property
    def info(self):
        return self._info

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
        self._chew_on_data()

    def history(self):
        return self._history.get()

    def _find_device(self):
        vid_pid_match = "VID:PID={}:{}".format(BATTERY_PCB16_READY_VID, BATTERY_PCB16_READY_PID)
        ports = serial_grep(vid_pid_match)
        self._devices = [p.device for p in ports]  # ['/dev/ttyACM0', ...]

    def _chew_on_data(self):
        if self._data:
            self._callback(self._data)
            self._history.add(self._data)

    def _read_next(self, dev, quiet: bool = True):
        try:
            raw = dev.read_until().decode('utf-8')
            cleaned = re.sub(r"\x00\s*", "", raw).rstrip()
            cleaned = re.sub(r"-\s+", "-", cleaned)
            try:
                parsed = yaml.load(cleaned, yaml.SafeLoader)
                return parsed
            except yaml.YAMLError as e:
                if self._logger:
                    self._logger.error(str(e))
                return None
        except BaseException as e:
            if quiet:
                traceback.print_exc()
            else:
                raise e

    def _work(self, quiet: bool = True):
        while True:
            if self._is_shutdown:
                return
            # ---
            # if we don't have a battery device, search again
            if len(self._devices) == 0:
                self._find_device()
            # if we still don't have it, just sleep for 5 seconds
            if len(self._devices) == 0:
                self._logger.warning('No battery found. Retrying in 5 seconds.')
            else:
                # we have at least one candidate device, try reading
                for device in self._devices:
                    with serial.Serial(device, BATTERY_PCB16_BAUD_RATE) as dev:
                        # once the device is open, try reading from it forever
                        # break only on unknown errors
                        while True:
                            if self._is_shutdown:
                                return
                            # ---
                            if self._command is not None:
                                # there is a command to be sent, send it and continue
                                for _ in range(3):
                                    dev.write(self._command)
                                    dev.flush()
                                self._command = None
                                continue
                            if self._data is not None and self._info is None:
                                # we were able to read from the battery at least once, request ??
                                dev.write(b'??')
                                dev.flush()
                            # ---
                            try:
                                line = self._read_next(dev, quiet=quiet)
                                if line is None:
                                    continue
                                # first time we read?
                                if self._device is None:
                                    self._device = device
                                    self._logger.info('Battery found at {}.'.format(device))
                                # distinguish between 'data' packet and answer to '??'
                                if 'FirmwareVersion' in line:
                                    self._info = self._format_info(line)
                                elif 'SOC(%)' in line:
                                    self.data = self._format_data(line)
                            except BaseException as e:
                                if quiet:
                                    traceback.print_exc()
                                    break
                                raise e
            if self._logger:
                self._logger.warning('An error occurred while reading from the battery.')
            # allow 5 seconds for things to reset
            self._reset_reminder.reset()
            while not self._reset_reminder.is_time():
                if self._is_shutdown:
                    return
                time.sleep(0.5)

    @staticmethod
    def _format_data(data):
        return {
            "temperature": round(KELVIN_TO_CELSIUS(data['CellTemp(degK)']), 2),
            "cell_voltage": round(float(data['CellVoltage(mV)']) / 1000, 2),
            "input_voltage": round(float(data['ChargerVoltage(mV)']) / 1000, 2),
            "current": round(float(data['Current(mA)']) / 1000, 2),
            "cycle_count": data['CycleCount'],
            "percentage": data['SOC(%)'],
            "time_to_empty": int(data['TimeToEmpty(min)'] * 60),
            "usb_out_1_voltage": round(float(data['USB OUT-1(mV)']) / 1000, 2),
            "usb_out_2_voltage": round(float(data['USB OUT-2(mV)']) / 1000, 2)
        }

    @staticmethod
    def _format_info(info):
        boot_data = str(info["BootData"])
        firmware_version = str(info["FirmwareVersion"])
        major, minor, patch, *_ = firmware_version + "000"
        dd, mm, yy = boot_data[3:5], boot_data[5:7], boot_data[7:9]
        return {
            "firmware_version": f"v{major}.{minor}.{patch}",
            "boot": {
                "code_version": boot_data[0],
                "pcb_version": boot_data[1:3],
                "date": f"{mm}/{dd}/{yy}"
            },
            "serial_number": info["SerialNumber"]
        }
