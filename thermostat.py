from utils.relay_utils import Relay
from utils.temperature_utils import read_temp
import time 
## todo: check less than or equal is working
## add threshold measurements
## add unit tests!
## add note that all values are celcius

class Thermostat:
    def __init__(self, relay_pin):
        self._heating_relay = Relay(relay_pin)
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
    relay_pin = 26
    thermostat = Thermostat(relay_pin)
    thermostat.set_target_temperature(22)
    thermostat.start()
