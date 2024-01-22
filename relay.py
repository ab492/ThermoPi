from utils.relay_utils import Relay
import time

# # Setup GPIO using BCM numbering
# GPIO.setmode(GPIO.BCM)

# Define the GPIO pin for the relay channel
heating_relay_pin = 26  # CH3
heating_relay = Relay(pin=heating_relay_pin)

led_relay_pin = 21
led_relay = Relay(pin=led_relay_pin)

try:
    heating_relay.turn_on()
    led_relay.turn_on()
    time.sleep(20)
    heating_relay.turn_off()
    led_relay.turn_off()

finally:
    heating_relay.cleanup()
    led_relay.cleanup()
