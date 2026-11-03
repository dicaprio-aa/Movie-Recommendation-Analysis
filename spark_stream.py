
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    from_json, col, current_timestamp
)
from pyspark.sql.types import (
    StructType, StructField,
    IntegerType, DoubleType, LongType
)

spark = (
    SparkSession.builder
    .appName("MovieRecommendationStreaming")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

schema = StructType([
    StructField("userId", IntegerType(), True),
    StructField("movieId", IntegerType(), True),
    StructField("rating", DoubleType(), True),
    StructField("timestamp", LongType(), True)
])

print("Connecting Spark to Kafka...")

kafka_stream = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "movie-ratings")
    .option("startingOffsets", "earliest")
    .load()
)

ratings = (
    kafka_stream
    .selectExpr("CAST(value AS STRING) AS json_value")
    .select(from_json(col("json_value"), schema).alias("data"))
    .select("data.*")
    .filter(
        col("userId").isNotNull() &
        col("movieId").isNotNull() &
        col("rating").between(0.5, 5.0)
    )
    .withColumn("processed_at", current_timestamp())
)

query = (
    ratings.writeStream
    .format("json")
    .outputMode("append")
    .option("path", "data/processed_stream")
    .option("checkpointLocation", "data/checkpoints")
    .start()
)

print("Spark Streaming Started!")
print("Listening to Kafka topic: movie-ratings")

query.awaitTermination()
