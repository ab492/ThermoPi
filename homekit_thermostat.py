"""An example of how to setup and start an Accessory.

This is:
1. Create the Accessory object you want.
2. Add it to an AccessoryDriver, which will advertise it on the local network,
    setup a server to answer client queries, etc.
"""
import logging
import signal
import random

from pyhap.accessory import Accessory, Bridge
from pyhap.accessory_driver import AccessoryDriver
import pyhap.loader as loader
from pyhap import camera
from pyhap.const import CATEGORY_SENSOR

logging.basicConfig(level=logging.INFO, format="[%(module)s] %(message)s")


class TemperatureSensor(Accessory):
    """Fake Temperature sensor, measuring every 3 seconds."""

    category = CATEGORY_SENSOR

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        serv_temp = self.add_preload_service('TemperatureSensor')
        self.char_temp = serv_temp.configure_char('CurrentTemperature')

    @Accessory.run_at_interval(3)
    async def run(self):
        self.char_temp.set_value(random.randint(18, 26))


def get_bridge(driver):
    """Call this method to get a Bridge instead of a standalone accessory."""
    bridge = Bridge(driver, 'Bridge')
    temp_sensor = TemperatureSensor(driver, 'Sensor 2')
    temp_sensor2 = TemperatureSensor(driver, 'Sensor 1')
    bridge.add_accessory(temp_sensor)
    bridge.add_accessory(temp_sensor2)

    return bridge


def get_accessory(driver):
    """Call this method to get a standalone Accessory."""
    return TemperatureSensor(driver, 'MyTempSensor')


# Start the accessory on port 51826
driver = AccessoryDriver(port=51826)

# Change `get_accessory` to `get_bridge` if you want to run a Bridge.
driver.add_accessory(accessory=get_accessory(driver))

# We want SIGTERM (terminate) to be handled by the driver itself,
# so that it can gracefully stop the accessory, server and advertising.
signal.signal(signal.SIGTERM, driver.signal_handler)

# Start it!
driver.start()

# class Thermostat(Accessory):
#     category = CATEGORY_THERMOSTAT
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         # Add the services that this Accessory will support with add_preload_service here
#         serv_temp = self.add_preload_service('TemperatureSensor')
#         self.char_temp = serv_temp.configure_char('CurrentTemperature')
        
#         self.char_temp.setter_callback = self.temperature_changed
        
#     def temperature_changed(self, value):
#         """This will be called every time the value of the CurrentTemperature
#         is changed. Use setter_callbacks to react to user actions, e.g. setting the
#         lights On could fire some GPIO code to turn on a LED (see pyhap/accessories/LightBulb.py).
#         """
#         print('Temperature changed to: ', value)
        
#     @Accessory.run_at_interval(3)
#     async def run(self):
#         temperature = read_temp()
#         celcius = temperature.celcius
#         self.char_temp.set_value(celcius)
        
# def get_accessory(driver):
#     return Thermostat(driver, 'ThermoBoy') # This is the name of the accessory in homekit.
    
# # Start the accessory on port 51826
# driver = AccessoryDriver(port=51826)

# driver.add_accessory(accessory=get_accessory(driver))
    
# # We want SIGTERM (terminate) to be handled by the driver itself,
# # so that it can gracefully stop the accessory, server and advertising.
# signal.signal(signal.SIGTERM, driver.signal_handler)     
    
# # Start it!
# driver.start()