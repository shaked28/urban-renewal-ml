const pptxgen = require("pptxgenjs");
const path = require("path");
const fs = require("fs");

// ── Paths ─────────────────────────────────────────────────────
const ROOT = path.join(__dirname, "..");
const FIGS = path.join(ROOT, "docs", "figures");
const OUT  = path.join(__dirname, "final_presentation.pptx");

// ── Palette — Dark Navy / Teal ────────────────────────────────
const C = {
  bg:      "0f1923",
  surface: "111d2b",
  navy:    "1A3A5C",
  teal:    "1B6B6B",
  tealLt:  "2a9d8f",
  green:   "2E7D32",
  greenLt: "4CAF50",
  red:     "C62828",
  text:    "D0E8F8",
  muted:   "7A9AB0",
  white:   "FFFFFF",
  accent:  "64B5F6",
};

function imgPath(name) {
  return path.join(FIGS, name);
}

// ────────────────────────────────────────────────────────────────
let pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "Shaked Akrish";
pres.title  = "Urban Renewal Feasibility ML";

// ══════════════════════════════════════════════════════════════
// Slide 1 — Title
// ══════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.bg };

  // Teal accent bar left
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.12, h: 5.625, fill: { color: C.teal } });

  // Decorative circle top-right
  s.addShape(pres.shapes.OVAL, {
    x: 8.2, y: -0.8, w: 3.5, h: 3.5,
    fill: { color: C.teal, transparency: 85 },
    line: { color: C.teal, width: 1 }
  });

  // Main title
  s.addText("כלי בדיקת כדאיות", {
    x: 0.4, y: 0.7, w: 9.2, h: 0.9,
    fontSize: 40, fontFace: "Calibri", bold: true,
    color: C.white, align: "right", rtlMode: true
  });
  s.addText("התחדשות עירונית — ML", {
    x: 0.4, y: 1.5, w: 9.2, h: 0.9,
    fontSize: 40, fontFace: "Calibri", bold: true,
    color: C.accent, align: "right", rtlMode: true
  });
  s.addText("Urban Renewal Feasibility Scoring Tool", {
    x: 0.4, y: 2.4, w: 9.2, h: 0.45,
    fontSize: 16, fontFace: "Calibri",
    color: C.muted, align: "right"
  });

  // Divider line
  s.addShape(pres.shapes.LINE, {
    x: 0.4, y: 3.0, w: 9.2, h: 0,
    line: { color: C.teal, width: 1.5 }
  });

  // Meta info
  s.addText([
    { text: "שקד עקריש", options: { bold: true, color: C.text } },
    { text: "   |   מנחה: ד\"ר איל זינגר", options: { color: C.muted } },
  ], { x: 0.4, y: 3.15, w: 9.2, h: 0.4, fontSize: 14, fontFace: "Calibri", align: "right", rtlMode: true });

  s.addText([
    { text: "קורס פרויקט מעשי בלמידת מכונה  ·  סמסטר קיץ תשפ\"ה", options: { color: C.muted } }
  ], { x: 0.4, y: 3.5, w: 9.2, h: 0.35, fontSize: 12, fontFace: "Calibri", align: "right", rtlMode: true });

  // Badges
  const badges = ["Python", "scikit-learn", "XGBoost", "Streamlit", "SHAP", "500 עסקאות"];
  badges.forEach((b, i) => {
    const bx = 0.4 + i * 1.55;
    s.addShape(pres.shapes.RECTANGLE, {
      x: bx, y: 4.3, w: 1.45, h: 0.38,
      fill: { color: C.navy }, line: { color: C.teal, width: 0.8 }
    });
    s.addText(b, {
      x: bx, y: 4.3, w: 1.45, h: 0.38,
      fontSize: 10, fontFace: "Calibri", color: C.accent, align: "center", valign: "middle"
    });
  });
}

