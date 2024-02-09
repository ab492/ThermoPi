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
        
        self.tasks = []  # Store references to tasks


    async def start_thermostat(self):
        print("Starting thermostat...")
        # await self.thermostat.start()
        # await self.driver.async_start()
        
        thermostat_task = asyncio.create_task(self.thermostat.start())
        self.tasks.append(thermostat_task)  # Store task reference
        
        driver_task = asyncio.create_task(self.driver.async_start())
        self.tasks.append(driver_task)  # Store task reference
        
        # while True:
        #     temperature = await self.temperature_sensor.get_temperature()
        #     self.homekit_thermostat.set_current_temperature(temperature)
        #     await asyncio.sleep(3)  # Wait for 3 seconds before the next cycle
            
    def thermostat_temperature_did_change(self, new_temperature):
        print(f"New temperature: {new_temperature}")
        self.homekit_thermostat.set_current_temperature(new_temperature)
    
    async def stop_thermostat(self):
        print("Stopping thermostat...")
        for task in self.tasks:
            task.cancel()  # Cancel each task
            try:
                await task  # Wait for the task to be cancelled
            except asyncio.CancelledError:
                pass  # Task cancellation is expected, so we can ignore this exception

        
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
    
    # loop = asyncio.get_event_loop()

    # Set up the controller
    controller = ThermostatController(loop)

    try:
        loop.run_until_complete(controller.start_thermostat())
        loop.run_forever()  # Keep the loop running
    except KeyboardInterrupt:
        pass  # Handle keyboard interrupt
    finally:
        loop.run_until_complete(controller.stop_thermostat())  # Ensure everything is stopped properly
        loop.close()