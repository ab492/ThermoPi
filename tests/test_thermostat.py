import unittest
from unittest.mock import patch
from utils.thermostat import Thermostat
from utils.temperature_utils import TemperatureInfo
from mocks.mock_relay import MockRelay

# WARNING: Read the comment on test_current_temperature_is_reported_correctly regarding patches. It'll save headaches when writing additional tests.
class ThermostatTests(unittest.TestCase):
    
    def setUp(self):
        self.mock_relay = MockRelay()
        self.sut = Thermostat(self.mock_relay)
        
    # Notice the patch is actually updating THERMOSTAT.read_temp, even though read_temp comes from the temperature_utils file.
    # This is because the test file still imports temperature_utils.read_temp as normal, and then patches it once in the THERMOSTAT file.     
    @patch('utils.thermostat.read_temp')
    def test_current_temperature_is_reported_correctly(self, mock_read_temp):
        mock_read_temp.return_value = TemperatureInfo(30.0, 70.0)
            
        self.assertEqual(self.sut.current_temperature, 30.0, "The reported current temperature should match the mocked value.")

    def test_set_target_temperature_correctly_updates_value(self):
        self.sut.set_target_temperature(21.5)
        
        self.assertEqual(self.sut.target_temperature, 21.5, "The reported target temperature should match the set value.")
        
    def test_default_target_temperature_set_on_init(self):        
        self.assertEqual(self.sut.target_temperature, 20.0, "The target temperature should be set on init.")

    def test_is_active_reflects_relay_status_when_relay_on(self):
        self.mock_relay.value_to_return_for_is_active = True
        
        self.assertEqual(self.sut.is_active, True, "The reported is active value should match the relay's value.")

    def test_is_active_reflects_relay_status_when_relay_off(self):
        self.mock_relay.value_to_return_for_is_active = False
        
        self.assertEqual(self.sut.is_active, False, "The reported is active value should match the relay's value.")

    @patch('utils.thermostat.read_temp')
    def test_start_turns_on_relay_when_current_temp_below_target_minus_hysteresis(self, mock_read_temp):
        mock_read_temp.return_value = TemperatureInfo(15.0, 70.0)
        self.sut.set_target_temperature(16.0)
        
        self.sut._check_and_control_temperature()
        
        self.assertEqual(self.mock_relay.turn_on_call_count, 1, "The relay should be switched on to meet the target temperature (including hysteresis).")

    @patch('utils.thermostat.read_temp')
    def test_start_turns_off_relay_when_current_temp_below_target_plus_hysteresis(self, mock_read_temp):
        mock_read_temp.return_value = TemperatureInfo(21, 70.0)
        self.mock_relay.value_to_return_for_is_active = True # Relay must be on for it to turn off in this branch.
        self.sut.set_target_temperature(20)
        
        self.sut._check_and_control_temperature()
        
        self.assertEqual(self.mock_relay.turn_off_call_count, 1, "The relay should be switched off when temp is above the target temperature (including hysteresis).")

    def test_stop_calls_relay_cleanup(self):
        self.sut.stop()
        
        self.assertEqual(self.mock_relay.cleanup_call_count, 1, "Cleanup method should be called on stop.")
        
if __name__ == '__main__':
    unittest.main()