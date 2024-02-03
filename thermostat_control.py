import argparse
from utils.thermostat import Thermostat
from utils.relay import Relay
from homekit_thermostat import HomeKitThermostat
import time

class ThermostatController:
    def __init__(self):
        self.relay = Relay(pin=26)
        self.thermostat = Thermostat(self.relay)
        self.target_temperature = 21
        
        self.thermostat.register_for_temperature_did_change_notifcation(self.thermostat_temperature_did_change)
        self.homekit_thermostat = HomeKitThermostat('HomeKit Boy')
        self.homekit_thermostat.register_for_heating_cooling_state_did_change_notifications(self.on_heating_cooling_state_did_change)
        self.homekit_thermostat.register_for_target_temperature_did_change_notifications(self.on_target_temperature_did_change)

    def on_heating_cooling_state_did_change(self, state):
        print(f"State here: {state}")
        
    def on_target_temperature_did_change(self, new_temperature):
        self.thermostat.set_target_temperature(new_temperature)
        print(f"Thermostat target temp: {self.thermostat.target_temperature}")
        
    def thermostat_temperature_did_change(self, new_temperature):
        self.homekit_thermostat.set_current_temperature(self.thermostat.current_temperature)
        
    def start_thermostat(self):
        print("Starting thermostat...")
        self.thermostat.set_target_temperature(self.target_temperature)
        self.thermostat.start()
        self.homekit_thermostat.start()

    def stop_thermostat(self):
        print("Stopping thermostat...")
        # Add logic to stop the thermostat if necessary.
        self.thermostat.stop()
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Thermostat Control Script")
    parser.add_argument('--start', action='store_true', help="Start the thermostat")
    parser.add_argument('--stop', action='store_true', help="Stop the thermostat")

    args = parser.parse_args()
    controller = ThermostatController()

    if args.start:
        controller.start_thermostat()
    elif args.stop:
        controller.stop_thermostat()