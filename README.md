# University Food Reservation System (UFRS)

UFRS در وضعیت فعلی یک سامانه رزرو غذای دانشگاهی با معماری `Django + DRF + Web UI` است و فاز کلاینت ویندوزی از ریپازیتوری حذف شده است.

## ساختار پروژه

```text
backend/    Django backend + web frontend
docs/       deployment and architecture docs
tests/      lightweight project-level tests
```

## Installation

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Environment

فایل‌های نمونه:

- `./.env.example` برای توسعه
- `./.env.production.example` برای production

نمونه تنظیمات توسعه:

```env
DJANGO_SETTINGS_MODULE=config.settings.local
DEBUG=True
SECRET_KEY=change-me
DB_ENGINE=sqlite
```

نمونه تنظیمات production:

```env
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
SECRET_KEY=replace-with-a-long-random-secret
ALLOWED_HOSTS=127.0.0.1,localhost,your-domain.com
DB_NAME=ufrs_db
DB_USER=ufrs_user
DB_PASSWORD=StrongPassword123!
DB_HOST=127.0.0.1
DB_PORT=3306
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

در production می‌توانید مسیر env را با `BACKEND_ENV_FILE` مشخص کنید.

## Backend

اجرای migration:

```powershell
python backend\manage.py migrate
```

اجرای سرور توسعه:

```powershell
python backend\manage.py runserver
```

اجرای تست‌های اصلی وب و API:

```powershell
python backend\manage.py test accounts students meals reservations dashboard reports audit_logs common --settings=config.settings.test
python -m unittest discover -s tests -p "test_*.py"
```

## Web Authentication

- دریافت CSRF: `GET /api/auth/csrf/`
- ورود دانشجو برای وب: `POST /api/auth/student/login/`
  - اگر حساب از قبل وجود داشته باشد، با `student_code` و `phone_number` وارد می‌شود.
  - اگر اولین ورود باشد، همان endpoint با `first_name` و `last_name` حساب دانشجویی را ایجاد یا پروفایل ناقص را کامل می‌کند.
- ورود مدیر برای وب: `POST /api/auth/admin/login/`
- کاربر جاری: `GET /api/auth/me/`
- خروج: `POST /api/auth/logout/`

## Production Docs

- [راهنمای استقرار](file:///f:/project/self_food/docs/deployment.md)
- [راهنمای backup و restore](file:///f:/project/self_food/docs/production_backup.md)
