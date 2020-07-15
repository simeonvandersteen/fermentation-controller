from dataclasses import dataclass
import logging

from .sensor import Sensor
from .switch import Switch
from .runnable import Runnable

from simple_pid import PID


@dataclass
class Controller(Runnable):
    target_temp: float
    sample_time: int
    threshold: float
    heater: Switch
    cooler: Switch
    current_temp: Sensor

    def __post_init__(self) -> None:
        self.pid = PID(Kp=1.0, Ki=0.0, Kd=0.0,
                       setpoint=self.target_temp,
                       sample_time=self.sample_time)

        self.logger = logging.getLogger(__name__)

    def run(self) -> None:
        self.control()

    def shutdown(self) -> None:
        self.logger.debug("Shutting down controller")
        pass

    def control(self) -> None:
        control = self.pid(self.current_temp.get())
        self.logger.info("Received control value %s", control)

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
        else:
            if self.heater.get():
                self.heater.set(False)
            if not self.cooler.get():
                self.cooler.set(True)
