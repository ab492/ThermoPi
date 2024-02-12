import logging
import signal
import asyncio
from pyhap.accessory import Accessory
from pyhap.accessory_driver import AccessoryDriver
from pyhap.const import CATEGORY_THERMOSTAT
from enum import Enum, unique

logging.basicConfig(level=logging.INFO, format="[%(module)s] %(message)s")

@unique
class TargetHeatingCoolingState(Enum):
    OFF = 0 
    HEAT = 1 # Set the thermostat to heat to the target temperature.
    COOL = 2 # Set the thermostat to cool to the target temperature.
    AUTO = 3 # The thermostat automatically heats or cools to maintain the target temberature.
    
## Wraps the HomeKit functionality directly.
class HKThermostat(Accessory):
    category = CATEGORY_THERMOSTAT
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Characteristic options from services.json
        thermostat_service = self.add_preload_service('Thermostat')
        self._current_heating_cooling_state = thermostat_service.configure_char('CurrentHeatingCoolingState') 
        self._target_heating_cooling_state = thermostat_service.configure_char('TargetHeatingCoolingState', setter_callback=self.set_target_heating_cooling_state) 
        self._curent_temperature = thermostat_service.configure_char('CurrentTemperature')
        self._target_temperature = thermostat_service.configure_char('TargetTemperature', setter_callback=self.set_target_temperature)
        self._temperature_units = thermostat_service.configure_char('TemperatureDisplayUnits') # Can this be forced to only C?!
        self._target_heating_cooling_state_did_change_callback = None
        self._target_temperature_did_change_callback = None
    
    @property
    def current_target_temperature(self):
        """Returns the current target temperature."""
        return self._target_temperature.get_value()

    @property
    def current_heating_cooling_state(self):
        """Returns the current heating/cooling state."""
        current_state = self._current_heating_cooling_state.get_value()
        return TargetHeatingCoolingState(current_state)
    
    def set_current_temperature(self, value):
        self._curent_temperature.set_value(value)    
    
    def set_target_temperature(self, value):
        if self._target_temperature_did_change_callback is not None:
            self._target_temperature_did_change_callback(value)
            
    def register_for_target_temperature_did_change_notifications(self, callback):
        self._target_temperature_did_change_callback = callback

    def register_for_heating_cooling_state_did_change_notifications(self, callback):
        self._target_heating_cooling_state_did_change_callback = callback

    def set_target_heating_cooling_state(self, new_state):
        if self._target_heating_cooling_state_did_change_callback is not None:
            state_enum = TargetHeatingCoolingState(new_state)
            self._target_heating_cooling_state_did_change_callback(state_enum)