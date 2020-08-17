import json
from dataclasses import dataclass


@dataclass
class Config:
    filename: str

    def __post_init__(self) -> None:
        self.__load()

    def get(self, key: str):
        return self.config.get(key)

    def reload(self) -> None:
        self.__load()

    def __load(self) -> None:
        with open(self.filename, 'r') as config_raw:
            self.config = json.load(config_raw)
