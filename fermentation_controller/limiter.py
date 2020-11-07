import logging
from dataclasses import dataclass, field
from typing import Iterable


from .switch import Switch, SwitchListener


@dataclass
class Limiter(Switch):
    name: str
    heater: Switch
    listeners: Iterable[SwitchListener]

    on: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.on = False

    def set(self, on: bool) -> None:
        logging.info("Switching '%s' %s", self.name, "on" if on else "off")
        self.on = on

        if on and self.heater.get():
            self.heater.set(False)
        self.__publish(self.on)

    def __publish(self, value: bool) -> None:
        for l in self.listeners:
            l.handle_switch(self.name, value)

    def get(self) -> bool:
        return self.on
