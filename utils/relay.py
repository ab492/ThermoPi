import RPi.GPIO as GPIO
from .relay_protocol import RelayProtocol

class Relay(RelayProtocol):
    """
    A class to represent a relay controlled by Raspberry Pi. This is designed to work with an ACTIVE LOW relay (i.e. LOW turns the relay on).
    """
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM) # Refer to pins by their Broadcom SOC channel number (associated to Broadcom chipset on the Pi).
        GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.HIGH) # Initially OFF for ACTIVE LOW.
    
    @property
    def is_active(self):
        return GPIO.input(self.pin) == GPIO.LOW
    
    def turn_on(self):
        GPIO.output(self.pin, GPIO.LOW)
        print("Relay ON")

    def turn_off(self):
        GPIO.output(self.pin, GPIO.HIGH)
        print("Relay OFF")

    def cleanup(self):
        GPIO.cleanup(self.pin)
        print("GPIO Cleaned up")

if __name__ == "__main__":
    pin_number = 17  # Example GPIO pin number, change this to your actual relay GPIO pin
    relay = Relay(pin_number)

    try:
        print("Turning relay ON...")
        relay.turn_on()

        # Keeping the relay ON for a certain duration to observe the change, for example, 5 seconds
        input("Press Enter to continue...")  # Wait for user input to proceed (or use time.sleep(5) to wait for 5 seconds)

    finally:
        # It's important to clean up GPIO settings to ensure the GPIO pins are reset properly when the script ends
        relay.cleanup()