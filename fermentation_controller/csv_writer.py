import csv
import logging
import time
from dataclasses import dataclass
from typing import List

from .controller import ControllerListener
from .runnable import Runnable
from .sensor import SensorListener
from .switch import SwitchListener


@dataclass
class CsvWriter(Runnable, SensorListener, SwitchListener, ControllerListener):
    sensor_names: List[str]
    switch_names: List[str]

    def __post_init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.file = open('data.csv', 'a', newline='')
        self.writer = csv.writer(self.file)
        sensor_avgs = list(map(lambda name: name + "_avg", self.sensor_names))
        self.data = {name: 0 for name in
                     self.sensor_names + sensor_avgs + self.switch_names + ['p', 'i', 'd', 'control']}

    def run(self) -> None:
        self.writer.writerow([time.time()] + list(self.data.values()))
        self.file.flush()

    def shutdown(self) -> None:
        self.file.close()

    def handle_switch(self, name: str, on: bool) -> None:
        self.data[name] = int(on)

    def handle_temperature(self, name: str, temperature: float, avg_temperature: float) -> None:
        self.data[name] = temperature
        self.data[name + "_avg"] = avg_temperature

    def handle_controller(self, p: float, i: float, d: float, control: float) -> None:
        self.data['p'] = p
        self.data['i'] = i
        self.data['d'] = d
        self.data['control'] = control
