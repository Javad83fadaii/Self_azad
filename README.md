# University Food Reservation System (UFRS)

UFRS یک سامانه رزرو غذای دانشگاهی با معماری `Django REST API + PySide6 Desktop Client` است. در فاز ۸ پروژه برای استقرار و بسته‌بندی روی Windows نهایی شده و Desktop دانشجو اکنون قابلیت Build به صورت `EXE` و آماده‌سازی برای Installer را دارد.

## ساختار پروژه

```text
backend/    Django + DRF backend
desktop/    PySide6 desktop client
installer/  Inno Setup script
tests/      runtime and packaging tests
```

Desktop فقط برای دانشجو است. مسیرهای `Admin`، `Reports` و `Charts` از طریق APIهای Backend ارائه می‌شوند.

## Installation

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## MySQL Setup

1. دیتابیس را بسازید:

```sql
CREATE DATABASE ufrs_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. کاربر دیتابیس را ایجاد کنید:

```sql
CREATE USER 'ufrs_user'@'localhost' IDENTIFIED BY 'StrongPassword123!';
GRANT ALL PRIVILEGES ON ufrs_db.* TO 'ufrs_user'@'localhost';
FLUSH PRIVILEGES;
```

3. برای Production از فایل نمونه `./.env.production.example` استفاده کنید.

## Environment

سه فایل نمونه برای Environment آماده شده است:

- `./.env.example` برای Development
- `./.env.production.example` برای Backend در Production
- `./desktop.env.example` برای Desktop Client

### Development

در Development اگر `DB_NAME` تنظیم نشود، تنظیمات `config.settings.local` به صورت خودکار از SQLite محلی استفاده می‌کند و هیچ اطلاعات MySQL به صورت hard-code لازم نیست.

نمونه:

```env
DJANGO_SETTINGS_MODULE=config.settings.local
DEBUG=True
SECRET_KEY=change-me
DB_ENGINE=sqlite
API_BASE_URL=http://127.0.0.1:8000
API_TIMEOUT_SECONDS=10
```

### Production

در Production دیتابیس فقط از Environment خوانده می‌شود و همه مقادیر `DB_*` الزامی هستند:

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

برای Backend می‌توانید فایل env جداگانه را با متغیر `BACKEND_ENV_FILE` معرفی کنید.

## Backend

اجرای Migration:

```powershell
python backend\manage.py migrate
```

اجرای سرور Development:

```powershell
python backend\manage.py runserver
```

اجرای Backend با تنظیمات Production:

```powershell
$env:BACKEND_ENV_FILE="F:\path\to\.env.production"
$env:DJANGO_SETTINGS_MODULE="config.settings.production"
python backend\manage.py migrate
python backend\manage.py collectstatic --noinput
```

## Desktop

اجرای مستقیم نسخه دسکتاپ از سورس:

```powershell
python desktop\main.py
```

Desktop فایل Environment را با این اولویت جستجو می‌کند:

1. مسیر معرفی‌شده در `UFRS_ENV_FILE`
2. فایل `.env` کنار فایل EXE
3. فایل `desktop.env` کنار فایل EXE
4. فایل `config\desktop.env` کنار فایل EXE
5. فایل `%APPDATA%\ufrs_student_desktop\desktop.env`
6. فایل `.env` ریشه پروژه در اجرای سورس

نمونه تنظیمات Desktop:

```env
API_BASE_URL=http://127.0.0.1:8000
API_TIMEOUT_SECONDS=10
```

## Build EXE

اسکریپت بیلد:

```powershell
.\build_windows.bat
```

این اسکریپت:

- dependencyها را نصب می‌کند
- `PyInstaller` را اجرا می‌کند
- خروجی `dist\UFRSStudentDesktop\` را می‌سازد
- فایل‌های `desktop.env.example` و `backend.production.env.example` را داخل `config\` خروجی قرار می‌دهد
- `README.md` را کنار EXE کپی می‌کند
- در صورت وجود `ISCC.exe`، Installer را هم می‌سازد

## PyInstaller

تنظیمات Build در فایل `./ufrs_student_desktop.spec` قرار دارد.

منابعی که در بیلد نهایی مدیریت می‌شوند:

- `desktop/resources/app_icon.ico`
- `desktop/resources/app_icon.svg`
- سایر فایل‌های داخل `desktop/resources/`
- `desktop.env.example`
- `.env.production.example`
- `README.md`

Backend داخل EXE بسته‌بندی نشده است و Desktop از طریق `API_BASE_URL` به Backend در حال اجرا متصل می‌شود.

## Installer

اسکریپت Inno Setup:

```text
installer\ufrs_student_desktop.iss
```

ویژگی‌های آماده‌شده:

- پشتیبانی از ساخت Installer با `ISCC.exe`
- ایجاد Shortcut
- کپی فایل نمونه `desktop.env.example` به `%APPDATA%\ufrs_student_desktop`
- قابلیت override برای `MyAppVersion` و `MyAppSourceDir`

خروجی Installer:

```text
installer\Output\
```

## Final Test

اعتبارسنجی نهایی ویندوزی با این تست‌ها و smoke check پوشش داده می‌شود:

- Start Desktop
- Login
- Student profile
- Admin login API
- Meal and schedule listing
- Reservation
- Cancel reservation
- Reports
- Dashboard / charts

اجرای تست‌های Backend:

```powershell
python backend\manage.py test accounts students meals reservations dashboard reports --settings=config.settings.test
```

اجرای تست‌های Runtime و Packaging:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

Smoke test اجرای Desktop:

```powershell
$env:UFRS_AUTO_EXIT_MS=2000
python desktop\main.py
```

## Troubleshooting

### Desktop به Backend وصل نمی‌شود

- مقدار `API_BASE_URL` را بررسی کنید.
- مطمئن شوید Backend در حال اجرا است.
- اگر از HTTPS استفاده می‌کنید، آدرس را کامل و صحیح وارد کنید.

### خطای Database Connection

- مقادیر `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` را بررسی کنید.
- برای MySQL از نصب بودن `mysqlclient` و ابزارهای Build ویندوز مطمئن شوید.
- در Development اگر MySQL لازم ندارید، `DB_ENGINE=sqlite` را نگه دارید.

### EXE اجرا می‌شود ولی Login کار نمی‌کند

- فایل `desktop.env` یا `config\desktop.env` را بررسی کنید.
- از دسترسی Desktop به Backend در `API_BASE_URL` مطمئن شوید.

### Installer ساخته نمی‌شود

- Inno Setup 6 را نصب کنید.
- وجود `ISCC.exe` در `PATH` یا مسیر پیش‌فرض نصب را بررسی کنید.

### تست‌ها با Redirect یا HSTS خطا می‌دهند

- از `config.settings.test` استفاده کنید.
- در این تنظیمات redirect اجباری غیرفعال شده است.

## گزارش نهایی فاز ۸

- تنظیمات `Development` و `Production` از هم تفکیک شدند.
- اطلاعات دیتابیس برای Production فقط از Environment خوانده می‌شوند.
- Development بدون hard-code دیتابیس به صورت پیش‌فرض با SQLite محلی بالا می‌آید.
- فایل `ufrs_student_desktop.spec` برای Build ویندوزی تکمیل شد.
- Resourceهای دسکتاپ، آیکن‌ها و فایل‌های پیکربندی در خروجی Build مدیریت شدند.
- اسکریپت `build_windows.bat` برای Build و ساخت اختیاری Installer تکمیل شد.
- ساختار `Inno Setup` برای نصب Windows آماده شد.
- مستندات نهایی نصب، Environment، Backend، Desktop، Build EXE و رفع اشکال تکمیل شدند.
