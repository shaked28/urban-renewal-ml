"""
Urban Renewal Feasibility - ML Training Pipeline
"""
import pandas as pd
import numpy as np
import joblib
import json
from pathlib import Path

from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    roc_auc_score, classification_report, confusion_matrix,
    mean_squared_error, r2_score, accuracy_score
)
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

try:
    from xgboost import XGBClassifier, XGBRegressor
    HAS_XGB = True
except ImportError:
    HAS_XGB = False
    print("XGBoost not installed — skipping XGB models")

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False

DATA_PATH = Path(__file__).parent.parent / "data" / "urban_renewal_dataset.xlsx"
MODELS_DIR = Path(__file__).parent


def load_and_prepare(path=DATA_PATH):
    df = pd.read_excel(path, sheet_name="Dataset")

    # ── Feature engineering ────────────────────────────────────────────
    df["יחס_דירות_חדש_לישן"]      = df["מספר_דירות_חדשות"] / df["מספר_דירות_קיימות"]
    df["הכנסה_לדירה_קיימת"]       = df['הכנסות_ממכירת_דירות_ש"ח'] / df["מספר_דירות_קיימות"]
    df["עלות_לדירה_חדשה"]         = df['סה"כ_עלויות_ש"ח'] / df["מספר_דירות_חדשות"].clip(lower=1)
    df["שטח_כולל_חדש_מ2"]         = df["מספר_דירות_חדשות"] * df["שטח_ממוצע_חדש_מ2"]
    df["מינוף_שטח"]               = df["שטח_כולל_חדש_מ2"] / (df["מספר_דירות_קיימות"] * df["שטח_ממוצע_קיים_מ2"])
    df["עלות_לקיים_יחסי"]         = df['עלות_בנייה_ש"ח'] / df['הכנסות_ממכירת_דירות_ש"ח'].clip(lower=1)

    # Categorical features
    cat_cols  = ["עיר", "סוג_פרויקט"]
    # Numeric features — all relevant columns
    num_cols  = [
        "גיל_בניין_שנים", "מספר_דירות_קיימות", "שטח_ממוצע_קיים_מ2",
        "מספר_קומות_קיים", "מספר_דירות_חדשות", "שטח_ממוצע_חדש_מ2",
        'מחיר_מכירה_למ2_קיים_ש"ח', 'מחיר_מכירה_למ2_חדש_ש"ח',
        'מרווח_גולמי_%', 'IRR_משוער_%',
        "חודשי_היתר", "חודשי_בנייה", "חודשי_מכירות", "חודשי_החתמה",
        "משך_כולל_פרויקט_חודשים", 'הסתברות_אישור_%',
        'עלות_למ2_בנייה_ש"ח',
        "יחס_דירות_חדש_לישן", "הכנסה_לדירה_קיימת",
        "עלות_לדירה_חדשה", "מינוף_שטח", "עלות_לקיים_יחסי",
    ]

    feature_cols = num_cols + cat_cols
    target_bin   = 'כדאי_1_לא_0'
    target_reg   = 'ציון_כדאיות_0_100'

    X = df[feature_cols].copy()
    y_cls = df[target_bin].copy()
    y_reg = df[target_reg].copy()

    return X, y_cls, y_reg, num_cols, cat_cols, df


