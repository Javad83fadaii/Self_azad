اکنون وارد Phase 7 پروژه University Food Reservation System شو.

هدف این فاز:

آماده‌سازی کامل پروژه برای Deployment روی Server و استفاده واقعی.

⚠️ این فاز نباید Business Logic سامانه را تغییر دهد.

⚠️ Desktop Application نباید تغییر رفتاری داشته باشد.

⚠️ Database Schema فقط در صورت ضرورت واقعی تغییر کند.

⚠️ قبل از هر تغییر، وضعیت واقعی پروژه را از روی کد بررسی کن.

━━━━━━━━━━━━━━━━━━━━

1. Project Audit
   ━━━━━━━━━━━━━━━━━━━━

ابتدا وضعیت فعلی را بررسی کن:

* Django settings
* Environment variables
* MySQL configuration
* Static files
* Templates
* Media files
* Authentication
* CSRF
* CORS
* Allowed Hosts
* API permissions
* Logging
* Error handling
* Export system
* Audit Log
* Tests

همچنین ساختار فعلی پروژه را بررسی کن و چیزی که از قبل پیاده شده دوباره نساز.

━━━━━━━━━━━━━━━━━━━━
2. Development / Production Settings
━━━━━━━━━━━━━━━━━━━━

بررسی کن که تنظیمات Development و Production از هم جدا باشند.

ترجیحاً ساختار موجود را حفظ کن.

مثلاً:

config/settings/
base.py
local.py
test.py
production.py

اگر پروژه ساختار دیگری دارد:

همان ساختار موجود را حفظ کن.

تنظیمات Production باید حداقل موارد زیر را کنترل کند:

DEBUG

SECRET_KEY

ALLOWED_HOSTS

DATABASE

CSRF_TRUSTED_ORIGINS

STATIC

MEDIA

EMAIL

LOGGING

━━━━━━━━━━━━━━━━━━━━
3. Environment Variables
━━━━━━━━━━━━━━━━━━━━

اطمینان حاصل کن اطلاعات حساس Hard-code نشده باشند.

حداقل:

SECRET_KEY

DEBUG

DB_NAME

DB_USER

DB_PASSWORD

DB_HOST

DB_PORT

ALLOWED_HOSTS

CSRF_TRUSTED_ORIGINS

WEB_FRONTEND_URL

در صورت نیاز:

EMAIL_HOST

EMAIL_PORT

EMAIL_HOST_USER

EMAIL_HOST_PASSWORD

و سایر موارد موجود.

مقادیر واقعی Secret یا Password را داخل Repository قرار نده.

━━━━━━━━━━━━━━━━━━━━
4. .env.example
━━━━━━━━━━━━━━━━━━━━

فایل:

.env.example

را بررسی و در صورت نیاز تکمیل کن.

این فایل نباید مقدار واقعی Password یا Secret داشته باشد.

برای هر Variable توضیح کوتاه قرار بده.

━━━━━━━━━━━━━━━━━━━━
5. Production Secret
━━━━━━━━━━━━━━━━━━━━

بررسی کن:

SECRET_KEY

در Production از Environment Variable خوانده شود.

اگر Secret در Source Code قرار دارد:

اصلاح کن.

اما Secret فعلی را در Git History دستکاری نکن مگر اینکه کاربر صراحتاً درخواست کرده باشد.

━━━━━━━━━━━━━━━━━━━━
6. DEBUG
━━━━━━━━━━━━━━━━━━━━

در Production:

DEBUG=False

باشد.

نباید امکان فعال شدن ناخواسته DEBUG در Production وجود داشته باشد.

━━━━━━━━━━━━━━━━━━━━
7. ALLOWED_HOSTS
━━━━━━━━━━━━━━━━━━━━

ALLOWED_HOSTS باید Environment-based باشد.

مثلاً:

