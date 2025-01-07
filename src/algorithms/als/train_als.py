import wandb
from src.algorithms.als.als_utils import create_als_model, save_model, make_predictions
from src.training.evaluation_metrics import compute_regression_metrics
from src.configs.setup import load_config
from pyspark.sql.functions import collect_list 
import logging

config = load_config('src/configs/config.yaml')

def train_als_model(training_data, validation_data, model_save_path):
    config = load_config('src/configs/config.yaml')
    wandb.login(key=config.get('wandb_key'))
    wandb.init(
        project="MIND-RS",
        name=f"als_rank_{config['ALS_CONFIG']['rank']}_reg_{config['ALS_CONFIG']['reg_param']}",
        config=config['ALS_CONFIG'],

    )

    logging.info("Starting ALS model training...")
    als = create_als_model()
    
    for iteration in range(config['ALS_CONFIG']["max_iter"]):
        
        als.setMaxIter(iteration + 1)
        model = als.fit(training_data)
        predictions = make_predictions(model, validation_data)

        # Compute regression metrics
        regression_metrics = compute_regression_metrics(predictions)
        rmse = regression_metrics["RMSE"]
        
        logging.info(f"Training ALS model - Iteration {iteration + 1}/{config['ALS_CONFIG']['max_iter']}")
        

        wandb.log({
            "RMSE": rmse,
            "Iteration": iteration + 1,
            })

    # Final predictions and metrics
    predictions = make_predictions(model, validation_data)
    predictions.show()
    regression_metrics = compute_regression_metrics(predictions)
    #metrics = compute_ranking_metrics(predictions, top_k=5)
    rmse = regression_metrics["RMSE"]
    
    wandb.log({
        "Final RMSE": rmse,
        })
    
    logging.info(f"Final RMSE: {rmse}")


    logging.info("Saving the trained ALS model...")
    save_model(model, config['ALS_CONFIG']["model_save_path"])
    
    logging.info(f"ALS model saved successfully to {model_save_path}.")
    wandb.finish()
    logging.info("Training process completed and WandB session closed.")
    return model

def get_top_predictions(model, data, top_n=10):
    """
    Retrieves the top N predictions for each user.

    Args:
        model: The trained ALS model.
        data: The dataset for which predictions are to be made.
        top_n: Number of top predictions to retrieve.

    Returns:
        A DataFrame containing the top N predictions for each user.
    """
    logging.info("Generating top predictions...")
    predictions = make_predictions(model, data)
    
    # Assuming predictions DataFrame has 'userId', 'itemId', and 'prediction' columns
    top_predictions = predictions.orderBy(['userId', 'prediction'], ascending=[True, False])
    top_predictions = top_predictions.groupBy('userId').agg(
        collect_list('itemId').alias('top_items'),
        collect_list('prediction').alias('top_scores')
    )
    
    # Limit to top N
    top_predictions = top_predictions.select(
        'userId',
        top_predictions['top_items'][0:top_n].alias('top_items'),
        top_predictions['top_scores'][0:top_n].alias('top_scores')
    )

    logging.info("Top predictions generated successfully.")
    return top_predictions