def build_preprocessor(num_cols, cat_cols):
    return ColumnTransformer(transformers=[
        ("num", StandardScaler(), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
    ])


def train_all(X, y_cls, y_reg, num_cols, cat_cols):
    X_tr, X_te, yc_tr, yc_te, yr_tr, yr_te = train_test_split(
        X, y_cls, y_reg, test_size=0.2, random_state=42, stratify=y_cls
    )

    prep = build_preprocessor(num_cols, cat_cols)

    results = {}

    # ── Classification models ─────────────────────────────────────────
    cls_models = {
        "logistic_regression": LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced"),
        "random_forest": RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42, class_weight="balanced"),
        "gradient_boosting": GradientBoostingClassifier(n_estimators=200, max_depth=4, learning_rate=0.05, random_state=42),
    }
    if HAS_XGB:
        cls_models["xgboost"] = XGBClassifier(
            n_estimators=300, max_depth=5, learning_rate=0.05,
            use_label_encoder=False, eval_metric="logloss",
            random_state=42, verbosity=0
        )

    best_cls_score = -1
    best_cls_name  = None
    best_cls_pipe  = None

    for name, model in cls_models.items():
        pipe = Pipeline([("prep", prep), ("clf", model)])
        pipe.fit(X_tr, yc_tr)
        y_pred     = pipe.predict(X_te)
        y_prob     = pipe.predict_proba(X_te)[:, 1]
        auc        = roc_auc_score(yc_te, y_prob)
        acc        = accuracy_score(yc_te, y_pred)
        cv_auc     = cross_val_score(pipe, X_tr, yc_tr, cv=5, scoring="roc_auc").mean()
        results[f"cls_{name}"] = {"auc_test": round(auc,4), "acc_test": round(acc,4), "cv_auc": round(cv_auc,4)}
        print(f"  [CLS] {name:25s}  AUC={auc:.4f}  ACC={acc:.4f}  CV-AUC={cv_auc:.4f}")
        if auc > best_cls_score:
            best_cls_score = auc
            best_cls_name  = name
            best_cls_pipe  = pipe

    # ── Regression models ─────────────────────────────────────────────
    reg_models = {
        "ridge": Ridge(alpha=1.0),
        "random_forest_reg": RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42),
        "gradient_boosting_reg": GradientBoostingClassifier(n_estimators=200, max_depth=4, learning_rate=0.05, random_state=42),
    }
    if HAS_XGB:
        reg_models["xgboost_reg"] = XGBRegressor(
            n_estimators=300, max_depth=5, learning_rate=0.05,
            random_state=42, verbosity=0
        )
    # Fix: gradient boosting is classifier, use real regressor
    reg_models["gradient_boosting_reg"] = __import__(
        "sklearn.ensemble", fromlist=["GradientBoostingRegressor"]
    ).GradientBoostingRegressor(n_estimators=200, max_depth=4, learning_rate=0.05, random_state=42)

    best_reg_score = 9999
    best_reg_name  = None
    best_reg_pipe  = None

    for name, model in reg_models.items():
        pipe = Pipeline([("prep", build_preprocessor(num_cols, cat_cols)), ("reg", model)])
        pipe.fit(X_tr, yr_tr)
        y_pred = pipe.predict(X_te)
        rmse   = np.sqrt(mean_squared_error(yr_te, y_pred))
        r2     = r2_score(yr_te, y_pred)
        results[f"reg_{name}"] = {"rmse": round(rmse,3), "r2": round(r2,4)}
        print(f"  [REG] {name:25s}  RMSE={rmse:.3f}  R2={r2:.4f}")
        if rmse < best_reg_score:
            best_reg_score = rmse
            best_reg_name  = name
            best_reg_pipe  = pipe

    # ── Save best models ──────────────────────────────────────────────
    joblib.dump(best_cls_pipe, MODELS_DIR / "best_classifier.pkl")
    joblib.dump(best_reg_pipe, MODELS_DIR / "best_regressor.pkl")

    # Save feature info for app
    prep_fitted = best_cls_pipe.named_steps["prep"]
    cat_feature_names = prep_fitted.named_transformers_["cat"].get_feature_names_out(cat_cols).tolist()
    all_feature_names = num_cols + cat_feature_names

    meta = {
        "num_cols": num_cols,
        "cat_cols": cat_cols,
        "feature_names_encoded": all_feature_names,
        "best_classifier": best_cls_name,
        "best_classifier_auc": best_cls_score,
        "best_regressor": best_reg_name,
        "best_regressor_rmse": best_reg_score,
        "results": results,
        "cities": sorted(X["עיר"].unique().tolist()),
        "project_types": sorted(X["סוג_פרויקט"].unique().tolist()),
    }
    with open(MODELS_DIR / "model_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Best classifier : {best_cls_name} (AUC={best_cls_score:.4f})")
    print(f"✓ Best regressor  : {best_reg_name} (RMSE={best_reg_score:.3f})")
    print(f"✓ Models saved to {MODELS_DIR}")

    # ── SHAP explainer (on best classifier) ──────────────────────────
    if HAS_SHAP:
        try:
            X_tr_enc = best_cls_pipe.named_steps["prep"].transform(X_tr)
            clf = best_cls_pipe.named_steps["clf"]
            if hasattr(clf, "feature_importances_"):
                explainer = shap.TreeExplainer(clf)
            else:
                explainer = shap.LinearExplainer(clf, X_tr_enc)
            joblib.dump(explainer, MODELS_DIR / "shap_explainer.pkl")
            print("✓ SHAP explainer saved")
        except Exception as e:
            print(f"  SHAP explainer failed: {e}")

    return best_cls_pipe, best_reg_pipe, meta, X_te, yc_te, yr_te


if __name__ == "__main__":
    print("Loading data...")
    X, y_cls, y_reg, num_cols, cat_cols, df = load_and_prepare()
    print(f"Dataset: {len(df)} rows, {X.shape[1]} features")
    print("\nTraining models...")
    train_all(X, y_cls, y_reg, num_cols, cat_cols)
