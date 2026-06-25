# main.py
import os
from generate_data import create_synthetic_csv
from data_loader import load_csv_dataset
from data_processor import clean_and_build_training_dataframe
from models import train_rf_classifier, serialize_model_asset
from explainability import generate_feature_importance_report, export_importance_visualization, export_importance_csv_file

def execute_complete_ml_pipeline():
    """Orchestrates directory setups, data ingestions, model updates, and metrics compilation."""
    print("🏁 [Pipeline Orchestrator] Initializing active training pipeline loop workflow...")
    os.makedirs('ml', exist_ok=True)
    
    # 1. Verification Data Check
    csv_file = "crime_dataset_india.csv"
    if not os.path.exists(csv_file):
        create_synthetic_csv(csv_file, count=3000)

    # 2. Extract and Process Data Logs
    raw_dataframe = load_csv_dataset(csv_file)
    processed_dataframe = clean_and_build_training_dataframe(raw_dataframe)
    processed_dataframe.to_csv("ml/intelligence_processed_data.csv", index=False)

    # 3. Model Training Operations
    trained_model = train_rf_classifier(processed_dataframe)
    serialize_model_asset(trained_model, "ml/crime_rf_model.pkl")

    # 4. Generate Explainability Matrices and Physical File Exports
    export_importance_visualization(trained_model)
    report_df = generate_feature_importance_report(trained_model)
    export_importance_csv_file(report_df)
    
    print("\n🎯 Complete pipeline loop executed successfully. Summary feature coefficients output:")
    print(report_df.to_string(index=False))

if __name__ == "__main__":
    execute_complete_ml_pipeline()