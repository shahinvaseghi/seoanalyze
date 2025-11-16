SEOAnalyzePro - مروری سریع (فارسی)
=================================

هدف
----
چارچوب مینیمال برای ساخت ابزار تحلیل SEO با Python/Flask: صفحه لاگین، مدیریت نشست، و ذخیره‌سازی کاربران در فایل JSON.

شروع سریع
---------
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -c "from app.services.storage import UserStorage; UserStorage().ensure_default_admin()"
python -c "from app.web.app import app; app.run('127.0.0.1', 5000, debug=True)"
```

ورود
----
- آدرس: http://127.0.0.1:5000
- کاربر پیش‌فرض: `admin` / `admin123` (لطفاً فوراً تغییر دهید)

دیپلوی
------
- Gunicorn + systemd + Nginx. برای SSL از Let's Encrypt یا Cloudflare استفاده کنید (سند `docs/README_HTTPS.md`).

نکات امنیتی
-----------
- `SECRET_KEY` قوی برای محیط واقعی تنظیم شود.
- دسترسی اینترنتی فقط از طریق Nginx انجام شود.


