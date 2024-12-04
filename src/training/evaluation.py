import pyspark.sql.functions as F
from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALSModel
import wandb
from configs.als_configs import ALS_CONFIG, EVAL_CONFIG
from data_management.data_utils import load_data_split
from training.evaluation_metrics import compute_ranking_metrics 

wandb.init(project="MIND-RS", entity="MIND-RS", name="ALS_Evaluation")  # MIND-RS project should be set up as your default location on wandb

def evaluate_model(spark: SparkSession, als_model_path: str, test_data_path: str, k: int = 10):
    print(f"Loading ALS model from: {als_model_path}")
    als_model = ALSModel.load(als_model_path) 

    print(f"Loading test data from: {test_data_path}")  
    test_data = load_data_split(spark, test_data_path)

    print("Generating recommendations...")
    user_recommendations = als_model.recommendForAllUsers(k)

    print("Formatting recommendations...")
    exploded_recommendations = user_recommendations.withColumn(
        "recommendations", F.explode(F.col("recommendations"))
    ).select(
        F.col("userId"),
        F.col("recommendations.itemId").alias("itemId"),
        F.col("recommendations.rating").alias("rating"),
    )

    print("Evaluating the model...")
    ranking_metrics = compute_ranking_metrics(exploded_recommendations, k)

    wandb.log(ranking_metrics)

    for metric, value in ranking_metrics.items():
        print(f"{metric}: {value}")

    print("Evaluation completed and metrics logged to WandB.")


if __name__ == "__main__":
    spark = SparkSession.builder.appName("ALS_Evaluation").getOrCreate()

    # Using the config dictionary explicitly
    als_model_path = ALS_CONFIG["model_save_path"]
    test_data_path = f"./MINDdemo_train.zip/data/mind/valid/behaviors.tsv"  # Using validation set for testing, MAKE SURE THIS IS CORRECT
    k = EVAL_CONFIG["k"]  # Number of recommendations

    evaluate_model(spark, als_model_path, test_data_path, k)

    spark.stop()