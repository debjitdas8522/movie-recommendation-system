import streamlit as st
import sys
import os
import pandas as pd
import requests
import re
import random


st.set_page_config(page_title="Movie Recommender", layout="wide")

st.markdown("""
<style>

.movie-card {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    border-radius: 10px;
    overflow: hidden;
}

.movie-card img {
    border-radius: 10px;
}

.movie-card:hover {
    transform: scale(1.06) translateY(-8px);
    box-shadow: 0px 12px 30px rgba(0,0,0,0.6);
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.stColumns {
    overflow-x: auto;
}
</style>
""", unsafe_allow_html=True)

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.recommender import hybrid_recommendation

# Load movies
movies = pd.read_csv("data/movies.csv")

genres_list = sorted(set("|".join(movies["genres"]).split("|")))

movies['year'] = movies['title'].str.extract(r'\((\d{4})\)').astype(float)
movies = movies[movies['year'] >= 1990]

API_KEY = "517cb3f1b394099e928268f4c14e78c8"


@st.cache_data
def fetch_movie_details(movie_title):

    movie_title = re.sub(r"\(\d{4}\)", "", movie_title).strip()

    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_title}"

    try:
        response = requests.get(url)
        data = response.json()

        if "results" in data and len(data["results"]) > 0:

            movie = data["results"][0]

            poster_path = movie.get("poster_path")
            overview = movie.get("overview", "No description available.")
            rating = movie.get("vote_average", 0)

            if poster_path:
                poster = "https://image.tmdb.org/t/p/w500" + poster_path
            else:
                poster = None

            return poster, overview, rating

    except:
        pass

    return None, "", 0


@st.cache_data
def fetch_trailer(movie_title):

    movie_title = re.sub(r"\(\d{4}\)", "", movie_title).strip()

    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_title}"

    try:
        response = requests.get(url)
        data = response.json()

        if "results" in data and len(data["results"]) > 0:

            movie_id = data["results"][0]["id"]

            video_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}"

            video_response = requests.get(video_url)
            video_data = video_response.json()

            for video in video_data["results"]:

                if video["type"] == "Trailer" and video["site"] == "YouTube":

                    return f"https://www.youtube.com/watch?v={video['key']}"

    except:
        pass

    return None


@st.cache_data
def get_trending_movies():

    url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={API_KEY}"

    try:
        response = requests.get(url, timeout=5)
        data = response.json()
    except:
        return []

    movies_list = []

    if "results" in data:

        movies_random = random.sample(data["results"], 5)

        for movie in movies_random:

            title = movie["title"]
            rating = movie["vote_average"]
            poster_path = movie.get("poster_path")
            if poster_path:
                poster = "https://image.tmdb.org/t/p/w500" + poster_path
            else:
                continue

            movies_list.append((title, poster, rating))

    return movies_list



st.markdown("# 🎬 Movie Recommendation System")
st.markdown("AI-powered movie discovery using hybrid recommendation techniques.")

st.markdown("## 📊 Dataset Insights")

ratings = pd.read_csv("data/ratings.csv")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Movies", len(movies))

with col2:
    st.metric("Total Ratings", len(ratings))

with col3:
    st.metric("Unique Users", ratings["userId"].nunique())

st.divider()
st.markdown("Find movies you'll love using AI-powered recommendations.")

st.markdown("## 🔥 Trending Movies Today")

trending_movies = get_trending_movies()

cols = st.columns(5)

for i, (title, poster, rating) in enumerate(trending_movies):

    with cols[i % 5]:

        poster_img, overview, rating = fetch_movie_details(title)
        trailer = fetch_trailer(title)

        if poster_img:
            st.markdown(f"""
            <div class="movie-card">
                <img src="{poster_img}" width="100%">
            </div>
            """, unsafe_allow_html=True)

        st.caption(f"🎬 {title} ⭐ {round(rating,1)}")

        with st.expander("📖 Overview"):
            st.write(overview)

        if trailer:
            with st.expander("▶ Watch Trailer"):
                st.video(trailer)

st.divider()


st.markdown("## ⭐ Top Rated Movies")
@st.cache_data
def get_top_rated_movies():

    url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={API_KEY}"

    try:
        response = requests.get(url, timeout=5)
        data = response.json()
    except:
        return []

    movies_list = []

    if "results" in data:

        movies_random = random.sample(data["results"], 5)

        for movie in movies_random:

            title = movie["title"]
            rating = movie["vote_average"]

            poster_path = movie.get("poster_path")

            if poster_path:
                poster = "https://image.tmdb.org/t/p/w500" + poster_path
            else:
                continue

            movies_list.append((title, poster, rating))

    return movies_list

top_movies = get_top_rated_movies()

cols = st.columns(5)

for i, (title, poster, rating) in enumerate(top_movies):

    with cols[i]:

        poster_img, overview, rating = fetch_movie_details(title)
        trailer = fetch_trailer(title)

        if poster_img:
            st.markdown(f"""
            <div class="movie-card">
                <img src="{poster_img}" width="100%">
            </div>
            """, unsafe_allow_html=True)

        st.caption(f"🎬 {title} ⭐ {round(rating,1)}")

        with st.expander("📖 Overview"):
            st.write(overview)
        
        if trailer:
            with st.expander("▶ Watch Trailer"):
                st.video(trailer)


selected_genre = st.selectbox(
    "🎭 Filter by Genre",
    ["All"] + genres_list
)

if selected_genre != "All":
    movies = movies[movies["genres"].str.contains(selected_genre)]

movie = st.text_input("🔎 Search any Movie to explore details")

if movie:
    matches = movies[movies["title"].str.contains(movie, case=False, na=False)]

    if not matches.empty:
        movie = st.selectbox("Select from results", matches["title"].values)


st.divider()
st.markdown("## 🔍 Movie Details")

if movie:

    poster, overview, rating = fetch_movie_details(movie)
    trailer = fetch_trailer(movie)

    col1, col2 = st.columns([1,2])

    with col1:
        if poster:
            st.image(poster, width=300)

    with col2:
        st.subheader(movie)
        st.write(f"⭐ Rating: {round(rating,1)}")

        st.markdown("### 📖 Overview")
        st.write(overview)

        if trailer:
            st.markdown("### ▶ Trailer")
            tcol1, tcol2, tcol3 = st.columns([1,2,1])

            with tcol2:
                st.video(trailer)


if st.button("Recommend Movies") and movie:

    with st.spinner("🤖 AI is finding the best movies for you..."):

        recommendations = hybrid_recommendation(movie)

        st.divider()
        st.subheader(f"🍿Movies similar to {movie}")

        cols = st.columns(5)

        for i, title in enumerate(recommendations["title"]):

            poster , overview, rating = fetch_movie_details(title)
            trailer =  fetch_trailer(title)

            with cols[i % 5]:

                st.markdown(f"""
                <div class="movie-card">
                    <img src="{poster}" width="100%">
                </div>
                """, unsafe_allow_html=True)

                st.caption(f"🎬 {title} ⭐ {round(rating,1)}")

                with st.expander("📖 Overview"):
                    st.write(overview)

                if trailer:
                    with st.expander("▶ Watch Trailer"):
                        st.video(trailer)

        
        st.divider()
        st.markdown(
        """
        <center>

        Built with using **Python, Streamlit, Scikit-Learn and TMDB API**

        Movie Recommendation System – Portfolio Project

        </center>
        """,
        unsafe_allow_html=True
        )