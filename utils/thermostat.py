from .relay import Relay
from .temperature_utils import read_temp
import time 
import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class Thermostat:
    """
    Controls a heating system through a relay based on current and target temperatures,
    maintaining the desired environment within a hysteresis range.
    
    Note: All temperature is handled in celcius.

    Key Attributes:
        _heating_relay (Relay): Relay object controlling the heating element.
        _target_temperature (float): Desired temperature in Celsius. Defaults to 20.0°C.
        _hysteresis (float): Temperature leeway in determining when to activate/deactivate the relay. Set to 0.5°C.

    Methods:
        set_target_temperature(temperature): Sets a new target temperature.
        start(): Starts the control loop in an asynchronous task to monitor and control temperature.
        stop(): Terminates the thermostat control loop if it's running.
        shutdown(): Performs cleanup actions, particularly for GPIO resources used by the relay. Once shutdown has been called, you cannot re-start.
        register_for_temperature_did_change_notification(callback): Registers a callback to be invoked with the latest temperature reading.
    """
    
    def __init__(self, relay: Relay, target_temperature: float = 20.0):
        self._logger = logging.getLogger(__name__)
        self._heating_relay = relay
        self._target_temperature = target_temperature
        self._hysteresis = 0.5
        self._temperature_did_change_notification = None
        self._control_loop_task = None
                
    async def current_temperature(self):
        current_temperature = await read_temp()
        return current_temperature.celcius
    
    @property
    def target_temperature(self):
        return self._target_temperature
    
    @property
    def is_active(self):
        """Boolean indicating if the relay (and thus the heating element) is active."""
        return self._heating_relay.is_active
    
    def set_target_temperature(self, temperature):
        self._target_temperature = temperature
        self._logger.info("Target temperature set to: %s°C", self._target_temperature)

    async def start(self):
        # If start() is called with an existing task running, cancel it.
        if self._control_loop_task and not self._control_loop_task.done():
            self._logger.info("Stopping existing control loop before starting a new one.")
            self._control_loop_task.cancel()
            await self._control_loop_task  # Wait for the existing control loop to finish
            
        # Start a new control loop task
        self._control_loop_task = asyncio.create_task(self.control_loop())
        self._logger.info("Control loop started.")

    async def control_loop(self):
        try:
            while True:  # Keep the loop running indefinitely
                await self._check_and_control_temperature()
                await asyncio.sleep(3)  # Sleep for 3 seconds between checks
        except asyncio.CancelledError:
            self._logger.info("Control loop stopped.")
                         
    async def _check_and_control_temperature(self):
        current_temperature = await self.current_temperature()

        if self._temperature_did_change_notification:
            self._temperature_did_change_notification(current_temperature)
       
        if not self.is_active and current_temperature < (self.target_temperature - self._hysteresis):
            self._logger.info("Current temperature (%s°C) below target (%s°C). Turning ON.", current_temperature, self._target_temperature)
            # self._heating_relay.turn_on()
        elif self.is_active and current_temperature > (self.target_temperature + self._hysteresis):
            self._logger.info("Current temperature (%s°C) above target (%s°C). Turning OFF.", current_temperature, self._target_temperature)
            # self._heating_relay.turn_off()
        else:
            if self.is_active:
                self._logger.info(f"Heating is ON, current temperature ({current_temperature}°C) is approaching the target ({self.target_temperature}°C).")
            else:
                self._logger.info(f"Heating is OFF, current temperature ({current_temperature}°C) is above the lower threshold ({self.target_temperature - self._hysteresis}°C). No action required.")
    
    async def stop(self):
        if self._control_loop_task:
            self._control_loop_task.cancel()  # Cancel the control loop task
            try:
                await self._control_loop_task  # Wait for the control loop task to be cancelled
            except asyncio.CancelledError:
                # This exception is expected when the task is cancelled, so you can ignore it
                self._logger.info("Control loop task cancelled.")
            
            self._control_loop_task = None  # Clear the task reference after it's finished
            
        self._logger.info("Thermostat stopped.")

    def register_for_temperature_did_change_notifcation(self, callback):
        self._temperature_did_change_notification = callback
        self._logger.info("Temperature change notification callback registered.")

    def shutdown(self):
        if self._heating_relay:
            self._heating_relay.cleanup()
        self._logger.info("Thermostat shutdown complete. Resources have been cleaned up.")
        
# Example usage
async def main():
    relay = Relay(26)
    thermostat = Thermostat(relay)
    thermostat.set_target_temperature(18)
    await thermostat.start()

if __name__ == "__main__":
    asyncio.run(main())