from unittest.mock import PropertyMock, patch, call

import pytest

from fermentation_controller.display import Display


class TestDisplay:

    @patch('fermentation_controller.display.CharLCD')
    def test_lcd_inits_with_zero_temperature_and_switches_off(self, lcd_mock_class):
        lcd_mock = lcd_mock_class.return_value

        cursor_mock = PropertyMock()
        type(lcd_mock).cursor_pos = cursor_mock

        display = Display(["environment", "vessel", "fridge", "target"], ["heater", "cooler"])

        display.run()

        lcd_mock.clear.assert_called()

        lcd_mock.write_string.assert_has_calls(
            [call("E 0.0"), call("V 0.0"), call("F 0.0"), call("T 0.0"), call(" "), call(" ")])

    @patch('fermentation_controller.display.CharLCD')
    def test_writes_temperatures_to_lcd(self, lcd_mock_class):
        lcd_mock = lcd_mock_class.return_value

        cursor_mock = PropertyMock()
        type(lcd_mock).cursor_pos = cursor_mock

        display = Display(["environment", "vessel", "fridge", "target"], [])

        display.handle_temperature("environment", 12.3)
        display.handle_temperature("vessel", 14.3)
        display.handle_temperature("fridge", 11.3)
        display.handle_temperature("target", 22.3)

        cursor_mock.assert_not_called()
        lcd_mock.write_string.assert_not_called()

        display.run()

        cursor_mock.assert_has_calls([call((0, 0)), call((0, 7)), call((1, 0)), call((1, 7))])
        lcd_mock.write_string.assert_has_calls([call("E 12.3"), call("V 14.3"), call("F 11.3"), call("T 22.3")])

    @pytest.mark.parametrize("switch_status", [True, False, ])
    @patch('fermentation_controller.display.CharLCD')
    def test_writes_switches_on_to_lcd(self, lcd_mock_class, switch_status):
        lcd_mock = lcd_mock_class.return_value

        cursor_mock = PropertyMock()
        type(lcd_mock).cursor_pos = cursor_mock

        display = Display([], ["heater", "cooler"])

        display.handle_switch("heater", switch_status)
        display.handle_switch("cooler", switch_status)

        cursor_mock.assert_not_called()
        lcd_mock.write_string.assert_not_called()

        display.run()

        cursor_mock.assert_has_calls([call((0, 14)), call((1, 14))])
        lcd_mock.write_string.assert_has_calls(
            [call("H" if switch_status else " "), call("C" if switch_status else " ")])