// ══════════════════════════════════════════════════════════════
// Slide 2 — הבעיה
// ══════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.bg };

  // Header bar
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.85, fill: { color: C.navy } });
  s.addText("הבעיה", {
    x: 0.3, y: 0.08, w: 9.4, h: 0.68,
    fontSize: 28, fontFace: "Calibri", bold: true,
    color: C.white, align: "right", rtlMode: true
  });

  // Stat cards
  const stats = [
    { val: "1,800+", label: "פרויקטים פעילים\nבישראל", color: C.teal },
    { val: "< 30%", label: "מגיעים לביצוע\nבפועל", color: C.red },
    { val: "חודשים", label: "זמן בדיקה ידנית\nממוצע", color: C.teal },
    { val: "אין", label: "כלי סינון\nשיטתי", color: C.red },
  ];
  stats.forEach((st, i) => {
    const cx = 0.35 + i * 2.35;
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: 1.0, w: 2.2, h: 1.8,
      fill: { color: C.surface }, line: { color: st.color, width: 1.5 }
    });
    s.addText(st.val, {
      x: cx, y: 1.05, w: 2.2, h: 0.9,
      fontSize: 34, fontFace: "Calibri", bold: true,
      color: st.color, align: "center", valign: "middle"
    });
    s.addText(st.label, {
      x: cx, y: 1.9, w: 2.2, h: 0.85,
      fontSize: 12, fontFace: "Calibri", color: C.muted,
      align: "center", valign: "top"
    });
  });

  // Problem text
  const problems = [
    "בדיקות כדאיות מסורתיות הן ידניות, זמן-רבות ואינן ניתנות להשוואה",
    "שמאים אינם יכולים לסרוק מאות פרויקטים ביעילות",
    "היעדר סטנדרטיזציה מוביל להחלטות סובייקטיביות",
    "משאבי תכנון יקרים מבוזבזים על פרויקטים שנידונים מראש לכישלון"
  ];
  problems.forEach((p, i) => {
    s.addShape(pres.shapes.OVAL, {
      x: 0.38, y: 3.08 + i * 0.52, w: 0.22, h: 0.22,
      fill: { color: C.teal }
    });
    s.addText(p, {
      x: 0.7, y: 3.0 + i * 0.52, w: 8.9, h: 0.42,
      fontSize: 14, fontFace: "Calibri", color: C.text,
      align: "right", rtlMode: true
    });
  });
}

// ══════════════════════════════════════════════════════════════
// Slide 3 — הפתרון + ארכיטקטורה
// ══════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.bg };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.85, fill: { color: C.navy } });
  s.addText("הפתרון — מערכת מלאה מקצה לקצה", {
    x: 0.3, y: 0.08, w: 9.4, h: 0.68,
    fontSize: 26, fontFace: "Calibri", bold: true,
    color: C.white, align: "right", rtlMode: true
  });

  // Architecture pipeline
  const steps = [
    { icon: "📂", title: "Data", sub: "500 עסקאות\n33 שדות" },
    { icon: "⚙️", title: "Feature Eng.", sub: "+6 פיצ'רים\nמחושבים" },
    { icon: "🔄", title: "Preprocessing", sub: "Scaler +\nOneHotEncoder" },
    { icon: "🤖", title: "ML Pipeline", sub: "4 מודלים\n× Classification + Reg" },
    { icon: "🏆", title: "בחירה אוטומטית", sub: "AUC / RMSE\nבאופן אוטומטי" },
    { icon: "📊", title: "Streamlit UI", sub: "SHAP +\nSensitivity" },
  ];

  steps.forEach((st, i) => {
    const cx = 0.3 + i * 1.6;
    // Card
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: 1.1, w: 1.45, h: 2.4,
      fill: { color: C.surface }, line: { color: C.teal, width: 1 }
    });
    // Teal top accent
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: 1.1, w: 1.45, h: 0.06,
      fill: { color: C.teal }
    });
    s.addText(st.icon, {
      x: cx, y: 1.2, w: 1.45, h: 0.55,
      fontSize: 26, align: "center", valign: "middle"
    });
    s.addText(st.title, {
      x: cx, y: 1.75, w: 1.45, h: 0.45,
      fontSize: 11, fontFace: "Calibri", bold: true,
      color: C.accent, align: "center"
    });
    s.addText(st.sub, {
      x: cx, y: 2.2, w: 1.45, h: 1.15,
      fontSize: 9.5, fontFace: "Calibri", color: C.muted,
      align: "center"
    });
    // Arrow between steps
    if (i < steps.length - 1) {
      s.addShape(pres.shapes.LINE, {
        x: cx + 1.45, y: 2.3, w: 0.15, h: 0,
        line: { color: C.teal, width: 1.5 }
      });
    }
  });

  // Key features row
  const features = [
    { label: "ציון 0–100 רציף", icon: "🎯" },
    { label: "סיווג בינארי", icon: "✅" },
    { label: "SHAP Explainability", icon: "🔍" },
    { label: "ניתוח רגישות — 6 תרחישים", icon: "📈" },
    { label: "ממשק בעברית (RTL)", icon: "🇮🇱" },
  ];
  features.forEach((f, i) => {
    s.addText(`${f.icon}  ${f.label}`, {
      x: 0.2 + i * 1.95, y: 4.6, w: 1.85, h: 0.55,
      fontSize: 11, fontFace: "Calibri", color: C.text,
      align: "center",
      fill: { color: C.navy }
    });
  });
}

