import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

# Database configuration
DB_CONFIG = {
    "host": "localhost",  # Localhost since Streamlit runs locally
    "dbname": "airflow",
    "user": "postgres",
    "password": "masterclass",
    "port": 5433  # Port for PostgreSQL container
}

# Connect to the database
def connect_to_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        st.success("✅ Connected to PostgreSQL database!")
        return conn
    except Exception as e:
        st.error(f"❌ Failed to connect to PostgreSQL: {str(e)}")
        return None

# List all tables in the database
def list_all_tables(conn):
    try:
        query = "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public';"
        tables_df = pd.read_sql_query(query, conn)
        return tables_df['tablename'].tolist()
    except Exception as e:
        st.error(f"❌ Failed to list tables: {str(e)}")
        return []

# Load data from the manufacturer table
def load_manufacturer_data(conn):
    try:
        query = "SELECT * FROM manufacturer;"
        df = pd.read_sql_query(query, conn)
        df.columns = df.columns.str.strip().str.lower()  # Normalize column names
        return df
    except Exception as e:
        st.error(f"❌ Failed to load data from PostgreSQL: {str(e)}")
        return pd.DataFrame()

# Streamlit app layout
st.title("📊 Manufacturer Data Visualization")

# Connect to the PostgreSQL database
conn = connect_to_db()

# List all database tables
if conn:
    st.sidebar.header("📋 Database Tables")
    all_tables = list_all_tables(conn)
    st.sidebar.write("**Available Tables:**")
    for table in all_tables:
        st.sidebar.write(f"- {table}")

# Load and display manufacturer data
if conn:
    st.header("🔍 Manufacturer Data")
    df = load_manufacturer_data(conn)
    if not df.empty:
        st.dataframe(df)
    else:
        st.warning("No data found in the manufacturer table.")
else:
    st.error("Database connection failed. Check your credentials or connection.")

# Ensure there is data before creating visualizations
if not df.empty:
    st.header("📈 Data Visualizations")

    # Visualization 1: Bar Chart - Count of Manufacturers by Country
    st.subheader("📊 Bar Chart - Manufacturers by Country")
    country_counts = df['country'].value_counts().reset_index()
    country_counts.columns = ['country', 'count']
    fig1 = px.bar(country_counts, x='country', y='count', title='Manufacturers by Country')
    st.plotly_chart(fig1)

    # Visualization 2: Pie Chart - Manufacturer Counts by Vehicle Types
    st.subheader("🥧 Pie Chart - Vehicle Types")
    vehicle_type_counts = df['vehicletypes'].value_counts().reset_index()
    vehicle_type_counts.columns = ['vehicletypes', 'count']
    fig2 = px.pie(vehicle_type_counts, names='vehicletypes', values='count', title='Distribution of Vehicle Types')
    st.plotly_chart(fig2)

    # Visualization 3: Line Chart - Number of Manufacturers Created Over Time
    st.subheader("📈 Line Chart - Manufacturer Count Over Time")
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'])
        date_counts = df.groupby(df['created_at'].dt.date).size().reset_index(name='count')
        fig3 = px.line(date_counts, x='created_at', y='count', title='Manufacturers Created Over Time')
        st.plotly_chart(fig3)
    else:
        st.warning("No 'created_at' column found in the data to create a line chart.")

    # Visualization 4: Histogram - Distribution of Manufacturers by Country
    st.subheader("📊 Histogram - Manufacturer Distribution by Country")
    fig4 = px.histogram(df, x='country', nbins=30, title='Manufacturer Distribution by Country')
    st.plotly_chart(fig4)

    # Visualization 5: Scatter Plot - Manufacturer Names vs Vehicle Types
    st.subheader("📈 Scatter Plot - Manufacturer Name vs Vehicle Types")
    if 'mfr_name' in df.columns and 'vehicletypes' in df.columns:
        fig5 = px.scatter(df, x='mfr_name', y='vehicletypes', title='Manufacturer Name vs Vehicle Types')
        st.plotly_chart(fig5)
    else:
        st.warning("Columns 'mfr_name' and 'vehicletypes' are required for this scatter plot.")

# Close the database connection
if conn:
    conn.close()
