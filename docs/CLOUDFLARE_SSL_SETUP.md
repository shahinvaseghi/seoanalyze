# راهنمای نصب SSL با Cloudflare

شما از Cloudflare استفاده می‌کنید، پس بهترین روش استفاده از Origin Certificate یا DNS Challenge است.

## روش 1: Cloudflare Origin Certificate (ساده‌ترین - توصیه می‌شود)

این روش سریع‌ترین و آسان‌ترین راه است.

### مرحله 1: ایجاد Origin Certificate در Cloudflare

1. به [Cloudflare Dashboard](https://dash.cloudflare.com) بروید
2. دامنه `shahinvaseghi.ir` را انتخاب کنید
3. برو به: **SSL/TLS** → **Origin Server**
4. روی **Create Certificate** کلیک کنید
5. تنظیمات:
   - Private key type: RSA (2048)
   - Hostnames: `seoanalyze.shahinvaseghi.ir` یا `*.shahinvaseghi.ir`
   - Certificate Validity: 15 years (توصیه می‌شود)
6. روی **Create** کلیک کنید
7. دو بخش نشان داده می‌شود:
   - **Origin Certificate**: کل محتوا را کپی کنید
   - **Private Key**: کل محتوا را کپی کنید

### مرحله 2: ذخیره گواهی در سرور

```bash
# ایجاد دایرکتوری
sudo mkdir -p /etc/ssl/cloudflare

# ذخیره Certificate (محتوای کپی شده از مرحله 1 را جایگزین کنید)
sudo nano /etc/ssl/cloudflare/cert.pem
# محتوای Origin Certificate را paste کنید و ذخیره کنید (Ctrl+X, Y, Enter)

# ذخیره Private Key
sudo nano /etc/ssl/cloudflare/key.pem
# محتوای Private Key را paste کنید و ذخیره کنید

# تنظیم دسترسی‌ها
sudo chmod 600 /etc/ssl/cloudflare/key.pem
sudo chmod 644 /etc/ssl/cloudflare/cert.pem
```

### مرحله 3: به‌روزرسانی پیکربندی Nginx

فایل nginx config را ویرایش کنید:

```bash
sudo nano /home/shahin/seoanalyzepro/configs/nginx/seoanalyzepro
```

مسیرهای گواهی را تغییر دهید:

از:
```nginx
ssl_certificate /etc/letsencrypt/live/seoanalyze.shahinvaseghi.ir/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/seoanalyze.shahinvaseghi.ir/privkey.pem;
```

به:
```nginx
ssl_certificate /etc/ssl/cloudflare/cert.pem;
ssl_certificate_key /etc/ssl/cloudflare/key.pem;
```

### مرحله 4: اعمال تغییرات

```bash
# کپی پیکربندی
sudo cp /home/shahin/seoanalyzepro/configs/nginx/seoanalyzepro /etc/nginx/sites-available/seoanalyzepro

# تست
sudo nginx -t

# اگر موفق بود، reload کنید
sudo systemctl reload nginx
```

### مرحله 5: تنظیم Cloudflare SSL Mode

در Cloudflare Dashboard:

1. برو به **SSL/TLS** → **Overview**
2. SSL/TLS encryption mode را روی **Full (strict)** تنظیم کنید
   - **مهم:** حتماً "Full (strict)" انتخاب شود، نه "Flexible"

### مرحله 6: تست

```bash
# تست از سرور
curl -I https://seoanalyze.shahinvaseghi.ir

# باز کردن در مرورگر
https://seoanalyze.shahinvaseghi.ir
```

---

## روش 2: Let's Encrypt با DNS Challenge

اگر ترجیح می‌دهید از Let's Encrypt استفاده کنید:

### مرحله 1: نصب پلاگین Cloudflare

```bash
sudo apt update
sudo apt install python3-certbot-dns-cloudflare
```

### مرحله 2: دریافت Cloudflare API Token

1. به [Cloudflare Dashboard](https://dash.cloudflare.com/profile/api-tokens) بروید
2. **Create Token** → از template **Edit zone DNS** استفاده کنید
3. تنظیمات:
   - Permissions: Zone - DNS - Edit
   - Zone Resources: Include - Specific zone - `shahinvaseghi.ir`
4. **Continue to summary** → **Create Token**
5. Token را کپی کنید (فقط یک بار نشان داده می‌شود!)

### مرحله 3: ذخیره API Token

```bash
sudo mkdir -p /root/.secrets
sudo nano /root/.secrets/cloudflare.ini
```

محتوای فایل:
```
dns_cloudflare_api_token = YOUR_API_TOKEN_HERE
```

ایمن‌سازی:
```bash
sudo chmod 600 /root/.secrets/cloudflare.ini
```

### مرحله 4: دریافت گواهی

```bash
sudo certbot certonly --dns-cloudflare \
  --dns-cloudflare-credentials /root/.secrets/cloudflare.ini \
  -d seoanalyze.shahinvaseghi.ir \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email
```

### مرحله 5: اعمال تغییرات

```bash
# کپی پیکربندی اصلی (با مسیرهای Let's Encrypt)
sudo cp /home/shahin/seoanalyzepro/configs/nginx/seoanalyzepro /etc/nginx/sites-available/seoanalyzepro

# تست و reload
sudo nginx -t && sudo systemctl reload nginx
```

### تمدید خودکار

گواهی‌های Let's Encrypt هر 90 روز منقضی می‌شوند اما certbot به صورت خودکار آن‌ها را تمدید می‌کند.

تست تمدید:
```bash
sudo certbot renew --dry-run
```

---

## تنظیمات امنیتی Cloudflare (توصیه می‌شود)

### 1. فعال‌سازی HSTS

در Cloudflare Dashboard:
- **SSL/TLS** → **Edge Certificates**
- **Always Use HTTPS**: ON
- **HTTP Strict Transport Security (HSTS)**: Enable
  - Max Age: 6 months
  - Include subdomains: ON
  - Preload: ON (اختیاری)

### 2. تنظیمات امنیتی دیگر

- **Security** → **Settings**
  - Security Level: Medium یا High
  - Challenge Passage: 30 minutes
- **Security** → **Bots**
  - Bot Fight Mode: ON

### 3. بهینه‌سازی Performance

- **Speed** → **Optimization**
  - Auto Minify: JavaScript, CSS, HTML
  - Brotli: ON
  - Early Hints: ON

---

## مقایسه دو روش

| ویژگی | Origin Certificate | Let's Encrypt |
|-------|-------------------|---------------|
| مدت اعتبار | 15 سال | 90 روز |
| تمدید خودکار | نیاز نیست | بله (certbot) |
| سرعت نصب | سریع‌تر | کمی کندتر |
| پشتیبانی مرورگر | از طریق Cloudflare | مستقیم |
| پیچیدگی | آسان | متوسط |
| **توصیه** | ✅ **بهترین برای Cloudflare** | برای کنترل بیشتر |

---

## عیب‌یابی

### خطا: ERR_SSL_VERSION_OR_CIPHER_MISMATCH

- بررسی کنید که SSL Mode در Cloudflare روی "Full (strict)" باشد
- مطمئن شوید گواهی در سرور صحیح نصب شده

### خطا: 525 SSL Handshake Failed

```bash
# بررسی لاگ nginx
sudo tail -f /var/log/nginx/seoanalyzepro.error.log

# بررسی گواهی
sudo openssl x509 -in /etc/ssl/cloudflare/cert.pem -text -noout
```

### سایت هنوز HTTP است

- Cache مرورگر را پاک کنید
- در Cloudflare "Always Use HTTPS" را فعال کنید
- بررسی کنید nginx روی پورت 443 گوش می‌دهد:
  ```bash
  sudo netstat -tulpn | grep :443
  ```

---

## تست نهایی

```bash
# تست از سرور
curl -I https://seoanalyze.shahinvaseghi.ir

# تست SSL
openssl s_client -connect seoanalyze.shahinvaseghi.ir:443 -servername seoanalyze.shahinvaseghi.ir

# تست redirect HTTP به HTTPS
curl -I http://seoanalyze.shahinvaseghi.ir
```

همه چیز آماده است! فقط یکی از دو روش بالا را انتخاب و اجرا کنید. 🚀

