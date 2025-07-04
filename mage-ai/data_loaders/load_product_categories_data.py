import pandas as pd
from sqlalchemy import create_engine
import logging
from load_helpers.postgres_helper import get_pg_url_from_env

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
@data_loader
def load_product_categories_data(*args, **kwargs):
    try:
        engine = create_engine(get_pg_url_from_env())
        return pd.read_sql("SELECT * FROM main.product_categories", engine)
    except Exception as e:
        logger.error(f"Error connecting to PostgreSQL: {str(e)}")
        raise