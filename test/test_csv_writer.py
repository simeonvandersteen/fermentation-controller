from unittest.mock import patch, Mock

from fermentation_controller.csv_writer import CsvWriter


class TestCsvWriter:

    @patch("time.time")
    @patch("builtins.open")
    def test_writes_csv_to_file(self, mock_file, mock_time):
        mock_time.return_value = 12.3

        collected_data = {
            "environment": 1.2,
            "environment_avg": 1.3,
            "vessel": 2,
            "vessel_avg": 2.3,
            "fridge": 3,
            "fridge_avg": 3.3,
            "target": 31.2,
            "target_avg": 31.3,
            "heater": 1,
            "cooler": 0,
            "limiter": 1,
            "p": 2.3,
            "i": 3.4,
            "d": -5.6,
            "control": 12.5,
        }

        collector = Mock()
        collector.get_data_map.return_value = collected_data

        writer = CsvWriter(collector)
        writer.run()

        handle = mock_file()
        handle.write.assert_called_once_with('12.3,12.5,0,-5.6,1.2,1.3,3,3.3,1,3.4,1,2.3,31.2,31.3,2,2.3\r\n')
        handle.flush.assert_called()

    @patch("builtins.open")
    def test_writes_no_data_if_nothing_was_collected(self, mock_file):
        collector = Mock()
        collector.get_data_map.return_value = None

        writer = CsvWriter(collector)
        writer.run()

        handle = mock_file()
        handle.write.assert_not_called()

    @patch("builtins.open")
    def test_close_file_on_shutdown(self, mock_file):
        writer = CsvWriter(Mock())
        writer.shutdown()

        handle = mock_file()
        handle.close.assert_called()
