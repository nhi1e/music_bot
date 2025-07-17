import pandas as pd
import numpy as np
from gensim.models import Word2Vec
import re

def word_tokenize(text):
    """Simple tokenization function"""
    # Handle NaN values
    if pd.isna(text):
        return []
    cleaned_text = re.sub(r'[^\w\s]', ' ', str(text).lower())
    return [word for word in cleaned_text.split() if word.strip()]

def show_embeddings(embeddings):
    """Display embedding information"""
    embeddings_array = np.array(embeddings)
    print(f"Embeddings shape: {embeddings_array.shape}")
    if len(embeddings) > 0:
        print(f"Sample embedding: {embeddings[0][:5]}...")

raw_song_df = pd.read_csv("data/dataset.csv")

# 1 Pre process
song_df = raw_song_df.add_prefix("song_")
song_df = song_df.drop(columns=["song_id", "song_release_date"])
def fix_artist(str_list):
    # Handle NaN values and convert to string
    if pd.isna(str_list):
        return "Unknown Artist"
    str_list = str(str_list)
    return ", ".join([v for v in str_list.rstrip("']").lstrip("['").split("', '")])
song_df["song_artists"] = song_df["song_artists"].apply(fix_artist)

song_df.insert(0, "song_description", song_df["song_name"] + " - " + song_df["song_artists"])

song_data = song_df[~song_df.duplicated(subset=["song_description"], keep="first")].reset_index(drop=True)

# 2 Create song vector embeddings

#tokenize the description
tokenized_song_descs = [word_tokenize( v.lower()) for v in song_data["song_description"]]

embedding_dim = 15
word2Vec_model = Word2Vec(
    sentences = tokenized_song_descs,
    vector_size = embedding_dim,
    window = 5,
    min_count = 1,
    sg = 1,
)

def get_embedding(song_desc_tokens, model, embedding_dim):
    vectors = [model.wv[token] for token in song_desc_tokens if token in model.wv]
    return sum(vectors) / len(vectors) if vectors else np.zeros(embedding_dim)

categorical_embeddings = [
    get_embedding(song_desc_tokens, word2Vec_model, embedding_dim) for song_desc_tokens in tokenized_song_descs
]

# embed numeric song metadata

numeric_cols = list(
    song_data.drop(columns=["song_name", "song_artists", "song_description"]).columns
)

scaled_numeric_cols = [
    (song_data[col] - song_data[col].mean()) / np.std(song_data[col])
    for col in numeric_cols
]
numeric_embeddings = list(map(list, zip(*scaled_numeric_cols)))

show_embeddings(numeric_embeddings)

# merge the embeddings
row_embeddings = [
    np.concatenate([cat_row, num_row])
    for cat_row, num_row in zip(categorical_embeddings, numeric_embeddings)
]
show_embeddings(row_embeddings)

# create dataframe with embeddings
embedded_song_df = song_data[["song_name", "song_artists", "song_year"]]
embedded_song_df["song_embedding"] = row_embeddings


