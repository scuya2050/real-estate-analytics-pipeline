# Real Estate Analytics Pipeline

## Overview
The Real Estate Analytics Pipeline project is a comprehensive solution for scraping, processing, and visualizing real estate data from a web marketplace. It consists of multiple components, including a web scraper, a database, and a Streamlit dashboard for data visualization.

## Project Structure

```
real-estate-analytics-pipeline/
├── airflow/                # Airflow setup for orchestrating workflows
├── dashboard/              # Streamlit dashboard for data visualization
├── rdbms/                  # Database setup and initialization scripts
├── web-scraper/            # Web scraper for collecting real estate data
```

### Key Components

#### 1. Web Scraper
- **Description**: Scrapes real estate data from the web, processes it, and loads it into a database.
- **Key Files**:
  - `web_scraper.py`: Main script to run the web scraper.
  - `db_loader.py`: Loads processed data into the database.

#### 2. Database (RDBMS)
- **Description**: PostgreSQL database for storing raw and processed real estate data.
- **Key Files**:
  - `01_create_schema.sql`: Creates the database schema.
  - `02_create_landing_table.sql`: Creates the landing table for raw data.
  - `03_create_clean_table.sql`: Creates the clean table for processed data.
  - init.sh

#### 3. Dashboard
- **Description**: Streamlit-based dashboard for visualizing real estate data.
- **Key Features**:
  - Fetches data dynamically from the database.
  - Visualizes data using interactive charts and tables.
- **Key Files**:
  - `app.py`: Main script that contains the dashboard.
  - `run_streamlit.py` : Runs the app with environment variables

#### 4. Airflow
- **Description**: Manages workflows for data scraping, processing, and loading.
- **Key Files**:
  - `docker-compose`: Custom docker-compose file based on the official airflow setup
  - `dags/run_reap_web_scraper.py`: DAG for running the web scraper.

## Installation

### Prerequisites
- Docker (to run all components in containers)
- Git
- User permissions for docker and other operations

### Steps

The following steps depict the setup for the installation with default setting. Most settings (user, password, host, port, etc.) can be passed as arguments in the scripts.
1. Create shared network
   ```bash
   docker network create reap-network
   ```
2. Clone the repository, move the `airflow` and `rdbms` folders outside:
   ```bash
   git clone https://github.com/scuya2050/real-estate-analytics-pipeline
   cd real-estate-analytics-pipeline
   mv airflow ../airflow
   mv rdbms ../rdbms
   ```
3. Set up airflow (containerized) using the [guide for running airflow in docker](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html), but using the custom image. Additionally, an extra command needs to be ran to include the airflow user to the docker user group so it can execture docker commands:
   ```bash
   cd ../airflow
   echo -e "AIRFLOW_UID=$(id -u)" > .env
   echo "DOCKER_GID=$(stat -c '%g' /var/run/docker.sock)" >> .env
   docker compose up airflow-init
   docker compose up -d
   ```
4. Run scripts to create variables and connections:
   ```bash
   chmod +x create_connection.sh
   ./create_connection.sh
   chmod +x create_variables.sh
   ./create_variables.sh
   ```
5. Set up the database (containerized):
   ```bash
   cd ../rdbms
   docker compose up -d
6. Run script to run sql scripts to create schema and tables, and return:
   ```bash
   chmod +x init.sh
   ./init.sh
   ```
7. Build the Docker image for the web scraper:
   ```bash
   cd ../real-estate-analytics-pipeline
   cd web-scraper
   docker build -t reap-web-scraper-image .
   ```
8. Build the Docker image for the web dashboard and run it:
   ```bash
   cd ../dashboard
   docker compose up --build -d
   ```

## Usage
### Pipeline orchestration
Access the airflow GUI at `http://<your-ip>:8080` with username and password `airflow`. (Make sure to open the port)

The airfllow DAG in `airflow/dags/run_reap_web_scraper.py` already:
1. Runs the web scraper
2. Loads the scraped data into the postgres database
3. Refreshes the materialized view with clean data.

Currently, the run is scheduled to run at 02:30 GMT-5

### Dashboard
Access the dashboard at `http://<your-ip>:8501` to visualize data. (Make sure to open the port)