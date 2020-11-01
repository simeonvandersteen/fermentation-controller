from unittest.mock import patch, mock_open

from fermentation_controller.csv_writer import CsvWriter


class TestCsvWriter:

    @patch("time.time")
    @patch("builtins.open")
    def test_writes_csv_to_file(self, mock_file, mock_time):
        mock_time.return_value = 12.3

        writer = CsvWriter(["environment", "vessel", "fridge", "target"], ["heater", "cooler"])

        writer.handle_temperature("environment", 1.2)
        writer.handle_temperature("vessel", 2)
        writer.handle_temperature("fridge", 3)
        writer.handle_temperature("target", 31.2)
        writer.handle_switch("heater", True)
        writer.handle_switch("cooler", False)
        writer.handle_controller(2.3, 3.4, -5.6, 12.5)

        writer.run()

        handle = mock_file()
        handle.write.assert_called_once_with('12.3,1.2,2,3,31.2,1,0,2.3,3.4,-5.6,12.5\r\n')
        handle.flush.assert_called()

    @patch("builtins.open")
    def test_close_file_on_shutdown(self, mock_file):
        writer = CsvWriter(["environment", "vessel", "fridge", "target"], ["heater", "cooler"])
        writer.shutdown()

        handle = mock_file()
        handle.close.assert_called()
