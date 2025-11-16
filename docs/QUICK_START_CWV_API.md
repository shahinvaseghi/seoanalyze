# 🚀 Quick Start: Real Core Web Vitals with Google API

## ✨ بهبود یافته! اعداد واقعی به جای تصادفی

### ❌ قبلاً (با اعداد تصادفی):
```
هر بار اجرا → اعداد متفاوت
LCP: گاهی 2.3s، گاهی 4.1s
تصمیم‌گیری → غیرممکن!
```

### ✅ الان (با Google API):
```
هر بار اجرا → اعداد واقعی ثابت
LCP: 2.456s (از Chrome users واقعی)
تصمیم‌گیری → دقیق و قابل اعتماد!
```

---

## 📝 راهنمای سریع (5 دقیقه)

### گام 1️⃣: دریافت API Key رایگان

```bash
# 1. برو به:
https://console.cloud.google.com/

# 2. ساخت یا انتخاب پروژه
Click "New Project" → نام: "SEO Tools" → Create

# 3. فعال کردن API
https://console.cloud.google.com/apis/library
جستجو: "PageSpeed Insights API" → Enable

# 4. ساخت API Key
https://console.cloud.google.com/apis/credentials
Click "Create Credentials" → "API Key"
Copy کن: AIzaSyBXXXXXXXXXXXXXXXXXX
```

### گام 2️⃣: تنظیم API Key

**روش ساده (Config File):**

```bash
cd /home/shahin/seoanalyzepro
cp configs/api_keys.json.example configs/api_keys.json
nano configs/api_keys.json
```

فایل رو اینطوری ویرایش کن:
```json
{
  "google_pagespeed_api_key": "AIzaSyBXXXXXXXXXXXXXXXXXX"
}
```

Save: `Ctrl+O` → Enter → Exit: `Ctrl+X`

**روش حرفه‌ای (Environment Variable):**

```bash
sudo systemctl edit seoanalyzepro
```

اضافه کن:
```ini
[Service]
Environment="GOOGLE_PAGESPEED_API_KEY=AIzaSyBXXXXXXXXXXXXXXXXXX"
```

Save و خروج، سپس:
```bash
sudo systemctl daemon-reload
sudo systemctl restart seoanalyzepro
```

### گام 3️⃣: ریستارت سرویس

```bash
sudo systemctl restart seoanalyzepro
```

### گام 4️⃣: تست

1. برو به: http://seoanalyze.shahinvaseghi.ir/core-web-vitals/
2. وارد کن: `https://web.dev`
3. کلیک "Analyze"
4. باید ببینی: "✅ Real metrics obtained from Google API"

---

## 📊 تفاوت واضح

### بدون API (قبلی):
```
⚠️ No API key configured, using static analysis
LCP: 3.2s (تخمینی تصادفی)
INP: 156ms (تخمینی تصادفی)
CLS: 0.09 (تخمینی تصادفی)
```

### با API (جدید):
```
📊 Using Google PageSpeed Insights API for real metrics...
✅ Real metrics obtained from Google API
LCP: 2.456s (واقعی از کاربران Chrome)
INP: 234ms (واقعی از کاربران Chrome)
CLS: 0.123 (واقعی از کاربران Chrome)
Performance Score: 78/100 (Lighthouse واقعی)
```

---

## 💡 نکات مهم

### امنیت:
- ✅ فایل `configs/api_keys.json` در `.gitignore` است
- ✅ هرگز API key رو commit نکن
- ✅ از environment variable در production استفاده کن

### محدودیت‌ها:
- ✅ 25,000 request در روز (رایگان)
- ✅ برای 100 تحلیل روزانه کافیه
- ✅ اگه quota تموم شد → auto fallback به static analysis

### بهینه‌سازی:
- 💾 می‌تونی نتایج رو cache کنی (برای همون URL در 24 ساعت)
- ⚡ API call معمولاً 5-10 ثانیه طول می‌کشه
- 📊 دیتا از میلیون‌ها کاربر واقعی Chrome

---

## 🔍 چک کردن وضعیت

```bash
# ببین API key load شده یا نه:
cd /home/shahin/seoanalyzepro
source venv/bin/activate
python3 -c "from app.core.cwv_analyzer import CWVAnalyzer; a = CWVAnalyzer(); print('API Status:', 'ENABLED ✅' if a.use_real_api else 'DISABLED ⚠️')"
```

---

## 📚 مستندات کامل

- **راهنمای دریافت API**: `docs/GOOGLE_PAGESPEED_API_SETUP.md`
- **Config راهنما**: `configs/README.md`
- **Core Web Vitals Doc**: `CORE_WEB_VITALS_DOCUMENTATION.md`

---

## 🎉 موفق باشید!

با این تغییرات، Core Web Vitals Analyzer شما حالا یک **ابزار حرفه‌ای و دقیق** است که می‌تونید روی نتایجش اعتماد کنید!

