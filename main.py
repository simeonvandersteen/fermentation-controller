import logging
import signal
from threading import Thread, Event

from fermentation_controller.config import Config
from fermentation_controller.controller import Controller
from fermentation_controller.csv_writer import CsvWriter
from fermentation_controller.display import Display
from fermentation_controller.sensor import Sensor
from fermentation_controller.switch import Switch

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

logger = logging.getLogger(__name__)

shutdown = Event()


def start_shutdown(signum, frame):
    global shutdown
    shutdown.set()


signal.signal(signal.SIGINT, start_shutdown)
signal.signal(signal.SIGTERM, start_shutdown)


def main():
    config = Config("./config.json")
    controller_sample_time = 5
    controller_threshold = 0.0

    display = Display(["environment", "vessel", "fridge", "target"], ["heater", "cooler"])
    display.handle_temperature("target", config.get("target"))

    csv_writer = CsvWriter(["environment", "vessel", "fridge", "target"], ["heater", "cooler"])
    csv_writer.handle_temperature("target", config.get("target"))

    env_sensor = Sensor("environment", "28-0301a2798a9f", "/sys/bus/w1/devices", [display, csv_writer])
    vessel_sensor = Sensor("vessel", "28-0301a2799ddf", "/sys/bus/w1/devices", [display, csv_writer])
    fridge_sensor = Sensor("fridge", "28-0301a27988e2", "/sys/bus/w1/devices", [display, csv_writer])

    heater_switch = Switch("heater", 20, [display, csv_writer])
    cooler_switch = Switch("cooler", 16, [display, csv_writer])

    controller = Controller(config, controller_sample_time, controller_threshold, heater_switch, cooler_switch,
                            vessel_sensor, [csv_writer])

    runnables = [(env_sensor, 1), (vessel_sensor, 1), (fridge_sensor, 1), (controller, controller_sample_time),
                 (config, 5), (csv_writer, 10)]

    threads = []
    for runnable, interval in runnables:
        t = Thread(target=runnable.start, args=(interval,))
        threads.append(t)
        t.start()

    shutdown.wait()

    logger.info("Received interrupt, shutting down")

    for index, (runnable, interval) in enumerate(runnables):
        runnable.stop()
        threads[index].join()

    display.shutdown()
    heater_switch.shutdown()
    # cooler_switch.shutdown()


if __name__ == '__main__':
    main()
