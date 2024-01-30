import argparse
from utils.thermostat import Thermostat
from utils.relay import Relay

import sys
print(sys.path)


relay = Relay(pin=26)
thermostat = Thermostat(relay)
target_temperature = 21

def start_thermostat():
    thermostat.set_target_temperature(target_temperature)
    thermostat.start()
    
def stop_thermostat():
    thermostat.stop()
  
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Thermostat Control Script")
    parser.add_argument('--start', action='store_true', help="Start the thermostat")
    parser.add_argument('--stop', action='store_true', help="Stop the thermostat")

    args = parser.parse_args()

    if args.start:
        start_thermostat()
    elif args.stop:
        stop_thermostat()