// ══════════════════════════════════════════════════════════════
// Slide 4 — נתונים ו-Features
// ══════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.bg };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.85, fill: { color: C.navy } });
  s.addText("נתונים ו-Feature Engineering", {
    x: 0.3, y: 0.08, w: 9.4, h: 0.68,
    fontSize: 26, fontFace: "Calibri", bold: true,
    color: C.white, align: "right", rtlMode: true
  });

  // Left column — Dataset info
  s.addText("ה-Dataset", {
    x: 5.2, y: 1.1, w: 4.5, h: 0.45,
    fontSize: 16, fontFace: "Calibri", bold: true,
    color: C.accent, align: "right", rtlMode: true
  });
  const dsInfo = [
    "500 עסקאות סינתטיות (שוק ישראלי)",
    "33 שדות מחולקים ל-4 קטגוריות",
    "כוילו לפי נתוני מדלן/יד2",
    "עלויות ממינהל הבנייה",
    "חוסר איזון במחלקות — 80% כדאי",
  ];
  dsInfo.forEach((item, i) => {
    s.addShape(pres.shapes.OVAL, {
      x: 9.4, y: 1.65 + i * 0.46, w: 0.18, h: 0.18,
      fill: { color: C.teal }
    });
    s.addText(item, {
      x: 5.2, y: 1.58 + i * 0.46, w: 4.1, h: 0.4,
      fontSize: 12, fontFace: "Calibri", color: C.text,
      align: "right", rtlMode: true
    });
  });

  // Right column — Feature engineering
  s.addText("Feature Engineering", {
    x: 0.3, y: 1.1, w: 4.5, h: 0.45,
    fontSize: 16, fontFace: "Calibri", bold: true,
    color: C.accent, align: "left"
  });
  const features = [
    ["יחס דירות חדש/ישן", "new / existing"],
    ["הכנסה לדירה קיימת", "revenue / units"],
    ["עלות לדירה חדשה", "cost / new_units"],
    ["שטח כולל חדש מ²", "units × sqm"],
    ["מינוף שטח", "new_area / old_area"],
    ["עלות לקיים יחסי", "cost / revenue"],
    ["עלות למ² בנייה", "cost_per_sqm (₪/m²)"],
    ["חודשי החתמה", "signing_months"],
  ];
  features.forEach(([heb, eng], i) => {
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.3, y: 1.6 + i * 0.4, w: 4.5, h: 0.36,
      fill: { color: C.surface }, line: { color: C.border || "1e3a54", width: 0.5 }
    });
    s.addText(heb, {
      x: 2.6, y: 1.61 + i * 0.4, w: 2.15, h: 0.34,
      fontSize: 11, fontFace: "Calibri", color: C.text, align: "right"
    });
    s.addText(eng, {
      x: 0.35, y: 1.61 + i * 0.4, w: 2.2, h: 0.34,
      fontSize: 9.5, fontFace: "Calibri", color: C.muted, align: "left"
    });
  });

  // Divider
  s.addShape(pres.shapes.LINE, {
    x: 4.95, y: 1.0, w: 0, h: 4.4,
    line: { color: C.teal, width: 0.75 }
  });

  // Bottom note
  s.addText("הוספת הפיצ'רים המחושבים שיפרה את ה-AUC ב-0.04 בממוצע · class_weight='balanced' לטיפול בחוסר האיזון", {
    x: 0.3, y: 5.05, w: 9.4, h: 0.38,
    fontSize: 11, fontFace: "Calibri", color: C.muted, align: "center",
    italic: true
  });
}

