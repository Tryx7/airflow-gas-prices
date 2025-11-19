# init_db.py (optional - if you need to create the table first)
import os
import pandas as pd
from sqlalchemy import create_engine, text

# Aiven PostgreSQL connection details
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
dbname = os.getenv("POSTGRES_DB")
ssl_mode = os.getenv("POSTGRES_SSL_MODE", "require")

# Create SQLAlchemy engine with SSL
connection_string = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}?sslmode={ssl_mode}'
engine = create_engine(connection_string)

# Create gas_prices table
create_table_sql = """
CREATE TABLE IF NOT EXISTS gas_prices (
    state VARCHAR(10),
    city VARCHAR(100),
    gasoline DECIMAL(10,2),
    midGrade DECIMAL(10,2),
    premium DECIMAL(10,2),
    diesel DECIMAL(10,2),
    last_updated TEXT,
    fetch_timestamp TIMESTAMP
);
"""

try:
    with engine.connect() as conn:
        conn.execute(text(create_table_sql))
        conn.commit()
    print("✅ gas_prices table created successfully")
except Exception as e:
    print(f"❌ Error creating table: {e}")