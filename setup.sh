# setup.sh
#!/bin/bash

echo "🚀 Setting up Airflow with SQLite..."

# Stop any running containers
docker-compose down

# Create necessary directories
mkdir -p dags logs plugins data

# Remove old docker-compose.yml and create new one
rm -f docker-compose.yml
cat > docker-compose.yml << 'EOF'
# docker-compose.yml
services:
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

  airflow-webserver:
    image: apache/airflow:2.7.0
    environment:
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__CORE__SQL_ALCHEMY_CONN=sqlite:////opt/airflow/airflow.db
      - AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=true
      - AIRFLOW__CORE__LOAD_EXAMPLES=false
      - AIRFLOW__API__AUTH_BACKENDS=airflow.api.auth.backend.basic_auth
      - POSTGRES_USER=avnadmin
      - POSTGRES_PASSWORD=AVNS_G1ajzCj_WUpXrLzc-3t
      - POSTGRES_DB=defaultdb
      - POSTGRES_HOST=pg-c63647-lagatkjosiah-692c.c.aivencloud.com
      - POSTGRES_PORT=24862
      - POSTGRES_SSL_MODE=require
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
      - ./data:/opt/airflow/data
    ports:
      - "8080:8080"
    command: >
      bash -c "
        if [ ! -f /opt/airflow/airflow.db ]; then
          airflow db init &&
          airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
        fi &&
        airflow webserver
      "
    depends_on:
      - redis
    restart: unless-stopped

  airflow-scheduler:
    image: apache/airflow:2.7.0
    environment:
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__CORE__SQL_ALCHEMY_CONN=sqlite:////opt/airflow/airflow.db
      - AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=true
      - AIRFLOW__CORE__LOAD_EXAMPLES=false
      - POSTGRES_USER=avnadmin
      - POSTGRES_PASSWORD=AVNS_G1ajzCj_WUpXrLzc-3t
      - POSTGRES_DB=defaultdb
      - POSTGRES_HOST=pg-c63647-lagatkjosiah-692c.c.aivencloud.com
      - POSTGRES_PORT=24862
      - POSTGRES_SSL_MODE=require
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
      - ./data:/opt/airflow/data
    command: >
      bash -c "
        sleep 10 &&
        airflow scheduler
      "
    depends_on:
      - redis
    restart: unless-stopped
EOF

# Start services
echo "Starting Airflow services..."
docker-compose up -d

echo "✅ Airflow is starting up..."
echo "🌐 Web UI: http://localhost:8080"
echo "👤 Username: admin"
echo "🔑 Password: admin"
echo ""
echo "Note: Aiven PostgreSQL connection may fail due to WSL2 DNS issues."
echo "The DAG will still run and save data locally for testing."