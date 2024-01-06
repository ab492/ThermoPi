from pyhap.accessory import Accessory
from pyhap.accessory_driver import AccessoryDriver
from pyhap.const import CATEGORY_SENSOR
import signal
from utils.temperature_utils import read_temp

## Temporary TemperatureSensor code while testing and building out the code for the thermostat.
class TemperatureSensor(Accessory):
    category = CATEGORY_SENSOR
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        serv_temp = self.add_preload_service('TemperatureSensor')
        self.char_temp = serv_temp.configure_char('CurrentTemperature')

    @Accessory.run_at_interval(3)
    async def run(self):
        temperature = read_temp()
        celcius = temperature.celcius
        self.char_temp.set_value(celcius)
        # self.char_temp.set_value(random.randint(18, 26))

def get_accessory(driver):
    return TemperatureSensor(driver, 'MyTempSensor') # This is the name of the accessory in homekit.
    
# Start the accessory on port 51826
driver = AccessoryDriver(port=51826)

driver.add_accessory(accessory=get_accessory(driver))
    
# We want SIGTERM (terminate) to be handled by the driver itself,
# so that it can gracefully stop the accessory, server and advertising.
signal.signal(signal.SIGTERM, driver.signal_handler)     
    
# Start it!
driver.start()