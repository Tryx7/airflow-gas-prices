from airflow import DAG
from airflow.operators.dummy import DummyOperator
from datetime import datetime

with DAG(
    'test_dag',
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    
    task1 = DummyOperator(task_id='task1')
    task2 = DummyOperator(task_id='task2')
    
    task1 >> task2
