import os
import streamlit as st
import pandas as pd
import psycopg2
import numpy as np
import matplotlib.pyplot as plt
from jinja2 import Template
from utils.queries import (
    GET_REGIONS_TEMPLATE,
    GET_CITIES_TEMPLATE,
    GET_DISTRICTS_TEMPLATE,
    GET_PRICE_TYPES_TEMPLATE,
    GET_FILTERED_PROPERTIES_TEMPLATE
)
from typing import Optional, Dict


def main() -> None:
    """
    Main function to run the Streamlit dashboard for real estate data visualization.
    """
    # Set Streamlit page layout
    st.set_page_config(
        layout="wide", 
        page_title="Real Estate Dashboard", 
        page_icon="🏠", 
        initial_sidebar_state="expanded"
    )

    # Database connection settings
    DB_NAME: str = os.getenv("DB_NAME", "default")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST: str = os.getenv("DB_HOST", "rdbms-postgres-1")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_SCHEMA: str = os.getenv("DB_SCHEMA", "rsm")
    DB_LANDING_TABLE: str = os.getenv("DB_LANDING_TABLE", "properties_landing")
    DB_CLEAN_TABLE: str = os.getenv("DB_CLEAN_TABLE", "properties_clean")
    DB_LANDING_DIM: str = os.getenv("DB_LANDING_DIM", "locations_landing")
    DB_CLEAN_DIM: str = os.getenv("DB_CLEAN_DIM", "locations_clean")

    @st.cache_data
    def fetch_data(query: str, params: Optional[list] = None) -> pd.DataFrame:
        """
        Fetch data from the database using the provided SQL query and parameters.

        Args:
            query (str): The SQL query to execute.
            params (Optional[list]): Parameters for the SQL query.

        Returns:
            pd.DataFrame: The resulting data as a Pandas DataFrame.
        """
        try:
            conn = psycopg2.connect(
                host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
            )
            df = pd.read_sql_query(query, conn, params=params)
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
        return df

    # Render queries dynamically using Jinja2 templates
    def render_query(template: Template, context: Dict[str, str]) -> str:
        """
        Render a SQL query using a Jinja2 template and context variables.

        Args:
            template (Template): The Jinja2 template for the SQL query.
            context (Dict[str, str]): Context variables for the template.

        Returns:
            str: The rendered SQL query.
        """
        return template.render(context)

    # Sidebar filters
    st.sidebar.header("Filters")

    region_query = render_query(GET_REGIONS_TEMPLATE, {"schema": DB_SCHEMA, "table": DB_CLEAN_DIM})
    region_filter = st.sidebar.selectbox(
        "Region",
        options=fetch_data(region_query)['region'].tolist()
    )

    city_query = render_query(GET_CITIES_TEMPLATE, {"schema": DB_SCHEMA, "table": DB_CLEAN_DIM})
    city_filter = st.sidebar.selectbox(
        "City",
        options=fetch_data(city_query, params=[region_filter])['city'].tolist()
    )

    district_query = render_query(GET_DISTRICTS_TEMPLATE, {"schema": DB_SCHEMA, "table": DB_CLEAN_DIM})
    district_filter = st.sidebar.selectbox(
        "District",
        options=fetch_data(district_query, params=[region_filter, city_filter])['district'].tolist()
    )

    price_type_query = render_query(GET_PRICE_TYPES_TEMPLATE, {"schema": DB_SCHEMA, "table": DB_CLEAN_TABLE})
    price_type_filter = st.sidebar.selectbox(
        "Price Type",
        options=fetch_data(price_type_query)['price_type'].tolist()
    )

    day_filter = st.sidebar.date_input("Day", value=pd.Timestamp.today(), key="single_date")

    # Build dynamic SQL query with filters using Jinja2
    query_context = {
        "schema": DB_SCHEMA,
        "table": DB_CLEAN_TABLE,
        "filters": "region = '%s' AND city = '%s' AND district = '%s' AND price_type = '%s' AND date = '%s'" % (
            region_filter, city_filter, district_filter, price_type_filter, day_filter
        )
    }

    filtered_query = render_query(GET_FILTERED_PROPERTIES_TEMPLATE, query_context)

    # Fetch filtered data
    data = fetch_data(filtered_query)

    # Handle case where no data is returned
    if data.empty:
        st.warning("No data available for the selected date.")
        data_filtered_for_table = pd.DataFrame(columns=[
            "size_range", "region", "city", "district", "price_per_size", "total_size", "covered_size"
        ])
    else:
        data_filtered_for_table = data

    # Calculate KPIs
    avg_price_per_size = f"{data['price_per_size'].mean():.2f}"
    var_price_per_size = f"{data['price_per_size'].var():.2f}"
    max_price_per_size = f"{data['price_per_size'].max():.2f}"
    min_price_per_size = f"{data['price_per_size'].min():.2f}"

    # KPIs
    st.title("Real Estate Marketplace Dashboard")
    st.subheader("Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Average Price/Size", avg_price_per_size)
    with col2:
        st.metric("Variance Price/Size", var_price_per_size)
    with col3:
        st.metric("Max Price/Size", max_price_per_size)
    with col4:
        st.metric("Min Price/Size", min_price_per_size)

    # Graphs
    st.subheader("Visualizations")
    col1, col2 = st.columns(2)

    # Left: Scatterplot of price vs size (m²)
    with col1:
        st.write("Scatterplot: Price vs Size (m²)")

        if data.empty:
            st.warning("No data available to display the scatterplot.")
        else:
            scatter_data = data.dropna(subset=["price", "total_size"])
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(8, 6))
            scatter = ax.scatter(
                scatter_data["total_size"],
                scatter_data["price"],
                c=scatter_data["price"],
                cmap="cividis",
                alpha=0.8,
                edgecolor="white",
                linewidth=0.5
            )
            ax.set_xlabel("Size (m²)")
            ax.set_ylabel("Price (PEN)")
            ax.set_title("Price vs Size (m²)")
            cbar = fig.colorbar(scatter, ax=ax)
            cbar.set_label("Price (PEN)")
            st.pyplot(fig)

    # Right: Histogram of price per squared meter
    with col2:
        st.write("Histogram: Price per Squared Meter (PEN/m²)")

        if data_filtered_for_table.empty or data_filtered_for_table["price_per_size"].dropna().empty:
            st.warning("No data available to display the histogram.")
        else:
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.hist(data_filtered_for_table["price_per_size"], bins=20, color="dodgerblue", edgecolor="black", alpha=0.8)
            ax.set_xlabel("Price per Squared Meter (PEN/m²)")
            ax.set_ylabel("Frequency")
            ax.set_title("Distribution of Price per Squared Meter")
            st.pyplot(fig)


if __name__ == "__main__":
    main()
