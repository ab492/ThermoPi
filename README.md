# ThermoPi

This is the code for `ThermoPi`, a smart home controller for all things temperature in my flat. It's designed to run on a Raspberry Pi (Raspberry Pi 3 Model B Rev 1.2). 

## Getting Started
1. Clone the repo.
2. Run `python3 -m venv venv` to set up a virtual environment. If that doesn't work, run `sudo apt install python3-venv` to install `venv`.
3. Run `source venv/bin/activate` to activate `venv`.
4. Run `pip install -r requirements.txt` to install package dependencies.

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

---







```
[Unit]
Description = HAP-python daemon
After = local-fs.target network-wait-online.service pigpiod.service

[Service]
WorkingDirectory=/home/lesserdaemon/WeatherPi
User = lesserdaemon
ExecStartPre=/bin/sleep 30
ExecStart = /home/lesserdaemon/WeatherPi/venv/bin/python3 /home/lesserdaemon/WeatherPi/main.py

[Install]
WantedBy = multi-user.target
```

Here are some helpful commands:

```
> sudo systemctl start HAP-python
> systemctl status HAP-python
> sudo journalctl -u HAP-python -e  # To see the output of the start up script. The -e option means shows the end of the file.
> sudo systemctl stop HAP-python
```

### TODO  List
- Add an offline override if using the temperature sensor in a main room.

## Temperature Logging (previously WeatherPi)
This can only be tested with a DS18B20 installed via GPIO pins. It takes the temperature directly from the DS18B20 and sends it to an API (`api.bramblytech.co.uk`) which allows longer term tracking for data analysis, and for displaying current data on the Brambly iOS widget.

This was originally intended for outdoor temperature monitoring via solar and battery but wasn't really cost effective (see `Energy_Analysis.md` in existing commits).

### How To Use

- Copy `env.template` and rename to `.env`. Add in correct values.
- Activate the virtual Python environment: `source venv/bin/activate`.
- Run `python temperature_utils.py`.

The thinking is that the script is only ever run automatically using a Cron Job.

### Cron Job
The `temperature_metrics.py` script is set up to run via a Cron Job every hour. To set this up, run `crontab -e` and add `0 * * * * /home/andy/WeatherPi/venv/bin/python /home/andy/WeatherPi/temperature_metrics.py` for hourly measurements.

### Useful Articles
- https://pimylifeup.com/raspberry-pi-temperature-sensor/
- https://thepihut.com/blogs/raspberry-pi-tutorials/ds18b20-one-wire-digital-temperature-sensor-and-the-raspberry-pi

### TODO List
- Add error handing when POST call fails. Maybe it could send an email so I'm aware?
- Could also add email error handling when the sensor timesout too?
