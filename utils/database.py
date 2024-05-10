import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def insert_temperature_log(zone, indoor_temp, outdoor_temp, heating_status, target_temp):
    """
    Inserts a temperature log entry into the database.

    Parameters:
    zone (int): The zone number.
    indoor_temp (float): The indoor temperature.
    outdoor_temp (float): The outdoor temperature.
    heating_status (bool): The heating status (True for on, False for off).
    target_temp (float): The target temperature.
    """
    
    # Database connection parameters
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST")
    )
    cur = conn.cursor()

    # Insert data
    query = """
    INSERT INTO temperature_logs (zone, indoor_temp, outdoor_temp, heating_status, target_temp)
    VALUES (%s, %s, %s, %s, %s)
    """
    data = (zone, indoor_temp, outdoor_temp, heating_status, target_temp)

    cur.execute(query, data)
    conn.commit()
    cur.close()
    conn.close()