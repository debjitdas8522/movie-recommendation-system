import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

movies = pd.read_csv(os.path.join(BASE_DIR, "data", "movies.csv"))
ratings = pd.read_csv(os.path.join(BASE_DIR, "data", "ratings.csv"))

# Calculate movie popularity (average rating + rating count)
movie_ratings = ratings.groupby("movieId").agg(
    avg_rating=("rating", "mean"),
    rating_count=("rating", "count")
).reset_index()

# Merge ratings with movies dataset
movies = movies.merge(movie_ratings, on="movieId", how="left")


movies['year'] = movies['title'].str.extract(r'\((\d{4})\)').astype(float)
# Keep only movies from 1990 onwards
movies = movies[movies['year'] >= 1990].reset_index(drop=True)


# -----------------------------
# CONTENT BASED FILTERING
# -----------------------------

movies['genres'] = movies['genres'].str.replace('|', ' ')

tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies['genres'])

cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

indices = pd.Series(movies.index, index=movies['title']).drop_duplicates()


def recommend_movies(title):

    idx = indices[title]

    sim_scores = list(enumerate(cosine_sim[idx]))

    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    sim_scores = sim_scores[1:30]

    movie_indices = [i[0] for i in sim_scores]

    recommended = movies.iloc[movie_indices]

    # prioritize newer movies
    recommended = recommended.copy()
    recommended["recency_score"] = recommended["year"] * 0.1

    recommended = recommended.sort_values(
        by=["recency_score", "avg_rating", "rating_count"],
        ascending=False
    )

    return recommended[["title"]].head(5)


# -----------------------------
# HYBRID RECOMMENDER
# -----------------------------

def hybrid_recommendation(movie_title):
    return recommend_movies(movie_title)