import aiohttp
import asyncio
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("WEATHER_API_KEY")
location = os.getenv("COORDINATES")

async def get_temperature():
    try:
        url = f"https://api.tomorrow.io/v4/timelines?location={location}&fields=temperature&timesteps=current&units=metric&apikey={api_key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                temperature = data['data']['timelines'][0]['intervals'][0]['values']['temperature']
                return temperature
    except aiohttp.ClientError as e:
        print(f"Error fetching temperature data: {e}")
        raise  # Re-raise the exception
    except KeyError as e:
        print(f"Error parsing temperature data: {e}")
        raise  # Re-raise the exception
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise  # Re-raise the exception
    
async def main():
    current_temperature = await get_temperature()
    if current_temperature is not None:
        print(f"The current temperature at {location} is {current_temperature}°C")
    else:
        print("Failed to fetch temperature data.")

if __name__ == "__main__":
    asyncio.run(main())