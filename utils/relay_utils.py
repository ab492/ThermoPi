import RPi.GPIO as GPIO

class Relay:
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
