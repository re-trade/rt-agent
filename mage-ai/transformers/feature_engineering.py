import pandas as pd
import re
if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

def preprocess_columns(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    df[columns] = (
        df[columns]
        .replace('Đang cập nhật', '')
        .fillna('')
        .astype(str)
    )
    return df

def combine_features(df: pd.DataFrame, columns: list, new_column='combined_features') -> pd.DataFrame:
    valid_cols = [col for col in columns if col in df.columns]
    df[new_column] = df[valid_cols].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
    return df

@transformer
def transform(
    products_df: pd.DataFrame,
    orders_df: pd.DataFrame,
    product_categories_df: pd.DataFrame,
    categories_df: pd.DataFrame,
    *args,
    **kwargs
) -> pd.DataFrame:
    # Join product ↔ category name
    category_df = product_categories_df.merge(
        categories_df, left_on='category_id', right_on='id', how='left'
    ).rename(columns={'name': 'category_name'}).drop(columns='id')

    products_full = products_df.merge(
        category_df, left_on='id', right_on='product_id', how='left'
    )

    # Group customer_ids by product_id
    purchase_context = (
        orders_df.groupby('product_id')['customer_id']
        .apply(lambda x: ' '.join(map(str, x.unique())))
        .reset_index()
        .rename(columns={'customer_id': 'purchase_context'})
    )
    # Join product ↔ purchase context
    df = products_full.merge(purchase_context, left_on='id', right_on='product_id', how='left')

    selected_columns = ['name', 'description', 'category_name', 'purchase_context']
    df = preprocess_columns(df, selected_columns)
    df = combine_features(df, selected_columns)
    
    df['combined_features'] = (
        df['combined_features']
        .str.lower()
        .str.replace(r'[.,()\[\]\'\"{}—<>:;?!]', ' ', regex=True)
        .str.replace(r'\s+', ' ', regex=True)
        .str.strip()
    )
    df['tokenized_features'] = df['combined_features'].str.split()

    return df[['id', 'combined_features', 'tokenized_features']]

@test
def test_output(output: pd.DataFrame, *args) -> None:
    assert isinstance(output, pd.DataFrame)
    assert 'combined_features' in output.columns
    assert 'tokenized_features' in output.columns