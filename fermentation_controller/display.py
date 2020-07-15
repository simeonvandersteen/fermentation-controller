import logging
from dataclasses import dataclass
from threading import Lock
from typing import List
from math import floor

from RPLCD import CharLCD
from RPi import GPIO

from .sensor import SensorListener
from .switch import SwitchListener


@dataclass
class Display(SensorListener, SwitchListener):
    sensor_names: List[str]
    switch_names: List[str]

    def __post_init__(self) -> None:
        self.logger = logging.getLogger(__name__)

        self.logger.debug("Initiating LCD")
        self.lcd = CharLCD(numbering_mode=GPIO.BCM, cols=16, rows=2, pin_rs=22, pin_e=17, pins_data=[26, 19, 13, 6])
        self.lcd.cursor_mode = 'hide'
        self.lcd.clear()

        self.write_lock = Lock()

    def handle_switch(self, name: str, on: bool) -> None:
        if name not in self.switch_names:
            self.logger.warning("'%s' is not configured to be printed to lcd", name)
            return

        y = self.switch_names.index(name)

        self.__write(14, y, name[0].upper() if on else " ")

    def handle_temperature(self, name: str, temperate: float) -> None:
        if name not in self.sensor_names:
            self.logger.warning("Device '%s' is not configured to be printed to LCD", name)
            return

        y = floor(self.sensor_names.index(name) / 2)
        x = (self.sensor_names.index(name) - 2 * y) * 7

        self.__write(x, y, "%s %s" % (name[0].upper(), round(temperate, 1)))

    def __write(self, x, y, text) -> None:
        self.logger.debug("Writing '%s' to LCD at (%s,%s)", text, x, y)
        with self.write_lock:
            self.lcd.cursor_pos = (y, x)
            self.lcd.write_string(text)

    def shutdown(self) -> None:
        self.logger.debug("Shutting down LCD")
        self.lcd.close(clear=True)
