import logging
import signal

from pyhap.accessory import Accessory
from pyhap.accessory_driver import AccessoryDriver
from pyhap.const import CATEGORY_THERMOSTAT

from enum import Enum, unique

logging.basicConfig(level=logging.INFO, format="[%(module)s] %(message)s")

## Wraps the HomeKit functionality directly.
class Thermostat(Accessory):
    category = CATEGORY_THERMOSTAT
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Characteristic options from services.json
        thermostat_service = self.add_preload_service('Thermostat')
        self.current_heating_cooling_state = thermostat_service.configure_char('CurrentHeatingCoolingState') 
        self.target_heating_cooling_state = thermostat_service.configure_char('TargetHeatingCoolingState', setter_callback=self.set_target_heating_cooling_state) 
        self.curent_temperature = thermostat_service.configure_char('CurrentTemperature')
        self.target_temperature = thermostat_service.configure_char('TargetTemperature', setter_callback=self.set_target_temperature)
        self.temperature_units = thermostat_service.configure_char('TemperatureDisplayUnits')
        
        self.target_heating_cooling_state_did_change_callback = None
        self.target_temperature_did_change_callback = None

    # @Accessory.run_at_interval(3)
    # async def run(self):
    #     self.curent_temperature.set_value(18)

    def set_current_temperature(self, value):
        print(f"Update value: {value}")
        self.curent_temperature.set_value(value)    
    
    def set_target_temperature(self, value):
        if self.target_temperature_did_change_callback:
            self.target_temperature_did_change_callback(value)

    def set_target_heating_cooling_state(self, value):
        if self.target_heating_cooling_state_did_change_callback:
            self.target_heating_cooling_state_did_change_callback(value)
            

        
# def get_accessory(driver):
#     """Call this method to get a standalone Accessory."""
#     return Thermostat(driver, 'MyTempSensor')
        
# driver = AccessoryDriver(port=51826)
# driver.add_accessory(accessory=get_accessory(driver))
# signal.signal(signal.SIGTERM, driver.signal_handler)
# driver.start()

@unique
class TargetHeatingCoolingState(Enum):
    OFF = 0 
    HEAT = 1 # Set the thermostat to heat to the target temperature.
    COOL = 2 # Set the thermostat to cool to the target temperature.
    AUTO = 3 # The thermostat automatically heats or cools to maintain the target temberature.

class HomeKitThermostat:
    def __init__(self, name: str):
        self.driver = AccessoryDriver(port=51826)
        self.thermostat = Thermostat(self.driver, name)
        self.driver.add_accessory(accessory=self.thermostat)
        signal.signal(signal.SIGTERM, self.driver.signal_handler)
        
        self.thermostat.target_heating_cooling_state_did_change_callback = self._target_heating_cooling_state_did_change
        self.thermostat.target_temperature_did_change_callback = self._target_temperature_did_change
        
        self._on_target_heating_cooling_state_did_change_notification = None
        self._on_target_temperature_did_change_notification = None
        
    def _target_heating_cooling_state_did_change(self, new_state):
        state_enum = TargetHeatingCoolingState(new_state)
        if self._on_target_heating_cooling_state_did_change_notification is not None:
            self._on_target_heating_cooling_state_did_change_notification(state_enum)
            
    def _target_temperature_did_change(self, new_temperature):
        if self._on_target_temperature_did_change_notification is not None:
            self._on_target_temperature_did_change_notification(new_temperature)

    def start(self):
        self.driver.start()

    def set_current_temperature(self, value):
        print(f"VALUE: {value}")
        self.thermostat.set_current_temperature(value)
        
    def register_for_heating_cooling_state_did_change_notifications(self, callback):
        self._on_heating_cooling_state_did_change_callback = callback

    def register_for_target_temperature_did_change_notifications(self, callback):
        self._on_target_temperature_did_change_notification = callback