# explainability.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from config import PipelineConfig

def generate_feature_importance_report(model) -> pd.DataFrame:
    """Calculates feature coefficient weights from the classification model."""
    importances = model.feature_importances_
    records = [
        {"feature": name, "importance_weight": round(float(weight), 6)}
        for name, weight in zip(PipelineConfig.FEATURE_COLUMNS, importances)
    ]
    return pd.DataFrame(records).sort_values(by="importance_weight", ascending=False)

def export_importance_visualization(model):
    """Generates the feature importance chart image file on disk."""
    importances = model.feature_importances_
    
    plt.figure(figsize=(10, 5))
    plt.title("🧠 Global Feature Importances Breakdown", fontsize=11, fontweight='bold')
    sns.barplot(x=PipelineConfig.FEATURE_COLUMNS, y=importances, color="teal")
    plt.ylabel("Importance Weight Ratio")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(PipelineConfig.IMAGE_EXPORT_PATH)
    plt.close()
    print(f"📊 Feature importance chart generated at: '{PipelineConfig.IMAGE_EXPORT_PATH}'")

def export_importance_csv_file(report_df: pd.DataFrame):
    """Saves the feature importance metrics directly to a CSV file for backend consumption."""
    report_df.to_csv(PipelineConfig.CSV_EXPORT_PATH, index=False)
    print(f"📁 Analytics database records compiled to: '{PipelineConfig.CSV_EXPORT_PATH}'")