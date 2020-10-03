import json
from dataclasses import dataclass
from .runnable import Runnable


@dataclass
class Config(Runnable):
    filename: str

    def __post_init__(self) -> None:
        self.__load()

    def run(self) -> None:
        self.__load()

    def shutdown(self) -> None:
        pass

    def get(self, key: str):
        return self.config.get(key)

    def __load(self) -> None:
        with open(self.filename, 'r') as config_raw:
            self.config = json.load(config_raw)
