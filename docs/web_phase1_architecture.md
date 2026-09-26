# معماری وب - فاز ۱

## هدف

نسخه Web این سامانه باید از همان Backend فعلی Django + DRF و همان Database مشترک استفاده کند و به هیچ عنوان یک سیستم مستقل با دیتابیس جداگانه نباشد.

معماری هدف:

```text
            MySQL
              ^
              |
        Django + DRF
         /         \
        /           \
Windows Desktop   Web App
   PySide6       HTML/CSS/JS
```

## وضعیت فعلی پروژه

- Backend در مسیر `backend/` قرار دارد.
- Desktop Client در مسیر `desktop/` قرار دارد.
- Desktop اکنون از طریق `API_BASE_URL` به REST API متصل می‌شود.
- احراز هویت فعلی API مبتنی بر `DRF TokenAuthentication` است.
- Database Production از طریق متغیرهای محیطی `DB_*` برای MySQL تنظیم می‌شود.
- در Development در صورت نبودن `DB_NAME`، پروژه با SQLite محلی بالا می‌آید.

## مدل‌ها و منطق موجود که باید حفظ شوند

- `accounts.User`
- `students.Student`
- `meals.Meal`
- `meals.MealSchedule`
- `reservations.Reservation`
- `audit_logs.AuditLog`

منطق رزرو فعلی باید بدون بازنویسی حفظ شود، به‌خصوص:

- فقط یک رزرو فعال برای هر دانشجو در هر روز
- کنترل ظرفیت
- جلوگیری از رزرو روی وعده غیرفعال
- جلوگیری از رزرو برای تاریخ گذشته
- کنترل بازه زمانی رزرو
- استفاده از Transaction و قفل دیتابیس در سرویس رزرو

## APIهای فعلی قابل استفاده برای Web

### Authentication

- `POST /api/auth/login/`
- `POST /api/auth/student/register/`

### Student

- `GET /api/students/me/profile/`
- `GET /api/schedules/upcoming/`
- `GET /api/reservations/my/`
- `POST /api/reservations/`
- `DELETE /api/reservations/{id}/cancel/`

### Admin

- `GET /api/admin/dashboard/`
- `GET /api/admin/reservations/`
- `GET /api/admin/reservations/by-date/`
- `GET /api/admin/reservations/by-meal/`
- `GET /api/admin/reports/daily-meals/`
- `GET /api/admin/reports/students/`
- `GET /api/admin/reports/meals/`
- `GET /api/meals/`
- `GET /api/meals/active/`
- `POST /api/meals/`
- `PUT /api/meals/{id}/`
- `DELETE /api/meals/{id}/`
- `POST /api/schedules/`
- `PUT /api/schedules/{id}/`
- `DELETE /api/schedules/{id}/`

## شکاف‌های فعلی برای Web

### Authentication

نیاز Web:

- `POST /api/auth/logout/`
- `GET /api/auth/me/`

وضعیت فعلی:

- موجود نیست.
- Login فعلی فقط `username + password` را می‌پذیرد.
- برای سناریوی جدید دانشجو (`student_code + phone_number`) باید منطق در Backend توسعه یابد، اما بدون حذف روش فعلی.

### Admin Listing

برای پنل وب ادمین بهتر است endpointهای لیست نیز شفاف‌تر شوند:

- `GET /api/admin/students/`
- `GET /api/admin/meals/`
- `GET /api/admin/schedules/`

در حال حاضر بخشی از این داده‌ها از endpointهای عمومی/موجود قابل دریافت‌اند، اما برای پنل Admin بهتر است namespace اختصاصی و واضح داشته باشند یا حداقل mapping دقیقی برای استفاده مجدد تعریف شود.

## پیشنهاد معماری Web

برای این پروژه، گزینه مناسب در فاز بعد:

- نگه‌داشتن Frontend Web داخل همین پروژه Django
- استفاده از Django Templates برای صفحات، Layout و بوت‌استرپ اولیه
- استفاده از JavaScript ماژولار برای ارتباط با API

ساختار پیشنهادی:

```text
backend/
  templates/
    web/
      base/
      student/
      admin/
      components/
  static/
    web/
      css/
        core/
        student/
        admin/
      js/
        core/
        auth/
        student/
        admin/
        reservations/
        reports/
        utils/
      images/
      vendor/
```

دلیل این انتخاب:

- Backend و Web در یک کدبیس می‌مانند
- مدیریت Static و Template ساده‌تر می‌شود
- استقرار آینده روی سرور ساده‌تر خواهد بود
- برای HTML/CSS/JS خالص، Django Templates کاملاً کافی است
- از ایجاد پروژه Frontend جدا و پیچیدگی CORS غیرضروری جلوگیری می‌شود

## Authentication پیشنهادی برای Browser

در فاز ۱ هنوز پیاده‌سازی جدید انجام نمی‌شود، اما پیشنهاد فنی:

- برای Web Browser به‌جای تکیه مستقیم بر DRF Token در LocalStorage، از Session Authentication با CSRF استفاده شود
- برای Desktop همان Token Authentication فعلی حفظ شود
- در صورت نیاز به SPA یا جداسازی Origin در آینده، JWT فقط با طراحی دقیق Refresh/Expiry بررسی شود

نتیجه:

- Desktop: بدون تغییر
- Web Browser: Session-based پیشنهاد می‌شود

## CORS / CSRF / Environment

برای فاز بعد لازم است:

- `WEB_FRONTEND_URL` و در صورت نیاز `WEB_FRONTEND_ALLOWED_ORIGINS` از env خوانده شوند
- CORS به‌صورت محدود و whitelist-based تنظیم شود
- از `CORS_ALLOW_ALL_ORIGINS = True` استفاده نشود
- اگر Web داخل همان Django serve شود، نیاز CORS بسیار کمتر می‌شود

## کتابخانه‌های سبک پیشنهادی

- `Bootstrap 5 RTL` فقط برای Grid، Form و Componentهای پایه
- `Chart.js` برای نمودارهای Admin
- `Font Awesome` برای آیکن‌ها

از dependencyهای سنگین مانند React/Vue در این پروژه استفاده نشود.

## خط‌مشی فاز ۲

- هیچ مدل یا منطق رزرو فعلی بازنویسی نشود
- APIهای موجود تا جای ممکن reuse شوند
- هر API جدید فقط برای شکاف‌های واقعی اضافه شود
- Desktop App باید بدون تغییر رفتاری باقی بماند
- تست‌های Backend و Desktop بعد از هر تغییر مهم اجرا شوند
