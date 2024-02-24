import logging
from pyhap.accessory import Accessory
from pyhap.accessory_driver import AccessoryDriver
from pyhap.const import CATEGORY_THERMOSTAT
from enum import Enum, unique

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
        self._logger = logging.getLogger(__name__)
        
        # Characteristic options from services.json
        thermostat_service = self.add_preload_service('Thermostat')
        self._current_heating_cooling_state = thermostat_service.configure_char('CurrentHeatingCoolingState') 
        self._target_heating_cooling_state = thermostat_service.configure_char('TargetHeatingCoolingState', setter_callback=self._did_set_target_heating_cooling_state) 
        self._current_temperature = thermostat_service.configure_char('CurrentTemperature')
        self._target_temperature = thermostat_service.configure_char('TargetTemperature', setter_callback=self._did_set_target_temperature)
        self._temperature_units = thermostat_service.configure_char('TemperatureDisplayUnits')
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
        """Sets the current temperature in the HomeKit app."""
        self._current_temperature.set_value(value)
        self._logger.info("HomeKit current temperature did change to: %s°C.", value)
            
    def register_for_target_temperature_did_change_notifications(self, callback):
        """Registers for notifications about target temperature changing in HomeKit."""
        self._target_temperature_did_change_callback = callback

    def register_for_heating_cooling_state_did_change_notifications(self, callback):
        """Registers for notifications about the heating/cooling state changing in HomeKit."""
        self._target_heating_cooling_state_did_change_callback = callback
        
    def _did_set_target_temperature(self, value):
        if self._target_temperature_did_change_callback is not None:
            self._target_temperature_did_change_callback(value)

    def _did_set_target_heating_cooling_state(self, new_state):
        if self._target_heating_cooling_state_did_change_callback is not None:
            state_enum = TargetHeatingCoolingState(new_state)
            self._target_heating_cooling_state_did_change_callback(state_enum)