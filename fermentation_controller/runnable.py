from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from time import sleep


@dataclass
class Runnable(ABC):
    alive: bool = field(default=True, init=False)

    def start(self, interval: int) -> None:
        while self.alive:
            self.run()
            sleep(interval)
        self.shutdown()

    def stop(self) -> None:
        self.alive = False

    @abstractmethod
    def run(self) -> None:
        pass

    @abstractmethod
    def shutdown(self) -> None:
        pass
