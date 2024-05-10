import asyncio
from .weather_api import get_temperature
from .database import insert_temperature_log
from .error_reporter import ErrorReporter

class DataLogger:
    def __init__(self):
        self._temperature_callback = None
        self._target_temperature_callback = None
        self._state_callback = None
        self._error_reporter = ErrorReporter()
        
    async def log_data_periodically(self):
        while True:
            try:
                if self._temperature_callback:
                    current_temperature = await self._temperature_callback()
                    print(f"Current temperature {current_temperature}")

                if self._target_temperature_callback:
                    target_temperature = self._target_temperature_callback()
                    print(f"Target temperature {target_temperature}")

                if self._state_callback:
                    current_state = self._state_callback()
                    print(f"Current state {current_state}") # TODO TRANSLATE THIS STATE

                outdoor_temperature = await get_temperature()
                print(f"Outdoor temperature {outdoor_temperature}") # TODO PROPER ERROR HANDLING

                insert_temperature_log(3, current_temperature, 23, True, target_temperature)
                self._error_reporter.report_error("HELLO BOSS")
            except Exception as e:
                error_message = f"Error occurred while logging data: {e}"
                self._error_reporter.report_error(error_message)

            await asyncio.sleep(5) 
            # await asyncio.sleep(600)  # 600 seconds = 10 minutes

                
    def set_temperature_callback(self, callback):
        self._temperature_callback = callback
        
    def set_target_temperature_callback(self, callback):
        self._target_temperature_callback = callback
        
    def set_state_callback(self, callback):
        self._state_callback = callback