// ══════════════════════════════════════════════════════════════
// Slide 5 — תוצאות מודלים
// ══════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.bg };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.85, fill: { color: C.navy } });
  s.addText("תוצאות המודלים", {
    x: 0.3, y: 0.08, w: 9.4, h: 0.68,
    fontSize: 28, fontFace: "Calibri", bold: true,
    color: C.white, align: "right", rtlMode: true
  });

  // KPI row
  const kpis = [
    { val: "0.991", sub: "AUC-ROC", label: "Classification" },
    { val: "4.250", sub: "RMSE", label: "Regression" },
    { val: "0.918", sub: "R²", label: "Ridge Reg" },
    { val: "6/6", sub: "Tests", label: "Pytest pass" },
  ];
  kpis.forEach((k, i) => {
    const cx = 0.3 + i * 2.35;
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: 0.95, w: 2.2, h: 1.25,
      fill: { color: C.surface }, line: { color: C.teal, width: 1 }
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: 0.95, w: 2.2, h: 0.06,
      fill: { color: C.teal }
    });
    s.addText(k.val, {
      x: cx, y: 0.98, w: 2.2, h: 0.65,
      fontSize: 28, fontFace: "Calibri", bold: true,
      color: C.greenLt, align: "center", valign: "middle"
    });
    s.addText(k.sub, {
      x: cx, y: 1.62, w: 2.2, h: 0.3,
      fontSize: 12, fontFace: "Calibri", color: C.accent, align: "center"
    });
    s.addText(k.label, {
      x: cx, y: 1.9, w: 2.2, h: 0.28,
      fontSize: 10, fontFace: "Calibri", color: C.muted, align: "center"
    });
  });

  // Classification table
  s.addText("Classification", {
    x: 5.2, y: 2.45, w: 4.5, h: 0.4,
    fontSize: 14, fontFace: "Calibri", bold: true, color: C.accent, align: "right"
  });
  const clsData = [
    [{ text: "מודל", options: { bold: true, color: C.accent } },
     { text: "AUC", options: { bold: true, color: C.accent } },
     { text: "CV-AUC", options: { bold: true, color: C.accent } }],
    ["רגרסיה לוגיסטית ★", "0.9913", "0.9889"],
    ["Random Forest", "0.9863", "0.9904"],
    ["XGBoost", "0.9881", "0.9837"],
    ["Gradient Boost", "0.9612", "0.9627"],
  ];
  s.addTable(clsData, {
    x: 5.2, y: 2.85, w: 4.5,
    fontSize: 11, fontFace: "Calibri",
    border: { pt: 0.5, color: "1e3a54" },
    fill: { color: C.surface },
    color: C.text,
    colW: [2.5, 1.0, 1.0]
  });

  // Regression table
  s.addText("Regression", {
    x: 0.3, y: 2.45, w: 4.5, h: 0.4,
    fontSize: 14, fontFace: "Calibri", bold: true, color: C.accent, align: "left"
  });
  const regData = [
    [{ text: "מודל", options: { bold: true, color: C.accent } },
     { text: "RMSE", options: { bold: true, color: C.accent } },
     { text: "R²", options: { bold: true, color: C.accent } }],
    ["Ridge (L2) ★", "4.250", "0.918"],
    ["Random Forest", "4.614", "0.903"],
    ["Gradient Boost", "4.705", "0.899"],
    ["XGBoost Reg", "4.757", "0.897"],
  ];
  s.addTable(regData, {
    x: 0.3, y: 2.85, w: 4.5,
    fontSize: 11, fontFace: "Calibri",
    border: { pt: 0.5, color: "1e3a54" },
    fill: { color: C.surface },
    color: C.text,
    colW: [2.5, 1.0, 1.0]
  });

  // EDA chart
  if (fs.existsSync(imgPath("01_target_distribution.png"))) {
    s.addImage({ path: imgPath("01_target_distribution.png"), x: 0.3, y: 4.3, w: 9.4, h: 1.1 });
  }
}

