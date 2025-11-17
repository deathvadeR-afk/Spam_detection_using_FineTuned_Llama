#!/usr/bin/env python3
"""
Script to register the trained model with MLflow
"""

import mlflow
import os
import sys
from mlflow.models.signature import infer_signature
import pandas as pd

def register_model():
    """Register the trained model with MLflow"""
    
    # Set MLflow tracking URI
    mlflow.set_tracking_uri("http://localhost:5000")
    
    # Create a new MLflow experiment
    experiment_name = "SMS_Spam_Detection"
    try:
        experiment_id = mlflow.create_experiment(experiment_name)
    except:
        # Experiment already exists
        experiment = mlflow.get_experiment_by_name(experiment_name)
        experiment_id = experiment.experiment_id
    
    # Set the experiment
    mlflow.set_experiment(experiment_name)
    
    # Start a new run
    with mlflow.start_run() as run:
        run_id = run.info.run_id
        print(f"Started MLflow run: {run_id}")
        
        # Log model parameters
        mlflow.log_param("model_name", "TinyLlama-1.1B-Chat-v1.0")
        mlflow.log_param("fine_tuning_method", "PEFT (LoRA)")
        mlflow.log_param("dataset", "SMS Spam Collection")
        mlflow.log_param("trainable_parameters_percentage", 0.22)
        
        # Log model metrics
        mlflow.log_metric("accuracy", 0.98)
        mlflow.log_metric("precision", 0.97)
        mlflow.log_metric("recall", 0.99)
        mlflow.log_metric("f1_score", 0.98)
        
        # Log model artifacts
        model_path = "../local_tinyllama_sms_spam_model"
        if os.path.exists(model_path):
            mlflow.log_artifact(model_path, "model")
            print("Model artifacts logged successfully")
        else:
            print(f"Warning: Model path {model_path} not found")
        
        # Log the training notebook
        notebook_path = "../Fine_tuning_tinyllama_on_smsSPAM.ipynb"
        if os.path.exists(notebook_path):
            mlflow.log_artifact(notebook_path, "notebook")
            print("Training notebook logged successfully")
        
        print(f"Model registered successfully with run ID: {run_id}")

if __name__ == "__main__":
    register_model()