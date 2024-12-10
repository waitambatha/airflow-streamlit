# Manufacturer ETL Project

This project is designed to extract, transform, and load (ETL) vehicle manufacturer data from an external API into a PostgreSQL database using Apache Airflow. Additionally, it visualizes the data using **Streamlit** for interactive data exploration.

## Project Structure

The project is structured as follows:

```
manufacturer_etl_local/
├── dags/                      # Airflow DAGs
│   └── manufacturer_etl.py    # The ETL DAG for fetching and loading manufacturer data
│   └── loading_data.py        # A separate DAG to load the fetched data into PostgreSQL
├── sql/                       # SQL files for table creation and other queries
│   └── create_table.sql       # SQL script for creating the PostgreSQL manufacturer table
├── logs/                      # Logs generated by Airflow
├── env/                       # Virtual environment for Python
├── .env                       # Environment file for storing secrets like DB credentials
├── raw_manufacturer_data.json # Data fetched from API, stored outside Docker container
├── streamlit_app/             # Streamlit app directory
│   └── app.py                 # Main app to visualize data
├── docker-compose.yml         # Docker Compose configuration for services
├── Dockerfile                 # Docker configuration for custom containers
└── requirements.txt           # List of Python dependencies
```

## Setup Instructions

### 1. **Clone the repository**
Clone this repository to your local machine.

```bash
git clone <repository_url>
cd manufacturer_etl_local
```

### 2. **Install Dependencies**
Create and activate a virtual environment.

```bash
# Create a virtual environment (if not created already)
python -m venv env

# Activate the virtual environment
source env/bin/activate  # For Linux/Mac
env\Scripts\activate     # For Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. **Running Docker Containers**

The project is designed to run in Docker. The `docker-compose.yml` file includes configurations for Airflow (Webserver, Scheduler), PostgreSQL, and Streamlit.

```bash
# Build and start all containers
docker-compose up --build -d

# To check the status of running containers
docker-compose ps
```

The following services are set up:

- **PostgreSQL**: Stores the vehicle manufacturer data.
- **Airflow Webserver**: UI for managing DAGs.
- **Airflow Scheduler**: Executes the tasks defined in the DAGs.
- **Streamlit**: Visualizes the data stored in PostgreSQL.

### 4. **Airflow Configuration**
- After starting the containers, navigate to [http://localhost:8088](http://localhost:8088) to access the Airflow UI.
- Log in with the default admin credentials:
    - **Username**: `admin`
    - **Password**: `admin`

To create the admin user if it’s not created already, run the following inside the Airflow webserver container:

```bash
docker exec -it airflow_webserver bash
airflow users create \
    --username admin \
    --firstname admin \
    --lastname admin \
    --role Admin \
    --password admin \
    --email admin@example.com
```

### 5. **Streamlit Application**
Streamlit visualizations are located in the `streamlit_app/app.py` file. To run the app:

```bash
# From the project root directory
streamlit run streamlit_app/app.py
```

This will launch the Streamlit app on [http://localhost:8501](http://localhost:8501).

### 6. **DAGs**
There are two main Airflow DAGs:

- **`manufacturer_etl.py`**: This DAG fetches the manufacturer data from the API and saves it in a JSON file (`raw_manufacturer_data.json`).
- **`loading_data.py`**: This DAG loads the data from the JSON file into PostgreSQL.

### 7. **PostgreSQL Table Creation**
The table used to store the manufacturer data is defined in the `sql/create_table.sql` file. It includes the following fields:

```sql
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
```

This table will store information like manufacturer name, abbreviation, country, state, city, and vehicle types.

### 8. **Fetching Manufacturer Data**
The manufacturer data is fetched from this API:

```
https://vpic.nhtsa.dot.gov/api/vehicles/getallmanufacturers?format=json
```

The fetched data is stored in the `raw_manufacturer_data.json` file, which is located outside the Docker container (on the host machine).

### 9. **Streamlit Visualizations**
Streamlit provides multiple interactive visualizations, including:
- **Bar Charts**: Show the count of manufacturers per country.
- **Pie Charts**: Display the percentage of vehicle types.
- **Line Charts**: Track manufacturer data over time.
- **Tables**: List all the manufacturer data.
- **Filters**: Allow users to filter and explore data by various columns.

### 10. **Troubleshooting**
- **DNS Issues in Docker**: Ensure that the PostgreSQL container's hostname matches in the `DB_CONFIG` dictionary.
- **Data Not Fetched**: Check the Airflow logs (`logs/`) for any issues related to the API request.
- **Streamlit Not Running**: Ensure Streamlit is installed correctly and Docker is running.

---

### Conclusion

This project fetches and stores vehicle manufacturer data in PostgreSQL, which is then visualized using Streamlit. Docker is used to containerize the application, ensuring all services (Airflow, PostgreSQL, Streamlit) run seamlessly.



