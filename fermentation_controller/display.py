import logging
from dataclasses import dataclass
from math import floor
from typing import List

from RPLCD import CharLCD
from RPi import GPIO

from .runnable import Runnable
from .sensor import SensorListener
from .switch import SwitchListener


@dataclass
class Display(SensorListener, SwitchListener, Runnable):
    sensor_names: List[str]
    switch_names: List[str]

    def __post_init__(self) -> None:
        self.logger = logging.getLogger(__name__)

        self.logger.debug("Initiating LCD")
        # Use compatibility mode to avoid driver timing issues https://github.com/dbrgn/RPLCD/issues/70
        self.lcd = CharLCD(compat_mode=True, numbering_mode=GPIO.BCM, cols=16, rows=2, pin_rs=22, pin_e=17,
                           pins_data=[26, 19, 13, 6])

        self.sensor_data = {name: 0.0 for name in self.sensor_names}
        self.switch_data = {name: False for name in self.switch_names}

    def run(self) -> None:
        self.lcd.cursor_mode = 'hide'
        self.lcd.clear()

        for index, name in enumerate(self.sensor_names):
            y = floor(index / 2)
            x = (index - 2 * y) * 7

            self.__write(x, y, "%s %s" % (name[0].upper(), round(self.sensor_data[name], 1)))

        for index, name in enumerate(self.switch_names):
            self.__write(14, index, name[0].upper() if self.switch_data[name] else " ")

    def handle_switch(self, name: str, on: bool) -> None:
        if name not in self.switch_names:
            self.logger.warning("'%s' is not configured to be printed to lcd", name)
            return
        self.switch_data[name] = on

    def handle_temperature(self, name: str, temperature: float) -> None:
        if name not in self.sensor_names:
            self.logger.warning("Device '%s' is not configured to be printed to LCD", name)
            return
        self.sensor_data[name] = temperature

    def __write(self, x, y, text) -> None:
        self.logger.debug("Writing '%s' to LCD at (%s,%s)", text, x, y)
        self.lcd.cursor_pos = (y, x)
        self.lcd.write_string(text)

    def shutdown(self) -> None:
        self.logger.debug("Shutting down LCD")
        self.lcd.close(clear=True)
