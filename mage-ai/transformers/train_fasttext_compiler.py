import os
import fasttext
import fasttext.util
import pandas as pd
import numpy as np
from mage_ai.data_preparation.decorators import transformer, test

@transformer
def transform(data: pd.DataFrame, *args, **kwargs):
    vector_size = kwargs.get("vector_size", 100)
    
    tmp_path = "__tmp_fasttext_input.txt"
    data["combined_features"].to_csv(tmp_path, index=False, header=False)
    
    model = fasttext.train_unsupervised(tmp_path)
    fasttext.util.reduce_model(model, vector_size)

    os.remove(tmp_path)
    
    def embed(text: str) -> np.ndarray:
        tokens = text.split()
        if not tokens:
            return np.zeros(vector_size)
        vectors = [model.get_word_vector(t) for t in tokens if t in model.words]
        return np.mean(vectors, axis=0) if vectors else np.zeros(vector_size)
    result = pd.DataFrame()
    result["product_id"] = data["id"].astype(str)
    result["combined_features"] = data["combined_features"]
    result["vector"] = [embed(text) for text in data["combined_features"]]
    return result

@test
def test_output(output: pd.DataFrame, *args) -> None:
    assert output is not None, "Output is None"
    assert "product_id" in output.columns
    assert "vector" in output.columns
    assert isinstance(output.iloc[0]['vector'], (list, np.ndarray)), "vector column không hợp lệ"
