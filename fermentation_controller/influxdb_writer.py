import logging
import time
from dataclasses import dataclass

from influxdb import InfluxDBClient

from .config import Config
from .data_collector import DataCollector
from .runnable import Runnable


@dataclass
class InfluxDBWriter(Runnable):
    secrets: Config
    collector: DataCollector

    def __post_init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.client = InfluxDBClient(host=self.secrets.get("db_host"),
                                     port=self.secrets.get("db_port"),
                                     username=self.secrets.get("db_username"),
                                     password=self.secrets.get("db_password"))
        self.client.create_database(self.secrets.get("db_name"))
        self.client.switch_database(self.secrets.get("db_name"))

    def __create_json(self):
        data = self.collector.get_data_map()
        if data is None:
            return

        current_time = int(time.time() * 1000000000)
        data_json = []
        for key in data:
            construct_json = [{"measurement": key,
                               "time": current_time,
                               "tags": {"env": self.secrets.get("env")},
                               "fields": {"value": float(data[key])}
                               }]
            data_json.append(construct_json)
        return data_json

    def run(self) -> None:
        data = self.__create_json()
        if data is None:
            self.logger.warning("No data was collected, skipping InfluxDB write")
            return

        for measurement in data:
            self.client.write_points(measurement)

    def shutdown(self) -> None:
        pass
