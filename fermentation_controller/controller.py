import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable

from simple_pid import PID

from .config import Config
from .runnable import Runnable
from .sensor import Sensor
from .switch import Switch


class ControllerListener(ABC):

    @abstractmethod
    def handle_controller(self, p: float, i: float, d: float, control: float) -> None:
        pass


@dataclass
class Controller(Runnable):
    config: Config
    sample_time: int
    threshold: float
    heater: Switch
    cooler: Switch
    limiter: Switch
    current_temp: Sensor
    fridge_temp: Sensor
    listeners: Iterable[ControllerListener]

    def __post_init__(self) -> None:
        self.pid = PID(Kp=self.config.get("p"),
                       Ki=self.config.get("i"),
                       Kd=self.config.get("d"),
                       setpoint=self.config.get("target"),
                       sample_time=self.sample_time)

        self.logger = logging.getLogger(__name__)

    def run(self) -> None:
        self.control()

    def shutdown(self) -> None:
        self.logger.info("Shutting down controller")

    def control(self) -> None:
        self.__update_tunings()

        control = self.pid(self.current_temp.get_average())
        (p, i, d) = self.pid.components

        self.logger.debug("Received control value %s, pid values: %s %s %s", control, p, i, d)
        self.__publish(p, i, d, control)

        if self.__limit():
            return

        self.__control_switches(control)

    def __publish(self, p: float, i: float, d: float, control: float) -> None:
        for l in self.listeners:
            l.handle_controller(p, i, d, control)

    def __update_tunings(self) -> None:
        p = self.config.get("p")
        i = self.config.get("i")
        d = self.config.get("d")
        cur_p, cur_i, cur_d = self.pid.tunings
        if p != cur_p or i != cur_i or d != cur_d:
            self.logger.info("Setting PID values to %s, %s, %s.", p, i, d)
            self.pid.tunings = (p, i, d)

    def __limit(self) -> bool:
        heating_limit = self.config.get("heating_limit")
        limit_window = self.config.get("limit_window")

        if self.limiter.get():
            if self.fridge_temp.get() < (heating_limit - limit_window):
                self.limiter.set(False)
            else:
                self.logger.debug("Skipping control, limiter enabled")
                return True
        elif self.fridge_temp.get() > heating_limit:
            self.limiter.set(True)
            return True

        return False

    def __control_switches(self, control: float) -> None:
        if abs(control) < self.threshold:
            if self.heater.get():
                self.heater.set(False)
            if self.cooler.get():
                self.cooler.set(False)
            return

        if control > 0:
            if self.cooler.get():
                self.cooler.set(False)
            if not self.heater.get():
                self.heater.set(True)
        if control < 0:
            if self.heater.get():
                self.heater.set(False)
            if not self.cooler.get():
                self.cooler.set(True)
        if control == 0:
            if self.cooler.get():
                self.cooler.set(False)
            if self.heater.get():
                self.heater.set(False)
