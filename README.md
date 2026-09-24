# University Food Reservation System (UFRS)

UFRS یک سامانه رزرو غذای دانشگاهی با معماری `Backend + Desktop Client` است.
در فاز ۸، پروژه برای اجرای Production روی Windows آماده شده و موارد زیر به آن اضافه شده‌اند:

- تفکیک تنظیمات Development و Production
- پیکربندی PyInstaller برای ساخت EXE
- اسکریپت Build ویندوزی
- ساختار آماده برای Inno Setup
- مدیریت صحیح Environment و Resourceها در زمان Build

## ساختار کلی

```text
desktop/   -> کلاینت دسکتاپ PySide6 برای دانشجو
backend/   -> Django + DRF backend
installer/ -> اسکریپت Inno Setup
tests/     -> تست‌های کمکی و smoke/runtime
```

Desktop فقط کلاینت دانشجویی است. قابلیت‌های `Admin`، `Reports` و `Charts` در Backend از طریق API پیاده‌سازی شده‌اند.

## Installation

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## MySQL Setup

1. یک دیتابیس MySQL بسازید:

```sql
CREATE DATABASE ufrs_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. یک کاربر مناسب بسازید و دسترسی بدهید:

```sql
CREATE USER 'ufrs_user'@'localhost' IDENTIFIED BY 'StrongPassword123!';
GRANT ALL PRIVILEGES ON ufrs_db.* TO 'ufrs_user'@'localhost';
FLUSH PRIVILEGES;
```

3. فایل `.env` را از روی `.env.example` بسازید.

## Environment

نمونه متغیرهای محیطی:

```env
SECRET_KEY=change-me
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.local
DB_NAME=ufrs_db
DB_USER=ufrs_user
DB_PASSWORD=StrongPassword123!
DB_HOST=127.0.0.1
DB_PORT=3306
ALLOWED_HOSTS=127.0.0.1,localhost
API_BASE_URL=http://127.0.0.1:8000
API_TIMEOUT_SECONDS=10
```

### Development

برای توسعه از این تنظیمات استفاده کنید:

```env
DJANGO_SETTINGS_MODULE=config.settings.local
DEBUG=True
```

### Production

برای Production:

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
API_BASE_URL=https://your-backend-host
API_TIMEOUT_SECONDS=15
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

در Production اطلاعات Database دیگر نباید hard-code شوند و همگی از Environment خوانده می‌شوند.

## Backend

اجرای Migration:

```powershell
python backend\manage.py migrate
```

اجرای Development Server:

```powershell
python backend\manage.py runserver
```

اجرای Backend با تنظیمات Production:

```powershell
set DJANGO_SETTINGS_MODULE=config.settings.production
python backend\manage.py migrate
python backend\manage.py collectstatic --noinput
```

## Desktop

اجرای مستقیم نسخه دسکتاپ از سورس:

```powershell
python desktop\main.py
```

Desktop در زمان اجرا فایل Environment را به این ترتیب جستجو می‌کند:

1. مسیر مشخص‌شده در `UFRS_ENV_FILE`
2. فایل `.env` کنار فایل EXE
3. فایل `config\desktop.env` کنار فایل EXE
4. فایل `%APPDATA%\ufrs_student_desktop\desktop.env`
5. فایل `.env` ریشه پروژه در حالت اجرای سورس

تنظیم مهم Desktop:

```env
API_BASE_URL=http://127.0.0.1:8000
API_TIMEOUT_SECONDS=10
```

## Build EXE

اسکریپت آماده:

```powershell
.\build_windows.bat
```

این اسکریپت کارهای زیر را انجام می‌دهد:

- نصب dependencyها
- نصب `PyInstaller`
- ساخت خروجی EXE با فایل `ufrs_student_desktop.spec`
- کپی `README.md` و نمونه env داخل خروجی
- تلاش برای ساخت installer در صورت نصب بودن Inno Setup

خروجی نهایی:

```text
dist\UFRSStudentDesktop\
```

## PyInstaller

فایل تنظیمات PyInstaller:

```text
ufrs_student_desktop.spec
```

در Build نهایی این موارد مدیریت می‌شوند:

- `desktop/resources/app_icon.svg`
- `desktop/resources/app_icon.ico`
- `.env.example`
- `README.md`
- data fileهای package دسکتاپ

نکته: Backend داخل EXE بسته‌بندی نشده است؛ EXE به Backend در حال اجرا از طریق `API_BASE_URL` متصل می‌شود.

## Installer

اسکریپت آماده Inno Setup:

```text
installer\ufrs_student_desktop.iss
```

اگر `ISCC.exe` روی سیستم نصب باشد، `build_windows.bat` آن را هم اجرا می‌کند.

خروجی installer:

```text
installer\Output\
```

## API Summary

### Authentication

- `POST /api/auth/student/register/`
- `POST /api/auth/login/`

### Student

- `GET /api/students/me/profile/`
- `GET /api/schedules/upcoming/`
- `GET /api/reservations/my/`
- `POST /api/reservations/`
- `DELETE /api/reservations/{id}/cancel/`

### Admin

- `GET /api/admin/reservations/`
- `GET /api/admin/reservations/by-date/?date=YYYY-MM-DD`
- `GET /api/admin/reservations/by-meal/?meal_id=<id>`
- `GET /api/admin/dashboard/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- `GET /api/admin/reports/daily-meals/?date=YYYY-MM-DD`
- `GET /api/admin/reports/students/?student_code=&first_name=&last_name=&phone_number=`
- `GET /api/admin/reports/meals/`

## Final Test

برای اعتبارسنجی نهایی روی Windows این موارد باید بررسی شوند:

- Start Desktop
- Login
- Student Profile
- Meal List
- Schedule List
- Reservation
- Cancel Reservation
- Admin Login API
- Admin Reservation APIs
- Reports APIs
- Dashboard/Charts APIs

تست‌های پروژه:

```powershell
python backend\manage.py test accounts students meals reservations dashboard reports --settings=config.settings.test
python -m unittest discover -s tests -p "test_*.py"
```

برای Smoke Test اجرای Desktop:

```powershell
$env:UFRS_AUTO_EXIT_MS=2000
python desktop\main.py
```

## Troubleshooting

### 1. Desktop به Backend وصل نمی‌شود

- مقدار `API_BASE_URL` را بررسی کنید.
- مطمئن شوید Backend در حال اجرا است.
- اگر از HTTPS استفاده می‌کنید، آدرس را دقیق وارد کنید.

### 2. خطای Database Connection

- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` را بررسی کنید.
- از نصب بودن `mysqlclient` و Visual C++ Build Tools مطمئن شوید.

### 3. خطای 301 یا Redirect در تست‌ها

- برای تست از `config.settings.test` استفاده کنید.
- در این تنظیمات `SECURE_SSL_REDIRECT=False` شده است.

### 4. EXE اجرا می‌شود ولی Login کار نمی‌کند

- فایل env کنار EXE یا در `config\desktop.env` را بررسی کنید.
- `API_BASE_URL` باید به Backend قابل دسترس اشاره کند.

### 5. Installer ساخته نمی‌شود

- Inno Setup را نصب کنید.
- وجود `ISCC.exe` در `PATH` را بررسی کنید.

## وضعیت نهایی فاز ۸

- PyInstaller پیکربندی شد.
- فایل `.spec` اضافه شد.
- اسکریپت `build_windows.bat` اضافه شد.
- ساختار Inno Setup آماده شد.
- تنظیمات `Development` و `Production` از هم جدا شد.
- خواندن Environment برای Desktop و Backend بهبود یافت.
- مدیریت resourceهای مورد نیاز Build انجام شد.
