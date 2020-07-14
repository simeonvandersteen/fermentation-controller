from unittest.mock import patch, mock_open, Mock

from fermentation_controller.sensor import Sensor


class TestSensor:
    healthy_data = "58 01 55 05 7f a5 a5 66 45 : crc=45 YES\n" \
                   "58 01 55 05 7f a5 a5 66 45 t=21500"

    unhealthy_data = "58 01 55 05 7f a5 a5 66 45 : crc=45 NO\n" \
                     "something went wrong while reading"

    @patch("builtins.open", new_callable=mock_open, read_data=healthy_data)
    def test_reads_data_from_sensor(self, mock_file):
        device_id = "28-03.."
        device_dir = "/sys/bus/w1/devices"
        sensor = Sensor("some-sensor", device_id, device_dir, [])
        sensor.read()

        assert sensor.get() == 21.5
        mock_file.assert_called_once_with(device_dir + "/" + device_id + "/w1_slave", "r")

    @patch("builtins.open", new_callable=mock_open, read_data=unhealthy_data)
    def test_keeps_previous_value_on_read_failure(self, _):
        sensor = Sensor("some-sensor", "28-03..", "/sys", [])
        sensor.read()

        assert sensor.get() == 0.0

    @patch("builtins.open", new_callable=mock_open, read_data=healthy_data)
    def test_publishes_data_to_listeners(self, _):
        listener = Mock()
        name = "some-sensor"

        sensor = Sensor(name, "28-03..", "sys", [listener, listener])
        sensor.read()

        assert listener.handle_temperature.call_count == 2
        listener.handle_temperature.assert_called_with(name, 21.5)
