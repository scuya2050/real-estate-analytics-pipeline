import pendulum

from airflow.sdk import DAG, Param, task
from airflow.models import Variable
from airflow.hooks.base import BaseHook
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

# from airflow.providers.docker.operators.docker import DockerOperator

with DAG(
    dag_id="run_reap_web_scraper",
    max_active_runs=1,
    start_date=pendulum.datetime(2021, 1, 1, tz=pendulum.timezone("America/Lima")),
    schedule="30 2 * * *", 
    catchup=False,
    tags=["reap", "web_scraper"]
) as dag:

    conn_id = Variable.get("reap_web_scraper.rdbms.connection_id")
    conn = BaseHook.get_connection(conn_id)

    schema = Variable.get("reap_web_scraper.rdbms.schema")
    landing_table = Variable.get("reap_web_scraper.rdbms.landing_table")
    clean_table = Variable.get("reap_web_scraper.rdbms.clean_table")

    
    scrape_data = BashOperator(
        task_id="scrape_data",
        bash_command=(
            "docker run --rm " +
            "--name reap-web-scraper " +
            "-v reap-data:/web-scraper/data " +
            "reap-web-scraper-image python ./web_scraper.py  "
        )
    )

    load_to_db = BashOperator(
        task_id="load_to_db",
        bash_command=(
            "docker run --rm " +
            "--name reap-web-db-loader " +
            "-v reap-data:/web-scraper/data " +
            "--network reap-network " +
            "reap-web-scraper-image python ./db_loader.py " +
            f"--dbname {conn.schema} " +
            f"--user {conn.login} " +
            f"--password {conn.password} " +
            f"--host {conn.host} " +
            f"--port {conn.port} " +
            f"--schema {schema} " +
            f"--table {landing_table}"
        )
    )

    refresh_clean_table = SQLExecuteQueryOperator(
        task_id="refresh_clean_table",
        conn_id=conn_id,
        sql=f"REFRESH MATERIALIZED VIEW {schema}.{clean_table};",
    )

    scrape_data >> load_to_db >> refresh_clean_table
