import pandas as pd
from sqlalchemy import create_engine

import logging
from load_helpers.postgres_helper import get_pg_url_from_env

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
@data_loader
def load_product_data(*args, **kwargs):
    """
    Load product data from a PostgreSQL database into a pandas DataFrame for a recommendation system.
    """
    try:
        connection_string = get_pg_url_from_env()
        engine = create_engine(connection_string)
        query = "SELECT * FROM main.products"
        logger.info(f"Executing query: {query}")
        df = pd.read_sql(query, engine)
        logger.info(f"Successfully loaded {df.shape[0]} rows and {df.shape[1]} columns from main.products")
        engine.dispose()
        logger.info("Database connection closed.")
        return df
    except Exception as e:
        logger.error(f"Error loading data from PostgreSQL: {str(e)}")
        raise
    