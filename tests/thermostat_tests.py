import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch
from utils.thermostat import Thermostat
from utils.temperature_utils import TemperatureInfo
from mocks.mock_relay import MockRelay

class ThermostatTests(unittest.TestCase):
         
    @patch('thermostat_utils.read_temp')
    def test_current_temperature_is_reported_correctly(self, mock_read_temp):
        mock_read_temp.return_value = TemperatureInfo(30.0, 70.0)
        
        mock_relay = MockRelay()
        thermostat = Thermostat(mock_relay)
    
        self.assertEqual(thermostat.current_temperature, 30.0, "The reported current temperature should match the mocked value.")

        
        
        
        
        
if __name__ == '__main__':
    unittest.main()