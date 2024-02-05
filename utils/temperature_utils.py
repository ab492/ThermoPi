import os
import glob
import asyncio
from typing import NamedTuple

"""
This script allows you to read temperature data from a DS18B20 temperature sensor connected to a Raspberry Pi, return the temperature in celsius and fahrenheit.

Prerequisites:
- A Raspberry Pi with Raspbian OS installed.
- A DS18B20 temperature sensor properly connected to the GPIO pins of the Raspberry Pi (see references).
- The 1-Wire interface enabled on the Raspberry Pi.

Configuration:
Before running the script, ensure the Raspberry Pi is configured to interface with the DS18B20 sensor:
1. Add the line 'dtoverlay=w1-gpio' to /boot/config.txt. This enables the 1-Wire interface on the GPIO pin used by the sensor.
2. Add 'w1-gpio' and 'w1-therm' to /etc/modules. This ensures that the necessary modules are loaded at boot.

References:
For more information on setting up and using the DS18B20 temperature sensor with a Raspberry Pi, visit:
- https://thepihut.com/blogs/raspberry-pi-tutorials/ds18b20-one-wire-digital-temperature-sensor-and-the-raspberry-pi
- https://pimylifeup.com/raspberry-pi-temperature-sensor/

"""
class TemperatureInfo(NamedTuple):
    celcius: float
    fahrenheit: float
  
# This path is where 1-wire devices are mounted in the filesystem of a Linux-based system.
base_dir = '/sys/bus/w1/devices/'

# The '28' prefix is common for DS18B20 temperature sensors. Since we only have 1 sensor, we just grab the first.
try:
    device_folder = glob.glob(base_dir + '28*')[0]
except IndexError:
    raise FileNotFoundError("No temperature sensor found; is it wired correctly?")

# The 'w1_slave' is provided by 'w1-therm' module and contains the raw temperature data from the sensor.
device_file = device_folder + '/w1_slave'

async def _read_temp_raw():
    try:
        # Open is not natively async, so we use 'asyncio' to run it in a threadpool
        with await asyncio.to_thread(open, device_file, 'r') as f:
            lines = await asyncio.to_thread(f.readlines)
        return lines
    except Exception as e:  # It's good practice to specify the exception
        raise IOError(f"Failed to read device file; is the temperature sensor wired correctly? Error: {e}")

async def read_temp() -> TemperatureInfo:
    # The raw temperature comes over two lines in the following format:
    # 54 01 4b 46 7f ff 0c 10 fd : crc=fd YES
    # 54 01 4b 46 7f ff 0c 10 fd t=21250
    lines = await _read_temp_raw()

    max_attempts = 10
    attempts = 0
    
    # The first line is a checksum to indicate if the measurement is valid. 
    # If the line ends in 'YES', we can proceed. If 'NO', the sensor is not ready so we wait 0.2 seconds.
    while True:
        try:
            if lines[0].strip()[-3:] == 'YES':
                break  # Exit loop if the condition is met
            elif attempts >= max_attempts:
                raise TimeoutError("Sensor read attempt exceeded maximum retries.")
        except IndexError:
            raise IndexError("Unexpected data format from sensor; is the temperature sensor wired correctly?")

        await asyncio.sleep(0.2)
        lines = await _read_temp_raw()
        attempts += 1

    # Now we find the actual raw data by finding 't='.
    equals_pos = lines[1].find('t=')

    # If `equals_pos` is not -1, it means 't=' has been located.
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return TemperatureInfo(celcius=temp_c, fahrenheit=temp_f)
    
async def main():
    try:
        temperature_info = await read_temp()
        print(f"Temperature: {temperature_info.celcius}°C, {temperature_info.fahrenheit}°F")
    except Exception as e:
        print(f"Error reading temperature: {e}")

if __name__ == "__main__":
    # asyncio.run() is used to run the main function, which handles the async call to read_temp
    asyncio.run(main())