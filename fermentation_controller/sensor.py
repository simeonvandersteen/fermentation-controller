from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterable
import logging

from .runnable import Runnable


class SensorListener(ABC):

    @abstractmethod
    def handle_temperature(self, name: str, temperate: float):
        pass


@dataclass
class Sensor(Runnable):
    name: str
    device_id: str
    device_dir: str
    listeners: Iterable[SensorListener]

    data: float = field(default=0.0, init=False)

    def __post_init__(self) -> None:
        self.device_file = "w1_slave"
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
            self.data = round(float(temp_str) / 1000.0, 1)
            logging.debug("Read %s from sensor '%s' (%s)", self.data, self.name, self.device_id)

            self.__publish(self.data)

    def __publish(self, value: float) -> None:
        for l in self.listeners:
            l.handle_temperature(self.name, value)

    def get(self) -> float:
        return self.data
