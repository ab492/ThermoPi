import asyncio
from .weather_api import get_temperature
from .database import insert_temperature_log
from .error_reporter import ErrorReporter
import logging

class DataLogger:
    """
    A class for logging temperature data periodically to a database.
    
    Attributes:
        _zone (int): The heating zone identifier for which data is logged.
        _temperature_callback (callable): A callback function that returns the current indoor temperature.
        _target_temperature_callback (callable): A callback function that returns the target temperature.
        _is_active_callback (callable): A callback function that returns the heating system's current state.
        _error_reporter (ErrorReporter): An instance of ErrorReporter for logging errors.
        _logger (Logger): A logging instance for logging information and errors.
        
    Methods:
        set_temperature_callback(callback): Sets the temperature callback.
        set_target_temperature_callback(callback): Sets the target temperature callback.
        set_is_active_callback(callback): Sets the active state callback.
        log_data_periodically(): Logs data every 10 minutes to the database.
    """
    def __init__(self, zone: int):
        self._logger = logging.getLogger(__name__)
        self._zone = zone
        self._temperature_callback = None
        self._target_temperature_callback = None
        self._is_active_callback = None
        self._error_reporter = ErrorReporter()
        
    def set_temperature_callback(self, callback):
        self._temperature_callback = callback
        
    def set_target_temperature_callback(self, callback):
        self._target_temperature_callback = callback
        
    def set_is_active_callback(self, callback):
        self._is_active_callback = callback
        
    async def log_data_periodically(self):
        while True:
            current_temperature = None
            target_temperature = None
            current_state = None
            outdoor_temperature = None
            
            try:
                if self._temperature_callback:
                    current_temperature = await self._temperature_callback()
                else:
                    self._error_reporter.report_error("Temperature callback is not set.")

                if self._target_temperature_callback:
                    target_temperature = self._target_temperature_callback()
                else:
                    self._error_reporter.report_error("Target temperature callback is not set.")

                if self._is_active_callback:
                    current_state = self._is_active_callback()
                else:
                    self._error_reporter.report_error("Active state callback is not set.")

                outdoor_temperature = await get_temperature()

                # Insert log only if all required data is available
                if current_temperature is not None and target_temperature is not None and current_state is not None:
                    insert_temperature_log(zone=self._zone, indoor_temp=current_temperature, outdoor_temp=outdoor_temperature, heating_status=current_state, target_temp=target_temperature)
                    self._logger.info("Zone: %s, Current Temperature: %s°C, Outdoor Temperature: %s°C, Current State: %s, Target Temperature: %s°C", self._zone, current_temperature, outdoor_temperature, current_state, target_temperature)
                else:
                    self._error_reporter.report_error("Missing one or more required parameters: Cannot log temperature data.")

            except Exception as e:
                error_message = f"Error occurred while logging data: {e}"
                self._error_reporter.report_error(error_message)

            await asyncio.sleep(600)  # 600 seconds = 10 minutes