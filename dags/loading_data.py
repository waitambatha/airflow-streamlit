from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import psycopg2
import logging
import json
import os

# Database configuration
DB_CONFIG = {
    "host": "airflow_postgres",  # Reference the Docker service name
    "dbname": "airflow",
    "user": "postgres",
    "password": "masterclass",
    "port": 5432  # Default port for PostgreSQL
}

# Directory where the JSON file is located (external folder mapped to container)
DATA_DIR = '/opt/airflow/data'
JSON_FILE_PATH = os.path.join(DATA_DIR, 'raw_manufacturer_data.json')

# Default arguments for the DAG
default_args = {
    "depends_on_past": False,
    'owner': 'airflow',
    'start_date': datetime(2023, 12, 17, 7, 15, 0, 0),
}

# Create the DAG instance
dag = DAG(
    'load_data_to_postgres',
    default_args=default_args,
    description='Load manufacturer data from external JSON into PostgreSQL',
    schedule_interval='@daily',  # Run once daily
)


def load_json_to_postgres():
    """Load JSON data from an external file into the PostgreSQL database."""
    try:
        # Check if the JSON file exists
        if not os.path.exists(JSON_FILE_PATH):
            logging.error(f"JSON file {JSON_FILE_PATH} not found.")
            raise FileNotFoundError(f"JSON file {JSON_FILE_PATH} not found.")

        # Read the JSON file
        with open(JSON_FILE_PATH, 'r') as json_file:
            manufacturers = json.load(json_file)

        logging.info(f"Loaded {len(manufacturers)} manufacturer records from JSON file.")

        # Connect to PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Create the manufacturer table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS manufacturer (
            Mfr_ID SERIAL PRIMARY KEY,
            Mfr_Name VARCHAR(255),
            Mfr_CommonName VARCHAR(255),
            Mfr_ABBR VARCHAR(100),
            Mfr_Type VARCHAR(50),
            Country VARCHAR(100),
            State VARCHAR(100),
            City VARCHAR(100),
            VehicleTypes JSONB,  -- Store JSON data for Vehicle Types
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cur.execute(create_table_query)

        # Insert data into the manufacturer table
        insert_query = """
        INSERT INTO manufacturer (Mfr_ID, Mfr_Name, Mfr_CommonName, Mfr_ABBR, Mfr_Type, Country, State, City, VehicleTypes) 
        VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (Mfr_ID) 
        DO NOTHING;
        """

        for record in manufacturers:
            try:
                cur.execute(insert_query, (
                    record.get('Mfr_Name'),
                    record.get('Mfr_CommonName', 'N/A'),
                    record.get('Mfr_ABBR', 'N/A'),
                    record.get('Mfr_Type', 'N/A'),
                    record.get('Country', 'N/A'),
                    record.get('StateProvince', 'N/A'),
                    record.get('City', 'N/A'),
                    json.dumps(record.get('VehicleTypes', []))  # Ensure proper JSON format
                ))
            except Exception as e:
                logging.error(f"Failed to insert record {record} - Error: {str(e)}")

        conn.commit()
        cur.close()
        conn.close()
        logging.info("Data loaded into PostgreSQL successfully.")

    except Exception as e:
        logging.error(f"Failed to load data into PostgreSQL: {str(e)}")


# DAG Tasks
with dag:
    load_task = PythonOperator(
        task_id='load_json_to_postgres',
        python_callable=load_json_to_postgres
    )
