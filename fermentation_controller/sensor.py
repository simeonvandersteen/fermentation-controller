import logging
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from typing import Iterable

from .runnable import Runnable


class SensorListener(ABC):

    @abstractmethod
    def handle_temperature(self, name: str, temperate: float, avg_temperature: float):
        pass


@dataclass
class Sensor(Runnable):
    name: str
    device_id: str
    device_dir: str
    average_window: int
    listeners: Iterable[SensorListener]

    current: float = field(default=0.0, init=False)
    average: float = field(default=0.0, init=False)

    def __post_init__(self) -> None:
        self.device_file = "w1_slave"
        self.data = deque([], self.average_window)
        self.logger = logging.getLogger(__name__)

    def run(self) -> None:
        self.read()

    def shutdown(self) -> None:
        self.logger.info("Shutting down sensor '%s' (%s)", self.name, self.device_id)

    def read(self) -> None:
        path = self.device_dir + "/" + self.device_id + "/" + self.device_file

        with open(path, "r") as file:
            lines = file.read().split("\n")
            if lines[0].strip()[-3:] != "YES":
                return

        temp_line = lines[1]
        temp_pos = temp_line.find("t=")
        temp_str = temp_line[temp_pos + 2:]

        self.current = float(temp_str) / 1000
        logging.debug("Read %s from sensor '%s' (%s)", self.current, self.name, self.device_id)

        # update moving average
        self.data.append(self.current)
        self.average = round(sum(self.data) / len(self.data), 1)

        self.__publish()

    def __publish(self) -> None:
        for l in self.listeners:
            l.handle_temperature(self.name, self.get(), self.get_average())

    def get(self) -> float:
        return self.current

    def get_average(self) -> float:
        return self.average
