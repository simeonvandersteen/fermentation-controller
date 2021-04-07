from fermentation_controller.data_collector import DataCollector


class TestDataCollector:

    def test_provides_collected_data_for_configured_data_only(self):
        collector = DataCollector(["environment", "vessel", "fridge", "target"], ["heater", "cooler", "limiter"])

        collector.handle_temperature("environment", 1.2, 1.3)
        collector.handle_temperature("vessel", 2, 2.3)
        collector.handle_temperature("fridge", 3, 3.3)
        collector.handle_temperature("target", 31.2, 31.3)
        collector.handle_switch("heater", True)
        collector.handle_switch("cooler", False)
        collector.handle_switch("limiter", True)
        collector.handle_controller(2.3, 3.4, -5.6, 12.5)

        collector.handle_switch("something-not-configured", False)

        expected = {
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

        assert collector.get_data_map() == expected

    def test_does_not_provide_uncollected_data(self):
        collector = DataCollector(["environment", "vessel", "fridge", "target"], ["heater", "cooler", "limiter"])

        collector.handle_temperature("environment", 1.2, 1.3)
        collector.handle_temperature("vessel", 2, 2.3)
        # the rest is not yet updated

        assert collector.get_data_map() is None
