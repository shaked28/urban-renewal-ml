import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_PATH = ROOT / "data" / "urban_renewal_dataset.xlsx"
MODELS_DIR = ROOT / "models"
OUT_DIR = ROOT / "docs" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["figure.facecolor"] = "#0f1923"
plt.rcParams["axes.facecolor"]   = "#111d2b"
plt.rcParams["axes.edgecolor"]   = "#1e3a54"
plt.rcParams["text.color"]       = "#d0e8f8"
plt.rcParams["axes.labelcolor"]  = "#a0b8cc"
plt.rcParams["xtick.color"]      = "#a0b8cc"
plt.rcParams["ytick.color"]      = "#a0b8cc"
plt.rcParams["grid.color"]       = "#1e3a54"
TEAL  = "#1B6B6B"
GREEN = "#2E7D32"
RED   = "#c62828"
BLUE  = "#1A3A5C"

print("Loading data...")
df = pd.read_excel(DATA_PATH, sheet_name="Dataset")

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
fig.patch.set_facecolor("#0f1923")

counts = df["כדאי_1_לא_0"].value_counts()
axes[0].bar(["Not Feasible (0)", "Feasible (1)"],
            [counts.get(0,0), counts.get(1,0)],
            color=[RED, GREEN], edgecolor="#0f1923", linewidth=2)
axes[0].set_title("Target Distribution — Binary Label", fontsize=13, pad=12)
axes[0].set_ylabel("Count")
for bar in axes[0].patches:
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 4,
                 f"{int(bar.get_height())}", ha="center", fontsize=11, color="#d0e8f8")

axes[1].hist(df["ציון_כדאיות_0_100"], bins=25, color=TEAL, edgecolor="#0f1923")
axes[1].set_title("Feasibility Score Distribution (0–100)", fontsize=13, pad=12)
axes[1].set_xlabel("Score")
axes[1].set_ylabel("Count")
axes[1].axvline(55, color=RED, linestyle="--", linewidth=1.5, label="Threshold=55")
axes[1].legend()

plt.tight_layout(pad=2)
plt.savefig(OUT_DIR / "01_target_distribution.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✓ 01_target_distribution.png")

city_stats = df.groupby("עיר")["כדאי_1_לא_0"].agg(["mean","count"]).reset_index()
city_stats.columns = ["city", "feas_rate", "count"]
city_stats = city_stats.sort_values("feas_rate", ascending=True)

fig, ax = plt.subplots(figsize=(10, 7))
fig.patch.set_facecolor("#0f1923")
colors = [GREEN if r >= 0.55 else RED for r in city_stats["feas_rate"]]
bars = ax.barh(city_stats["city"], city_stats["feas_rate"] * 100,
               color=colors, edgecolor="#0f1923", height=0.7)
ax.set_xlabel("Feasibility Rate (%)")
ax.set_title("Feasibility Rate by City", fontsize=14, pad=12)
ax.axvline(55, color="#aaaaaa", linestyle="--", linewidth=1, alpha=0.6)
for bar, rate in zip(bars, city_stats["feas_rate"]):
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
            f"{rate*100:.0f}%", va="center", fontsize=9, color="#d0e8f8")
plt.tight_layout()
plt.savefig(OUT_DIR / "02_feasibility_by_city.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✓ 02_feasibility_by_city.png")

num_features = [
    "גיל_בניין_שנים", "מספר_דירות_קיימות", "שטח_ממוצע_קיים_מ2",
    "מספר_דירות_חדשות", 'מרווח_גולמי_%', 'IRR_משוער_%',
    "חודשי_היתר", "משך_כולל_פרויקט_חודשים", 'הסתברות_אישור_%',
    "ציון_כדאיות_0_100", "כדאי_1_לא_0"
]
corr = df[num_features].corr()

fig, ax = plt.subplots(figsize=(11, 9))
fig.patch.set_facecolor("#0f1923")
mask = np.zeros_like(corr, dtype=bool)
mask[np.triu_indices_from(mask)] = True
sns.heatmap(corr, mask=mask, ax=ax, annot=True, fmt=".2f", cmap="RdYlGn",
            center=0, linewidths=0.5, linecolor="#0f1923",
            annot_kws={"size": 8}, cbar_kws={"shrink": 0.8})
ax.set_title("Feature Correlation Matrix", fontsize=14, pad=12)
plt.xticks(rotation=45, ha="right", fontsize=8)
plt.yticks(fontsize=8)
plt.tight_layout()
plt.savefig(OUT_DIR / "03_correlation_heatmap.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✓ 03_correlation_heatmap.png")

fig, ax = plt.subplots(figsize=(9, 6))
fig.patch.set_facecolor("#0f1923")
colors = [GREEN if f == 1 else RED for f in df["כדאי_1_לא_0"]]
ax.scatter(df['מרווח_גולמי_%'], df["ציון_כדאיות_0_100"],
           c=colors, alpha=0.5, s=18, edgecolors="none")
ax.set_xlabel("Gross Margin (%)")
ax.set_ylabel("Feasibility Score")
ax.set_title("Score vs Gross Margin", fontsize=14, pad=12)
ax.axhline(55, color="#aaaaaa", linestyle="--", linewidth=1, alpha=0.7)
p1 = mpatches.Patch(color=GREEN, label="Feasible")
p2 = mpatches.Patch(color=RED,   label="Not Feasible")
ax.legend(handles=[p1, p2])
plt.tight_layout()
plt.savefig(OUT_DIR / "04_score_vs_margin.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✓ 04_score_vs_margin.png")

proj_stats = df.groupby("סוג_פרויקט").agg(
    feas_rate=("כדאי_1_לא_0", "mean"),
    avg_score=("ציון_כדאיות_0_100", "mean"),
    avg_margin=('מרווח_גולמי_%', "mean"),
    count=("מזהה_עסקה", "count")
).reset_index()

fig, axes = plt.subplots(1, 3, figsize=(13, 5))
fig.patch.set_facecolor("#0f1923")
fig.suptitle("Project Type Analysis", fontsize=14, y=1.02)

metrics = [("feas_rate", "Feasibility Rate", lambda x: f"{x*100:.0f}%"),
           ("avg_score", "Avg Feasibility Score", lambda x: f"{x:.1f}"),
           ("avg_margin", "Avg Gross Margin (%)", lambda x: f"{x:.1f}%")]

for ax, (col, title, fmt) in zip(axes, metrics):
    bars = ax.bar(proj_stats["סוג_פרויקט"], proj_stats[col],
                  color=[TEAL, "#1a6b3a", "#1a3a6b"], edgecolor="#0f1923")
    ax.set_title(title, fontsize=11)
    ax.set_xticklabels(proj_stats["סוג_פרויקט"], rotation=15, ha="right", fontsize=8)
    for bar, val in zip(bars, proj_stats[col]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                fmt(val), ha="center", fontsize=9, color="#d0e8f8")

plt.tight_layout()
plt.savefig(OUT_DIR / "05_project_type_analysis.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✓ 05_project_type_analysis.png")

meta_path = MODELS_DIR / "model_meta.json"
if meta_path.exists():
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)
    print("\n── Model Results ──────────────────────────")
    for k, v in meta.get("results", {}).items():
        print(f"  {k:35s}: {v}")
    print(f"\n  Best classifier : {meta['best_classifier']} (AUC={meta['best_classifier_auc']:.4f})")
    print(f"  Best regressor  : {meta['best_regressor']} (RMSE={meta['best_regressor_rmse']:.3f})")

print(f"\n✓ All figures saved to {OUT_DIR}")
print("  Run: streamlit run app/main.py")
