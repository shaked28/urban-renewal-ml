---
name: urban-renewal-ml
description: >
  סקיל להרצה, פיתוח ודיבוג של פרויקט ML לבדיקת כדאיות התחדשות עירונית.
  הפעל תמיד כשמדובר בפרויקט זה: train.py, app/main.py, EDA, models/,
  שגיאות Streamlit, שגיאות sklearn/xgboost/shap, בעיות dataset,
  feature engineering, model evaluation, GitHub, README, דוחות.
---

# Urban Renewal Feasibility ML — Project Skill

## מבנה הפרויקט

```
urban_renewal_project/
├── data/
│   └── urban_renewal_dataset.xlsx     ← 500 עסקאות, 31 עמודות
├── models/
│   ├── train.py                       ← Pipeline אימון מלא
│   ├── best_classifier.pkl            ← נוצר אחרי train
│   ├── best_regressor.pkl             ← נוצר אחרי train
│   ├── shap_explainer.pkl             ← נוצר אחרי train
│   └── model_meta.json                ← מטא + ביצועים
├── app/
│   └── main.py                        ← Streamlit UI
├── notebooks/
│   └── eda_and_eval.py                ← EDA + charts
├── docs/
│   └── figures/                       ← תמונות לדוח
├── tests/
│   └── test_pipeline.py               ← בדיקות יחידה
└── requirements.txt
```

## סדר הרצה

```bash
# 1. התקן תלויות
pip install -r requirements.txt

# 2. אמן מודלים (חייב לרוץ לפני האפליקציה)
cd urban_renewal_project
python models/train.py

# 3. הרץ EDA
python notebooks/eda_and_eval.py

# 4. הפעל אפליקציה
streamlit run app/main.py
```

## Feature Engineering

הפיצ'רים המחושבים (נוצרים ב-train.py וב-app/main.py):

| שם עמודה | נוסחה |
|----------|-------|
| יחס_דירות_חדש_לישן | new_units / existing_units |
| הכנסה_לדירה_קיימת | revenue / existing_units |
| עלות_לדירה_חדשה | total_cost / new_units |
| שטח_כולל_חדש_מ2 | new_units × new_sqm |
| מינוף_שטח | total_new_area / total_existing_area |
| עלות_לקיים_יחסי | construction_cost / revenue |

**חשוב**: שתי הפונקציות `load_and_prepare()` ו-`compute_derived()` חייבות להיות סינכרוניות בדיוק.

## מודלים

### Classification (target: כדאי_1_לא_0)
- LogisticRegression (baseline)
- RandomForestClassifier (n_estimators=200)
- GradientBoostingClassifier
- XGBClassifier (אם מותקן)

### Regression (target: ציון_כדאיות_0_100)
- Ridge (baseline)
- RandomForestRegressor
- GradientBoostingRegressor
- XGBRegressor (אם מותקן)

### מדדי הצלחה
| מדד | יעד |
|-----|-----|
| AUC-ROC | ≥ 0.80 |
| RMSE (ציון) | ≤ 10 |
| Precision (כדאי=1) | ≥ 0.78 |

## שגיאות נפוצות

### "Models not found" באפליקציה
```bash
python models/train.py   # חייב לרוץ קודם
```

### KeyError בעמודות
עמודות עם גרשיים עבריים צריכות backslash בפייתון:
```python
df['מחיר_מכירה_למ2_חדש_ש"ח']   # נכון
df["מחיר_מכירה_למ2_חדש_ש\"ח"]  # נכון
```

### SHAP לא עובד
SHAP עובד רק עם tree-based models. אם best model הוא LogisticRegression,
SHAP ישתמש ב-LinearExplainer. אם נכשל — האפליקציה תדלג בשקט.

### Class imbalance
ה-dataset מכיל ~80% positive. המודלים כוללים `class_weight="balanced"`.
אם רוצים SMOTE:
```python
from imblearn.over_sampling import SMOTE
X_res, y_res = SMOTE(random_state=42).fit_resample(X_train_enc, y_train)
```

## GitHub README

הכלל: README.md ברמת root. חייב לכלול:
- תיאור הפרויקט 2-3 משפטים
- How to run (install → train → app)
- Screenshots (מ-docs/figures/)
- Model results table
- License: MIT

## GitHub Pages (דף נחיתה)

קובץ `docs/index.html` — דף GitHub Pages עם:
- תיאור הפרויקט
- לינק לסרטון שיווקי
- לינק למצגת
- Screenshots

## מסמכי הגשה

| מסמך | תיאור |
|------|-------|
| docs/work_plan.docx | תוכנית עבודה (שבוע 4) ✓ |
| docs/mvp_report.docx | דוח MVP (שבוע 8) |
| docs/final_report.docx | דוח סיכום סופי |
| presentation/ | מצגת PowerPoint |

## תיעוד פגישות (נספח ב-MVP)

יצור קובץ `docs/meeting_log.md` עם כל מפגש:
```markdown
## פגישה 1 — [תאריך]
**נוכחים**: רועי אולמן, ד"ר איל זינגר
**נושאים**: הגדרת פרויקט, אישור dataset, מבנה מודל
**החלטות**: ...
**משימות לפגישה הבאה**: ...
```
