import logging
from unittest.mock import patch, Mock, PropertyMock

import pytest

from fermentation_controller.controller import Controller

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


class TestController:

    @patch('fermentation_controller.controller.PID')
    def test_initiates_with_pid_values_and_target_from_config(self, pid_mock_class):
        config = Mock()
        config.get.side_effect = lambda key: {"p": 1, "i": 2, "d": 3, "target": 23}.get(key)

        Controller(config, 5, 0.5, Mock(), Mock(), Mock(), [])

        pid_mock_class.assert_called_with(Kp=1, Ki=2, Kd=3,
                                          setpoint=23,
                                          sample_time=5)

    @patch('fermentation_controller.controller.PID')
    def test_updates_pid_values_on_control(self, pid_mock_class):
        pid_mock = pid_mock_class.return_value

        temperature = Mock()
        current_temp = Mock()

        temperature.get.return_value = current_temp

        config = Mock()
        config.get.side_effect = lambda key: {"p": 1, "i": 2, "d": 3, "target": 23}.get(key)

        tunings_mock = PropertyMock()
        type(pid_mock).tunings = tunings_mock
        tunings_mock.return_value = (1, 2, 3)

        components_mock = PropertyMock()
        type(pid_mock).components = components_mock
        components_mock.return_value = (4, 3, 2)

        controller = Controller(config, 5, 0.5, Mock(), Mock(), temperature, [])

        config.get.side_effect = lambda key: {"p": 4, "i": 5, "d": 6, "target": 23}.get(key)

        pid_mock.return_value = 5

        controller.control()

        tunings_mock.assert_called_with((4, 5, 6))

    @patch('fermentation_controller.controller.PID')
    def test_only_updates_pid_values_if_changed(self, pid_mock_class):
        pid_mock = pid_mock_class.return_value

        temperature = Mock()
        current_temp = Mock()

        temperature.get.return_value = current_temp

        config = Mock()
        config.get.side_effect = lambda key: {"p": 1, "i": 2, "d": 3, "target": 23}.get(key)

        tunings_mock = PropertyMock()
        type(pid_mock).tunings = tunings_mock
        tunings_mock.return_value = (1, 2, 3)

        components_mock = PropertyMock()
        type(pid_mock).components = components_mock
        components_mock.return_value = (4, 3, 2)

        controller = Controller(config, 5, 0.5, Mock(), Mock(), temperature, [])

        pid_mock.return_value = 5

        controller.control()

        tunings_mock.assert_called_once_with()

    @patch('fermentation_controller.controller.PID')
    def test_feeds_current_temperature_to_pid(self, pid_mock_class):
        pid_mock = pid_mock_class.return_value

        temperature = Mock()
        current_temp = Mock()

        temperature.get.return_value = current_temp

        tunings_mock = PropertyMock()
        type(pid_mock).tunings = tunings_mock
        tunings_mock.return_value = (1, 2, 3)

        components_mock = PropertyMock()
        type(pid_mock).components = components_mock
        components_mock.return_value = (4, 3, 2)

        controller = Controller(Mock(), 5, 0.5, Mock(), Mock(), temperature, [])

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

        tunings_mock = PropertyMock()
        type(pid_mock).tunings = tunings_mock
        tunings_mock.return_value = (1, 2, 3)

        components_mock = PropertyMock()
        type(pid_mock).components = components_mock
        components_mock.return_value = (4, 3, 2)

        controller = Controller(Mock(), 5, 0.5, heater, cooler, Mock(), [])

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

        tunings_mock = PropertyMock()
        type(pid_mock).tunings = tunings_mock
        tunings_mock.return_value = (1, 2, 3)

        components_mock = PropertyMock()
        type(pid_mock).components = components_mock
        components_mock.return_value = (4, 3, 2)

        controller = Controller(Mock(), 5, 0.5, heater, cooler, Mock(), [])

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

        tunings_mock = PropertyMock()
        type(pid_mock).tunings = tunings_mock
        tunings_mock.return_value = (1, 2, 3)

        components_mock = PropertyMock()
        type(pid_mock).components = components_mock
        components_mock.return_value = (4, 3, 2)

        controller = Controller(Mock(), 5, 0, heater, cooler, Mock(), [])

        controller.control()

        if h_switch is None:
            heater.set.assert_not_called()
        else:
            heater.set.assert_called_with(h_switch)

        if c_switch is None:
            cooler.set.assert_not_called()
        else:
            cooler.set.assert_called_with(c_switch)

    @patch('fermentation_controller.controller.PID')
    def test_publishes_to_listeners(self, pid_mock_class):
        pid_mock = pid_mock_class.return_value

        temperature = Mock()
        current_temp = Mock()
        listener = Mock()

        temperature.get.return_value = current_temp

        config = Mock()
        config.get.side_effect = lambda key: {"p": 1, "i": 2, "d": 3, "target": 23}.get(key)

        tunings_mock = PropertyMock()
        type(pid_mock).tunings = tunings_mock
        tunings_mock.return_value = (1, 2, 3)

        components_mock = PropertyMock()
        type(pid_mock).components = components_mock
        components_mock.return_value = (4, 3, 2)

        controller = Controller(config, 5, 0.5, Mock(), Mock(), temperature, [listener])

        pid_mock.return_value = 6

        controller.control()

        listener.handle_controller.assert_called_with(4, 3, 2, 6)
