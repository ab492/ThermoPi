import argparse
import asyncio
from utils.thermostat import Thermostat
from utils.relay import Relay
from homekit_thermostat import HKThermostat
import time
from pyhap.accessory_driver import AccessoryDriver
import signal
from enum import Enum, unique

class ThermostatController:
    def __init__(self, loop):
        self.loop = loop
        self.tasks = []  # Store references to for long running taskes

        # Setup thermostat
        self.relay = Relay(pin=26)
        self.thermostat = Thermostat(self.relay)
        self.target_temperature = 21
        self.thermostat.register_for_temperature_did_change_notifcation(self.thermostat_temperature_did_change)
        
        # Setup HomeKit integration
        self.driver = AccessoryDriver(port=51826, loop=self.loop)
        self.homekit_thermostat = HKThermostat(self.driver, "THERMOBOY")
        self.homekit_thermostat.register_for_heating_cooling_state_did_change_notifications(self.heating_cooling_state_did_change)
        self.homekit_thermostat.register_for_target_temperature_did_change_notifications(self.target_temperature_did_change)
        self.driver.add_accessory(accessory=self.homekit_thermostat)
        signal.signal(signal.SIGTERM, self.driver.signal_handler)
        
    async def start_thermostat(self):
        print("Starting thermostat...")
        thermostat_task = asyncio.create_task(self.thermostat.start())
        self.tasks.append(thermostat_task)
        
        print("Starting HomeKit integration...")
        driver_task = asyncio.create_task(self.driver.async_start())
        self.tasks.append(driver_task) 
        
    def thermostat_temperature_did_change(self, new_temperature):
        print(f"New temperature: {new_temperature}")
        self.homekit_thermostat.set_current_temperature(new_temperature)
        
    def target_temperature_did_change(self, new_temperature):
        print(f"Target temperature did change: {new_temperature}")
        self.thermostat.set_target_temperature(new_temperature)
    
    async def stop_thermostat(self):
        print("Stopping thermostat...")
        for task in self.tasks:
            task.cancel()  # Cancel each task
            try:
                await task  # Wait for the task to be cancelled
            except asyncio.CancelledError:
                pass  # Task cancellation is expected, so we can ignore this exception
            
    def heating_cooling_state_did_change(self, new_state):
        if new_state == TargetHeatingCoolingState.OFF {
            thermostat.stop()
        }

        
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