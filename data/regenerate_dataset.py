import pandas as pd
import numpy as np
from pathlib import Path

np.random.seed(42)

DATA_PATH = Path(__file__).parent / "urban_renewal_dataset.xlsx"

df = pd.read_excel(DATA_PATH, sheet_name="Dataset")
print(f"Loaded dataset: {len(df)} rows, {len(df.columns)} columns")
print(f"Original class balance: {df['כדאי_1_לא_0'].mean():.1%} positive")

is_full_rebuild = df["סוג_פרויקט"].str.contains("38/2|פינוי", regex=True)
units_to_build = np.where(
    is_full_rebuild,
    df["מספר_דירות_קיימות"] + df["מספר_דירות_חדשות"],
    df["מספר_דירות_חדשות"],
)

base_cost_per_sqm = df['עלות_בנייה_ש"ח'] / (units_to_build * df["שטח_ממוצע_חדש_מ2"])
noise = np.random.normal(1.0, 0.02, len(df))
cost_per_sqm = (base_cost_per_sqm * noise).round(0).clip(3000, 25000).astype(int)
df['עלות_למ2_בנייה_ש"ח'] = cost_per_sqm

def gen_signing_months(row):
    ptype = row["סוג_פרויקט"]
    n = row["מספר_דירות_קיימות"]
    rng = np.random.RandomState(int(row.name) + 1000)
    if "38/1" in ptype:
        base = 6 + (n // 12)
    elif "38/2" in ptype:
        base = 10 + (n // 10)
    else:
        base = 14 + (n // 8)
    val = int(base + rng.randint(-2, 3))
    return max(6, min(36, val))

df["חודשי_החתמה"] = df.apply(gen_signing_months, axis=1)

new_construction_cost = (units_to_build * df["שטח_ממוצע_חדש_מ2"] * df['עלות_למ2_בנייה_ש"ח']).round(0).astype(int)
df['עלות_בנייה_ש"ח'] = new_construction_cost

new_tenant_comp = np.where(
    is_full_rebuild,
    (6500 * df["מספר_דירות_קיימות"] * df["חודשי_בנייה"]).round(0).astype(int),
    0,
)
df['פיצוי_שוכרים_ש"ח'] = new_tenant_comp

df['סה"כ_עלויות_ש"ח'] = (
    df['עלות_בנייה_ש"ח']
    + df['עלות_חיזוק_ש"ח']
    + df['עלות_משפטית_ותכנונית_ש"ח']
    + df['עלות_מימון_ש"ח']
    + df['עלות_שיווק_ש"ח']
    + df['רזרבה_בלתמ"ים_ש"ח']
    + df['פיצוי_שוכרים_ש"ח']
).round(0).astype(int)

revenue = df["מספר_דירות_חדשות"] * df["שטח_ממוצע_חדש_מ2"] * df['מחיר_מכירה_למ2_חדש_ש"ח']
df['הכנסות_ממכירת_דירות_ש"ח'] = revenue.round(0).astype(int)

gross_profit = revenue - df['סה"כ_עלויות_ש"ח']
df['רווח_גולמי_ש"ח'] = gross_profit.round(0).astype(int)
df['מרווח_גולמי_%'] = (gross_profit / revenue.clip(lower=1) * 100).round(1)

df["משך_כולל_פרויקט_חודשים"] = (
    df["חודשי_החתמה"] + df["חודשי_היתר"] + df["חודשי_בנייה"] + df["חודשי_מכירות"]
)
years = df["משך_כולל_פרויקט_חודשים"] / 12
irr_raw = df['מרווח_גולמי_%'] / years + np.random.normal(0, 1.5, len(df))
df['IRR_משוער_%'] = irr_raw.round(1)

margin_capped = df['מרווח_גולמי_%'].clip(-50, 80)
approval = df['הסתברות_אישור_%']
score_base = 38 + 0.6 * margin_capped + 0.15 * approval
score_noisy = score_base + np.random.normal(0, 4.0, len(df))
df['ציון_כדאיות_0_100'] = score_noisy.clip(0, 100).round(1)

threshold = 55
df['כדאי_1_לא_0'] = (df['ציון_כדאיות_0_100'] >= threshold).astype(int)

actual_positive = df['כדאי_1_לא_0'].mean()
print(f"Score threshold: {threshold:.1f}")
print(f"New class balance: {actual_positive:.1%} positive")

all_cols = list(df.columns)
for c in ['חודשי_החתמה', 'עלות_למ2_בנייה_ש"ח']:
    if c in all_cols:
        all_cols.remove(c)

idx_cost = all_cols.index('עלות_בנייה_ש"ח')
all_cols.insert(idx_cost + 1, 'עלות_למ2_בנייה_ש"ח')
idx_months = all_cols.index('חודשי_מכירות')
all_cols.insert(idx_months + 1, 'חודשי_החתמה')
df = df[all_cols]

df.to_excel(DATA_PATH, sheet_name="Dataset", index=False)
print(f"\nDataset saved: {len(df)} rows, {len(df.columns)} columns")
print(f"Columns: {list(df.columns)}")
print("\nSample row:")
print(df.iloc[0][['מרווח_גולמי_%','IRR_משוער_%','ציון_כדאיות_0_100','כדאי_1_לא_0','חודשי_החתמה','עלות_למ2_בנייה_ש"ח']])
