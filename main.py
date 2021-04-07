import logging
import signal
from threading import Thread, Event

from fermentation_controller.config import Config
from fermentation_controller.controller import Controller
from fermentation_controller.csv_writer import CsvWriter
from fermentation_controller.data_collector import DataCollector
from fermentation_controller.influxdb_writer import InfluxDBWriter
from fermentation_controller.display import Display
from fermentation_controller.limiter import Limiter
from fermentation_controller.sensor import Sensor
from fermentation_controller.ssr import Ssr

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

shutdown = Event()


def start_shutdown(signum, frame):
    global shutdown
    shutdown.set()


signal.signal(signal.SIGINT, start_shutdown)
signal.signal(signal.SIGTERM, start_shutdown)


def main():
    config = Config("./config.json")
    secrets = Config("./secret.json")

    display = Display(["environment", "vessel", "fridge", "target"], ["heater", "cooler", "limiter"])
    display.handle_temperature("target", config.get("target"), config.get("target"))

    data_collector = DataCollector(["environment", "vessel", "fridge", "target"],
                                   ["heater", "cooler", "limiter"])
    csv_writer = CsvWriter(data_collector)
    influxdb_writer = InfluxDBWriter(secrets, data_collector)

    data_collector.handle_temperature("target", config.get("target"), config.get("target"))

    env_sensor = Sensor("environment", "28-0301a2798a9f", "/sys/bus/w1/devices", config.get("average_window"),
                        [display, data_collector])
    vessel_sensor = Sensor("vessel", "28-0301a2799ddf", "/sys/bus/w1/devices", config.get("average_window"),
                           [display, data_collector])
    fridge_sensor = Sensor("fridge", "28-0301a27988e2", "/sys/bus/w1/devices", config.get("average_window"),
                           [display, data_collector])

    heater_ssr = Ssr("heater", 16, [display, data_collector])
    cooler_ssr = Ssr("cooler", 20, [display, data_collector])

    limiter = Limiter("limiter", heater_ssr, [display, data_collector])

    controller = Controller(config, config.get("control_interval"), config.get("control_deadband"),
                            heater_ssr, cooler_ssr, limiter,
                            vessel_sensor, fridge_sensor, [data_collector])

    runnables = [(env_sensor, config.get("sensor_interval"), 0),
                 (vessel_sensor, config.get("sensor_interval"), 0),
                 (fridge_sensor, config.get("sensor_interval"), 0),
                 (controller, config.get("control_interval"), 2),
                 (config, config.get("config_interval"), 0),
                 (csv_writer, config.get("csv_interval"), 0),
                 (influxdb_writer, config.get("influxdb_interval"), 0)]

    threads = []
    for runnable, interval, init_delay in runnables:
        t = Thread(target=runnable.start, args=(interval, init_delay))
        threads.append(t)
        t.start()

    shutdown.wait()

    logger.info("Received interrupt, shutting down")

    for index, (runnable, interval, init_delay) in enumerate(runnables):
        runnable.stop()
        threads[index].join()

    display.shutdown()
    heater_ssr.shutdown()
    # cooler_ssr.shutdown()


if __name__ == '__main__':
    main()
