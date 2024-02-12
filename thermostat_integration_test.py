import argparse
import asyncio
from utils.thermostat import Thermostat
from utils.relay import Relay
from homekit_thermostat import HKThermostat, TargetHeatingCoolingState
import time
from pyhap.accessory_driver import AccessoryDriver
import signal
from enum import Enum, unique
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class ThermostatController:
    def __init__(self, loop):
        self._logger = logging.getLogger(__name__)
        self.loop = loop
        self.thermostat_task = None
        self.driver_task = None

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
        self._logger.info("Starting HomeKit integration...")
        self.driver_task = asyncio.create_task(self.driver.async_start())     
        
    def thermostat_temperature_did_change(self, new_temperature):
        self._logger.info("Current temperature did change to: %s°C. Updating HomeKit.", new_temperature)
        self.homekit_thermostat.set_current_temperature(new_temperature)
    
    def heating_cooling_state_did_change(self, new_state):
        self._logger.info("HomeKit heating cooling state did change to: %s. Updating Thermostat.", new_state)
        
        # Cancel any existing thermostat task before starting a new action
        if self.thermostat_task:
            self.thermostat_task.cancel()
            self.thermostat_task = None  # Clear the existing task
            
        # Depending on the new state, schedule the start or stop coroutine
        if new_state in (TargetHeatingCoolingState.HEAT, TargetHeatingCoolingState.AUTO):
            # Schedule the thermostat start coroutine without waiting for it
            self.thermostat_task = asyncio.create_task(self.thermostat.start())
        elif new_state in (TargetHeatingCoolingState.OFF, TargetHeatingCoolingState.COOL):
            # Schedule the thermostat stop coroutine without waiting for it
            self.thermostat_task = asyncio.create_task(self.thermostat.stop())
            
    def target_temperature_did_change(self, new_temperature):
        self._logger.info("HomeKit target temperature did change to: %s. Updating Thermostat.", new_temperature)
        self.thermostat.set_target_temperature(new_temperature)

    
    # TODO GET THIS TIDY!
    async def stop_thermostat(self):
        print("Stopping thermostat...")

        # Cancel and await the thermostat task if it exists
        if self.thermostat_task:
            self.thermostat_task.cancel()
            try:
                await self.thermostat_task
            except asyncio.CancelledError:
                print("Thermostat task cancelled.")
            self.thermostat.shutdown()
            self.thermostat_task = None  # Reset the task to None after cancellation

        # Cancel and await the driver task if it exists
        if self.driver_task:
            self.driver_task.cancel()
            try:
                await self.driver_task
            except asyncio.CancelledError:
                print("Driver task cancelled.")
            self.driver_task = None  # Reset the task to None after cancellation
               
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
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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