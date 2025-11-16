# راهنمای تنظیمات SMTP برای ارسال ایمیل

این راهنما نحوه تنظیم SMTP server برای ارسال گزارشات GSC به ایمیل را توضیح می‌دهد.

## مراحل تنظیم

### 1. ایجاد فایل تنظیمات

فایل `configs/smtp_config.json.example` را کپی کنید:

```bash
cd /home/shahin/seoanalyzepro
cp configs/smtp_config.json.example configs/smtp_config.json
```

### 2. ویرایش فایل تنظیمات

فایل `configs/smtp_config.json` را با ویرایشگر باز کنید:

```bash
nano configs/smtp_config.json
```

### 3. تنظیمات برای Gmail

اگر از Gmail استفاده می‌کنید:

```json
{
  "enabled": true,
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "use_tls": true,
  "username": "your-email@gmail.com",
  "password": "your-app-password",
  "from_email": "your-email@gmail.com",
  "from_name": "SEO Analyze Pro"
}
```

**نکته مهم برای Gmail:**
- باید از **App Password** استفاده کنید (نه password عادی)
- برای ساخت App Password:
  1. به Google Account Settings بروید
  2. Security > 2-Step Verification را فعال کنید
  3. App Passwords > Generate new app password
  4. App Password را در فایل config قرار دهید

### 4. تنظیمات برای سایر سرویس‌ها

#### Outlook/Hotmail:
```json
{
  "enabled": true,
  "smtp_server": "smtp-mail.outlook.com",
  "smtp_port": 587,
  "use_tls": true,
  "username": "your-email@outlook.com",
  "password": "your-password",
  "from_email": "your-email@outlook.com",
  "from_name": "SEO Analyze Pro"
}
```

#### SendGrid:
```json
{
  "enabled": true,
  "smtp_server": "smtp.sendgrid.net",
  "smtp_port": 587,
  "use_tls": true,
  "username": "apikey",
  "password": "your-sendgrid-api-key",
  "from_email": "your-verified-email@domain.com",
  "from_name": "SEO Analyze Pro"
}
```

#### Mailgun:
```json
{
  "enabled": true,
  "smtp_server": "smtp.mailgun.org",
  "smtp_port": 587,
  "use_tls": true,
  "username": "your-mailgun-username",
  "password": "your-mailgun-password",
  "from_email": "your-verified-email@domain.com",
  "from_name": "SEO Analyze Pro"
}
```

### 5. تنظیم دسترسی فایل

برای امنیت، دسترسی فایل را محدود کنید:

```bash
chmod 600 configs/smtp_config.json
```

### 6. تست تنظیمات

1. به صفحه GSC Reports بروید
2. یک گزارش تولید کنید
3. روی دکمه "📧 ارسال به ایمیل" کلیک کنید
4. ایمیل خود را وارد کنید
5. روی "ارسال" کلیک کنید

## عیب‌یابی

### خطای Authentication Failed
- بررسی کنید username و password درست باشد
- برای Gmail، از App Password استفاده کنید (نه password عادی)
- مطمئن شوید 2-Step Verification فعال است

### خطای Connection Timeout
- بررسی کنید firewall اجازه اتصال به SMTP port را بدهد
- بررسی کنید SMTP server و port درست باشد

### ایمیل ارسال نمی‌شود
- بررسی کنید `enabled: true` باشد
- لاگ‌های سرور را بررسی کنید: `journalctl -u seoanalyzepro -f`
- بررسی کنید فایل `smtp_config.json` در مسیر درست باشد

## امنیت

- **هرگز** فایل `smtp_config.json` را به Git commit نکنید
- فایل در `.gitignore` قرار دارد
- از App Password برای Gmail استفاده کنید
- دسترسی فایل را محدود کنید (`chmod 600`)

## غیرفعال کردن

برای غیرفعال کردن ارسال ایمیل:

```json
{
  "enabled": false
}
```

یا فایل `smtp_config.json` را حذف کنید.

