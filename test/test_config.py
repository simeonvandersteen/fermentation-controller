from unittest.mock import patch, mock_open

from fermentation_controller.config import Config


class TestConfig:
    config_data = '{"p": 2}'

    @patch("builtins.open", new_callable=mock_open, read_data=config_data)
    def test_reads_config_on_init(self, mock_config):
        Config("config.json")

        mock_config.assert_called_once_with("config.json", "r")

    @patch("builtins.open", new_callable=mock_open, read_data=config_data)
    def test_gets_value_from_config(self, _):
        config = Config("config.json")

        assert config.get("p") == 2

    @patch("builtins.open", new_callable=mock_open, read_data=config_data)
    def test_reloads_config(self, mock_config):
        later_config_data = '{"p": 5}'

        handlers = (mock_config.return_value, mock_open(read_data=later_config_data).return_value)
        mock_config.side_effect = handlers

        config = Config("config.json")
        config.reload()

        assert config.get("p") == 5
