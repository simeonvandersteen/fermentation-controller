from time import sleep
from threading import Thread

from unittest.mock import Mock, PropertyMock, patch, call

from fermentation_controller.display import Display


class TestDisplay:

    @patch('fermentation_controller.display.CharLCD')
    def test_clears_display_on_startup(self, lcd_mock_class):
        lcd_mock = lcd_mock_class.return_value

        Display([], [])

        lcd_mock.clear.assert_called()

    @patch('fermentation_controller.display.CharLCD')
    def test_writes_temperatures_to_lcd(self, lcd_mock_class):
        lcd_mock = lcd_mock_class.return_value

        cursor_mock = PropertyMock()
        type(lcd_mock).cursor_pos = cursor_mock

        display = Display(["environment", "vessel", "fridge", "target"], [])

        display.handle_temperature("environment", 12.3, 3)
        cursor_mock.assert_called_with((0, 0))
        lcd_mock.write_string.assert_called_with("E 12.3")

        display.handle_temperature("vessel", 14.3, 3)
        cursor_mock.assert_called_with((0, 7))
        lcd_mock.write_string.assert_called_with("V 14.3")

        display.handle_temperature("fridge", 11.3, 3)
        cursor_mock.assert_called_with((1, 0))
        lcd_mock.write_string.assert_called_with("F 11.3")

        display.handle_temperature("target", 22.3, 3)
        cursor_mock.assert_called_with((1, 7))
        lcd_mock.write_string.assert_called_with("T 22.3")

    @patch('fermentation_controller.display.CharLCD')
    def test_writes_switches_to_lcd(self, lcd_mock_class):
        lcd_mock = lcd_mock_class.return_value

        cursor_mock = PropertyMock()
        type(lcd_mock).cursor_pos = cursor_mock

        display = Display([], ["heater", "cooler", "limiter"])

        display.handle_switch("heater", True)
        cursor_mock.assert_called_with((0, 14))
        lcd_mock.write_string.assert_called_with("H")

        display.handle_switch("heater", False)
        cursor_mock.assert_called_with((0, 14))
        lcd_mock.write_string.assert_called_with(" ")

        display.handle_switch("cooler", True)
        cursor_mock.assert_called_with((1, 14))
        lcd_mock.write_string.assert_called_with("C")

        display.handle_switch("cooler", False)
        cursor_mock.assert_called_with((1, 14))
        lcd_mock.write_string.assert_called_with(" ")

        display.handle_switch("limiter", True)
        cursor_mock.assert_called_with((0, 15))
        lcd_mock.write_string.assert_called_with("L")

        display.handle_switch("limiter", False)
        cursor_mock.assert_called_with((0, 15))
        lcd_mock.write_string.assert_called_with(" ")

    @patch('fermentation_controller.display.CharLCD')
    def test_does_not_write_unknown_devices(self, lcd_mock_class):
        lcd_mock = lcd_mock_class.return_value

        cursor_mock = PropertyMock()
        type(lcd_mock).cursor_pos = cursor_mock

        display = Display(["vessel"], ["heater", "cooler"])

        display.handle_switch("inbetweener", True)
        display.handle_temperature("tropics", 42.3, 3)

        cursor_mock.assert_not_called()
        lcd_mock.write_string.assert_not_called()

    @patch('fermentation_controller.display.CharLCD')
    def test_writing_is_threadsafe(self, lcd_mock_class):
        lcd_mock = lcd_mock_class.return_value

        cursor_mock = PropertyMock()
        cursor_mock.side_effect = self.__delay
        type(lcd_mock).cursor_pos = cursor_mock

        display = Display(["environment"], ["heater"])

        manager = Mock()
        manager.attach_mock(lcd_mock, 'lcd_mock')
        manager.cursor_mock = cursor_mock

        t1 = Thread(target=display.handle_temperature, args=("environment", 12.3, 3))
        t2 = Thread(target=display.handle_switch, args=("heater", True,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        calls_in_order = [
            call.cursor_mock((0, 0)),
            call.lcd_mock.write_string("E 12.3"),
            call.cursor_mock((0, 14)),
            call.lcd_mock.write_string("H")
        ]

        assert manager.mock_calls == calls_in_order

    @staticmethod
    def __delay(_: tuple) -> None:
        sleep(0.01)
