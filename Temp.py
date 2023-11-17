import os
import glob
import time
 
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

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f

while True:
	print(read_temp())	
	time.sleep(1)