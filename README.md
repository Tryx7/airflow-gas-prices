# Gas Prices ETL Pipeline with Apache Airflow

A robust data pipeline for collecting, processing, and storing US gas prices data using Apache Airflow and PostgreSQL.

## 🌟 Overview

This project provides an automated ETL (Extract, Transform, Load) pipeline that fetches gas prices data from the CollectAPI, processes it, and stores it in a PostgreSQL database for analysis and reporting.

## 🏗️ Architecture

```
CollectAPI → Airflow DAG → Data Processing → PostgreSQL Database
     ↓            ↓              ↓               ↓
 Gas Prices   Orchestration  Transformation   Storage & Analytics
```

## 📁 Project Structure

```
├── dags/
│   └── gas_prices_dag.py          # Main Airflow DAG
├── scripts/
│   └── init_db.py                 # Database initialization
├── docker-compose.yml             # Airflow services
├── setup.sh                       # Environment setup script
├── requirements.txt               # Python dependencies
└── README.md                     # This file
```

## 🚀 Quick Start

### 1. Prerequisites

- Docker & Docker Compose
- Python 3.8+
- CollectAPI Gas Prices API key

### 2. Environment Setup

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup script
./setup.sh
```

### 3. Configure Environment Variables

Update the `docker-compose.yml` with your credentials:

```yaml
environment:
  - POSTGRES_USER=your_postgres_user
  - POSTGRES_PASSWORD=your_postgres_password
  - POSTGRES_DB=your_database
  - POSTGRES_HOST=your_postgres_host
  - POSTGRES_PORT=your_postgres_port
  - POSTGRES_SSL_MODE=require
  - GAS_API_KEY=your_collectapi_key_here
```

### 4. Start Services

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### 5. Access Airflow UI

- **URL**: http://localhost:8080
- **Username**: admin
- **Password**: admin

### 6. Initialize Database (Optional)

```bash
# Run database initialization
python init_db.py
```

## 🔧 Core Components

### 1. Airflow DAG (`gas_prices_dag.py`)

**Pipeline Workflow:**
1. **Fetch**: Retrieve gas prices data from CollectAPI
2. **Transform**: Process and clean the data
3. **Store**: Load data into PostgreSQL database

**DAG Schedule**: Runs daily

**Features:**
- Error handling and retry logic
- XCom for data passing between tasks
- Comprehensive logging
- SSL-enabled PostgreSQL connections

### 2. Data Schema

**PostgreSQL Table Structure:**
```sql
CREATE TABLE gas_prices (
    state VARCHAR(10),
    city VARCHAR(100),
    gasoline DECIMAL(10,2),
    midGrade DECIMAL(10,2),
    premium DECIMAL(10,2),
    diesel DECIMAL(10,2),
    last_updated TEXT,
    fetch_timestamp TIMESTAMP,
    data_loaded_at TIMESTAMP,
    data_batch_id DATE
);
```

### 3. API Integration

**CollectAPI Endpoint:**
- URL: `https://api.collectapi.com/gasPrice/stateUsaPrice`
- Authentication: API Key in headers
- Data Format: JSON response with state-wise gas prices

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `POSTGRES_USER` | PostgreSQL username | `avnadmin` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `your_password` |
| `POSTGRES_DB` | Database name | `defaultdb` |
| `POSTGRES_HOST` | Database host | `your-host.aivencloud.com` |
| `POSTGRES_PORT` | Database port | `24862` |
| `POSTGRES_SSL_MODE` | SSL connection mode | `require` |
| `GAS_API_KEY` | CollectAPI key | `your-api-key` |

### Airflow Configuration

- **Executor**: LocalExecutor
- **Database**: SQLite (development)
- **Webserver Port**: 8080
- **DAG Folder**: `/opt/airflow/dags`

## 📊 Data Pipeline Details

### Extraction Phase
- Fetches gas prices for all US states
- Handles API rate limits and errors
- Validates response data

### Transformation Phase
- Converts JSON response to structured DataFrame
- Adds metadata (timestamps, batch IDs)
- Data type validation and cleaning

