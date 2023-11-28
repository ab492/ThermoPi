import os
from utils.temperature_utils import read_temp
from utils.api_utils import send_balcony_temperature
def main():
    temperature = read_temp()
    celcius = temperature.celcius
    send_balcony_temperature(celcius)
    print(f"Temperature: {celcius} °C")


if __name__ == '__main__':
    main()