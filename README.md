# ThermoPi

ThermoPi is my smart thermostat project. It's a constant work in progress, used as opportunity to learn more about smart home green technology.

I've started writing up how I built it in a blog series [here](https://maverickprogramming.com/blog/how-to-build-a-smart-thermostat-part-1).

It's designed and tested on a Raspberry Pi (Raspberry Pi 3 Model B Rev 1.2).


# Working Notes
> Note: Everything below here are my working notes, used to document the code for my own future use.

## Getting Started

1. Clone the repo.
2. Copy `.env.template` to your local machine, rename to `.env` and update the values.
3. Install posgres with `sudo apt install postgresql`. See [Postgres Database](#postgres-database) for more details.
4. Run `python3 -m venv venv` to set up a virtual environment. If that doesn't work, run `sudo apt install python3-venv` to install `venv`.
5. Run `source venv/bin/activate` to activate `venv`.
6. Run `pip install -r requirements.txt` to install package dependencies.
7. Run `smart_thermostat.py` to start running the thermostat.

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

## Postgres Database
I used a Postgres database for data logging. The thermostat *should* run without a database setup because the error logger just reports errors, but I've not tested this thoroughly. Aside from installing Postgres, you'll need to have a table `temperature_logs` with the correct fields as per `database.py`. After creating the database you'll need to create a user with all privileges that matches the name of the user account (`developer`). See [postgres.md](documentation/postgres.md) for details and commands.

## Useful Articles
- https://pimylifeup.com/raspberry-pi-temperature-sensor/
- https://thepihut.com/blogs/raspberry-pi-tutorials/ds18b20-one-wire-digital-temperature-sensor-and-the-raspberry-pi

## TODO List
- Look into smarter temperature control. Due to the way underfloor heating works, it continues heating the room once the target temperature has been met. Look into calculating the rate of change in order to predict when to turn the heating element off.
- Add an offline override if using the temperature sensor in a main room.
  
## Bugs
- When initially powering on the device the target temperature is logged as 10 even though it’s set higher. Once the thermostat is turned on and updated it's reported correctly. Seems to be an issue with reporting initial state.