### Loading Phase
- Batch insertion into PostgreSQL
- Append-only strategy with timestamps
- Connection management with SSL

## 🛠️ Development

### Adding New Data Sources

1. **Create new DAG task:**
```python
def fetch_additional_data():
    # Your data fetching logic
    pass

def process_additional_data(**context):
    # Your processing logic
    pass
```

2. **Update pipeline:**
```python
additional_fetch_task = PythonOperator(
    task_id='fetch_additional_data',
    python_callable=fetch_additional_data,
)

additional_process_task = PythonOperator(
    task_id='process_additional_data',
    python_callable=process_additional_data,
)
```

### Customizing Data Processing

Modify the `transform_gas_prices` function in `gas_prices_dag.py`:

```python
def transform_gas_prices(**context):
    # Add custom transformations
    df['price_per_liter'] = df['gasoline'] / 3.78541  # Convert to liters
    df['price_category'] = df['gasoline'].apply(categorize_price)
    return df
```

### Extending Storage

Add new columns to the database schema:

```sql
ALTER TABLE gas_prices 
ADD COLUMN price_trend VARCHAR(20),
ADD COLUMN regional_avg DECIMAL(10,2);
```

## 📈 Monitoring & Operations

### Airflow Dashboard

- **DAG Runs**: Monitor pipeline execution
- **Task Logs**: Debug and troubleshoot issues
- **SLA Monitoring**: Track pipeline performance
- **Variable Management**: Configure pipeline parameters

### Database Monitoring

```sql
-- Check data freshness
SELECT MAX(fetch_timestamp) as latest_data,
       COUNT(*) as total_records
FROM gas_prices;

-- Monitor data quality
SELECT state, 
       COUNT(*) as records,
       AVG(gasoline) as avg_gasoline_price
FROM gas_prices
GROUP BY state;
```

## 🐛 Troubleshooting

### Common Issues

**API Connection Problems:**
```python
# Test API connectivity
import requests
response = requests.get(
    "https://api.collectapi.com/gasPrice/stateUsaPrice",
    headers={'authorization': 'apikey YOUR_KEY'}
)
print(response.status_code)
```

**Database Connection Issues:**
```python
# Test database connection
from sqlalchemy import create_engine
engine = create_engine('your_connection_string')
with engine.connect() as conn:
    print("Connection successful")
```

**Airflow DAG Not Appearing:**
- Check DAG file is in correct directory
- Verify no syntax errors in Python code
- Restart Airflow webserver and scheduler

### Logs and Debugging

```bash
# View Airflow logs
docker-compose logs airflow-webserver
docker-compose logs airflow-scheduler

# Check DAG status
docker-compose exec airflow-webserver airflow dags list

# Manual DAG trigger
docker-compose exec airflow-webserver airflow dags trigger gas_prices_dag
```

### Reset Environment

```bash
# Stop and clean
docker-compose down -v

# Reinitialize
./setup.sh
```

## 🔄 Pipeline Execution Flow

1. **Scheduled Trigger**: DAG runs daily at scheduled time
2. **Data Extraction**: Fetch gas prices from CollectAPI
3. **Data Validation**: Verify API response and data structure
4. **Data Transformation**: Clean and enrich the dataset
5. **Database Storage**: Insert records into PostgreSQL
6. **Completion**: Update execution metadata and logs

## 📝 API Documentation

### CollectAPI Gas Prices Endpoint

**Base URL**: `https://api.collectapi.com/gasPrice/stateUsaPrice`

**Headers:**
```http
authorization: apikey YOUR_API_KEY
content-type: application/json
```

**Response Format:**
```json
{
  "success": true,
  "result": [
    {
      "state": "CA",
      "city": "Los Angeles",
      "gasoline": 4.56,
      "midGrade": 4.78,
      "premium": 4.95,
      "diesel": 5.12,
      "last_updated": "2024-01-15"
    }
  ]
}
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create Pull Request

## 📄 License

This project is designed for educational and analytical purposes. Please ensure compliance with CollectAPI terms of service and usage limits.

---

**Note**: Replace all placeholder credentials with your actual API keys and database credentials. Ensure you have proper CollectAPI subscription and PostgreSQL database access.
