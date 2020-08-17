import logging
from unittest.mock import patch, Mock

import pytest

from fermentation_controller.controller import Controller

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


class TestController:

    @patch('fermentation_controller.controller.PID')
    def test_feeds_current_temperature_to_pid(self, pid_mock_class):
        pid_mock = pid_mock_class.return_value

        temperature = Mock()
        current_temp = Mock()

        temperature.get.return_value = current_temp

        controller = Controller(20, 5, 0.5, Mock(), Mock(), temperature)

        pid_mock.return_value = 5

        controller.control()

        pid_mock.assert_called_with(current_temp)

    @patch('fermentation_controller.controller.PID')
    def test_dont_switch_heating_on_if_under_heating_threshold(self, pid_mock_class):
        pid_mock = pid_mock_class.return_value

        heater = Mock()
        heater.get.return_value = False
        cooler = Mock()
        cooler.get.return_value = True

        pid_mock.return_value = 0.4

        controller = Controller(20, 5, 0.5, heater, cooler, Mock())

        controller.control()

        heater.set.assert_not_called()

    @pytest.mark.parametrize("control, h_current, c_current, h_switch, c_switch", [
        (5, False, False, True, None),  # switch heating on if above heating threshold
        (5, True, False, None, None),  # leave heating on if above heating threshold but already on
        (5, True, True, None, False),  # switch cooling off if above heating threshold
        (.4, False, False, None, None),  # don't switch heating on if under heating threshold
        (.4, True, True, False, False),  # do switch heating/cooling off if under heating threshold
        (-.4, True, True, False, False),  # do switch heating/cooling off if under cooling threshold
        (-.4, False, False, None, None),  # don't switch cooling on if under cooling threshold
        (-5, True, True, False, None),  # switch heating off if above cooling threshold
        (-5, False, True, None, None),  # leave cooling on if above cooling threshold but already on
        (-5, False, False, None, True),  # switch cooling on if above cooling threshold

    ])
    @patch('fermentation_controller.controller.PID')
    def test_switch_heating_and_cooling(
            self, pid_mock_class, control, h_current, h_switch, c_current, c_switch):
        pid_mock = pid_mock_class.return_value

        heater = Mock()
        heater.get.return_value = h_current
        cooler = Mock()
        cooler.get.return_value = c_current

        pid_mock.return_value = control

        controller = Controller(20, 5, 0.5, heater, cooler, Mock())

        controller.control()

        if h_switch is None:
            heater.set.assert_not_called()
        else:
            heater.set.assert_called_with(h_switch)

        if c_switch is None:
            cooler.set.assert_not_called()
        else:
            cooler.set.assert_called_with(c_switch)

    @pytest.mark.parametrize("control, h_current, c_current, h_switch, c_switch", [
        (.1, False, False, True, None),  # switch heating on if above zero
        (.1, True, False, None, None),  # leave heating on if above zero and already on
        (.1, True, True, None, False),  # switch cooling off if above zero
        (0, True, True, False, False),  # do switch heating/cooling off if zero
        (-.1, True, True, False, None),  # switch heating off if under zero
        (-.1, False, True, None, None),  # leave cooling on if under zero and already on
        (-.1, False, False, None, True),  # switch cooling on if under zero

    ])
    @patch('fermentation_controller.controller.PID')
    def test_switch_heating_and_cooling_without_threshold(
            self, pid_mock_class, control, h_current, h_switch, c_current, c_switch):
        pid_mock = pid_mock_class.return_value

        heater = Mock()
        heater.get.return_value = h_current
        cooler = Mock()
        cooler.get.return_value = c_current

        pid_mock.return_value = control

        controller = Controller(20, 5, 0, heater, cooler, Mock())

        controller.control()

        if h_switch is None:
            heater.set.assert_not_called()
        else:
            heater.set.assert_called_with(h_switch)

        if c_switch is None:
            cooler.set.assert_not_called()
        else:
            cooler.set.assert_called_with(c_switch)
