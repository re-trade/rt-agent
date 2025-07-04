import pandas as pd
from sqlalchemy import create_engine
from mage_ai.data_preparation.decorators import data_loader
import logging
from load_helpers.postgres_helper import get_pg_url_from_env

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


@data_loader
def load_order_data(*args, **kwargs):
    """
    Load product data from a PostgreSQL database into a pandas DataFrame for a recommendation system.
    """
    try:
        connection_string = get_pg_url_from_env()
        engine = create_engine(connection_string)
        query = """
        SELECT o.customer_id, oi.product_id, oi.quantity, o.created_at
        FROM main.orders o
        JOIN main.order_items oi ON o.id = oi.order_id
        """
        return pd.read_sql(query, engine)
    except Exception as e:
        logger.error(f"Error connecting to PostgreSQL: {str(e)}")
        raise
    
@data_loader
def load_product_categories_data(*args, **kwargs):
    try:
        engine = create_engine(get_pg_url_from_env())
        return pd.read_sql("SELECT * FROM main.product_categories", engine)
    except Exception as e:
        logger.error(f"Error connecting to PostgreSQL: {str(e)}")
        raise
    
@data_loader
def load_categories_data(*args, **kwargs):
    try:
        engine = create_engine(get_pg_url_from_env())
        return pd.read_sql("SELECT id, name FROM main.categories", engine)
    except Exception as e:
        logger.error(f"Error connecting to PostgreSQL: {str(e)}")
        raise
    