// ══════════════════════════════════════════════════════════════
// Slide 6 — Demo Screenshots
// ══════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.bg };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.85, fill: { color: C.navy } });
  s.addText("Demo — אפליקציית Streamlit", {
    x: 0.3, y: 0.08, w: 9.4, h: 0.68,
    fontSize: 26, fontFace: "Calibri", bold: true,
    color: C.white, align: "right", rtlMode: true
  });

  // 2 charts
  const imgs = [
    { file: "04_score_vs_margin.png", cap: "ציון כדאיות לעומת מרווח גולמי" },
    { file: "02_feasibility_by_city.png", cap: "שיעור כדאיות לפי עיר" },
  ];
  imgs.forEach((img, i) => {
    const cx = 0.3 + i * 4.85;
    if (fs.existsSync(imgPath(img.file))) {
      s.addImage({ path: imgPath(img.file), x: cx, y: 0.95, w: 4.6, h: 3.1 });
    } else {
      s.addShape(pres.shapes.RECTANGLE, {
        x: cx, y: 0.95, w: 4.6, h: 3.1,
        fill: { color: C.surface }, line: { color: C.border || "1e3a54", width: 1 }
      });
      s.addText(`[${img.file}]`, {
        x: cx, y: 0.95, w: 4.6, h: 3.1,
        fontSize: 11, color: C.muted, align: "center", valign: "middle"
      });
    }
    s.addText(img.cap, {
      x: cx, y: 4.07, w: 4.6, h: 0.35,
      fontSize: 11, fontFace: "Calibri", color: C.muted, align: "center", italic: true
    });
  });

  // UI feature list
  const uiFeatures = [
    "סרגל צד עם 15+ פרמטרי קלט",
    "תצוגת ציון גדולה + תג \"כדאי / לא כדאי\"",
    "סיכום כלכלי (הכנסות, עלויות, רווח)",
    "טבלת רגישות — 6 תרחישים אוטומטיים",
    "זמן תגובה < 1 שנייה",
  ];
  uiFeatures.forEach((f, i) => {
    s.addText(`• ${f}`, {
      x: 0.4, y: 4.5 + i * 0.22, w: 9.2, h: 0.22,
      fontSize: 12, fontFace: "Calibri", color: C.text, align: "right", rtlMode: true
    });
  });
}

// ══════════════════════════════════════════════════════════════
// Slide 7 — SHAP Insights
// ══════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.bg };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.85, fill: { color: C.navy } });
  s.addText("SHAP Insights — מה מנהל את ההחלטה?", {
    x: 0.3, y: 0.08, w: 9.4, h: 0.68,
    fontSize: 24, fontFace: "Calibri", bold: true,
    color: C.white, align: "right", rtlMode: true
  });

  // SHAP bar chart using pptxgenjs
  const shapFeatures = [
    { name: "מרווח גולמי_%", pct: 100, positive: true },
    { name: "IRR משוערת_%", pct: 88, positive: true },
    { name: "עיר (מיקום)", pct: 62, positive: true },
    { name: "גיל הבניין", pct: 44, positive: true },
    { name: "הסתברות אישור", pct: 38, positive: true },
    { name: "עלות_לקיים_יחסי", pct: 31, positive: false },
    { name: "משך כולל (חודשים)", pct: 25, positive: false },
    { name: "מינוף שטח", pct: 20, positive: true },
    { name: "סוג פרויקט", pct: 15, positive: true },
    { name: "מחיר מכירה חדש", pct: 12, positive: true },
  ];

  const maxW = 5.8;
  shapFeatures.forEach((f, i) => {
    const y = 1.0 + i * 0.43;
    const barW = maxW * (f.pct / 100);
    const col = f.positive ? C.green : C.red;

    // Feature name
    s.addText(f.name, {
      x: 0.3, y: y, w: 3.5, h: 0.38,
      fontSize: 12, fontFace: "Calibri", color: C.text,
      align: "right", rtlMode: true, valign: "middle"
    });
    // Background track
    s.addShape(pres.shapes.RECTANGLE, {
      x: 3.9, y: y + 0.06, w: maxW, h: 0.26,
      fill: { color: "1e3a54" }
    });
    // Value bar
    if (barW > 0.05) {
      s.addShape(pres.shapes.RECTANGLE, {
        x: 3.9, y: y + 0.06, w: barW, h: 0.26,
        fill: { color: col }
      });
    }
    // Percentage
    s.addText(`${f.pct}%`, {
      x: 3.9 + maxW + 0.1, y: y + 0.04, w: 0.5, h: 0.32,
      fontSize: 10, fontFace: "Calibri", color: col, align: "left"
    });
  });

  // SHAP explanation note
  s.addText("ירוק = תורם לכדאיות · אדום = תורם נגד · ערכי SHAP יחסיים (LinearExplainer — מנורמלים ל-100% עבור הפיצ'ר הדומיננטי)", {
    x: 0.3, y: 5.2, w: 9.4, h: 0.3,
    fontSize: 10, fontFace: "Calibri", color: C.muted, align: "center", italic: true
  });
}

