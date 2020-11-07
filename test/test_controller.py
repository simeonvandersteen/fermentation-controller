from unittest.mock import patch, Mock, PropertyMock

import pytest

from fermentation_controller.controller import Controller


class TestController:

    def setup_method(self):
        self.config = Mock()
        self.config.get.side_effect = lambda key: {"p": 1, "i": 2, "d": 3, "target": 23,
                                                   "heating_limit": 40,
                                                   "limit_window": 5}.get(key)
        self.limiter = Mock()
        self.limiter.get.return_value = False

        self.heater = Mock()
        self.heater.get.return_value = False

        self.cooler = Mock()
        self.cooler.get.return_value = False

        self.current_temp = Mock()
        self.current_temp.get.return_value = 18

        self.fridge_temp = Mock()
        self.fridge_temp.get.return_value = 20

        self.listener = Mock()

    @patch('fermentation_controller.controller.PID')
    def test_initiates_with_pid_values_and_target_from_config(self, pid_mock_class):
        Controller(self.config, 5, 0.5,
                   self.heater, self.cooler, self.limiter,
                   self.current_temp, self.fridge_temp,
                   [])

        pid_mock_class.assert_called_with(Kp=1, Ki=2, Kd=3,
                                          setpoint=23,
                                          sample_time=5)

    @patch('fermentation_controller.controller.PID')
    def test_updates_pid_values_on_control(self, pid_mock_class):
        pid_mock = pid_mock_class.return_value

        tunings_mock = PropertyMock()
        type(pid_mock).tunings = tunings_mock
        tunings_mock.return_value = (1, 2, 3)

        components_mock = PropertyMock()
        type(pid_mock).components = components_mock
        components_mock.return_value = (4, 3, 2)

        controller = Controller(self.config, 5, 0.5,
                                self.heater, self.cooler, self.limiter,
                                self.current_temp, self.fridge_temp,
                                [])

        self.config.get.side_effect = lambda key: {"p": 4, "i": 5, "d": 6, "target": 23,
                                                   "heating_limit": 40,
                                                   "limit_window": 5}.get(key)

        pid_mock.return_value = 5

        controller.control()

        tunings_mock.assert_called_with((4, 5, 6))

    @patch('fermentation_controller.controller.PID')
    def test_only_updates_pid_values_if_changed(self, pid_mock_class):
        pid_mock = pid_mock_class.return_value

        tunings_mock = PropertyMock()
        type(pid_mock).tunings = tunings_mock
        tunings_mock.return_value = (1, 2, 3)

        components_mock = PropertyMock()
        type(pid_mock).components = components_mock
        components_mock.return_value = (4, 3, 2)

        controller = Controller(self.config, 5, 0.5,
                                self.heater, self.cooler, self.limiter,
                                self.current_temp, self.fridge_temp,
                                [])

        pid_mock.return_value = 5

        controller.control()

        tunings_mock.assert_called_once_with()  # the getter, not the setter

    @patch('fermentation_controller.controller.PID')
    def test_feeds_current_temperature_to_pid(self, pid_mock_class):
        pid_mock = pid_mock_class.return_value

        current_temp = Mock()
        self.current_temp.get_average.return_value = current_temp

        tunings_mock = PropertyMock()
        type(pid_mock).tunings = tunings_mock
        tunings_mock.return_value = (1, 2, 3)

        components_mock = PropertyMock()
        type(pid_mock).components = components_mock
        components_mock.return_value = (4, 3, 2)

        controller = Controller(self.config, 5, 0.5,
                                self.heater, self.cooler, self.limiter,
                                self.current_temp, self.fridge_temp,
                                [])

        pid_mock.return_value = 5

        controller.control()

        pid_mock.assert_called_with(current_temp)

    @patch('fermentation_controller.controller.PID')
    def test_dont_switch_heating_on_if_under_heating_threshold(self, pid_mock_class):
        pid_mock = pid_mock_class.return_value

        self.heater.get.return_value = False

        pid_mock.return_value = 0.4

        tunings_mock = PropertyMock()
        type(pid_mock).tunings = tunings_mock
        tunings_mock.return_value = (1, 2, 3)

        components_mock = PropertyMock()
        type(pid_mock).components = components_mock
        components_mock.return_value = (4, 3, 2)

        controller = Controller(self.config, 5, 0.5,
                                self.heater, self.cooler, self.limiter,
                                self.current_temp, self.fridge_temp,
                                [])

        controller.control()

        self.heater.set.assert_not_called()

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

        self.heater.get.return_value = h_current
        self.cooler.get.return_value = c_current

        pid_mock.return_value = control

        tunings_mock = PropertyMock()
        type(pid_mock).tunings = tunings_mock
        tunings_mock.return_value = (1, 2, 3)

        components_mock = PropertyMock()
        type(pid_mock).components = components_mock
        components_mock.return_value = (4, 3, 2)

        controller = Controller(self.config, 5, 0.5,
                                self.heater, self.cooler, self.limiter,
                                self.current_temp, self.fridge_temp,
                                [])
        controller.control()

        if h_switch is None:
            self.heater.set.assert_not_called()
        else:
            self.heater.set.assert_called_with(h_switch)

        if c_switch is None:
            self.cooler.set.assert_not_called()
        else:
            self.cooler.set.assert_called_with(c_switch)

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

        self.heater.get.return_value = h_current
        self.cooler.get.return_value = c_current

        pid_mock.return_value = control

        tunings_mock = PropertyMock()
        type(pid_mock).tunings = tunings_mock
        tunings_mock.return_value = (1, 2, 3)

        components_mock = PropertyMock()
        type(pid_mock).components = components_mock
        components_mock.return_value = (4, 3, 2)

        controller = Controller(self.config, 5, 0,
                                self.heater, self.cooler, self.limiter,
                                self.current_temp, self.fridge_temp,
                                [])

        controller.control()

        if h_switch is None:
            self.heater.set.assert_not_called()
        else:
            self.heater.set.assert_called_with(h_switch)

        if c_switch is None:
            self.cooler.set.assert_not_called()
        else:
            self.cooler.set.assert_called_with(c_switch)

    @pytest.mark.parametrize("fridge_temperature, cb_current, cb_switch, h_current, h_switch", [
        (41, False, True, True, None),  # x fridge temp > limit, limiter off, switch on, don't control
        (41, True, None, False, None),  # x fridge temp > limit, limiter on, no-op
        (39, True, None, False, None),  # x fridge (limit - 5) < temp < limit, limiter on, no-op
        (34, True, False, False, True),  # x fridge temp < (limit - 5), limiter on, switch off, control
        (39, False, None, False, True),  # fridge (limit - 5) < temp < limit, limiter off, control
        (34, False, None, False, True),  # fridge temp < (limit - 5), limiter off, control
    ])
    @patch('fermentation_controller.controller.PID')
    def test_switch_off_heating_if_over_heating_limit(
            self, pid_mock_class, fridge_temperature, cb_current, cb_switch, h_current, h_switch):
        pid_mock = pid_mock_class.return_value

        self.fridge_temp.get.return_value = fridge_temperature

        self.heater.get.return_value = h_current
        self.cooler.get.return_value = False
        self.limiter.get.return_value = cb_current

        pid_mock.return_value = 3  # would trigger the heater

        tunings_mock = PropertyMock()
        type(pid_mock).tunings = tunings_mock
        tunings_mock.return_value = (1, 2, 3)

        components_mock = PropertyMock()
        type(pid_mock).components = components_mock
        components_mock.return_value = (4, 3, 2)

        controller = Controller(self.config, 5, 0,
                                self.heater, self.cooler, self.limiter,
                                self.current_temp, self.fridge_temp,
                                [])

        controller.control()

        if cb_switch is None:
            self.limiter.set.assert_not_called()
        else:
            self.limiter.set.assert_called_with(cb_switch)

        if h_switch is None:
            self.heater.set.assert_not_called()
        else:
            self.heater.set.assert_called_with(h_switch)

    @patch('fermentation_controller.controller.PID')
    def test_publishes_to_listeners(self, pid_mock_class):
        pid_mock = pid_mock_class.return_value

        tunings_mock = PropertyMock()
        type(pid_mock).tunings = tunings_mock
        tunings_mock.return_value = (1, 2, 3)

        components_mock = PropertyMock()
        type(pid_mock).components = components_mock
        components_mock.return_value = (4, 3, 2)

        controller = Controller(self.config, 5, 0.5,
                                self.heater, self.cooler, self.limiter,
                                self.current_temp, self.fridge_temp,
                                [self.listener])

        pid_mock.return_value = .4

        controller.control()

        self.listener.handle_controller.assert_called_with(4, 3, 2, .4)
