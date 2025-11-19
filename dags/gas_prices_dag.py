# dags/gas_prices_dag.py
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
import pandas as pd
import requests
import json
from sqlalchemy import create_engine
import os
import sys

def fetch_gas_prices():
    """
    Fetch gas prices from the API with error handling
    """
    url = "https://api.collectapi.com/gasPrice/stateUsaPrice"
    
    # Get API key from environment variable
    api_key = os.getenv("GAS_API_KEY", "1Xi3viyXBFXalmmYGM2zih:3mbjknDn924ITcjUAmcfkM")
    
    headers = {
        'authorization': f"apikey {api_key}",  # CollectAPI typically uses 'apikey' prefix
        'content-type': "application/json"
    }
    
    try:
        print("Fetching gas prices from API...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        data = response.json()
        print("Successfully fetched gas prices")
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching gas prices: {e}")
        raise

def transform_gas_prices(**context):
    """
    Transform the gas prices data
    """
    try:
        # Get data from previous task using XCom
        ti = context['ti']
        raw_data = ti.xcom_pull(task_ids='fetch_gas_prices')
        
        if not raw_data:
            raise ValueError("No data received from fetch task")
        
        # Extract the results from the API response
        if 'result' in raw_data and raw_data['result']:
            gas_data = raw_data['result']
        else:
            gas_data = raw_data
        
        # Convert to DataFrame
        df = pd.DataFrame(gas_data)
        
        # Add timestamp and metadata
        df['data_loaded_at'] = datetime.now()
        df['data_batch_id'] = context['ds']
        
        print(f"Transformed {len(df)} records")
        print(f"Columns: {df.columns.tolist()}")
        
        return df
        
    except Exception as e:
        print(f"Error transforming data: {e}")
        raise

def store_gas_prices(**context):
    """
    Store gas prices in PostgreSQL
    """
    try:
        # Get transformed data from previous task
        ti = context['ti']
        df = ti.xcom_pull(task_ids='process_gas_prices')
        
        if df is None or df.empty:
            print("No data to store")
            return
        
        # PostgreSQL connection details from environment variables
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        host = os.getenv("POSTGRES_HOST")
        port = os.getenv("POSTGRES_PORT")
        dbname = os.getenv("POSTGRES_DB")
        ssl_mode = os.getenv("POSTGRES_SSL_MODE", "require")
        
        print(f"Connecting to PostgreSQL: {host}:{port}")
        
        # Create SQLAlchemy engine with SSL
        engine = create_engine(
            f'postgresql://{user}:{password}@{host}:{port}/{dbname}',
            connect_args={'sslmode': ssl_mode},
            echo=False  # Set to True for debugging SQL queries
        )
        
        # Test connection
        with engine.connect() as conn:
            print("Successfully connected to PostgreSQL")
        
        # Write the dataframe to PostgreSQL
        df.to_sql(
            'gas_prices', 
            engine, 
            if_exists='append', 
            index=False, 
            method='multi',
            chunksize=1000
        )
        
        print(f"Successfully stored {len(df)} gas prices records in PostgreSQL")
        
        # Close engine
        engine.dispose()
        
    except Exception as e:
        print(f"Error storing data in PostgreSQL: {e}")
        raise

# Default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    'gas_prices_dag',
    default_args=default_args,
    description='A DAG to fetch, transform and store gas prices from CollectAPI',
    start_date=datetime(2024, 7, 7),
    schedule_interval='@daily',
    catchup=False,
    tags=['gas_prices', 'wsl2'],
    max_active_runs=1,
) as dag:
    
    start_task = DummyOperator(task_id='start')
    
    fetch_task = PythonOperator(
        task_id='fetch_gas_prices',
        python_callable=fetch_gas_prices,
    )
    
    transform_task = PythonOperator(
        task_id='process_gas_prices',
        python_callable=transform_gas_prices,
        provide_context=True,
    )
    
    store_task = PythonOperator(
        task_id='store_gas_prices',
        python_callable=store_gas_prices,
        provide_context=True,
    )
    
    end_task = DummyOperator(task_id='end')
    
    start_task >> fetch_task >> transform_task >> store_task >> end_task