# ThermoPi

This is the code for `ThermoPi`, a smart thermostat for my home. It's designed and tested on a Raspberry Pi (Raspberry Pi 3 Model B Rev 1.2).

## Getting Started
1. Clone the repo.
2. Run `python3 -m venv venv` to set up a virtual environment. If that doesn't work, run `sudo apt install python3-venv` to install `venv`.
3. Run `source venv/bin/activate` to activate `venv`.
4. Run `pip install -r requirements.txt` to install package dependencies.
5. Run `smart_thermostat.py` to start running the thermostat.

In reality, you want `smart_thermostat.py` to run on launch of the Pi automatically. You can set it up to run as a system service using the [template](service_files/thermostat.service).

There are some helpful [MAKE commands](Makefile) you can use to help.

## Thermostat
This is the core functionality of `ThermoPi` and is designed to work without an internet connection (local network required for access) and without the 'smart' elements like HomeKit integration and API tracking.

### Installing The Temperature Sensor
1. As sudo, add the following line to `/boot/config.txt`. This enables the 1-Wire interface on the GPIO pin used by the sensor. 
```
dtoverlay=w1-gpio
```
2. As sudo, add the following to `/etc/modules`. This ensures that the necessary modules are loaded at boot.
```
w1-gpio
w1-therm
```

### Setting Up The Relay
1. If you're using an unprivileged user, you'll need to run the following the grant permission to access the GPIO pins:
```
sudo adduser your-user gpio
```

## HomeKit Integration
I used [HAP-python](https://github.com/ikalchev/HAP-python) for my HomeKit integration.

Whilst developing with `HAP-python`, here are a few discoveries I made that might be useful in future debugging. These notes have been incorporated into the system, but I'm keeping them here for the record.

1. Use an unprivaledged user when running this startup script. 
2. Don't bother using "Wait for network" or their suggested fix: I couldn't get either working. I ended up using a 30 second wait, but this might be worth re-assessing in the future.
3. Initially I got errors about accessing temporary files; I believe this was linked to setting relative paths within my Python scripts. Adding `WorkingDirectory=/home/developer/ThermoPi` seemed to help the service run without errors.

### Useful Articles
- https://pimylifeup.com/raspberry-pi-temperature-sensor/
- https://thepihut.com/blogs/raspberry-pi-tutorials/ds18b20-one-wire-digital-temperature-sensor-and-the-raspberry-pi

### TODO List
- Look into smarter temperature control. Due to the way underfloor heating works, it continues heating the room once the target temperature has been met. Look into calculating the rate of change in order to predict when to turn the heating element off.
- Add an offline override if using the temperature sensor in a main room.

