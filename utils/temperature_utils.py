import os
import glob
import time
from typing import NamedTuple

# Code for interacting with sensor pinched from here: https://pimylifeup.com/raspberry-pi-temperature-sensor/ 

class TemperatureInfo(NamedTuple):
    celcius: float
    fahrenheit: float
 
# Load the kernel module for enabling GIPO I/O pins to communicate with 1-wire devices.
os.system('modprobe w1-gpio')

# Load the kernel module for reading data from 1-wire thermometers.
os.system('modprobe w1-therm')
 
# This path is where 1-wire devices are mounted in the filesystem of a Linux-based system.
base_dir = '/sys/bus/w1/devices/'

# The '28' prefix is common for DS18B20 temperature sensors. Since we only have 1 sensor, we just grab the first.
device_folder = glob.glob(base_dir + '28*')[0]

# The 'w1_slave' is provided by 'w1-therm' module and contains the raw temperature data from the sensor.
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp() -> TemperatureInfo:
    # The raw temperature comes over two lines in the following format:
    # 54 01 4b 46 7f ff 0c 10 fd : crc=fd YES
    # 54 01 4b 46 7f ff 0c 10 fd t=21250
    lines = read_temp_raw()

    max_attempts = 10
    attempts = 0
    
    # The first line is a checksum to indicate if the measurement is valid. 
    # If the line ends in 'YES', we can proceed. If 'NO', the sensor is not ready so we wait 0.2 seconds.
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
        attempts += 1
        if attempts >= max_attempts:
            raise TimeoutError("Sensor read attempt exceeded maximum retries.")
    
    # Now we find the actual raw data by finding 't='.
    equals_pos = lines[1].find('t=')

    # If `equals_pos` is not -1, it means 't=' has been located.
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return TemperatureInfo(celcius=temp_c, fahrenheit=temp_f)
    
if __name__ == "__main__":
    try:
        temperature_info = read_temp()
        print(f"Temperature: {temperature_info.celcius}°C, {temperature_info.fahrenheit}°F")
    except Exception as e:
        print(f"Error reading temperature: {e}")