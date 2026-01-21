import pandas as pd
import numpy as np
import pickle
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def process_data():
    print("Loading IMDB data...")
    movies = pd.read_parquet('data/movies.parquet')

    print("Cleaning & Preparing Data...")
    # 1. Rename columns for clarity
    movies.rename(columns={
        'Series_Title': 'title', 
        'Poster_Link': 'poster_path',
        'Overview': 'overview',
        'IMDB_Rating': 'rating',
        'Genre': 'genre',
        'Director': 'director',
        'Star1': 'star'
    }, inplace=True)
    
    # 2. HD Poster Fix (The "Hack")
    movies['poster_path'] = movies['poster_path'].apply(
        lambda x: x.split("._V1_")[0] + "._V1_UX500_.jpg" if isinstance(x, str) and "._V1_" in x else x
    )

    # 3. Create 'tags' for the AI (using important columns)
    movies['tags'] = movies['overview'] + " " + movies['genre'] + " " + movies['director'] + " " + movies['star']
    movies['tags'] = movies['tags'].fillna('').apply(lambda x: x.lower())

    # 4. SAVE EVERYTHING (We keep all columns now for the UI)
    final_df = movies[['title', 'poster_path', 'tags', 'overview', 'rating', 'genre', 'director', 'star']]

    print("Vectorizing...")
    cv = CountVectorizer(max_features=5000, stop_words='english')
    vectors = cv.fit_transform(final_df['tags']).toarray()
    similarity = cosine_similarity(vectors)

    if not os.path.exists('models'):
        os.makedirs('models')

    pickle.dump(final_df, open('models/movie_list.pkl', 'wb'))
    pickle.dump(similarity, open('models/similarity.pkl', 'wb'))
    print("Done! Data with full details saved.")

if __name__ == "__main__":
    process_data()