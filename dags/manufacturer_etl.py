from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import requests
import logging
import json
import os

# Configuration
API_URL = "https://vpic.nhtsa.dot.gov/api/vehicles/getallmanufacturers?format=json"

# Directory to store the fetched data as JSON (external directory)
DATA_DIR = '/opt/airflow/data'  # Path mapped to the host machine's ./data folder
os.makedirs(DATA_DIR, exist_ok=True)

# File path for storing fetched data
JSON_FILE_PATH = os.path.join(DATA_DIR, 'raw_manufacturer_data.json')

# Default arguments for the DAG
default_args = {
    "depends_on_past": False,
    'owner': 'airflow',
    'start_date': datetime(2023, 12, 17, 7, 15, 0, 0),
}

# Create the DAG instance
dag = DAG(
    'manufacturer_etl',
    default_args=default_args,
    description='Fetch and Save vehicle manufacturer details into a JSON file',
    schedule_interval='@daily',  # Run once daily
)

# Functions
def fetch_manufacturer_data(**kwargs):
    """Extract: Get manufacturer details from the API and save as a JSON file."""
    logging.info("Fetching manufacturer details from the API.")
    response = requests.get(API_URL)

    if response.status_code == 200:
        data = response.json()
        manufacturers = data.get('Results', [])
        logging.info(f"Successfully fetched {len(manufacturers)} manufacturer records.")

        # Save to JSON file (external to Docker container)
        with open(JSON_FILE_PATH, 'w') as json_file:
            json.dump(manufacturers, json_file)
        logging.info(f"Data saved to {JSON_FILE_PATH}")
    else:
        logging.error(f"Failed to fetch manufacturer details: {response.status_code} - {response.text}")
        raise Exception("API request failed.")

# DAG Tasks
with dag:
    fetch_task = PythonOperator(
        task_id='fetch_manufacturer_data',
        python_callable=fetch_manufacturer_data,
        provide_context=True  # Allows passing XCom (though it's not used now)
    )

    fetch_task
