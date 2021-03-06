import json
import time
import serial
import subprocess
import traceback
from threading import Thread
from logging import Logger

from dt_class_utils import DTReminder

from .constants import BATTERY_VID, BATTERY_PID
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
        self._baud_rate = 9600
        self._data = None
        self._is_shutdown = False
        self._logger = logger
        if not callable(callback):
            raise ValueError('Callback must be a callable object.')
        self._callback = callback
        self._reset_reminder = DTReminder(period=5)
        self._worker = Thread(target=self._work)
        self._history = BatteryHistory()

    def start(self):
        self._worker.start()

    def join(self):
        self._worker.join()

    def shutdown(self):
        self._is_shutdown = True
        self._worker.join()

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
        self._chew_on_data()

    def history(self):
        return self._history.get()

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

    def _find_device(self):
        cmd = ['find_device_by_vid_pid', '{}:{}'.format(BATTERY_VID, BATTERY_PID)]
        # find USB devices
        results = subprocess.check_output(cmd)
        self._devices = [
            '/dev/{}'.format(devname) for devname in results.decode('utf-8').splitlines()
            if devname.startswith('tty')
        ]

    def _chew_on_data(self):
        if self._data:
            self._callback(self._data)
            self._history.add(self._data)

    def _work(self):
        while True:
            if self._is_shutdown:
                return
            # ---
            last_data = None
            # if we don't have a battery device, search again
            if len(self._devices) == 0:
                self._find_device()
            # if we still don't have it, just sleep for 5 seconds
            if len(self._devices) == 0:
                self._logger.warning('No battery found. Retrying in 5 seconds.')
            else:
                # we have at least one candidate device, try reading
                for device in self._devices:
                    with serial.Serial(device, self._baud_rate) as dev:
                        # once the device is open, try reading from it forever
                        # break only on unknown errors
                        while True:
                            if self._is_shutdown:
                                return
                            # ---
                            try:
                                last_data = raw = dev.read_until().decode('utf-8')
                                cleaned = raw.replace('\x00 ', '').replace('\x00', '').rstrip()
                                try:
                                    parsed = self._format_data(json.loads(cleaned))
                                    if self.data is None:
                                        self._logger.info('Battery found at {}.'.format(device))
                                    self.data = parsed
                                except json.JSONDecodeError:
                                    pass
                            except BaseException:
                                traceback.print_exc()
                                break
            if self._logger and last_data:
                self._logger.warning('An error occurred while reading from the battery.'
                                     'The data received was:\n'
                                     'BEGIN>{}<END'.format(last_data))
            # allow 5 seconds for things to reset
            self._reset_reminder.reset()
            while not self._reset_reminder.is_time():
                if self._is_shutdown:
                    return
                time.sleep(0.5)
