import requests
import os
from dotenv import load_dotenv

load_dotenv()

def send_balcony_temperature(temp: float):
    url = 'http://api.bramblytech.co.uk/api/temperature/'
    api_key = os.getenv('API_KEY')

    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    data = {
    "location": 1,
    "temperature_celsius": temp
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 201:
        print("Event sent successfully")
    else:
        print(f"Failed to send event: {response.text}")

