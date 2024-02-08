import argparse
import asyncio
from utils.thermostat import Thermostat
from utils.relay import Relay
from homekit_thermostat import HKThermostat
import time
from pyhap.accessory_driver import AccessoryDriver
import signal

class DummySensor:
    async def get_temperature(self):
        await asyncio.sleep(3)  # Simulate a delay in getting the temperature
        return 22.5  # Return a dummy temperature
    
class ThermostatController:
    def __init__(self, loop):
        self.loop = loop
        self.temperature_sensor = DummySensor()
        
        self.relay = Relay(pin=26)
        self.thermostat = Thermostat(self.relay)
        self.target_temperature = 21
        self.thermostat.register_for_temperature_did_change_notifcation(self.thermostat_temperature_did_change)
        
        self.driver = AccessoryDriver(port=51826, loop=self.loop)
        self.homekit_thermostat = HKThermostat(self.driver, "THERMOBOY")
        self.driver.add_accessory(accessory=self.homekit_thermostat)
        signal.signal(signal.SIGTERM, self.driver.signal_handler)

    async def start_thermostat(self):
        print("Starting thermostat...")
        await self.thermostat.start()
        await self.driver.async_start()
        
        while True:
            temperature = await self.temperature_sensor.get_temperature()
            self.homekit_thermostat.set_current_temperature(temperature)
            await asyncio.sleep(3)  # Wait for 3 seconds before the next cycle
            
    def thermostat_temperature_did_change(self, new_temperature):
        print(f"New temperature: {new_temperature}")
        # self.homekit_thermostat.set_current_temperature(new_temperature)
        
        
async def main(loop):
    parser = argparse.ArgumentParser(description="Thermostat Control Script")
    parser.add_argument('--start', action='store_true', help="Start the thermostat")

    args = parser.parse_args()
    controller = ThermostatController(loop)

    if args.start:
        await controller.start_thermostat()
    elif args.stop:
        await controller.stop_thermostat()
        
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(main(loop))
    finally:
        loop.close()