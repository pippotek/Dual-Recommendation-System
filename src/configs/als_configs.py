# ALS model hyperparameters and configuration settings
ALS_CONFIG = {
    "rank": 5, #10,               # Number of latent factors
    "max_iter": 5, #20,           # Number of iterations to run the optimization
    "reg_param": 0.1,         # Regularization parameter
    "implicit_prefs": True,   # If True, ALS will use implicit feedback
    "alpha": 1.0,             # Confidence parameter (only relevant if implicit_prefs=True)
    "cold_start_strategy": "drop",  # Strategy to handle cold-start users/items
    "model_save_path": "saved_models/als_model",
}

DATASET_CONFIG = {
    "size": "demo",            # Dataset size: "demo", "small", or "large"
    "npratio": 4,              # Negative sampling ratio for training. Adjust this ratio based on class imbalance requirements
    "data_path": "./data/mind" # Path to store MIND datasets
}


TRAIN_TEST_SPLIT = {
    "train_ratio": 0.8,  
    "seed": 47,          
}

# Evaluation metrics
EVAL_CONFIG = {
    "k": 10,  # Number of recommendations for evaluation
}
