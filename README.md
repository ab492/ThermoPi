# WeatherPi

This is the code for `WeatherPi` which is designed to work with a Raspberry Pi and a DS18B20 temperature sensor.

## How To Use
This can only be tested with a DS18B20 installed via GPIO pins.
- Copy `env.template` and rename to `.env`. Add in correct values.
- Activate the virtual Python environment: `source venv/bin/activate`.
- Run `python temperature_utils.py`.

The thinking is that the script is only ever run automatically using a Cron Job.

## Cron Job
The `temperature_metrics.py` script is set up to run via a Cron Job every hour. To set this up, run `crontab -e` and add `0 * * * * /home/andy/WeatherPi/venv/bin/python /home/andy/WeatherPi/temperature_metrics.py` for hourly measurements.

## Useful Articles
- https://pimylifeup.com/raspberry-pi-temperature-sensor/