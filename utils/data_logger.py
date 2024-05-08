import asyncio
from .weather_api import get_temperature
from .database import insert_temperature_log

class DataLogger:
    def __init__(self):
        self.temperature_callback = None
        self.target_temperature_callback = None
        self.state_callback = None
        
        
    async def log_data_periodically(self):
        while True:
            try:
                if self.temperature_callback:
                    current_temperature = await self.temperature_callback()
                    print(f"Current temperature {current_temperature}")

                if self.target_temperature_callback:
                    target_temperature = self.target_temperature_callback()
                    print(f"Target temperature {target_temperature}")

                if self.state_callback:
                    current_state = self.state_callback()
                    print(f"Current state {current_state}") # TODO TRANSLATE THIS STATE

                outdoor_temperature = await get_temperature()
                print(f"Outdoor temperature {outdoor_temperature}") # TODO PROPER ERROR HANDLING

                insert_temperature_log(3, current_temperature, outdoor_temperature, True, target_temperature)

            except Exception as e:
                print(f"Error occurred while logging data: {e}")

            await asyncio.sleep(5) 
            # await asyncio.sleep(600)  # 600 seconds = 10 minutes

                
    def set_temperature_callback(self, callback):
        self.temperature_callback = callback
        
    def set_target_temperature_callback(self, callback):
        self.target_temperature_callback = callback
        
    def set_state_callback(self, callback):
        self.state_callback = callback