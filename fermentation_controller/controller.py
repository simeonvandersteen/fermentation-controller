import logging
from dataclasses import dataclass

from simple_pid import PID

from .config import Config
from .runnable import Runnable
from .sensor import Sensor
from .switch import Switch


@dataclass
class Controller(Runnable):
    config: Config
    sample_time: int
    threshold: float
    heater: Switch
    cooler: Switch
    current_temp: Sensor

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
        self.logger.debug("Shutting down controller")

    def control(self) -> None:
        self.__update_tunings()

        control = self.pid(self.current_temp.get())
        self.logger.info("Received control value %s", control)

        if abs(control) < self.threshold:
            if self.heater.get():
                self.heater.set(False)
            if self.cooler.get():
                self.cooler.set(False)
            return

        if control >= 0:
            if self.cooler.get():
                self.cooler.set(False)
            if not self.heater.get():
                self.heater.set(True)
        if control <= 0:
            if self.heater.get():
                self.heater.set(False)
            if not self.cooler.get():
                self.cooler.set(True)

    def __update_tunings(self) -> None:
        p = self.config.get("p")
        i = self.config.get("i")
        d = self.config.get("d")
        cur_p, cur_i, cur_d = self.pid.tunings
        if p != cur_p or i != cur_i or d != cur_d:
            self.logger.debug("Setting PID values to %s, %s, %s.", p, i, d)
            self.pid.tunings = (p, i, d)
