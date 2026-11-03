import streamlit as st
import pandas as pd
import plotly.express as px
import json
from pathlib import Path
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Movie Recommendation & Behaviour Analysis",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Movie Recommendation & User Behaviour Analysis")
st.caption("Hybrid Recommendation System | Kafka | Spark Streaming")

# Load datasets
@st.cache_data
def load_data():
    movies = pd.read_csv("data/movies_clean.csv")
    ratings = pd.read_csv("data/ratings_clean.csv")
    return movies, ratings

movies, ratings = load_data()

# Sidebar
st.sidebar.title("🎥 Movie Analytics")
page = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard",
        "Movie Analytics",
        "User Behaviour",
        "Recommendations",
        "Live Activity"
    ]
)

# Dashboard
if page == "Dashboard":
    st.header("Project Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Movies", f"{movies['movieId'].nunique():,}")
    c2.metric("Total Ratings", f"{len(ratings):,}")
    c3.metric("Total Users", f"{ratings['userId'].nunique():,}")
    c4.metric("Average Rating", f"{ratings['rating'].mean():.2f} ⭐")

    st.divider()

    st.subheader("Rating Distribution")

    rating_counts = (
        ratings["rating"]
        .value_counts()
        .sort_index()
        .reset_index()
    )
    rating_counts.columns = ["Rating", "Count"]

    fig = px.bar(
        rating_counts,
        x="Rating",
        y="Count",
        title="Distribution of Movie Ratings",
        color="Rating"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 10 Popular Movies")

    popular = ratings.groupby("movieId").agg(
        total_ratings=("rating", "count"),
        average_rating=("rating", "mean")
    ).reset_index()

    popular = popular.merge(movies, on="movieId")
    popular = popular.sort_values(
        "total_ratings", ascending=False
    ).head(10)

    st.dataframe(
        popular[["title", "total_ratings", "average_rating"]],
        use_container_width=True,
        hide_index=True
    )

# Movie Analytics
elif page == "Movie Analytics":
    st.header("🍿 Movie Analytics")

    genre_data = movies.assign(
        genres=movies["genres"].fillna("").str.split("|")
    ).explode("genres")

    genre_counts = genre_data[
        genre_data["genres"] != "(no genres listed)"
    ]["genres"].value_counts().reset_index()

    genre_counts.columns = ["Genre", "Movie Count"]

    fig = px.bar(
        genre_counts,
        x="Genre",
        y="Movie Count",
        title="Movies by Genre",
        color="Movie Count"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Search Movies")

    search = st.text_input("Enter movie name")

    if search:
        result = movies[
            movies["title"].str.contains(
                search, case=False, na=False
            )
        ]
        st.dataframe(result, use_container_width=True, hide_index=True)
    else:
        st.dataframe(movies.head(20), use_container_width=True)

# User Behaviour
elif page == "User Behaviour":
    st.header("👥 User Behaviour Analysis")

    user_id = st.selectbox(
        "Select User ID",
        sorted(ratings["userId"].unique())
    )

    user_ratings = ratings[ratings["userId"] == user_id]

    c1, c2, c3 = st.columns(3)
    c1.metric("Movies Rated", len(user_ratings))
    c2.metric("Average Rating", f"{user_ratings['rating'].mean():.2f}")
    c3.metric("Highest Rating", f"{user_ratings['rating'].max():.1f}")

    user_movies = user_ratings.merge(movies, on="movieId")

    st.subheader("User Rating Distribution")

    fig = px.histogram(
        user_ratings,
        x="rating",
        nbins=10,
        title=f"Rating Pattern of User {user_id}"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Movies Rated by User")
    st.dataframe(
        user_movies[["title", "genres", "rating"]],
        use_container_width=True,
        hide_index=True
    )

# Recommendations
elif page == "Recommendations":
    st.header("🤖 Hybrid Movie Recommendations")

    user_id = st.selectbox(
        "Choose User ID",
        sorted(ratings["userId"].unique())
    )

    number = st.slider("Number of recommendations", 5, 20, 10)

    if st.button("Generate Recommendations"):
        from recommender import recommend_movies

        recommendations = recommend_movies(user_id, number)

        if recommendations is not None and not recommendations.empty:
            st.success("Recommendations generated successfully!")
            st.dataframe(
                recommendations,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No recommendations available.")

# Live Activity
elif page == "Live Activity":
    st.header("⚡ Live Kafka Rating Activity")
    st.write("Incoming rating events processed by Spark Streaming.")

    st_autorefresh(interval=5000, key="live_refresh")

    output_folder = Path("data/processed_stream")
    events = []

    if output_folder.exists():
        for file in output_folder.rglob("*.json"):
            try:
                with file.open("r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            events.append(json.loads(line))
            except (OSError, json.JSONDecodeError):
                continue

    if events:
        live_data = pd.DataFrame(events)

        c1, c2 = st.columns(2)
        c1.metric("Processed Events", len(live_data))
        c2.metric(
            "Live Average Rating",
            f"{live_data['rating'].mean():.2f} ⭐"
        )

        st.subheader("Latest Rating Events")
        st.dataframe(
            live_data.sort_values(
                "processed_at", ascending=False
            ).head(50),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info(
            "No processed events found. Start Kafka and Spark Streaming, "
            "then run the producer."
        )

st.divider()
st.caption("Movie Recommendation & User Behaviour Analysis | Academic Project")