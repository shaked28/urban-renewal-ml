import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

MODELS_DIR = ROOT / "models"

st.set_page_config(
    page_title="כלי בדיקת כדאיות — התחדשות עירונית",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;700&display=swap');

    * { font-family: 'Heebo', sans-serif; direction: rtl; }
    .stApp { background: #0f1923; color: #e0e8f0; }
    .main .block-container { padding-top: 1.5rem; max-width: 1200px; }

    [data-testid="stSidebar"] {
        background: #111d2b;
        border-left: 2px solid #1B6B6B;
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stSlider label { color: #e8f4ff !important; font-size: 0.92rem; font-weight: 500; }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span { color: #ddeeff !important; }
    [data-testid="stSidebar"] input { color: #ffffff !important; background: #1a2d42 !important; }
    [data-testid="stSidebar"] .stMarkdown { color: #e8f4ff; }

    .score-card {
        background: linear-gradient(135deg, #1A3A5C 0%, #0d2035 100%);
        border: 1px solid #1B6B6B;
        border-radius: 12px;
        padding: 28px 32px;
        text-align: center;
        margin-bottom: 16px;
    }
    .score-number { font-size: 5rem; font-weight: 700; line-height: 1; }
    .score-label  { font-size: 1.1rem; color: #c8dff0; margin-top: 6px; font-weight: 500; }

    .verdict-feasible    { background: #1a4731; border: 1px solid #2E7D32; color: #a5d6a7;
                            border-radius: 8px; padding: 10px 20px; font-size: 1.2rem; font-weight: 700; }
    .verdict-infeasible  { background: #4a1515; border: 1px solid #c62828; color: #ffcdd2;
                            border-radius: 8px; padding: 10px 20px; font-size: 1.2rem; font-weight: 700; }

    .metric-tile {
        background: #111d2b;
        border: 1px solid #2a4a6a;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .metric-label { font-size: 0.85rem; color: #90b8d8; margin-bottom: 4px; font-weight: 500; }
    .metric-value { font-size: 1.4rem; font-weight: 700; color: #eaf4ff; }

    .shap-row { display: flex; align-items: center; margin-bottom: 6px; direction: rtl; }
    .shap-name { width: 220px; font-size: 0.85rem; color: #c8dff0; text-align: right; padding-left: 8px; font-weight: 500; }
    .shap-bar-wrap { flex: 1; height: 18px; background: #1e3a54; border-radius: 4px; overflow: hidden; }
    .shap-bar-pos { height: 100%; background: #2E7D32; }
    .shap-bar-neg { height: 100%; background: #c62828; margin-right: auto; }
    .shap-val { width: 70px; text-align: left; font-size: 0.85rem; color: #c8dff0; padding-right: 8px; font-weight: 600; }

    div[data-testid="stNumberInput"] input,
    div[data-testid="stSelectbox"] select { direction: ltr; }

    div[data-testid="stNumberInput"] input {
        color: #ffffff !important;
        background: #1a2d42 !important;
        border: 1px solid #2a4a6a !important;
        border-radius: 6px;
        font-size: 1rem;
        font-weight: 600;
    }

    p, span, div { color: inherit; }
    .stApp { color: #eaf4ff; }

    h1, h2, h3 { color: #eaf4ff; }
    h1 { font-size: 2rem !important; }

    .stButton > button {
        background: #1B6B6B; color: white; border: none;
        border-radius: 8px; font-size: 1rem; font-weight: 700;
        padding: 0.6rem 2rem; width: 100%;
    }
    .stButton > button:hover { background: #15857a; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_models():
    cls_path  = MODELS_DIR / "best_classifier.pkl"
    reg_path  = MODELS_DIR / "best_regressor.pkl"
    meta_path = MODELS_DIR / "model_meta.json"
    shap_path = MODELS_DIR / "shap_explainer.pkl"

    if not cls_path.exists():
        return None, None, None, None

    clf  = joblib.load(cls_path)
    reg  = joblib.load(reg_path)
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)
    shap_exp = joblib.load(shap_path) if shap_path.exists() else None
    return clf, reg, meta, shap_exp


clf, reg, meta, shap_exp = load_models()


def compute_derived(row: dict) -> dict:
    r = row.copy()
    r["יחס_דירות_חדש_לישן"]    = r["מספר_דירות_חדשות"] / max(r["מספר_דירות_קיימות"], 1)
    r["הכנסה_לדירה_קיימת"]     = (r['מחיר_מכירה_למ2_חדש_ש"ח'] * r["מספר_דירות_חדשות"] * r["שטח_ממוצע_חדש_מ2"]) / max(r["מספר_דירות_קיימות"], 1)
    r["עלות_לדירה_חדשה"]       = r['סה"כ_עלויות_ש"ח'] / max(r["מספר_דירות_חדשות"], 1)
    r["שטח_כולל_חדש_מ2"]       = r["מספר_דירות_חדשות"] * r["שטח_ממוצע_חדש_מ2"]
    r["מינוף_שטח"]             = r["שטח_כולל_חדש_מ2"] / max(r["מספר_דירות_קיימות"] * r["שטח_ממוצע_קיים_מ2"], 1)
    r["עלות_לקיים_יחסי"]       = r['עלות_בנייה_ש"ח'] / max(r["הכנסה_לדירה_קיימת"] * r["מספר_דירות_קיימות"], 1)
    return r

def predict_single(row_dict: dict):
    r = compute_derived(row_dict)
    num_cols = meta["num_cols"]
    cat_cols = meta["cat_cols"]
    df = pd.DataFrame([r])[num_cols + cat_cols]
    proba  = clf.predict_proba(df)[0][1]
    score  = float(np.clip(reg.predict(df)[0], 0, 100))
    is_feas = int(proba >= 0.5)

    shap_vals = None
    if shap_exp is not None:
        try:
            X_enc = clf.named_steps["prep"].transform(df)
            sv = shap_exp.shap_values(X_enc)
            if isinstance(sv, list):
                sv = sv[1]
            shap_vals = dict(zip(meta["feature_names_encoded"], sv[0].tolist()))
        except Exception:
            pass

    return proba, score, is_feas, shap_vals


st.markdown("# 🏗️ כלי בדיקת כדאיות — התחדשות עירונית")
st.markdown("#### הזן פרמטרים של פרויקט וקבל ניתוח כדאיות מיידי מבוסס ML")
st.divider()

if clf is None:
    st.error("⚠️ מודלים לא נמצאו. הרץ תחילה: `python models/train.py`")
    st.stop()

with st.sidebar:
    st.markdown("### 📋 פרמטרי הפרויקט")
    st.markdown("---")
    st.markdown("**📍 מיקום וסוג**")
    city     = st.selectbox("עיר", meta["cities"], index=0)
    proj_type = st.selectbox("סוג פרויקט", meta["project_types"], index=0)

    st.markdown("---")
    st.markdown("**🏢 מאפייני הבניין**")
    year_built     = st.number_input("שנת בניה",              1950, 1995, 1975, step=1)
    existing_units = st.number_input("מספר דירות קיימות",     6,    60,   16,   step=1)
    existing_sqm   = st.number_input("שטח דירות ממוצע (מ״ר)", 40,  150,   80,   step=5)
    floors         = st.number_input("מספר קומות",             2,    12,    4,   step=1)

    st.markdown("---")
    st.markdown("**🏗️ פרמטרי בנייה**")
    new_units       = st.number_input("תוספת דירות",                  2,   80,   12,    step=1)
    new_sqm         = st.number_input("שטח ממוצע לדירה חדשה (מ״ר)",  40,  150,   80,    step=5)
    cost_per_sqm    = st.number_input('עלות בניה למ"ר (₪)',          3000, 25000, 10000, step=500)
    st.caption("ב-38/2 ופינוי בינוי — עלות כוללת את כלל הדירות (קיימות + חדשות)")

    st.markdown("---")
    st.markdown("**💰 מחיר**")
    price_new = st.number_input('מחיר למ"ר לאחר בניה (₪)', 10000, 80000, 35000, step=1000)

    st.markdown("---")
    st.markdown("**⏱️ לוח זמנים**")
    signing_months   = st.number_input("חודשי ההחתמת דיירים",  3,  36, 12, step=1)
    permit_months    = st.number_input("חודשי היתר",           10,  40, 22, step=1)
    construct_months = st.number_input("חודשי בניה",           12,  48, 24, step=1)

    calc_btn = st.button("🔍 חשב כדאיות")

building_age  = 2024 - year_built
sales_months  = 12
price_old     = price_new * 0.82
irr           = 12.0
approval_pct  = 72.0
total_months  = signing_months + permit_months + construct_months + sales_months

is_full_rebuild   = ("38/2" in proj_type) or ("פינוי" in proj_type)
units_to_build    = (existing_units + new_units) if is_full_rebuild else new_units
construction_cost = units_to_build * new_sqm * cost_per_sqm
total_cost        = construction_cost + (6500 * existing_units * construct_months)
revenue           = new_units * new_sqm * price_new
gross_profit      = revenue - total_cost
gross_margin      = (gross_profit / revenue * 100) if revenue > 0 else 0.0

row_input = {
    "עיר": city,
    "סוג_פרויקט": proj_type,
    "גיל_בניין_שנים": building_age,
    "מספר_דירות_קיימות": existing_units,
    "שטח_ממוצע_קיים_מ2": existing_sqm,
    "מספר_קומות_קיים": floors,
    "מספר_דירות_חדשות": new_units,
    "שטח_ממוצע_חדש_מ2": new_sqm,
    'מחיר_מכירה_למ2_קיים_ש"ח': price_old,
    'מחיר_מכירה_למ2_חדש_ש"ח': price_new,
    'מרווח_גולמי_%': gross_margin,
    'IRR_משוער_%': irr,
    "חודשי_היתר": permit_months,
    "חודשי_בנייה": construct_months,
    "חודשי_מכירות": sales_months,
    "חודשי_החתמה": signing_months,
    "משך_כולל_פרויקט_חודשים": total_months,
    'הסתברות_אישור_%': approval_pct,
    'עלות_למ2_בנייה_ש"ח': cost_per_sqm,
    'הכנסות_ממכירת_דירות_ש"ח': revenue,
    'עלות_בנייה_ש"ח': construction_cost,
    'סה"כ_עלויות_ש"ח': total_cost,
}

if calc_btn:
    with st.spinner("מחשב..."):
        proba, score, is_feas, shap_vals = predict_single(row_input)

    col1, col2, col3 = st.columns([1.4, 1, 1])

    with col1:
        color = "#66BB6A" if is_feas else "#ef9a9a"
        st.markdown(f"""
        <div class="score-card">
            <div class="score-number" style="color:{color}">{score:.0f}</div>
            <div class="score-label">ציון כדאיות (0–100)</div>
            <br>
            <div class="{'verdict-feasible' if is_feas else 'verdict-infeasible'}">
                {'✅ הפרויקט כדאי' if is_feas else '❌ הפרויקט אינו כדאי'}
            </div>
            <br>
            <div style="color:#a0b8cc;font-size:0.9rem">הסתברות כדאיות: {proba*100:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("**סיכום כלכלי**")
        metrics = [
            ("הכנסות צפויות", f"₪{revenue:,.0f}"),
            ("עלויות כוללות",  f"₪{total_cost:,.0f}"),
            ("רווח גולמי",     f"₪{gross_profit:,.0f}"),
            ("מרווח",          f"{gross_margin:.1f}%"),
            ("IRR",             f"{irr:.1f}%"),
        ]
        for label, val in metrics:
            profit_color = "#66BB6A" if gross_profit > 0 and label == "רווח גולמי" else "#d0e8f8"
            st.markdown(f"""
            <div class="metric-tile">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{profit_color}">{val}</div>
            </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown("**פרמטרי פרויקט**")
        params = [
            ("סוג", proj_type),
            ("עיר", city),
            ("גיל בניין", f"{building_age} שנים"),
            ("דירות: קיים → חדש", f"{existing_units} → {new_units}"),
            ("החתמה / היתר / בניה", f"{signing_months} / {permit_months} / {construct_months} חודשים"),
            ("משך כולל", f"{total_months} חודשים"),
        ]
        for label, val in params:
            st.markdown(f"""
            <div class="metric-tile">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="font-size:1.1rem">{val}</div>
            </div>""", unsafe_allow_html=True)

    st.divider()
    if shap_vals:
        st.markdown("### 🔍 גורמים משפיעים על ההחלטה (SHAP)")
        sorted_shap = sorted(shap_vals.items(), key=lambda x: abs(x[1]), reverse=True)[:12]
        max_abs = max(abs(v) for _, v in sorted_shap) or 1

        shap_html = '<div style="direction:rtl">'
        for name, val in sorted_shap:
            pct = abs(val) / max_abs * 100
            color = "#2E7D32" if val > 0 else "#c62828"
            direction = "חיובי ↑" if val > 0 else "שלילי ↓"
            display_name = name.split("_")[0] if len(name) > 20 else name
            shap_html += f"""
            <div class="shap-row">
                <div class="shap-name">{display_name}</div>
                <div class="shap-bar-wrap">
                    <div style="height:100%;width:{pct:.1f}%;background:{color};border-radius:3px"></div>
                </div>
                <div class="shap-val" style="color:{color}">{direction}</div>
            </div>"""
        shap_html += "</div>"
        st.markdown(shap_html, unsafe_allow_html=True)
        st.caption("עמודות ירוקות = משפיעות לחיוב על הכדאיות | אדומות = משפיעות לשלילה")
    else:
        st.info("SHAP לא זמין — הרץ training עם מודל עץ (RandomForest/XGBoost) כדי לאפשר הסברים.")

    st.divider()
    st.markdown("### 📊 ניתוח רגישות — מה קורה אם...")
    def _sens_margin(cost_factor):
        c2 = construction_cost * cost_factor
        t2 = c2 + (6500 * existing_units * construct_months)
        return (revenue - t2) / revenue * 100 if revenue > 0 else 0.0

    deltas = {
        "מחיר מכירה +10%":  {"מחיר_מכירה_למ2_חדש_ש\"ח": price_new * 1.10},
        "מחיר מכירה -10%":  {"מחיר_מכירה_למ2_חדש_ש\"ח": price_new * 0.90},
        "עלות בניה +15%":   {"מרווח_גולמי_%": _sens_margin(1.15), 'עלות_בנייה_ש"ח': construction_cost * 1.15},
        "עלות בניה -15%":   {"מרווח_גולמי_%": _sens_margin(0.85), 'עלות_בנייה_ש"ח': construction_cost * 0.85},
        "עיכוב 6 חודשים":   {"חודשי_בנייה": construct_months + 6, "משך_כולל_פרויקט_חודשים": total_months + 6},
    }
    base_row = row_input.copy()
    sens_results = []
    for scenario, overrides in deltas.items():
        r2 = {**base_row, **overrides}
        _, s2, f2, _ = predict_single(r2)
        delta_score = s2 - score
        sens_results.append((scenario, s2, delta_score, f2))

    cols = st.columns(len(sens_results))
    for col, (scenario, s2, delta_score, f2) in zip(cols, sens_results):
        arrow    = "▲" if delta_score > 0 else ("▼" if delta_score < 0 else "–")
        d_color  = "#66BB6A" if delta_score > 0 else ("#ef9a9a" if delta_score < 0 else "#a0b8cc")
        verdict  = "✅ כדאי" if f2 else "❌ לא כדאי"
        v_color  = "#66BB6A" if f2 else "#ef9a9a"
        v_bg     = "#1a4731" if f2 else "#4a1515"
        col.markdown(f"""
        <div style="background:#111d2b;border:1px solid #2a4a6a;border-radius:10px;
                    padding:14px 12px;text-align:center;height:100%">
            <div style="font-size:0.82rem;color:#90b8d8;margin-bottom:8px;
                        font-weight:600;min-height:36px">{scenario}</div>
            <div style="font-size:2.4rem;font-weight:700;color:#eaf4ff;line-height:1">{s2:.0f}</div>
            <div style="font-size:1rem;color:{d_color};font-weight:700;margin:4px 0">
                {arrow} {abs(delta_score):.1f} נקודות</div>
            <div style="background:{v_bg};color:{v_color};border-radius:6px;
                        padding:4px 8px;font-size:0.85rem;font-weight:700;margin-top:8px">
                {verdict}</div>
        </div>
        """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align:center; padding: 60px 20px; color: #5a7a90">
        <div style="font-size:4rem">🏗️</div>
        <h2 style="color:#7a9ab0">מלא את הפרמטרים בסרגל הצד ולחץ "חשב כדאיות"</h2>
        <p>הכלי מנתח פרויקטי תמ״א 38/1, תמ״א 38/2 ופינוי-בינוי<br>
        ומחזיר ציון כדאיות, הסתברות, SHAP ותרחישי רגישות</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("ℹ️ אודות הכלי"):
        st.markdown("""
        **Urban Renewal Feasibility Scoring Tool**

        הכלי מבוסס על מודל ML שאומן על 500 עסקאות התחדשות עירונית סינתטיות
        המדמות את השוק הישראלי.

        **מודלים**: RandomForest · XGBoost · GradientBoosting · LogisticRegression

        **תוצאות**: ציון כדאיות (0–100) · סיווג בינארי · הסברי SHAP · ניתוח רגישות

        **מקורות נתונים**: מחירי שוק ממדלן/יד2, עלויות בנייה ממינהל הבנייה,
        לוחות זמנים מהרשות להתחדשות עירונית.
        """)
