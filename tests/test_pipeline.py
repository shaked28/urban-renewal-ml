import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


def test_dataset_loads():
    df = pd.read_excel(ROOT / "data" / "urban_renewal_dataset.xlsx", sheet_name="Dataset")
    assert len(df) == 500
    assert "כדאי_1_לא_0" in df.columns
    assert "ציון_כדאיות_0_100" in df.columns


def test_target_range():
    df = pd.read_excel(ROOT / "data" / "urban_renewal_dataset.xlsx", sheet_name="Dataset")
    assert df["ציון_כדאיות_0_100"].between(0, 100).all()
    assert df["כדאי_1_לא_0"].isin([0, 1]).all()


def test_no_nulls_in_features():
    df = pd.read_excel(ROOT / "data" / "urban_renewal_dataset.xlsx", sheet_name="Dataset")
    key_cols = ["עיר", "סוג_פרויקט", "גיל_בניין_שנים", "מספר_דירות_קיימות",
                'מרווח_גולמי_%', 'IRR_משוער_%']
    assert df[key_cols].isnull().sum().sum() == 0


def test_feature_engineering():
    from models.train import load_and_prepare
    X, y_cls, y_reg, num_cols, cat_cols, df = load_and_prepare()
    assert "יחס_דירות_חדש_לישן" in df.columns
    assert "מינוף_שטח" in df.columns
    assert X.shape[0] == 500


def test_model_files_exist():
    import joblib, json
    cls_path  = ROOT / "models" / "best_classifier.pkl"
    reg_path  = ROOT / "models" / "best_regressor.pkl"
    meta_path = ROOT / "models" / "model_meta.json"
    assert cls_path.exists(),  "Run python models/train.py first"
    assert reg_path.exists(),  "Run python models/train.py first"
    assert meta_path.exists(), "Run python models/train.py first"

    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)
    assert meta["best_classifier_auc"] >= 0.75, f"AUC too low: {meta['best_classifier_auc']}"
    assert meta["best_regressor_rmse"] <= 15,   f"RMSE too high: {meta['best_regressor_rmse']}"


def test_prediction_single():
    import joblib, json
    from models.train import load_and_prepare
    cls = joblib.load(ROOT / "models" / "best_classifier.pkl")
    reg = joblib.load(ROOT / "models" / "best_regressor.pkl")
    with open(ROOT / "models" / "model_meta.json", encoding="utf-8") as f:
        meta = json.load(f)

    X, _, _, _, _, _ = load_and_prepare()
    sample = X.iloc[[0]]
    proba = cls.predict_proba(sample)[0][1]
    score = reg.predict(sample)[0]
    assert 0 <= proba <= 1
    assert 0 <= score <= 100
