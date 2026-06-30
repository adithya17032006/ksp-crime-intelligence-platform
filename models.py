# models.py
import pickle
import pandas as pd  # <--- ADD THIS IMPORT HERE
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from config import PipelineConfig

def train_rf_classifier(df: pd.DataFrame) -> RandomForestClassifier:  # <--- CHANGE 'id' BACK TO 'pd'
    """Fits the Ensemble Classifier Model and displays validation performance matrices."""
    X = df[PipelineConfig.FEATURE_COLUMNS]
    y = df['Is_High_Risk']
    
    # Stratified split execution tracking to manage balanced dimensions
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=PipelineConfig.RANDOM_STATE, stratify=y
    )
    
    print("🧠 [Models] Fitting Random Forest Ensemble Core Engine Classifier Layers...")
    model = RandomForestClassifier(
        n_estimators=300, 
        max_depth=20,
        class_weight='balanced',
        random_state=PipelineConfig.RANDOM_STATE
    )
    model.fit(X_train, y_train)
    
    print("\n📋 [Validation Metrics Evaluation Matrix Results]:")
    predictions = model.predict(X_test)
    print(classification_report(y_test, predictions))
    
    return model

def serialize_model_asset(model, export_path: str):
    """Saves the trained model artifact to disk as a binary pickle file."""
    with open(export_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"💾 Model artifact successfully exported to: '{export_path}'")