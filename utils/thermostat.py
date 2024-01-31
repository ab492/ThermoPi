from .relay import Relay
from .temperature_utils import read_temp
import time 

class Thermostat:
    """
    Controls a heating system through a relay based on current and target temperatures,
    maintaining the desired environment within a hysteresis range.
    
    Note: All temperature is handled in celcius.

    Attributes:
        _heating_relay (Relay): Relay object controlling the heating element.
        _target_temperature (float): Desired temperature in Celsius. Defaults to 20.0°C.
        _hysteresis (float): Temperature leeway in determining when to activate/deactivate the relay.

    Methods:
        set_target_temperature(temperature): Sets a new target temperature.
        start(): Initiates the thermostat control loop.
        stop(): Terminates the control loop and performs cleanup.
    """
    
    def __init__(self, relay: Relay, target_temperature: float = 20.0):
        self._heating_relay = relay
        self._target_temperature = 20.0
        self._hysteresis = 0.5
                
    @property
    def current_temperature(self):
        current_temperature = read_temp()
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
        
    def start(self):
        try:
            # Continuously check and control the temperature
            while True:
                self._check_and_control_temperature()
                time.sleep(3)  # Wait for 3 seconds before checking again
        except KeyboardInterrupt:
            print("Terminating the thermostat control.")
        finally:
            self.stop()
        
    def _check_and_control_temperature(self):
        print(f"Current temp: {self.current_temperature}")
        if not self.is_active and self.current_temperature < (self.target_temperature - self._hysteresis):
            print(f"Current temperature ({self.current_temperature}°C) below target temperature ({self.target_temperature}°C). Turning thermostat ON.")
            self._heating_relay.turn_on()
        elif self.is_active and self.current_temperature > (self.target_temperature + self._hysteresis):
            print(f"Current temperature ({self.current_temperature}°C) above target temperature ({self.target_temperature}°C). Turning thermostat OFF.")
            self._heating_relay.turn_off()
  
    def stop(self):
        self._cleanup()
        
    def _cleanup(self):
        self._heating_relay.cleanup()
        
# Example usage
if __name__ == "__main__":
    # Define the GPIO pin for the relay and the temperature threshold
    relay = Relay(26)
    thermostat = Thermostat(relay)
    thermostat.set_target_temperature(21)
    thermostat.start()
