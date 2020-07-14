from unittest.mock import patch, Mock

from fermentation_controller.switch import Switch


class TestSwitch:

    @patch('fermentation_controller.switch.GPIO')
    def test_switched_off_by_default(self, mock_gpio):
        Switch("heater", 3, [])

        mock_gpio.setup.assert_called_once_with(3, mock_gpio.OUT)
        mock_gpio.output.assert_called_once_with(3, mock_gpio.LOW)

    @patch('fermentation_controller.switch.GPIO')
    def test_switch_on(self, mock_gpio):
        switch = Switch("heater", 3, [])
        switch.set(True)

        mock_gpio.output.assert_called_with(3, mock_gpio.HIGH)
        assert switch.get() is True

    @patch('fermentation_controller.switch.GPIO')
    def test_switch_off(self, mock_gpio):
        switch = Switch("heater", 3, [])
        switch.set(False)

        mock_gpio.output.assert_called_with(3, mock_gpio.LOW)
        assert switch.get() is False

    @patch('fermentation_controller.switch.GPIO')
    def test_switching_publishes_to_listeners(self, _):
        listener = Mock()
        name = "heater"

        switch = Switch(name, 3, [listener, listener])
        switch.set(True)

        assert listener.handle_switch.call_count == 2
        listener.handle_switch.assert_called_with(name, True)

    @patch('fermentation_controller.switch.GPIO')
    def test_shutdown(self, mock_gpio):
        switch = Switch("heater", 3, [])
        switch.shutdown()

        mock_gpio.cleanup.assert_called()
