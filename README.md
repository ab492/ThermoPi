# ThermoPi

This is the code for `ThermoPi`, a smart home controller for all things temperature in my flat. It's designed to run on a Raspberry Pi. There are two core components to the code: the smart thermostat component and the temperature logging component. 

## Smart Thermostat
This is the WIP component and requires some setup on the Raspberry Pi as well as having this code installed.

Currently this is a single HomeKit temperature sensor integration, run using `main.py` which uses `temperature_utils.py` to fetch the temperature. The core setup relies on [HAP-python](https://github.com/ikalchev/HAP-python), with a few of my own findings. First follow the HAP-python installation instructions and then use my notes.

1. Definitely create a 'lesserdaemon' user with write access to this repository. I tried using my admin user and kept getting errors about writing a temporary folder. This error only occurred when running the `HAP-python.service`, not directly running `main.py`.
2. Don't bother using "Wait for network" or their suggested fix: I couldn't get either working. I ended up using a 30 second wait, but this might be worth re-assessing in the future.
3. After some debugging, adding `WorkingDirectory=/home/lesserdaemon/WeatherPi` seemed to help the service run without errors.

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

### TODO List
- Add error handing when POST call fails. Maybe it could send an email so I'm aware?
- Could also add email error handling when the sensor timesout too?
