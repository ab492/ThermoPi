import logging
import signal

from pyhap.accessory import Accessory
from pyhap.accessory_driver import AccessoryDriver
from pyhap.const import CATEGORY_THERMOSTAT

logging.basicConfig(level=logging.INFO, format="[%(module)s] %(message)s")

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

    @Accessory.run_at_interval(3)
    async def run(self):
        self.curent_temperature.set_value(18)
        self.current_heating_cooling_state = 1
    
    def set_target_temperature(self, value):
        print(f'TARGET VALUE: {value}')

    def set_target_heating_cooling_state(self, value):
        print(f'TARGET HEATING COOLING STATE: {value}')

        
def get_accessory(driver):
    """Call this method to get a standalone Accessory."""
    return Thermostat(driver, 'MyTempSensor')
        
driver = AccessoryDriver(port=51826)
driver.add_accessory(accessory=get_accessory(driver))
signal.signal(signal.SIGTERM, driver.signal_handler)
driver.start()

class HomeKitThermostat:
    def __init__(self, name: str):
        self.driver = AccessoryDriver(port=51826)
        self.therm
