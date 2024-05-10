import argparse
import asyncio
from utils.thermostat import Thermostat
from utils.relay import Relay
from utils.homekit_thermostat import HKThermostat, TargetHeatingCoolingState
from utils.data_logger import DataLogger
import time
from pyhap.accessory_driver import AccessoryDriver
import signal
from enum import Enum, unique
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class SmartThermostat:
    """
    Sets up a smart thermostat. The key purpose is to coordinate between the 'dumb' thermostat (`thermostat.py`) and the HomeKit integration (`homekit_thermostat.py`).
    
    Note: All temperature is handled in celcius.

    Key Attributes:
        _heating_relay (Relay): Relay object controlling the heating element.
        _target_temperature_celcius (float): Desired temperature in Celsius. Defaults to 20.0°C.
        _hysteresis (float): Temperature leeway in determining when to activate/deactivate the relay. Set to 0.5°C.

    Methods:
        set_target_temperature_celcius(temperature): Sets a new target temperature.
        start(): Starts the control loop in an asynchronous task to monitor and control temperature.
        register_for_temperature_did_change_notification(callback): Registers a callback to be invoked with the latest temperature reading.
        start_monitoring_current_temperature(): If you've registed for notifcations, this starts the observation process for current temperature.
        shutdown(): Performs cleanup actions, particularly for GPIO resources used by the relay. Once shutdown has been called, you cannot restart.
    """
    
    # Initialization

    def __init__(self, loop):
        self._logger = logging.getLogger(__name__)
        self.loop = loop
        self.thermostat_task = None
        self.driver_task = None

        # Setup thermostat
        relay = Relay(pin=26)
        self.thermostat = Thermostat(relay)
        self.thermostat.register_for_temperature_did_change_notification(self.thermostat_temperature_did_change)
        
        # Setup HomeKit integration
        self.driver = AccessoryDriver(port=51826, loop=self.loop)
        self.homekit_thermostat = HKThermostat(self.driver, "Office Thermostat")
        self.homekit_thermostat.register_for_heating_cooling_state_did_change_notifications(self.heating_cooling_state_did_change)
        self.homekit_thermostat.register_for_target_temperature_did_change_notifications(self.target_temperature_did_change)
        self.driver.add_accessory(accessory=self.homekit_thermostat)
        signal.signal(signal.SIGTERM, self.driver.signal_handler)
        
        self.data_logger = DataLogger(zone=3)
        
    # Public Methods
        
    async def start_thermostat(self):
        self._logger.info("Starting HomeKit integration...")
        self.driver_task = asyncio.create_task(self.driver.async_start())  
        await self.thermostat.start_monitoring_current_temperature()
        
        self.data_logger.set_temperature_callback(self.thermostat.current_temperature_celcius)
        self.data_logger.set_target_temperature_callback(self.thermostat.target_temperature_celcius)
        self.data_logger.set_is_active_callback(self.thermostat.is_active)
        await self.data_logger.log_data_periodically()
        
        
    async def shutdown(self):
        self._logger.info("Shutting down thermostat...")

      # Cancel and await the thermostat task if it exists
        await self._cancel_and_await_task(self.thermostat_task, "Thermostat")
        await self.thermostat.shutdown()
        self.thermostat_task = None  # Reset the task to None after cancellation
            
        # Cancel and await the driver task if it exists
        await self._cancel_and_await_task(self.driver_task, "Driver")
        self.driver_task = None  # Ensure the task reference is cleared
        
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
        self.thermostat.set_target_temperature_celcius(new_temperature)
        
    # Private Methods
   
    async def _cancel_and_await_task(self, task, task_name):
        """
        Cancels the given asyncio Task and waits for it to finish.

        Arguments:
            task (asyncio.Task): The asyncio Task to cancel and await.
            task_name (str): The name of the task for logging purposes.
        """
        if task is not None:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                self._logger.info(f"{task_name} task cancelled.")
            except Exception as e:
                self._logger.error(f"Error stopping {task_name} task: {e}", exc_info=True)
                
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop) # This sets the global event loop and prevents clashing between HAP-Python asyncio.
    controller = SmartThermostat(loop)

    try:
        loop.run_until_complete(controller.start_thermostat())
        loop.run_forever()  # Keep the loop running
    except KeyboardInterrupt:
        pass  # Handle keyboard interrupt
        logging.info("Program terminated by user.")
    except Exception as e:  # Catching other exceptions
        logging.error(f"Unexpected error: {e}", exc_info=True)  # Log the error with stack trace
    finally:
        logging.info("Shutting down gracefully...")
        loop.run_until_complete(controller.shutdown())  # Ensure everything is stopped properly
        loop.close()