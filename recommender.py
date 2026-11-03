import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load cleaned datasets
movies = pd.read_csv("data/movies_clean.csv")
ratings = pd.read_csv("data/ratings_clean.csv")

# Prepare movie genres
movies["genres"] = movies["genres"].fillna("").str.replace("|", " ", regex=False)

# Content-based similarity
vectorizer = TfidfVectorizer()
genre_matrix = vectorizer.fit_transform(movies["genres"])
content_similarity = cosine_similarity(genre_matrix)

# User-movie rating matrix
user_movie_matrix = ratings.pivot_table(
    index="userId",
    columns="movieId",
    values="rating"
).fillna(0)

# Collaborative similarity between users
user_similarity = cosine_similarity(user_movie_matrix)
user_similarity_df = pd.DataFrame(
    user_similarity,
    index=user_movie_matrix.index,
    columns=user_movie_matrix.index
)


def recommend_movies(user_id, number=10):
    if user_id not in user_movie_matrix.index:
        print("User ID not found. Try another user.")
        return

    user_ratings = user_movie_matrix.loc[user_id]
    rated_movies = user_ratings[user_ratings > 0].index.tolist()

    if not rated_movies:
        print("No rating history found for this user.")
        return

    # Collaborative filtering scores
    similar_users = user_similarity_df[user_id].drop(user_id)
    similar_users = similar_users.sort_values(ascending=False).head(20)

    collaborative_scores = (
        user_movie_matrix.loc[similar_users.index].T
        .dot(similar_users)
    )

    collaborative_scores = collaborative_scores / (
        similar_users.abs().sum() + 1e-9
    )

    # Content-based scores
    movie_index = movies.reset_index(drop=True)
    movie_to_index = pd.Series(
        movie_index.index,
        index=movie_index["movieId"]
    )

    content_scores = np.zeros(len(movie_index))

    for movie_id in rated_movies:
        if movie_id in movie_to_index.index:
            idx = movie_to_index[movie_id]
            content_scores += (
                content_similarity[idx] * user_ratings[movie_id]
            )

    content_scores = content_scores / len(rated_movies)

    # Combine both methods: 60% content + 40% collaborative
    results = movie_index.copy()

    results["content_score"] = content_scores
    results["collaborative_score"] = (
        results["movieId"].map(collaborative_scores).fillna(0).values
    )

    results["hybrid_score"] = (
        0.6 * results["content_score"]
        + 0.4 * results["collaborative_score"]
    )

    # Exclude already rated movies
    results = results[~results["movieId"].isin(rated_movies)]

    recommendations = results.sort_values(
        "hybrid_score", ascending=False
    ).head(number)

    return recommendations[
        ["movieId", "title", "genres", "hybrid_score"]
    ]


if __name__ == "__main__":
    print("\nMOVIE RECOMMENDATION SYSTEM")
    print("---------------------------")

    user_id = int(input("Enter User ID (1-610): "))

    recommendations = recommend_movies(user_id)

    if recommendations is not None:
        print("\nRecommended Movies:\n")
        print(recommendations.to_string(index=False))