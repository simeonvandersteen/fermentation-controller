from unittest.mock import patch, mock_open, Mock

from fermentation_controller.sensor import Sensor


class TestSensor:
    healthy_data = "58 01 55 05 7f a5 a5 66 45 : crc=45 YES\n" \
                   "58 01 55 05 7f a5 a5 66 45 t={}"

    unhealthy_data = "58 01 55 05 7f a5 a5 66 45 : crc=45 NO\n" \
                     "something went wrong while reading"

    @patch("builtins.open", new_callable=mock_open, read_data=healthy_data.format(21512))
    def test_reads_data_from_sensor(self, mock_file):
        device_id = "28-03.."
        device_dir = "/sys/bus/w1/devices"
        sensor = Sensor("some-sensor", device_id, device_dir, 2, [])
        sensor.read()

        assert sensor.get() == 21.512
        mock_file.assert_called_once_with(device_dir + "/" + device_id + "/w1_slave", "r")

    @patch("builtins.open", new_callable=mock_open, read_data=healthy_data.format(20000))
    def test_reads_moving_average_from_sensor(self, mock_file):
        handlers = (mock_file.return_value,
                    mock_open(read_data=self.healthy_data.format(10000)).return_value,
                    mock_open(read_data=self.healthy_data.format(9930)).return_value)
        mock_file.side_effect = handlers

        sensor = Sensor("some-sensor", "28-03..", "/sys/bus/w1/devices", 2, [])
        assert sensor.get_average() == 0.0  # init value
        sensor.read()
        assert sensor.get_average() == 20.0
        sensor.read()
        assert sensor.get_average() == 15.0
        sensor.read()
        assert sensor.get_average() == 10.0

    @patch("builtins.open", new_callable=mock_open, read_data=unhealthy_data)
    def test_keeps_previous_value_on_read_failure(self, _):
        sensor = Sensor("some-sensor", "28-03..", "/sys", 2, [])
        sensor.read()

        assert sensor.get() == 0.0

    @patch("builtins.open", new_callable=mock_open, read_data=healthy_data.format(21512))
    def test_publishes_data_to_listeners(self, _):
        listener = Mock()
        name = "some-sensor"

        sensor = Sensor(name, "28-03..", "sys", 2, [listener, listener])
        sensor.read()

        assert listener.handle_temperature.call_count == 2
        listener.handle_temperature.assert_called_with(name, 21.512, 21.5)
