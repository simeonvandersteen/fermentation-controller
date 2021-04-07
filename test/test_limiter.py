from unittest.mock import Mock

from fermentation_controller.limiter import Limiter


class TestLimiter:

    def test_off_by_default(self):
        limiter = Limiter("limiter", Mock(), [])

        assert limiter.get() is False

    def test_publishes_default_to_listeners(self):
        name = "limiter"
        listener = Mock()
        Limiter(name, Mock(), [listener, listener])

        assert listener.handle_switch.call_count == 2
        listener.handle_switch.assert_called_with(name, False)

    def test_on_switches_off_heater_if_on(self):
        heater = Mock()
        heater.get.return_value = True

        limiter = Limiter("limiter", heater, [])
        limiter.set(True)

        heater.set.assert_called_with(False)
        assert limiter.get() is True

    def test_on_does_not_switch_heater_if_off(self):
        heater = Mock()
        heater.get.return_value = False

        limiter = Limiter("limiter", heater, [])
        limiter.set(True)

        heater.set.assert_not_called()

    def test_off_does_not_switch_heater(self):
        heater = Mock()
        heater.get.return_value = True

        limiter = Limiter("limiter", heater, [])
        limiter.set(True)

        limiter.set(False)
        heater.set.assert_called_once_with(False)

    def test_switching_publishes_to_listeners(self):
        name = "limiter"
        listener = Mock()
        limiter = Limiter(name, Mock(), [listener, listener])
        limiter.set(True)

        assert listener.handle_switch.call_count == 2 * 2  # twice for init, twice for update
        listener.handle_switch.assert_called_with(name, True)
