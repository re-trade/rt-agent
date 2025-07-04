import pandas as pd
from sqlalchemy import create_engine
import logging
from load_helpers.postgres_helper import get_pg_url_from_env
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
@data_loader
def load_order_data(*args, **kwargs):
    """
    Load product data from a PostgreSQL database into a pandas DataFrame for a recommendation system.
    """
    try:
        connection_string = get_pg_url_from_env()
        engine = create_engine(connection_string)
        query = """
        SELECT o.customer_id, oi.product_id, oi.quantity, o.created_date
        FROM main.orders o
        JOIN main.order_items oi ON o.id = oi.order_id
        """
        return pd.read_sql(query, engine)
    except Exception as e:
        logger.error(f"Error connecting to PostgreSQL: {str(e)}")
        raise