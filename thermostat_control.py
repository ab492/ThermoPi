import argparse
import asyncio
from utils.thermostat import Thermostat
from utils.relay import Relay
from homekit_thermostat import HKThermostat
import time
from pyhap.accessory_driver import AccessoryDriver
import signal

class ThermostatController:
    def __init__(self):
        self.relay = Relay(pin=26)
        self.thermostat = Thermostat(self.relay)
        self.target_temperature = 21
        # self.thermostat.register_for_temperature_did_change_notifcation(self.thermostat_temperature_did_change)
        
        self.driver = AccessoryDriver(port=51826)
        self.homekit_thermostat = HKThermostat(self.driver, "THERMOBOY")
        self.driver.add_accessory(accessory=self.homekit_thermostat)
        signal.signal(signal.SIGTERM, self.driver.signal_handler)
        # self.homekit_thermostat.register_for_heating_cooling_state_did_change_notifications(self.on_heating_cooling_state_did_change)
        # self.homekit_thermostat.register_for_target_temperature_did_change_notifications(self.on_target_temperature_did_change)

    def on_heating_cooling_state_did_change(self, state):
        print(f"State here: {state}")
        
    def on_target_temperature_did_change(self, new_temperature):
        self.thermostat.set_target_temperature(new_temperature)
        print(f"Thermostat target temp: {self.thermostat.target_temperature}")
        
    # def thermostat_temperature_did_change(self, new_temperature):
    #     self.homekit_thermostat.set_current_temperature(self.thermostat.current_temperature)
        
    async def start_thermostat(self):
        print("Starting thermostat...")
        self.thermostat.set_target_temperature(self.target_temperature)
        await self.thermostat.start()
        print("DID YOU GET HERE?")
        self.driver.start()

    async def stop_thermostat(self):
        print("Stopping thermostat...")
        # Add logic to stop the thermostat if necessary.
        await self.thermostat.stop()
        
async def main():
    parser = argparse.ArgumentParser(description="Thermostat Control Script")
    parser.add_argument('--start', action='store_true', help="Start the thermostat")
    parser.add_argument('--stop', action='store_true', help="Stop the thermostat")

    args = parser.parse_args()
    controller = ThermostatController()

    if args.start:
        await controller.start_thermostat()
    elif args.stop:
        await controller.stop_thermostat()
        
if __name__ == "__main__":
    loop = asyncio.get_event_loop()  # Get the current event loop
    try:
        loop.run_until_complete(main())  # Run the main coroutine
    finally:
        loop.close()  # Close the loop when done