import os
import subprocess

def main():
    os.environ["DB_NAME"] = os.getenv("DB_NAME", "default")
    os.environ["DB_USER"] = os.getenv("DB_USER", "postgres")
    os.environ["DB_PASSWORD"] = os.getenv("DB_PASSWORD", "postgres")
    os.environ["DB_HOST"] = os.getenv("DB_HOST", "rdbms-pg-1")
    os.environ["DB_PORT"] = os.getenv("DB_PORT", "5432")
    os.environ["DB_SCHEMA"] = os.getenv("DB_SCHEMA", "reap")
    os.environ["DB_LANDING_TABLE"] = os.getenv("DB_LANDING_TABLE", "properties_landing")
    os.environ["DB_CLEAN_TABLE"] = os.getenv("DB_CLEAN_TABLE", "properties_clean")
    os.environ["DB_LANDING_DIM"] = os.getenv("DB_LANDING_DIM", "locations_landing")
    os.environ["DB_CLEAN_DIM"] = os.getenv("DB_CLEAN_DIM", "locations_clean")

    subprocess.run(["streamlit", "run", "app.py"])


if __name__ == "__main__":
    main()