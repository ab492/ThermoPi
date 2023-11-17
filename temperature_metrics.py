import os
from utils.temperature_utils import read_temp

def main():
    temperature = read_temp()
    celcius = temperature.celcius
    print(f"Temperature: {celcius} °C")

if __name__ == '__main__':
    main()