// ══════════════════════════════════════════════════════════════
// Slide 8 — מסקנות + תרומה
// ══════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.bg };

  // Dark header
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.85, fill: { color: C.teal } });
  s.addText("מסקנות ותרומה", {
    x: 0.3, y: 0.08, w: 9.4, h: 0.68,
    fontSize: 28, fontFace: "Calibri", bold: true,
    color: C.white, align: "right", rtlMode: true
  });

  // Summary KPIs
  const sum = [
    { icon: "🏆", val: "AUC = 0.991", sub: "Classification" },
    { icon: "📉", val: "RMSE = 4.25", sub: "Regression" },
    { icon: "📊", val: "SHAP", sub: "Explainability" },
    { icon: "⚡", val: "< 1 שנייה", sub: "זמן תגובה" },
  ];
  sum.forEach((item, i) => {
    const cx = 0.3 + i * 2.35;
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: 0.95, w: 2.2, h: 1.1,
      fill: { color: C.navy }, line: { color: C.teal, width: 1 }
    });
    s.addText(item.icon, {
      x: cx, y: 0.98, w: 0.55, h: 0.95,
      fontSize: 22, align: "center", valign: "middle"
    });
    s.addText(item.val, {
      x: cx + 0.55, y: 0.98, w: 1.6, h: 0.6,
      fontSize: 16, fontFace: "Calibri", bold: true, color: C.greenLt, align: "left", valign: "middle"
    });
    s.addText(item.sub, {
      x: cx + 0.55, y: 1.52, w: 1.6, h: 0.45,
      fontSize: 11, fontFace: "Calibri", color: C.muted, align: "left"
    });
  });

  // Contributions
  s.addText("תרומת הפרויקט", {
    x: 0.3, y: 2.25, w: 9.4, h: 0.45,
    fontSize: 18, fontFace: "Calibri", bold: true, color: C.accent, align: "right", rtlMode: true
  });
  const contribs = [
    "כלי לסינון מוקדם ואוטומטי המסנן פרויקטים לפני הקצאת משאבי תכנון",
    "ארכיטקטורת ML מלאה — פחות מ-900 שורות Python",
    "SHAP explainability שמגלה את הגורמים הדומיננטיים לכדאיות",
    "ממשק Streamlit בעברית מלאה (RTL) עם הסברי SHAP חזותיים",
    "dataset ישראלי סינתטי מבוסס נתוני שוק אמת",
  ];
  contribs.forEach((c, i) => {
    s.addShape(pres.shapes.OVAL, {
      x: 9.55, y: 2.82 + i * 0.46, w: 0.18, h: 0.18,
      fill: { color: C.teal }
    });
    s.addText(c, {
      x: 0.4, y: 2.75 + i * 0.46, w: 9.1, h: 0.42,
      fontSize: 13, fontFace: "Calibri", color: C.text, align: "right", rtlMode: true
    });
  });

  // Future work
  s.addText("המשך מוצע: מפת חום גיאוגרפית (folium) · עיבוד אצווה (CSV) · שילוב נתוני שוק חיים", {
    x: 0.3, y: 5.15, w: 9.4, h: 0.35,
    fontSize: 11, fontFace: "Calibri", color: C.muted, align: "center", italic: true
  });
}

// ── Write file ─────────────────────────────────────────────────
pres.writeFile({ fileName: OUT }).then(() => {
  console.log("Presentation saved to:", OUT);
}).catch(err => {
  console.error("Error:", err);
  process.exit(1);
});
