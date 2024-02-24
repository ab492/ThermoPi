from .relay import Relay
from .temperature_utils import read_temp
import time 
import asyncio
import logging
import random

class Thermostat:
    """
    Controls a heating system through a relay based on current and target temperatures, maintaining the desired environment within a hysteresis range.
    
    Note: All temperature is handled in celcius.

    Key Attributes:
        _heating_relay (Relay): Relay object controlling the heating element.
        _target_temperature_celcius (float): Desired temperature in Celsius. Defaults to 20.0°C.
        _hysteresis (float): Temperature leeway in determining when to activate/deactivate the relay. Set to 0.5°C.

    Methods:
        set_target_temperature_celcius(temperature): Sets a new target temperature.
        start(): Starts the control loop in an asynchronous task to monitor and control temperature.
        stop(): Terminates the thermostat control loop if it's running.
        register_for_temperature_did_change_notification(callback): Registers a callback to be invoked with the latest temperature reading.
        start_monitoring_current_temperature(): If you've registed for notifcations, this starts the observation process for current temperature.
        shutdown(): Performs cleanup actions, particularly for GPIO resources used by the relay. Once shutdown has been called, you cannot restart.
    """
    
    # Initialization

    def __init__(self, relay: Relay, target_temperature_celcius: float = 20.0):
        self._logger = logging.getLogger(__name__)
        self._heating_relay = relay
        self._target_temperature_celcius = target_temperature_celcius
        self._hysteresis = 0.5
        self._temperature_did_change_notification = None
        self._control_loop_task = None
        self._temperature_monitor_task = None
    
    # Public Properties  
      
    async def current_temperature_celcius(self):
        current_temperature = await read_temp()
        return current_temperature.celcius
    
    def target_temperature_celcius(self):
        return self._target_temperature_celcius
    
    def is_active(self):
        """Boolean indicating if the relay (and thus the heating element) is active."""
        return self._heating_relay.is_active
    
    # Public Methods
    
    def set_target_temperature_celcius(self, temperature):
        self._target_temperature_celcius = temperature
        self._logger.info("Target temperature set to: %s°C", self._target_temperature_celcius)

    def register_for_temperature_did_change_notification(self, callback):
        self._temperature_did_change_notification = callback
        self._logger.info("Temperature change notification callback registered.")

    async def start_monitoring_current_temperature(self):
        """If you've registered for current temperature notifications, this will start monitoring and notifying of the current temperature every 10 seconds."""
        if self._temperature_monitor_task is None:
            self._temperature_monitor_task = asyncio.create_task(self._temperature_monitor_loop())
            self._logger.info("Temperature monitor loop started.")
        
    async def start(self):
        """Starts regulating the temperature as per the thermostat settings."""

        # If start() is called with an existing control loop task running, cancel it.
        if self._control_loop_task and not self._control_loop_task.done():
            self._logger.info("Stopping existing control loop before starting a new one.")
            self._control_loop_task.cancel()
            await self._control_loop_task  # Wait for the existing control loop to finish
            
        # Start a new control loop task
        self._control_loop_task = asyncio.create_task(self._control_loop())
        self._logger.info("Control loop started.")
    
    async def stop(self):
        """Stops regulating the temperature."""

        if self._control_loop_task:
            self._control_loop_task.cancel()  # Cancel the control loop task
            try:
                await self._control_loop_task  # Wait for the control loop task to be cancelled
            except asyncio.CancelledError:
                self._logger.info("Control loop task cancelled.")
            except Exception as e:
                self._logger.error(f"Unexpected error while stopping the control loop: {e}")
            
            self._control_loop_task = None  # Clear the task reference after it's finished
            
        self._heating_relay.turn_off()
        self._logger.info("Thermostat stopped.")
    
    async def shutdown(self):
        """Shuts down the thermostat by cleaning up the relay and cancelling notification. Once this is called, you can't restart."""

        if self._heating_relay:
            self._heating_relay.cleanup()
            
        if self._temperature_monitor_task:
            self._temperature_monitor_task.cancel()
            try: 
                await self._temperature_monitor_task
            except asyncio.CancelledError:
                self._logger.info("Temperature monitor task cancelled.")
            self._temperature_monitor_task = None
            
        self._logger.info("Thermostat shutdown complete. Resources have been cleaned up and notifications stopped.")
        
    # Private Methods
        
    async def _temperature_monitor_loop(self):
        try:
            while True:
                current_temperature = await self.current_temperature_celcius()
                if self._temperature_did_change_notification:
                    self._temperature_did_change_notification(current_temperature)
                await asyncio.sleep(10) # Sleep for 10 seconds between checks
        except asyncio.CancelledError:
            self._logger.info("Temperature monitor loop stopped.")
        except Exception as e:
            self._logger.error(f"Unexpected error in temperature monitor loop: {e}")
            
    async def _control_loop(self):
        try:
            while True:  # Keep the loop running indefinitely
                await self._check_and_control_temperature()
                await asyncio.sleep(5)  # Sleep for 5 seconds between checks
        except asyncio.CancelledError:
            self._logger.info("Control loop stopped.")
        except Exception as e:
            self._logger.error(f"Unexpected error while stopping the control loop: {e}")
                         
    async def _check_and_control_temperature(self):
        current_temperature = await self.current_temperature_celcius()
               
        if not self.is_active and current_temperature < (self._target_temperature_celcius - self._hysteresis):
            self._logger.info("Current temperature (%s°C) below target (%s°C). Turning ON.", current_temperature, self._target_temperature_celcius)
            self._heating_relay.turn_on()
        elif self.is_active and current_temperature > (self._target_temperature_celcius + self._hysteresis):
            self._logger.info("Current temperature (%s°C) above target (%s°C). Turning OFF.", current_temperature, self._target_temperature_celcius)
            self._heating_relay.turn_off()
        else:
            if self.is_active:
                self._logger.info(f"Heating is ON, current temperature ({current_temperature}°C) is approaching the target ({self._target_temperature_celcius}°C).")
            else:
                self._logger.info(f"Heating is OFF, current temperature ({current_temperature}°C) is above the lower threshold ({self._target_temperature_celcius - self._hysteresis}°C). No action required.")
    
# Example usage
async def main():
    relay = Relay(26)
    thermostat = Thermostat(relay)
    thermostat.set_target_temperature_celcius(18)
    await thermostat.start()

if __name__ == "__main__":
    asyncio.run(main())