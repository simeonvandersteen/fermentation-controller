from abc import ABC, abstractmethod


class SwitchListener(ABC):

    @abstractmethod
    def handle_switch(self, name: str, on: bool):
        pass


class Switch(ABC):

    @abstractmethod
    def set(self, on: bool) -> None:
        pass

    @abstractmethod
    def get(self) -> bool:
        pass
