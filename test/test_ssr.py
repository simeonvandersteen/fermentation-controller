from unittest.mock import patch, Mock

from fermentation_controller.ssr import Ssr


class TestSsr:

    @patch('fermentation_controller.ssr.GPIO')
    def test_ssr_off_by_default(self, mock_gpio):
        Ssr("heater", 3, [])

        mock_gpio.setup.assert_called_once_with(3, mock_gpio.OUT)
        mock_gpio.output.assert_called_once_with(3, mock_gpio.LOW)

    @patch('fermentation_controller.ssr.GPIO')
    def test_publishes_default_to_listeners(self, _):
        listener = Mock()
        name = "heater"

        Ssr(name, 3, [listener, listener])

        assert listener.handle_switch.call_count == 2
        listener.handle_switch.assert_called_with(name, False)

    @patch('fermentation_controller.ssr.GPIO')
    def test_ssr_on(self, mock_gpio):
        ssr = Ssr("heater", 3, [])
        ssr.set(True)

        mock_gpio.output.assert_called_with(3, mock_gpio.HIGH)
        assert ssr.get() is True

    @patch('fermentation_controller.ssr.GPIO')
    def test_ssr_off(self, mock_gpio):
        ssr = Ssr("heater", 3, [])
        ssr.set(False)

        mock_gpio.output.assert_called_with(3, mock_gpio.LOW)
        assert ssr.get() is False

    @patch('fermentation_controller.ssr.GPIO')
    def test_switching_publishes_to_listeners(self, _):
        listener = Mock()
        name = "heater"

        ssr = Ssr(name, 3, [listener, listener])
        ssr.set(True)

        assert listener.handle_switch.call_count == 2 * 2  # twice for init, twice for update
        listener.handle_switch.assert_called_with(name, True)

    @patch('fermentation_controller.ssr.GPIO')
    def test_shutdown(self, mock_gpio):
        ssr = Ssr("heater", 3, [])
        ssr.shutdown()

        mock_gpio.cleanup.assert_called()
