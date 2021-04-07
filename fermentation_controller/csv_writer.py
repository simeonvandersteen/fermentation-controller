import csv
import logging
import time
from dataclasses import dataclass

from .data_collector import DataCollector
from .runnable import Runnable


@dataclass
class CsvWriter(Runnable):
    collector: DataCollector

    def __post_init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.file = open('data.csv', 'a', newline='')
        self.writer = csv.writer(self.file)

    def run(self) -> None:
        data = self.collector.get_data_map()
        if data is None:
            self.logger.warning("No data was collected, skipping CSV write")
            return

        # writes fields in alphabetic order, prefixed with a timestamp
        self.writer.writerow([time.time()] + [v for k, v in sorted(data.items())])
        self.file.flush()

    def shutdown(self) -> None:
        self.file.close()
