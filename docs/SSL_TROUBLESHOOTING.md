# راهنمای رفع مشکل SSL

## مشکل فعلی

گواهی SSL نمی‌تونه دریافت بشه چون Let's Encrypt نمی‌تونه به سرور دسترسی پیدا کنه.

**جزئیات:**
- دامنه DNS: `seoanalyze.shahinvaseghi.ir`
- IP در DNS: `185.172.212.234`
- IP عمومی سرور: `5.135.213.213`
- خطا: Connection timeout

## راه‌حل‌ها

### راه‌حل 1: استفاده از Certbot با DNS Challenge (توصیه می‌شود برای Cloudflare)

اگر از Cloudflare استفاده می‌کنید:

#### مرحله 1: نصب پلاگین Cloudflare

```bash
sudo apt install python3-certbot-dns-cloudflare
```

#### مرحله 2: ایجاد فایل اعتبارسنجی

```bash
sudo mkdir -p /root/.secrets
sudo nano /root/.secrets/cloudflare.ini
```

محتوای فایل:
```
dns_cloudflare_api_token = YOUR_CLOUDFLARE_API_TOKEN
```

**نحوه دریافت API Token از Cloudflare:**
1. به [Cloudflare Dashboard](https://dash.cloudflare.com) بروید
2. Profile → API Tokens → Create Token
3. از template "Edit zone DNS" استفاده کنید
4. Zone Resources: Include → Specific zone → shahinvaseghi.ir
5. Create Token و کپی کنید

#### مرحله 3: تنظیم دسترسی فایل

```bash
sudo chmod 600 /root/.secrets/cloudflare.ini
```

#### مرحله 4: دریافت گواهی

```bash
sudo certbot certonly --dns-cloudflare \
  --dns-cloudflare-credentials /root/.secrets/cloudflare.ini \
  -d seoanalyze.shahinvaseghi.ir \
  --email your-email@example.com \
  --agree-tos
```

### راه‌حل 2: استفاده از Manual DNS Challenge (برای هر DNS Provider)

این روش برای همه ارائه‌دهندگان DNS کار می‌کنه:

```bash
sudo certbot certonly --manual --preferred-challenges dns \
  -d seoanalyze.shahinvaseghi.ir \
  --email your-email@example.com \
  --agree-tos
```

**مراحل:**
1. Certbot یک رکورد TXT به شما می‌ده
2. باید این رکورد رو به DNS دامنه‌تون اضافه کنید:
   - Type: TXT
   - Name: `_acme-challenge.seoanalyze`
   - Value: (مقداری که certbot بهتون میده)
3. صبر کنید تا DNS منتشر بشه (2-10 دقیقه)
4. بررسی کنید: `nslookup -type=TXT _acme-challenge.seoanalyze.shahinvaseghi.ir`
5. بعد در certbot Enter بزنید

### راه‌حل 3: اصلاح تنظیمات شبکه/DNS

اگر DNS باید به این سرور اشاره کنه:

#### بررسی وضعیت:

```bash
# بررسی IP عمومی
curl ifconfig.me

# بررسی DNS
nslookup seoanalyze.shahinvaseghi.ir

# بررسی دسترسی از خارج
curl -I http://seoanalyze.shahinvaseghi.ir
```

#### اگر از NAT استفاده می‌کنید:

مطمئن شوید که پورت‌های 80 و 443 به این سرور forward شده‌اند:

```bash
# روی روتر/فایروال خارجی:
# Port 80 (HTTP) → 192.168.11.3:80
# Port 443 (HTTPS) → 192.168.11.3:443
```

#### اگر DNS اشتباه است:

DNS رو به‌روزرسانی کنید که به `5.135.213.213` اشاره کنه (یا IP صحیح سرور).

### راه‌حل 4: استفاده از گواهی موجود یا خودامضا (فقط برای تست)

#### گواهی خودامضا (برای development):

```bash
sudo mkdir -p /etc/ssl/self-signed
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/self-signed/selfsigned.key \
  -out /etc/ssl/self-signed/selfsigned.crt \
  -subj "/C=IR/ST=Tehran/L=Tehran/O=Development/CN=seoanalyze.shahinvaseghi.ir"
```

سپس nginx config را ویرایش کنید:

```nginx
ssl_certificate /etc/ssl/self-signed/selfsigned.crt;
ssl_certificate_key /etc/ssl/self-signed/selfsigned.key;
```

**نکته:** گواهی خودامضا فقط برای تست است و مرورگرها هشدار امنیتی نشان می‌دهند.

## بعد از دریافت موفقیت‌آمیز گواهی

وقتی گواهی رو دریافت کردید:

```bash
# کپی پیکربندی نهایی
sudo cp /home/shahin/seoanalyzepro/configs/nginx/seoanalyzepro /etc/nginx/sites-available/seoanalyzepro

# تست nginx
sudo nginx -t

# اگر تست موفق بود، reload کنید
sudo systemctl reload nginx
```

## بررسی وضعیت گواهی

```bash
# لیست گواهی‌ها
sudo certbot certificates

# تست تمدید
sudo certbot renew --dry-run

# مشاهده جزئیات گواهی
sudo openssl x509 -in /etc/letsencrypt/live/seoanalyze.shahinvaseghi.ir/fullchain.pem -text -noout
```

## تست سایت HTTPS

بعد از راه‌اندازی:

```bash
# از خود سرور
curl -I https://seoanalyze.shahinvaseghi.ir

# بررسی امنیت SSL
curl https://www.ssllabs.com/ssltest/analyze.html?d=seoanalyze.shahinvaseghi.ir
```

## لاگ‌های مفید

```bash
# Nginx errors
sudo tail -f /var/log/nginx/seoanalyzepro.error.log

# Certbot logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# System logs
sudo journalctl -u nginx -f
```

## سوالات متداول

### Q: چطور می‌فهمم از Cloudflare استفاده می‌کنم؟

```bash
nslookup -type=NS shahinvaseghi.ir
```

اگر در نتیجه نام‌های `cloudflare.com` دیدید، از Cloudflare استفاده می‌کنید.

### Q: آیا می‌تونم از Cloudflare SSL استفاده کنم؟

بله! در Cloudflare:
1. SSL/TLS → Origin Server → Create Certificate
2. گواهی و کلید رو کپی کنید
3. در سرور ذخیره کنید و در nginx استفاده کنید

### Q: چرا بعد از دریافت گواهی هنوز کار نمی‌کنه؟

- بررسی کنید nginx reload شده باشه
- پیکربندی nginx رو چک کنید: `sudo nginx -t`
- لاگ‌ها رو بررسی کنید
- مطمئن شوید فایروال پورت 443 رو باز کرده
- cache مرورگر رو پاک کنید

## کمک بیشتر

اگر همچنان مشکل دارید:

1. لاگ کامل certbot رو بررسی کنید:
   ```bash
   sudo cat /var/log/letsencrypt/letsencrypt.log
   ```

2. وضعیت شبکه رو بررسی کنید:
   ```bash
   sudo netstat -tulpn | grep -E ':80|:443'
   ```

3. تست اتصال به سرور:
   ```bash
   telnet seoanalyze.shahinvaseghi.ir 80
   telnet seoanalyze.shahinvaseghi.ir 443
   ```

