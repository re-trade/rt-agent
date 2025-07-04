from mage_ai.io.file import FileIO
from pandas import DataFrame
import fasttext, json, subprocess, fasttext.util

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data_to_file(df: DataFrame, **kwargs) -> None:

    cutoff = kwargs['cutoff']
    vector_size = kwargs['vector_size']
    filepath = kwargs['movie_trainning_data_filepath']

    model = fasttext.train_unsupervised(filepath)
    print(model.get_nearest_neighbors("Good-hearted"))
    # print("Save Model")
    # model.save_model(path="data_demo/trainning_data/movie_10000.bin")
    fasttext.util.reduce_model(model, vector_size)
    words = model.get_words()

    words = words[:cutoff]

    model_data = {
        'words': []
    }

    for word in words:
        vector = model.get_word_vector(word)
        model_data['words'].append({
            'word': word,
            'vector': vector.tolist()  
        }) 

    # Lưu dữ liệu vào file JSON
    with open(kwargs['embedding_json_filepath'], 'w') as f:
        json.dump(model_data, f)

    print("Saved Json File !!!")
