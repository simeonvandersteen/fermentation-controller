from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from threading import Event


@dataclass
class Runnable(ABC):
    stop_triggered: Event = field(default=Event(), init=False)

    def start(self, interval: int, init_delay: int) -> None:
        self.stop_triggered.wait(init_delay)
        while not self.stop_triggered.is_set():
            self.run()
            self.stop_triggered.wait(interval)
        self.shutdown()

    def stop(self) -> None:
        self.stop_triggered.set()

    @abstractmethod
    def run(self) -> None:
        pass

    @abstractmethod
    def shutdown(self) -> None:
        pass
