edit_thermostat_service:
	sudo nano /etc/systemd/system/thermostat.service

logs:
	sudo journalctl -u thermostat.service -e

start_thermostat:
	sudo systemctl start thermostat.service

stop_thermostat:
	sudo systemctl stop thermostat.service

thermostat_startup_logs:
	sudo journalctl -u thermostat.service -e

enable_thermostat_at_boot:
	sudo systemctl enable thermostat.service

disable_thermostat_at_boot:
	sudo systemctl disable thermostat.service

run_tests:
	python -m unittest discover -s tests
