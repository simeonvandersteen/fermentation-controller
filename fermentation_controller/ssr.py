import logging
from dataclasses import dataclass, field
from typing import Iterable

from RPi import GPIO

from .switch import SwitchListener


@dataclass
class Ssr:
    name: str
    port: int
    listeners: Iterable[SwitchListener]

    on: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        self.logger = logging.getLogger(__name__)

        self.on = False

        GPIO.setup(self.port, GPIO.OUT)
        GPIO.output(self.port, GPIO.LOW)

    def set(self, on: bool) -> None:
        logging.debug("Switching '%s' %s", self.name, "on" if on else "off")
        GPIO.output(self.port, GPIO.HIGH if on else GPIO.LOW)
        self.on = on
        self.__publish(self.on)

    def __publish(self, value: bool) -> None:
        for l in self.listeners:
            l.handle_switch(self.name, value)

    def get(self) -> bool:
        return self.on

    def shutdown(self) -> None:
        logging.debug("Shutting down switch '%s'", self.name)
        GPIO.cleanup()
