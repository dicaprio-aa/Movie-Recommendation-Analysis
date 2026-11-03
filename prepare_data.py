
import pandas as pd
import os

DATA_DIR = "data"

print("Loading MovieLens dataset...")

movies = pd.read_csv(os.path.join(DATA_DIR, "movies.csv"))
ratings = pd.read_csv(os.path.join(DATA_DIR, "ratings.csv"))
tags = pd.read_csv(os.path.join(DATA_DIR, "tags.csv"))

# Remove duplicate records
movies = movies.drop_duplicates(subset=["movieId"])
ratings = ratings.drop_duplicates()
tags = tags.drop_duplicates()

# Remove missing values
movies = movies.dropna(subset=["movieId", "title"])
ratings = ratings.dropna(subset=["userId", "movieId", "rating"])

# Keep valid ratings
ratings = ratings[ratings["rating"].between(0.5, 5.0)]

# Keep only ratings for existing movies
ratings = ratings[ratings["movieId"].isin(movies["movieId"])]

# Save cleaned datasets
movies.to_csv(os.path.join(DATA_DIR, "movies_clean.csv"), index=False)
ratings.to_csv(os.path.join(DATA_DIR, "ratings_clean.csv"), index=False)
tags.to_csv(os.path.join(DATA_DIR, "tags_clean.csv"), index=False)

print("\nDATA PREPARATION COMPLETED!")
print("--------------------------------")
print("Total Movies:", len(movies))
print("Total Ratings:", len(ratings))
print("Total Users:", ratings["userId"].nunique())
print("Total Tags:", len(tags))
print("--------------------------------")
