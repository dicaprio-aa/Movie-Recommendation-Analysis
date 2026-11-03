
import pandas as pd
import json
import time
from kafka import KafkaProducer

# Load cleaned ratings
ratings = pd.read_csv("data/ratings_clean.csv")

# Connect to Kafka
producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    value_serializer=lambda value: json.dumps(value).encode("utf-8")
)

print("Movie Rating Producer Started!")
print("Sending ratings to Kafka...")

try:
    for index, row in ratings.head(500).iterrows():

        event = {
            "userId": int(row["userId"]),
            "movieId": int(row["movieId"]),
            "rating": float(row["rating"]),
            "timestamp": int(row["timestamp"])
        }

        producer.send("movie-ratings", value=event)

        print("Sent:", event)

        time.sleep(0.3)

    producer.flush()
    print("\nAll 500 rating events sent successfully!")

except KeyboardInterrupt:
    print("\nProducer stopped by user.")

finally:
    producer.flush()
    producer.close()
