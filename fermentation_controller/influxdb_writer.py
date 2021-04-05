import logging
import time
from dataclasses import dataclass
from typing import List

from influxdb import InfluxDBClient

from .config import Config
from .controller import ControllerListener
from .runnable import Runnable
from .sensor import SensorListener
from .switch import SwitchListener
from .csv_writer import CsvWriter

@dataclass
class InfluxDBWriter(CsvWriter):
    secrets: Config

    def __post_init__(self) -> None:
        self.logger = logging.getLogger(__name__)

        # Code duplication - prevent with super?
        sensor_avgs = list(map(lambda name: name + "_avg", self.sensor_names))
        self.data = {name: 0.0 for name in
                     self.sensor_names + sensor_avgs + self.switch_names + ['p', 'i', 'd', 'control']}
        # End code duplication

        self.client = InfluxDBClient(host=self.secrets.get("db_host"),
                                     port=self.secrets.get("db_port"),
                                     username=self.secrets.get("db_username"),
                                     password=self.secrets.get("db_password"))
        self.client.create_database(self.secrets.get("db_name"))
        self.client.switch_database(self.secrets.get("db_name"))

    def __create_json(self) -> None:
        current_time = int(time.time() * 1000000000)

        self.data_json = []
        for key in self.data:
            construct_json = [{"measurement":key,
                               "time": current_time,
                               "tags": {"env":self.secrets.get("env")},
                               "fields": {"value":float(self.data[key])}
                              }]
            self.data_json.append(construct_json)

    def run(self) -> None:
        self.__create_json()
        for measurement in self.data_json:
            write = self.client.write_points(measurement)
