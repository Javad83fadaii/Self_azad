# راهنمای Deployment

این سند فقط برای آماده‌سازی پروژه جهت استقرار واقعی نوشته شده است و هیچ تغییر مستقیمی روی سرور واقعی اعمال نمی‌کند.

## معماری پیشنهادی

```text
Internet
  |
  v
Nginx
  |
  v
Gunicorn
  |
  v
Django
  |
  v
MySQL

Static: توسط Nginx از backend/staticfiles
Media: توسط Nginx از backend/media
```

در وضعیت فعلی پروژه، استفاده از `WhiteNoise` ضروری نیست؛ چون سناریوی هدف برای Production، سرو `static` و `media` از طریق Nginx است.

## نیازمندی‌های سرور

- Linux Server یا Windows Server با امکان اجرای Python 3.12
- Python `3.12.x`
- MySQL `8.x` یا نسخه سازگار با `mysqlclient`
- Nginx به عنوان reverse proxy
- Gunicorn برای اجرای WSGI
- دسترسی فایل‌سیستم برای مسیرهای log و static/media

## Dependencyهای Production

فایل `requirements.txt` همین حالا dependencyهای اصلی موردنیاز Production را دارد:

- `Django==5.2.9`
- `djangorestframework==3.17.1`
- `mysqlclient==2.2.7`
- `python-dotenv==1.1.1`
- `openpyxl==3.1.5`
- `reportlab==4.4.4`

Dependencyهای desktop نیز در همان فایل وجود دارند؛ در این فاز حذف نشده‌اند تا رفتار build فعلی تغییر نکند.

## Environment Variables

برای Production از `DJANGO_SETTINGS_MODULE=config.settings.production` استفاده کنید.

حداقل متغیرهای لازم:

```env
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=<long-random-secret>
DEBUG=False
ALLOWED_HOSTS=example.com,www.example.com
WEB_FRONTEND_URL=https://example.com
CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com

DB_NAME=ufrs_db
DB_USER=ufrs_user
DB_PASSWORD=<strong-password>
DB_HOST=127.0.0.1
DB_PORT=3306

SECURE_SSL_REDIRECT=True
USE_X_FORWARDED_PROTO=True
USE_X_FORWARDED_HOST=True

LOG_LEVEL=INFO
DJANGO_LOG_LEVEL=WARNING
ENABLE_FILE_LOGGING=True
LOG_DIR=/var/log/self_food
```

نکات مهم:

- `SECRET_KEY` باید فقط از Environment خوانده شود.
- در Production اگر `DB_*` ناقص باشند، برنامه باید fail fast شود و به SQLite برنگردد.
- `ALLOWED_HOSTS` و `CSRF_TRUSTED_ORIGINS` باید متناسب با دامنه واقعی سرور تنظیم شوند.
- اگر frontend روی همان دامنه Django سرو می‌شود، CORS اضافی لازم نیست.

## آماده‌سازی محیط

1. ساخت virtual environment و نصب dependencyها:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

2. انتقال کد به سرور
3. قرار دادن فایل env خارج از repository یا در مسیری امن

در صورت نیاز می‌توان مسیر env را با `BACKEND_ENV_FILE` مشخص کرد.

## آماده‌سازی Database

نمونه ایجاد دیتابیس و کاربر MySQL:

```sql
CREATE DATABASE ufrs_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ufrs_user'@'127.0.0.1' IDENTIFIED BY 'change-this-password';
GRANT ALL PRIVILEGES ON ufrs_db.* TO 'ufrs_user'@'127.0.0.1';
FLUSH PRIVILEGES;
```

## Migration و Collectstatic

قبل از بالا آوردن سرویس:

```bash
export DJANGO_SETTINGS_MODULE=config.settings.production
export BACKEND_ENV_FILE=/opt/self_food/.env.production

python backend/manage.py migrate
python backend/manage.py collectstatic --noinput
python backend/manage.py check --deploy
```

اگر دیتابیس نمونه یا local SQLite استفاده شده است، آن را با دیتابیس Production اشتباه نگیرید. Production فقط باید به MySQL متصل شود.

## ساخت Superuser

در صورت نیاز:

```bash
python backend/manage.py createsuperuser
```

نکته: ورود مدیر در خود سامانه از flow فعلی پروژه استفاده می‌کند و نباید برای دانشجو تغییر کند.

## اجرای برنامه

نمونه اجرای Gunicorn:

```bash
gunicorn config.wsgi:application --bind 127.0.0.1:8001 --workers 3 --chdir /opt/self_food/backend
```

بهتر است Gunicorn با `systemd` یا supervisor مدیریت شود.

## Reverse Proxy

نمونه تنظیم مفهومی Nginx:

```nginx
server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com www.example.com;

    client_max_body_size 10m;

    location /static/ {
        alias /opt/self_food/backend/staticfiles/;
    }

    location /media/ {
        alias /opt/self_food/backend/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

این نمونه فقط برای documentation است و در این فاز نباید روی سرور واقعی اعمال شود.

## HTTPS و Cookie Security

تنظیمات Production فعلی برای HTTPS آماده هستند:

- `DEBUG=False`
- `SESSION_COOKIE_SECURE=True`
- `CSRF_COOKIE_SECURE=True`
- `SECURE_SSL_REDIRECT=True` به صورت environment-based
- `SECURE_PROXY_SSL_HEADER` در صورت فعال بودن `USE_X_FORWARDED_PROTO`
- `SECURE_HSTS_*` به صورت environment-based
- `SECURE_CONTENT_TYPE_NOSNIFF=True`
- `X_FRAME_OPTIONS=DENY`

`SECURE_BROWSER_XSS_FILTER` در Django 5 دیگر setting مؤثر و توصیه‌شده‌ای نیست؛ بنابراین عمداً اضافه نشده تا با نسخه فعلی Django سازگار بمانیم.

## Logging

پروژه در Production از console logging پشتیبانی می‌کند و در صورت فعال بودن `ENABLE_FILE_LOGGING=True` از rotating file logs نیز استفاده می‌کند.

پوشش logging فعلی:

- `django`
- `django.request`
- `django.db.backends`
- `django.security`
- `django.security.csrf`
- `accounts`
- `common`
- `dashboard`
- `meals`
- `reservations`
- `reports`
- `students`
- `audit_logs`

## Error Handling

برای مسیرهای HTML و API، error handling از هم جدا شده است:

- `400`
- `403`
- `404`
- `500`
- `CSRF failure`

برای API پاسخ JSON برمی‌گردد و برای Web صفحه HTML هماهنگ با UI رندر می‌شود.

## چک‌لیست قبل از Deployment واقعی

1. مقدار واقعی `SECRET_KEY` تولید و خارج از repository نگه‌داری شود.
2. دامنه واقعی در `ALLOWED_HOSTS` و `CSRF_TRUSTED_ORIGINS` قرار بگیرد.
3. فایل env روی سرور در مسیر امن ذخیره شود.
4. دیتابیس MySQL واقعی ساخته و دسترسی آن محدود شود.
5. `migrate`, `collectstatic`, `check --deploy` اجرا شوند.
6. لاگ‌ها و مسیر `LOG_DIR` روی سرور بررسی شوند.
7. HTTPS و reverse proxy روی Infrastructure واقعی تنظیم شوند.