ALLOWED_HOSTS=example.com,[www.example.com](http://www.example.com)

اما Domain واقعی را حدس نزن.

از مقدار Environment استفاده کن.

━━━━━━━━━━━━━━━━━━━━
8. CSRF Trusted Origins
━━━━━━━━━━━━━━━━━━━━

برای Web Session Authentication:

CSRF_TRUSTED_ORIGINS

را بررسی کن.

در صورت استفاده از HTTPS:

https://example.com

و در صورت نیاز:

https://www.example.com

قرار گیرد.

Domain واقعی باید از Environment خوانده شود.

━━━━━━━━━━━━━━━━━━━━
9. CORS
━━━━━━━━━━━━━━━━━━━━

اگر Web داخل همان Django Serve می‌شود:

CORS غیرضروری ایجاد نکن.

اگر CORS package موجود است:

بررسی کن که:

CORS_ALLOW_ALL_ORIGINS

فعال نباشد.

اگر CORS مورد نیاز نیست:

تنظیمات اضافی آن را بی‌دلیل اضافه نکن.

━━━━━━━━━━━━━━━━━━━━
10. Secure Cookies
━━━━━━━━━━━━━━━━━━━━

برای Production بررسی کن:

SESSION_COOKIE_SECURE

CSRF_COOKIE_SECURE

SECURE_BROWSER_XSS_FILTER

SECURE_CONTENT_TYPE_NOSNIFF

X_FRAME_OPTIONS

در صورت سازگاری با پروژه فعال شوند.

تنظیمات امنیتی را با نسخه Django فعلی سازگار کن.

━━━━━━━━━━━━━━━━━━━━
11. HTTPS
━━━━━━━━━━━━━━━━━━━━

Production باید برای HTTPS آماده باشد.

در صورت استفاده از Reverse Proxy:

SECURE_PROXY_SSL_HEADER

بررسی شود.

Redirect HTTP → HTTPS

فقط در Production فعال شود.

⚠️ در Local Development باعث خراب شدن سایت نشود.

━━━━━━━━━━━━━━━━━━━━
12. Static Files
━━━━━━━━━━━━━━━━━━━━

Static structure را بررسی کن.

اطمینان حاصل کن:

STATIC_URL

STATIC_ROOT

STATICFILES_DIRS

به شکل صحیح تنظیم شده باشند.

دستور:

python manage.py collectstatic

را در محیط تست اجرا کن.

بررسی کن تمام:

CSS

JS

Images

Fonts

Bootstrap

Chart.js

Font Awesome

در Production قابل سرو شدن باشند.

━━━━━━━━━━━━━━━━━━━━
13. Media Files
━━━━━━━━━━━━━━━━━━━━

اگر پروژه Media دارد:

MEDIA_ROOT

MEDIA_URL

را بررسی کن.

اگر فعلاً Media نداریم:

تنظیم غیرضروری ایجاد نکن.

━━━━━━━━━━━━━━━━━━━━
14. WhiteNoise
━━━━━━━━━━━━━━━━━━━━

بررسی کن آیا WhiteNoise در پروژه وجود دارد.

اگر وجود دارد:

تنظیم آن را بررسی و اصلاح کن.

اگر وجود ندارد:

فقط در صورتی اضافه کن که برای Deployment فعلی واقعاً مفید باشد.

برای Server + Nginx الزاماً نیاز به WhiteNoise نیست.

━━━━━━━━━━━━━━━━━━━━
15. Database Production
━━━━━━━━━━━━━━━━━━━━

MySQL Production را بررسی کن.

Environment Variables:

DB_NAME

DB_USER

DB_PASSWORD

DB_HOST

DB_PORT

باید استفاده شوند.

SQLite نباید به صورت ناخواسته در Production فعال شود.

━━━━━━━━━━━━━━━━━━━━
16. Database Safety
━━━━━━━━━━━━━━━━━━━━

بررسی کن اگر:

DB_NAME

در Production وجود نداشت:

برنامه به SQLite fallback نکند.

Production باید Fail Fast باشد.

یعنی Configuration اشتباه سریعاً مشخص شود.

━━━━━━━━━━━━━━━━━━━━
17. Database Connection
━━━━━━━━━━━━━━━━━━━━

تنظیمات MySQL را بررسی کن:

charset

timezone

connection lifetime

strict mode

در صورت نیاز.

تنظیماتی که از قبل صحیح هستند را تغییر نده.

━━━━━━━━━━━━━━━━━━━━
18. Migrations
━━━━━━━━━━━━━━━━━━━━

بررسی کن:

python manage.py makemigrations --check

و:

python manage.py showmigrations

اجرا شوند.

اگر Migration Pending وجود دارد:

گزارش کن.

Migration جدید بدون نیاز ایجاد نکن.

━━━━━━━━━━━━━━━━━━━━
19. Deployment Check
━━━━━━━━━━━━━━━━━━━━

اجرا کن:

python manage.py check --deploy

اگر Warning وجود دارد:

هر Warning را بررسی کن.

Warningهای واقعی Security را تا حد امکان رفع کن.

Warningهایی که وابسته به Infrastructure هستند را در گزارش نهایی مشخص کن.

━━━━━━━━━━━━━━━━━━━━
20. Logging
━━━━━━━━━━━━━━━━━━━━

Logging Production را بررسی کن.

حداقل:

Django Errors

Server Errors

Authentication Errors

API Errors

Database Errors

ثبت شوند.

Password

Token

Secret

CSRF Token

اطلاعات حساس

نباید در Log ثبت شوند.

━━━━━━━━━━━━━━━━━━━━
21. Log Rotation
━━━━━━━━━━━━━━━━━━━━

اگر File Logging وجود دارد:

بررسی کن Logها بی‌نهایت رشد نکنند.

در صورت نیاز:

RotatingFileHandler

یا راهکار مناسب محیط Server استفاده شود.

اگر Logging توسط Supervisor/Systemd/Docker مدیریت می‌شود:

راهکار موجود را حفظ کن.

━━━━━━━━━━━━━━━━━━━━
22. Error Pages
━━━━━━━━━━━━━━━━━━━━

صفحات:

400

403

404

500

را بررسی کن.

برای Web:

UI هماهنگ با سایت داشته باشند.

برای API:

JSON Response مناسب باقی بماند.

API نباید به جای JSON صفحه HTML دریافت کند مگر در Endpointهای HTML.

━━━━━━━━━━━━━━━━━━━━
23. Authentication Production Review
━━━━━━━━━━━━━━━━━━━━

بررسی کن:

Student Login

Admin Login

Session

CSRF

Logout

Session Expiration

Role Permissions

در Production صحیح باشند.

Desktop:

Token Authentication

باید بدون تغییر باقی بماند.

━━━━━━━━━━━━━━━━━━━━
24. Session Security
━━━━━━━━━━━━━━━━━━━━

Session Cookie را بررسی کن.

در Production:

Secure

HttpOnly

SameSite

تنظیم مناسب داشته باشد.

مقادیر را با Flow فعلی Web سازگار نگه دار.

━━━━━━━━━━━━━━━━━━━━
25. Admin Security
━━━━━━━━━━━━━━━━━━━━

بررسی کن:

Student

نتواند:

Admin Dashboard

Reports

Exports

Activity Logs

را مشاهده کند.

حتی با وارد کردن مستقیم URL.

Frontend Check کافی نیست.

Backend Permission باید مرجع اصلی باشد.

━━━━━━━━━━━━━━━━━━━━
26. API Security Review
━━━━━━━━━━━━━━━━━━━━

Endpointهای زیر را بررسی کن:

Authentication

Student

Reservation

Admin

Reports

Export

Activity

برای هر کدام:

Authentication

Permission

CSRF

Rate Limiting در صورت نیاز

بررسی شود.

━━━━━━━━━━━━━━━━━━━━
27. Rate Limiting
━━━━━━━━━━━━━━━━━━━━

Throttleهای فعلی را بررسی کن.

مخصوصاً:

Login

Student Login

Authentication

اگر Rate Limit مناسب وجود دارد:

حفظ شود.

اگر کمبود واضحی وجود دارد:

حداقل تغییر لازم را انجام بده.

Throttle تست‌ها را خراب نکن.

━━━━━━━━━━━━━━━━━━━━
28. Password / Login
━━━━━━━━━━━━━━━━━━━━

روش Login فعلی را تغییر نده.

Student:

student_code + phone_number

Admin:

روش فعلی

باید حفظ شود.

⚠️ در این فاز Password Login جدید برای Student اضافه نکن.

━━━━━━━━━━━━━━━━━━━━
29. Backup Strategy
━━━━━━━━━━━━━━━━━━━━

برای MySQL یک مستند Backup ایجاد کن.

مثلاً:

docs/production_backup.md

شامل:

mysqldump

زمان‌بندی Backup

محل Backup

Retention

Restore Procedure

باشد.

⚠️ Backup واقعی Production را بدون درخواست اجرا نکن.

━━━━━━━━━━━━━━━━━━━━
30. Restore Documentation
━━━━━━━━━━━━━━━━━━━━

مراحل Restore را مستند کن.

مثلاً:

mysql database < backup.sql

اما Command را متناسب با Database واقعی پروژه بنویس.

━━━━━━━━━━━━━━━━━━━━
31. Deployment Documentation
━━━━━━━━━━━━━━━━━━━━

سند:

docs/deployment.md

ایجاد یا تکمیل کن.

شامل:

Server Requirements

Python Version

MySQL Version

Environment Variables

Install Dependencies

Database Setup

Migration

Collectstatic

Create Superuser

Run Application

Reverse Proxy

HTTPS

باشد.

━━━━━━━━━━━━━━━━━━━━
32. Server Architecture
━━━━━━━━━━━━━━━━━━━━

یک Architecture پیشنهادی مستند کن:

Internet

↓

Nginx

↓

Gunicorn

↓

Django

↓

MySQL

Static / Media

از مسیر مناسب سرو شوند.

اما فعلاً هیچ Server واقعی را بدون اطلاعات کاربر تغییر نده.

━━━━━━━━━━━━━━━━━━━━
33. Requirements
━━━━━━━━━━━━━━━━━━━━

فایل:

requirements.txt

یا ساختار فعلی Dependency Management را بررسی کن.

اطمینان حاصل کن Dependencyهای Production مشخص باشند.

Packageهای غیرضروری را حذف نکن مگر مطمئن باشی استفاده نمی‌شوند.

━━━━━━━━━━━━━━━━━━━━
34. Dependency Review
━━━━━━━━━━━━━━━━━━━━

بررسی کن:

Django

DRF

MySQL Driver

openpyxl

Chart.js

Bootstrap

و سایر Dependencyها.

نسخه‌های فعلی را بدون دلیل Upgrade نکن.

این فاز Migration به نسخه جدید Framework نیست.

━━━━━━━━━━━━━━━━━━━━
35. Static Third-party Assets
━━━━━━━━━━━━━━━━━━━━

بررسی کن آیا:

Bootstrap

Chart.js

Font Awesome

از CDN می‌آیند یا Local.

برای Production تصمیم فعلی پروژه را حفظ کن.

اگر CDN استفاده شده:

بررسی کن CSP یا Network restrictions باعث خرابی نشوند.

━━━━━━━━━━━━━━━━━━━━
36. Content Security
━━━━━━━━━━━━━━━━━━━━

یک بررسی سبک امنیت Frontend انجام بده.

بررسی:

Inline Script

Inline Event Handler

External CDN

unsafe-eval

unsafe-inline

اما CSP کامل را فقط اگر بدون شکستن پروژه قابل پیاده‌سازی است اضافه کن.

━━━━━━━━━━━━━━━━━━━━
37. File Upload Security
━━━━━━━━━━━━━━━━━━━━

اگر پروژه Upload دارد:

File Type

File Size

Filename

Storage

را بررسی کن.

اگر Upload ندارد:

این بخش را تغییر نده.

━━━━━━━━━━━━━━━━━━━━
38. Export Security
━━━━━━━━━━━━━━━━━━━━

Exportهای:

CSV

XLSX

PDF

را بررسی کن.

Student نباید بتواند آنها را دریافت کند.

Export باید Permission Admin داشته باشد.

نام فایل‌ها نباید شامل اطلاعات حساس غیرضروری باشد.

━━━━━━━━━━━━━━━━━━━━
39. Audit Log Production
━━━━━━━━━━━━━━━━━━━━

ثبت Activityهای مهم را بررسی کن.

حداقل:

Admin Login

Admin Logout

Create Meal

Update Meal

Delete Meal

Create Schedule

Update Schedule

Delete Schedule

Export Report

را در صورت پشتیبانی فعلی ثبت کن.

اگر بعضی Actionها قبلاً ثبت می‌شوند:

Duplicate Logging ایجاد نکن.

━━━━━━━━━━━━━━━━━━━━
40. Timezone
━━━━━━━━━━━━━━━━━━━━

Timezone پروژه را بررسی کن.

تاریخ‌های:

Reservation

Schedule

Report

Audit Log

باید با Timezone مورد نظر پروژه سازگار باشند.

⚠️ Timezone را حدس نزن.

از تنظیم فعلی پروژه استفاده کن و فقط در صورت وجود مشکل اصلاح کن.

━━━━━━━━━━━━━━━━━━━━
41. Persian Date
━━━━━━━━━━━━━━━━━━━━

اگر UI از تاریخ شمسی استفاده می‌کند:

Backend Date استاندارد را تغییر نده.

Presentation Layer مسئول تبدیل نمایش باشد.

گزارش‌ها باید تاریخ صحیح Backend را دریافت کنند.

━━━━━━━━━━━━━━━━━━━━
42. Production Performance
━━━━━━━━━━━━━━━━━━━━

بررسی سبک:

N+1 Queries

Dashboard Queries

Reports Queries

Reservation Queries

Admin Tables

انجام بده.

اگر Query بهینه‌سازی واضحی لازم دارد:

حداقل تغییر امن را انجام بده.

━━━━━━━━━━━━━━━━━━━━
43. Database Indexes
━━━━━━━━━━━━━━━━━━━━

Modelها را بررسی کن.

اگر Index مهمی کاملاً مفقود است:

فقط گزارش کن یا در صورت ضرورت واقعی با احتیاط Migration ایجاد کن.

Indexهای حدسی اضافه نکن.

━━━━━━━━━━━━━━━━━━━━
44. Frontend Production
━━━━━━━━━━━━━━━━━━━━

بررسی کن:

Console Error

Broken JS

404 Static

Broken CSS

Chart Errors

Failed API Requests

وجود نداشته باشند.

━━━━━━━━━━━━━━━━━━━━
45. Browser QA
━━━━━━━━━━━━━━━━━━━━

با Browser واقعی بررسی کن:

Login

Student Dashboard

Meal Schedule

Reservation

My Reservations

Admin Dashboard

Meals

Schedules

Reservations

Students

Reports

Exports

Activity

Logout

━━━━━━━━━━━━━━━━━━━━
46. Responsive QA
━━━━━━━━━━━━━━━━━━━━

حداقل:

360px

576px

768px

992px

1200px

بررسی شود.

صفحات:

Student

Admin

Reports

Export UI

هیچ Horizontal Overflow غیرضروری نداشته باشند.

━━━━━━━━━━━━━━━━━━━━
47. Full Regression
━━━━━━━━━━━━━━━━━━━━

تمام Test Suiteهای موجود را اجرا کن.

Backend

Web

Admin

Desktop

Packaging

نتیجه دقیق را گزارش کن.

━━━━━━━━━━━━━━━━━━━━
48. Static Verification
━━━━━━━━━━━━━━━━━━━━

اجرا کن:

python manage.py collectstatic --noinput

و بررسی کن Staticها بدون Error جمع‌آوری می‌شوند.

━━━━━━━━━━━━━━━━━━━━
49. Production Check
━━━━━━━━━━━━━━━━━━━━

اجرا کن:

python manage.py check

و:

python manage.py check --deploy

و:

python manage.py makemigrations --check

نتایج را ثبت کن.

━━━━━━━━━━━━━━━━━━━━
50. Do Not Deploy Yet
━━━━━━━━━━━━━━━━━━━━

⚠️ در این فاز به هیچ Server واقعی متصل نشو.

⚠️ SSH نکن.

⚠️ Nginx واقعی را تغییر نده.

⚠️ MySQL Production را تغییر نده.

⚠️ DNS را تغییر نده.

⚠️ SSL واقعی نصب نکن.

فقط پروژه را:

Production-Ready

کن و Deployment Documentation آماده کن.

━━━━━━━━━━━━━━━━━━━━
51. Final Report
━━━━━━━━━━━━━━━━━━━━

در پایان یک گزارش مدیریتی بده.

گزارش شامل:

1. وضعیت Production Readiness

2. تنظیمات Production

3. Environment Variables

4. Database

5. Static Files

6. Security

7. Authentication

8. Authorization

9. Logging

10. Backup Documentation

11. Deployment Documentation

12. Export Security

13. Audit Log

14. Performance Review

15. Browser QA

16. Responsive QA

17. Tests

18. manage.py check

19. check --deploy

20. makemigrations --check

21. مواردی که هنوز نیاز به تنظیم Server واقعی دارند

22. مشکلات باقی‌مانده

23. پیشنهاد Phase 8

━━━━━━━━━━━━━━━━━━━━
قوانین نهایی Phase 7
━━━━━━━━━━━━━━━━━━━━

فقط Phase 7 را انجام بده.

وارد Deployment واقعی نشو.

Business Logic را تغییر نده.

Reservation Logic را بازنویسی نکن.

Desktop را تغییر رفتاری نده.

Database را بدون ضرورت تغییر نده.

API موجود را Duplicate نکن.

Secret واقعی داخل Repository قرار نده.

در پایان متوقف شو.
