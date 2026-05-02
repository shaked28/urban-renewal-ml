# 🚀 הוראות פריסה (Deploy)

מסמך זה מסביר כיצד להפעיל את האפליקציה באינטרנט במקום להריץ אותה מקומית.

---

## אופציה 1 — Streamlit Community Cloud (מומלץ, חינמי)

### דרישות מקדימות
- חשבון GitHub פעיל (תחת השם `shaked-akrish` או דומה).
- כל קבצי הפרויקט במצב מוכן (`urban_renewal_project/`).

### צעד 1 — צור רפו ב-GitHub

1. גש ל-https://github.com/new
2. **Repository name**: `urban-renewal-ml`
3. **Visibility**: `Public` (חובה לפריסה חינמית)
4. **לא** לסמן "Initialize with README" (יש כבר README מקומי)
5. לחץ **Create repository**

### צעד 2 — דחוף את הקוד

פתח PowerShell בתיקיית `urban_renewal_project` והרץ:

```powershell
# החלף <USERNAME> בשם המשתמש שלך ב-GitHub
git remote set-url origin https://github.com/<USERNAME>/urban-renewal-ml.git

# בדוק שאין קבצים גדולים מדי (>100MB)
git status

# אם זו פריסה ראשונה והרפו ריק:
git add -A
git commit -m "Initial deploy — Urban Renewal ML"
git push -u origin main
```

> **הערה**: אם אתה מקבל שגיאת autauthentication, התקן GitHub CLI והפעל:
> ```powershell
> gh auth login --web
> ```

### צעד 3 — חבר ל-Streamlit Cloud

1. גש ל-https://share.streamlit.io
2. לחץ **Sign in** → התחבר עם GitHub (אישור הרשאות).
3. לחץ **New app**.
4. מלא:
   - **Repository**: `<USERNAME>/urban-renewal-ml`
   - **Branch**: `main`
   - **Main file path**: `app/main.py`
   - **App URL** (מותאם אישית): `urban-renewal-ml`
5. לחץ **Deploy!**

הפריסה לוקחת 3–5 דקות. בסיום תקבל URL בצורה:
```
https://urban-renewal-ml.streamlit.app/
```
(או דומה אם השם תפוס).

### צעד 4 — עדכן את דף הנחיתה

ערוך את `docs/index.html` והחלף בכפתור "פתח את האפליקציה" את ה-URL הזמני ב-URL הסופי:

```html
<a href="https://urban-renewal-ml.streamlit.app/" class="btn btn-primary">...</a>
```

דחוף שוב:
```powershell
git add docs/index.html
git commit -m "Update live app URL after deployment"
git push
```

---

## אופציה 2 — Hugging Face Spaces

חלופה למי שלא רוצה רפו GitHub פומבי.

### דרישות
- חשבון Hugging Face (https://huggingface.co/join)

### שלבים
1. צור Space חדש: https://huggingface.co/new-space
   - **SDK**: Streamlit
   - **Hardware**: CPU basic (חינמי)
2. שכפל את ה-Space מקומית:
   ```powershell
   git clone https://huggingface.co/spaces/<USER>/urban-renewal-ml hf-space
   cd hf-space
   ```
3. העתק לתוכו את כל קבצי `urban_renewal_project/` (לא כולל `.git`, `node_modules`, `__pycache__`).
4. דחוף:
   ```powershell
   git add -A
   git commit -m "Deploy to HF Spaces"
   git push
   ```

ה-URL יהיה: `https://huggingface.co/spaces/<USER>/urban-renewal-ml`.

---

## אופציה 3 — Render.com (Container)

מתאים אם רוצים שליטה מלאה על תהליכי Build.

1. צור חשבון ב-https://render.com.
2. **New** → **Web Service** → חבר ל-GitHub repo.
3. הגדר:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app/main.py --server.port $PORT --server.address 0.0.0.0`
4. **Create Web Service**.

---

## פתרון בעיות נפוצות

### "ModuleNotFoundError" בפריסה
- וודא שכל החבילות ב-`requirements.txt` עם טווחי גרסה תקינים.
- בדוק את `runtime.txt` — `python-3.12` (לא 3.14, לא נתמך ב-Cloud).

### "Models not found"
- ה-`*.pkl` חייבים להיות ב-repo. בדוק `git ls-files models/` — אם חסרים, ערוך את `.gitignore` והוסף אותם.

### האפליקציה איטית בפריסה הראשונה
- Streamlit Cloud "מתעורר" אחרי חוסר פעילות. הפעלה ראשונה לוקחת ~30 שניות. המשך גישה — מהיר.

### עדכוני קוד לא מופיעים
- כל `git push` ל-`main` מפעיל פריסה חדשה אוטומטית. בדוק את לוג הפריסה ב-Streamlit Cloud dashboard.

---

## מה הוגדר מראש (כבר במערכת)

| קובץ | תפקיד |
|------|-------|
| `runtime.txt` | קובע Python 3.12 לפריסה |
| `.streamlit/config.toml` | תמה כהה, RTL hint, headless mode |
| `requirements.txt` | טווחי חבילות תואמים ל-Python 3.12 |
| `app/main.py` | נקודת כניסה — Streamlit UI |

---

מפותח ע"י **שקד עקריש** · הקריה האקדמית אונו · 2025
