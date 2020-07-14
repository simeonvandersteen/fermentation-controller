import logging
from threading import Thread
from time import sleep

from fermentation_controller.display import Display
from fermentation_controller.sensor import Sensor
from fermentation_controller.switch import Switch

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

logger = logging.getLogger(__name__)


def main():
    display = Display(["environment", "vessel", "fridge", "target"], ["heater", "chiller"])
    display.handle_temperature("target", 18)

    env_sensor = Sensor("environment", "28-0301a27988e2", "/sys/bus/w1/devices", [display])
    vessel_sensor = Sensor("vessel", "28-0301a2799ddf", "/sys/bus/w1/devices", [display])
    fridge_sensor = Sensor("fridge", "28-0301a2798a9f", "/sys/bus/w1/devices", [display])

    heater_switch = Switch("heater", 16, [display])
    chiller_switch = Switch("chiller", 20, [display])

    runnables = [(env_sensor, 1), (vessel_sensor, 1), (fridge_sensor, 1)]

    threads = []
    for runnable, interval in runnables:
        t = Thread(target=runnable.start, args=(interval,))
        threads.append(t)
        t.start()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        logger.info("Received interrupt, shutting down")

        for index, (runnable, interval) in enumerate(runnables):
            runnable.stop()
            threads[index].join()

    display.shutdown()
    heater_switch.shutdown()
    # chiller_switch.shutdown()


if __name__ == '__main__':
    main()