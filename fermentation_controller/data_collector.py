import logging
from dataclasses import dataclass
from typing import List

from .controller import ControllerListener
from .sensor import SensorListener
from .switch import SwitchListener


@dataclass
class DataCollector(SensorListener, SwitchListener, ControllerListener):
    sensor_names: List[str]
    switch_names: List[str]

    def __post_init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.valid_fields = \
            list(map(lambda name: name + "_avg", self.sensor_names)) + \
            self.sensor_names + self.switch_names + \
            ['p', 'i', 'd', 'control']
        self.data = {}

    def handle_switch(self, name: str, on: bool) -> None:
        if self.__is_valid_field(name):
            self.data[name] = int(on)

    def handle_temperature(self, name: str, temperature: float, avg_temperature: float) -> None:
        if self.__is_valid_field(name):
            self.data[name] = temperature
            self.data[name + "_avg"] = avg_temperature

    def handle_controller(self, p: float, i: float, d: float, control: float) -> None:
        self.data['p'] = p
        self.data['i'] = i
        self.data['d'] = d
        self.data['control'] = control

    def get_data_map(self):
        return None if len(self.data) != len(self.valid_fields) else self.data

    def __is_valid_field(self, name) -> bool:
        if name not in self.valid_fields:
            self.logger.warning("Ignoring field %s, not configured!", name)
            return False
        return True
