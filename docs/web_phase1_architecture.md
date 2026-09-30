اکنون وارد فاز ۵ پروژه University Food Reservation System شو.

فازهای قبلی با موفقیت انجام شده‌اند.

━━━━━━━━━━━━━━━━━━━━
وضعیت فعلی پروژه
━━━━━━━━━━━━━━━━━━━━

Architecture:

Django 5.2
+
Django REST Framework
+
MySQL
+
Django Templates
+
HTML/CSS/JavaScript
+
Bootstrap 5 RTL
+
Font Awesome

Desktop:

PySide6
+
Token Authentication

Web:

Django Templates
+
Session Authentication
+
CSRF

Student Web:

پیاده‌سازی شده و Functional است.

Student Flow:

Login
→
Dashboard
→
Meal Schedule
→
Reservation
→
My Reservations
→
Cancel Reservation
→
Profile

Responsive:

Mobile / Tablet / Desktop بررسی و اصلاح شده است.

Backend Tests:

قبلاً 54 تست پاس شده‌اند.

Desktop Tests:

8 تست پاس شده‌اند.

در فازهای بعد ممکن است تعداد تست‌ها افزایش پیدا کرده باشد؛
قبل از شروع تست‌ها تعداد واقعی را بررسی کن.

━━━━━━━━━━━━━━━━━━━━
هدف Phase 5
━━━━━━━━━━━━━━━━━━━━

در این فاز Admin Panel واقعی و Functional پیاده‌سازی شود.

Admin باید بتواند:

1. داشبورد مدیریتی را ببیند.
2. آمار کلی سامانه را مشاهده کند.
3. غذاها را مدیریت کند.
4. برنامه غذایی روزها را مدیریت کند.
5. رزروهای دانشجویان را مشاهده کند.
6. رزروها را بر اساس تاریخ و غذا بررسی کند.
7. دانشجویان را مشاهده کند.
8. گزارش‌های موجود را مشاهده کند.
9. نمودارهای مدیریتی داشته باشد.
10. همه این موارد را با APIهای موجود انجام دهد.

━━━━━━━━━━━━━━━━━━━━
قانون اصلی Phase 5
━━━━━━━━━━━━━━━━━━━━

⚠️ قبل از هر تغییر:

کدهای زیر را بررسی کن:

accounts
students
meals
reservations
dashboard
reports
audit_logs

همچنین:

API URLs
Serializers
Views
Services
Permissions
Tests

را بررسی کن.

APIهایی که در Backend وجود دارند را دوباره نساز.

اگر API موجود نیاز UI را پوشش می‌دهد:

همان API را مصرف کن.

━━━━━━━━━━━━━━━━━━━━
APIهای Admin موجود
━━━━━━━━━━━━━━━━━━━━

APIهای زیر را بررسی و در صورت مناسب بودن Reuse کن:

GET /api/admin/dashboard/

GET /api/admin/reservations/

GET /api/admin/reservations/by-date/

GET /api/admin/reservations/by-meal/

GET /api/admin/reports/daily-meals/

GET /api/admin/reports/students/

GET /api/admin/reports/meals/

GET /api/admin/students/

GET /api/admin/meals/

GET /api/admin/schedules/

همچنین CRUDهای موجود:

GET /api/meals/

POST /api/meals/

PUT /api/meals/{id}/

DELETE /api/meals/{id}/

POST /api/schedules/

PUT /api/schedules/{id}/

DELETE /api/schedules/{id}/

قبل از استفاده، Response و Request واقعی هر API را از کد بررسی کن.

Payload را حدس نزن.

━━━━━━━━━━━━━━━━━━━━

1. Admin Dashboard
   ━━━━━━━━━━━━━━━━━━━━

صفحه:

/admin/

را از Placeholder به Dashboard واقعی تبدیل کن.

اطلاعات واقعی از:

GET /api/admin/dashboard/

دریافت شود.

Dashboard شامل:

Total Students

Today's Reservations

Today's Meals

Upcoming Reservations

باشد.

اگر API اطلاعات بیشتری برمی‌گرداند:

فقط اطلاعات مرتبط را نمایش بده.

━━━━━━━━━━━━━━━━━━━━
2. Dashboard Statistics Cards
━━━━━━━━━━━━━━━━━━━━

کارت‌های آماری حرفه‌ای طراحی کن.

مثلاً:

دانشجویان فعال

رزروهای امروز

غذاهای امروز

رزروهای آینده

هر Card:

Icon
Title
Value
Description

داشته باشد.

اعداد واقعی Backend باشند.

Mock Data استفاده نکن.

━━━━━━━━━━━━━━━━━━━━
3. Dashboard Date
━━━━━━━━━━━━━━━━━━━━

اگر Dashboard برای تاریخ خاصی است:

تاریخ فعلی را از Backend یا منطق موجود بگیر.

در صورت وجود امکان انتخاب تاریخ:

Date Picker مناسب ایجاد کن.

اما API را بررسی کن و قابلیت‌هایی که Backend پشتیبانی نمی‌کند اختراع نکن.

━━━━━━━━━━━━━━━━━━━━
4. Dashboard Meal Summary
━━━━━━━━━━━━━━━━━━━━

اگر API اطلاعات غذاهای امروز را برمی‌گرداند:

لیستی از غذاهای امروز نمایش بده.

برای هر غذا:

نام غذا

وعده

تعداد رزرو

ظرفیت

ظرفیت باقی‌مانده

وضعیت

نمایش داده شود.

━━━━━━━━━━━━━━━━━━━━
5. Dashboard Charts
━━━━━━━━━━━━━━━━━━━━

از:

Chart.js

استفاده کن.

حداقل نمودارهای مفید:

نمودار تعداد رزرو غذاها

نمودار رزروهای روزانه

در صورت وجود Data مناسب:

نمودار وضعیت رزروها

Chartها باید از API واقعی تغذیه شوند.

Mock Chart نساز.

━━━━━━━━━━━━━━━━━━━━
6. Chart Responsive
━━━━━━━━━━━━━━━━━━━━

Chartها باید روی:

Desktop
Tablet
Mobile

Responsive باشند.

در Mobile:

ارتفاع مناسب داشته باشند.

باعث Horizontal Overflow نشوند.

━━━━━━━━━━━━━━━━━━━━
7. Admin Meal Management
━━━━━━━━━━━━━━━━━━━━

صفحه:

/admin/meals/

ایجاد کن.

هدف:

مدیر بتواند غذاها را مشاهده و مدیریت کند.

از APIهای موجود استفاده کن.

━━━━━━━━━━━━━━━━━━━━
8. Meal List
━━━━━━━━━━━━━━━━━━━━

جدول غذاها:

نام غذا

وضعیت

تاریخ ایجاد در صورت وجود

اطلاعات موجود در API

Actions

باشد.

اگر Model اطلاعات بیشتری دارد و برای مدیریت مفید است:

بعد از بررسی Model نمایش بده.

━━━━━━━━━━━━━━━━━━━━
9. Create Meal
━━━━━━━━━━━━━━━━━━━━

دکمه:

«افزودن غذا»

یک Modal یا Page Form باز کند.

Form دقیقاً بر اساس Serializer فعلی Meal ساخته شود.

هیچ Field را حدس نزن.

Fieldهای واقعی Model/Serializer را بررسی کن.

━━━━━━━━━━━━━━━━━━━━
10. Edit Meal
━━━━━━━━━━━━━━━━━━━━

برای هر غذا:

«ویرایش»

وجود داشته باشد.

PUT:

/api/meals/{id}/

استفاده شود.

Form با اطلاعات فعلی Prefill شود.

━━━━━━━━━━━━━━━━━━━━
11. Delete Meal
━━━━━━━━━━━━━━━━━━━━

برای غذا:

«حذف»

قرار بده.

قبل از حذف:

Confirmation Modal

نمایش بده.

مثلاً:

«آیا از حذف این غذا مطمئن هستید؟»

از DELETE API موجود استفاده کن.

━━━━━━━━━━━━━━━━━━━━
12. Meal Active/Inactive
━━━━━━━━━━━━━━━━━━━━

اگر Model/API وضعیت Active دارد:

امکان مدیریت آن را بر اساس API موجود فراهم کن.

اگر API مستقلی برای Toggle وجود ندارد:

بدون بررسی Serializer و Backend چیزی اختراع نکن.

در صورت نیاز از Update موجود استفاده کن.

━━━━━━━━━━━━━━━━━━━━
13. Meal Search
━━━━━━━━━━━━━━━━━━━━

اگر تعداد غذاها زیاد می‌شود:

Search UI اضافه کن.

Search باید یا:

از Query Parameter پشتیبانی Backend استفاده کند

یا روی داده‌های دریافت‌شده انجام شود.

اگر Backend Search ندارد:

در این فاز Search سمت Client قابل قبول است.

━━━━━━━━━━━━━━━━━━━━
14. Meal Empty State
━━━━━━━━━━━━━━━━━━━━

اگر غذایی وجود ندارد:

«هنوز غذایی ثبت نشده است.»

و Button:

«افزودن غذا»

نمایش بده.

━━━━━━━━━━━━━━━━━━━━
15. Admin Schedule Management
━━━━━━━━━━━━━━━━━━━━

صفحه:

/admin/schedules/

ایجاد کن.

این صفحه برای مدیریت برنامه غذایی است.

مدیر باید بتواند:

تاریخ

غذا

وعده

ظرفیت

بازه رزرو

و وضعیت

را مدیریت کند؛

اما فقط Fieldهایی که واقعاً در Model/Serializer موجود هستند.

━━━━━━━━━━━━━━━━━━━━
16. Schedule List
━━━━━━━━━━━━━━━━━━━━

نمایش:

Date

Meal

Meal Type / Serving

Capacity

Reserved

Remaining

Reservation Start

Reservation End

Status

Actions

اگر Fieldی وجود ندارد:

نمایش نده.

━━━━━━━━━━━━━━━━━━━━
17. Create Schedule
━━━━━━━━━━━━━━━━━━━━

دکمه:

«افزودن برنامه غذایی»

Form ایجاد کن.

از:

POST /api/schedules/

استفاده کن.

Mealها از API دریافت شوند.

مدیر بتواند غذا را انتخاب کند.

━━━━━━━━━━━━━━━━━━━━
18. Edit Schedule
━━━━━━━━━━━━━━━━━━━━

از:

PUT /api/schedules/{id}/

استفاده کن.

اطلاعات فعلی Prefill شوند.

━━━━━━━━━━━━━━━━━━━━
19. Delete Schedule
━━━━━━━━━━━━━━━━━━━━

از:

DELETE /api/schedules/{id}/

استفاده کن.

قبل از حذف Confirmation بگیر.

━━━━━━━━━━━━━━━━━━━━
20. Schedule Calendar / Weekly View
━━━━━━━━━━━━━━━━━━━━

یک View مناسب برای برنامه هفتگی ایجاد کن.

ترجیحاً:

شنبه
یکشنبه
دوشنبه
سه‌شنبه
چهارشنبه
پنجشنبه
جمعه

و برنامه هر روز زیر آن.

اما Date واقعی Backend مرجع باشد.

مدیر باید بتواند به سرعت بفهمد:

هر روز چه غذاهایی دارد.

━━━━━━━━━━━━━━━━━━━━
21. Admin Reservations
━━━━━━━━━━━━━━━━━━━━

صفحه:

/admin/reservations/

ایجاد کن.

API:

GET /api/admin/reservations/

را مصرف کن.

جدول شامل:

Student

Student Code

Phone

Meal

Date

Serving

Reservation Code

Status

Created At

باشد؛

فقط اگر این اطلاعات واقعاً در Response موجود هستند.

━━━━━━━━━━━━━━━━━━━━
22. Reservation Filters
━━━━━━━━━━━━━━━━━━━━

فیلترهای مناسب ایجاد کن.

حداقل:

تاریخ

وعده

غذا

وضعیت

دانشجو

اما فقط در صورتی که Backend از آنها پشتیبانی کند.

اگر API فیلتر Query Parameter دارد:

همان را استفاده کن.

اگر ندارد:

بر اساس Data دریافت‌شده Filtering Client-side انجام بده.

━━━━━━━━━━━━━━━━━━━━
23. Reservations By Date
━━━━━━━━━━━━━━━━━━━━

صفحه/Modal یا View:

«رزروهای یک روز»

با API:

GET /api/admin/reservations/by-date/

پیاده‌سازی کن.

مدیر بتواند یک تاریخ را انتخاب کند.

لیست رزروهای آن روز نمایش داده شود.

━━━━━━━━━━━━━━━━━━━━
24. Reservations By Meal
━━━━━━━━━━━━━━━━━━━━

با:

GET /api/admin/reservations/by-meal/

امکان مشاهده رزروهای مربوط به یک غذا فراهم شود.

اگر Endpoint به Parameter خاصی نیاز دارد:

از Serializer/View واقعی استخراج کن.

حدس نزن.

━━━━━━━━━━━━━━━━━━━━
25. Reservation Detail
━━━━━━━━━━━━━━━━━━━━

در صورت وجود Endpoint یا اطلاعات کافی:

یک Detail Modal برای رزرو ایجاد کن.

اطلاعات کامل رزرو نمایش داده شود.

در این فاز:

ویرایش رزرو دانشجو را انجام نده.

فقط View.

━━━━━━━━━━━━━━━━━━━━
26. Admin Students
━━━━━━━━━━━━━━━━━━━━

صفحه:

/admin/students/

ایجاد کن.

API:

GET /api/admin/students/

استفاده شود.

لیست شامل اطلاعات موجود:

نام

نام خانوادگی

کد دانشجویی

شماره موبایل

وضعیت

تاریخ ثبت

و هر Field مدیریتی مفید موجود باشد.

━━━━━━━━━━━━━━━━━━━━
27. Student Search
━━━━━━━━━━━━━━━━━━━━

Search:

نام

نام خانوادگی

کد دانشجویی

شماره موبایل

در صورت امکان.

اگر Backend Search ندارد:

Client-side Search قابل استفاده است.

━━━━━━━━━━━━━━━━━━━━
28. Student Detail
━━━━━━━━━━━━━━━━━━━━

در صورت وجود اطلاعات کافی:

Student Detail Modal/Page ایجاد کن.

نمایش:

اطلاعات دانشجو

رزروهای اخیر

در صورت موجود بودن API.

اما API جدید فقط در صورت نیاز واقعی ایجاد شود.

━━━━━━━━━━━━━━━━━━━━
29. Admin Reports
━━━━━━━━━━━━━━━━━━━━

صفحه:

/admin/reports/

ایجاد کن.

از APIهای موجود استفاده کن:

/api/admin/reports/daily-meals/

/api/admin/reports/students/

/api/admin/reports/meals/

━━━━━━━━━━━━━━━━━━━━
30. Daily Meal Report
━━━━━━━━━━━━━━━━━━━━

گزارش:

تاریخ

غذا

تعداد رزرو

ظرفیت

باقی‌مانده

در صورت وجود اطلاعات.

━━━━━━━━━━━━━━━━━━━━
31. Student Report
━━━━━━━━━━━━━━━━━━━━

گزارش مرتبط با دانشجویان را از API واقعی نمایش بده.

Fieldهای واقعی Response را بررسی کن.

━━━━━━━━━━━━━━━━━━━━
32. Meal Report
━━━━━━━━━━━━━━━━━━━━

گزارش مربوط به عملکرد غذاها را نمایش بده.

در صورت وجود:

تعداد رزرو

تعداد دفعات استفاده

ظرفیت

و سایر اطلاعات موجود.

━━━━━━━━━━━━━━━━━━━━
33. Reports Charts
━━━━━━━━━━━━━━━━━━━━

برای Reports از Chart.js استفاده کن.

حداقل:

Bar Chart برای تعداد رزرو غذاها

Line Chart برای روند رزروها

در صورت وجود Data مناسب:

Doughnut Chart برای وضعیت‌ها

Chartها باید Dynamic باشند.

━━━━━━━━━━━━━━━━━━━━
34. Date Range
━━━━━━━━━━━━━━━━━━━━

اگر API Reports از بازه تاریخ پشتیبانی می‌کند:

Date From

Date To

اضافه کن.

اگر پشتیبانی نمی‌کند:

API را تغییر نده مگر اینکه واقعاً لازم باشد.

━━━━━━━━━━━━━━━━━━━━
35. Admin Navigation
━━━━━━━━━━━━━━━━━━━━

Sidebar را کامل کن:

داشبورد

غذاها

برنامه غذایی

رزروها

دانشجویان

گزارش‌ها

تنظیمات

فعلاً Settings را فقط Placeholder قرار بده.

━━━━━━━━━━━━━━━━━━━━
36. Active Navigation
━━━━━━━━━━━━━━━━━━━━

صفحه فعلی در Sidebar مشخص باشد.

مثلاً:

Dashboard فعال

Meals فعال

Schedules فعال

و غیره.

━━━━━━━━━━━━━━━━━━━━
37. Admin HTTP Layer
━━━━━━━━━━━━━━━━━━━━

تمام Requestها باید از:

core/http.js

استفاده کنند.

در Admin JS:

fetch مستقیم ممنوع.

━━━━━━━━━━━━━━━━━━━━
38. Admin JS Architecture
━━━━━━━━━━━━━━━━━━━━

ساختار:

static/web/js/admin/

dashboard.js
meals.js
schedules.js
reservations.js
students.js
reports.js

در صورت نیاز:

static/web/js/admin/components/

ایجاد کن.

کدها Modular باشند.

از یک فایل عظیم admin.js خودداری کن.

━━━━━━━━━━━━━━━━━━━━
39. Reusable Admin Components
━━━━━━━━━━━━━━━━━━━━

Componentهای قابل استفاده مجدد:

Data Table

Filter Bar

Pagination

Modal

Confirm Modal

Stats Card

Chart Container

Empty State

Loading State

Error State

Toast / Alert

ایجاد یا Reuse کن.

━━━━━━━━━━━━━━━━━━━━
40. Pagination
━━━━━━━━━━━━━━━━━━━━

اگر API Pagination دارد:

Pagination واقعی پیاده‌سازی کن.

اگر API Pagination ندارد:

Client-side Pagination فقط در صورت نیاز.

Pagination را از خودت به API تحمیل نکن.

━━━━━━━━━━━━━━━━━━━━
41. Loading State
━━━━━━━━━━━━━━━━━━━━

برای تمام صفحات Admin:

Initial Loading

Table Loading

Chart Loading

Form Submit Loading

داشته باش.

━━━━━━━━━━━━━━━━━━━━
42. Error Handling
━━━━━━━━━━━━━━━━━━━━

تمام API Errorها از HTTP Layer عبور کنند.

پیام مناسب نمایش بده.

مثلاً:

«دریافت اطلاعات با مشکل مواجه شد.»

«ثبت غذا با مشکل مواجه شد.»

«برنامه غذایی ذخیره نشد.»

اما Error واقعی Backend را در Console برای Debug حفظ کن.

اطلاعات حساس را در UI نمایش نده.

━━━━━━━━━━━━━━━━━━━━
43. Confirmation
━━━━━━━━━━━━━━━━━━━━

برای عملیات destructive:

Delete Meal

Delete Schedule

از Confirmation Modal استفاده کن.

━━━━━━━━━━━━━━━━━━━━
44. Security
━━━━━━━━━━━━━━━━━━━━

Admin Pages فقط برای:

IsAdminRole

قابل دسترسی باشند.

Student:

نباید Admin UI را ببیند.

حتی اگر URL را مستقیم وارد کند، Backend/Server-side access باید جلوگیری کند.

Frontend Role Check فقط UX است.

Permission Backend مرجع اصلی است.

━━━━━━━━━━━━━━━━━━━━
45. CSRF
━━━━━━━━━━━━━━━━━━━━

POST

PUT

PATCH

DELETE

باید CSRF مناسب داشته باشند.

از HTTP Layer موجود استفاده کن.

CSRF را Disable نکن.

━━━━━━━━━━━━━━━━━━━━
46. Desktop Compatibility
━━━━━━━━━━━━━━━━━━━━

هیچ تغییری نباید:

Token Authentication

Desktop API

Desktop Login

Desktop Reservation

را خراب کند.

Desktop Client نباید تغییر رفتاری داشته باشد.

━━━━━━━━━━━━━━━━━━━━
47. Database
━━━━━━━━━━━━━━━━━━━━

در این فاز:

Schema را تغییر نده.

Migration ایجاد نکن مگر اینکه واقعاً لازم باشد.

Business Logic تغییر نکند.

━━━━━━━━━━━━━━━━━━━━
48. Backend Business Logic
━━━━━━━━━━━━━━━━━━━━

Admin UI فقط Client است.

قوانین اصلی:

Reservation

Capacity

Schedule

Meal

Permission

همچنان در Backend باقی بمانند.

Business Logic را به JavaScript منتقل نکن.

━━━━━━━━━━━━━━━━━━━━
49. Responsive Admin
━━━━━━━━━━━━━━━━━━━━

تمام صفحات Admin را روی:

360px

576px

768px

992px

1200px

بررسی کن.

به ویژه:

Sidebar

Topbar

Tables

Filters

Charts

Forms

Modals

نباید Overflow ایجاد کنند.

━━━━━━━━━━━━━━━━━━━━
50. Mobile Tables
━━━━━━━━━━━━━━━━━━━━

جدول‌های Admin روی Mobile باید:

Responsive

Scrollable

باشند.

از:

.table-responsive

استفاده کن.

اطلاعات مهم نباید به دلیل Width مخفی شوند.

━━━━━━━━━━━━━━━━━━━━
51. Mobile Filters
━━━━━━━━━━━━━━━━━━━━

Filter Bar در Mobile:

Stack

یا

Accordion/Collapse

شود.

Inputها Width مناسب داشته باشند.

━━━━━━━━━━━━━━━━━━━━
52. Browser QA
━━━━━━━━━━━━━━━━━━━━

این فاز حتماً Browser QA واقعی داشته باشد.

صفحات:

/admin/

/admin/meals/

/admin/schedules/

/admin/reservations/

/admin/students/

/admin/reports/

را اجرا کن.

هم Desktop و هم Mobile بررسی شوند.

━━━━━━━━━━━━━━━━━━━━
53. Real Data Test
━━━━━━━━━━━━━━━━━━━━

از Mock Data استفاده نکن.

با Database فعلی:

حداقل:

یک Meal

یک Schedule

چند Student

چند Reservation

داشته باش.

اگر داده تست موجود نیست:

داده تست ایجاد کن یا از Fixture/Test DB استفاده کن؛

اما داده واقعی Production را بدون اجازه تغییر نده.

━━━━━━━━━━━━━━━━━━━━
54. Full Admin Flow
━━━━━━━━━━━━━━━━━━━━

این Flow را دستی تست کن:

Admin Login

↓

Admin Dashboard

↓

مشاهده آمار

↓

Meals

↓

ایجاد غذا

↓

ویرایش غذا

↓

Schedules

↓

ایجاد Schedule

↓

ویرایش Schedule

↓

Reservations

↓

Filter By Date

↓

مشاهده Reservation

↓

Students

↓

مشاهده Student

↓

Reports

↓

مشاهده Chart

━━━━━━━━━━━━━━━━━━━━
55. Regression Tests
━━━━━━━━━━━━━━━━━━━━

بعد از پیاده‌سازی:

تمام Backend Tests

تمام Desktop Tests

را اجرا کن.

تعداد دقیق تست‌ها را گزارش کن.

همچنین تست‌های Admin جدید اضافه کن.

حداقل تست‌ها:

1. Admin Dashboard access

2. Student cannot access Admin Dashboard

3. Admin Meals access

4. Student cannot access Admin Meals

5. Create Meal

6. Update Meal

7. Delete Meal

8. Create Schedule

9. Update Schedule

10. Delete Schedule

11. Admin Reservations

12. Admin Students

13. Admin Reports

14. Admin API permission checks

━━━━━━━━━━━━━━━━━━━━
56. API Regression
━━━━━━━━━━━━━━━━━━━━

تمام APIهای Desktop را نیز بررسی کن.

مخصوصاً:

POST /api/auth/login/

و Reservation APIها.

نباید به دلیل تغییر Admin UI خراب شوند.

━━━━━━━━━━━━━━━━━━━━
57. No Unnecessary Backend Changes
━━━━━━━━━━━━━━━━━━━━

اگر Backend کاملاً API مورد نیاز UI را دارد:

Backend را تغییر نده.

اگر API Response واقعاً ناقص است:

اول دقیقاً مشخص کن چه چیزی کم است.

سپس حداقل تغییر ممکن را انجام بده.

━━━━━━━━━━━━━━━━━━━━
58. Code Quality
━━━━━━━━━━━━━━━━━━━━

کد:

Readable

Modular

Reusable

Maintainable

باشد.

Duplicate JavaScript ایجاد نکن.

Duplicate API Logic ایجاد نکن.

Magic Stringها را تا حد امکان مدیریت کن.

━━━━━━━━━━━━━━━━━━━━
59. Final Verification
━━━━━━━━━━━━━━━━━━━━

قبل از پایان:

python manage.py check

را اجرا کن.

سپس:

تمام Backend Tests

تمام Desktop Tests

تمام Web/Admin Tests

را اجرا کن.

اگر پروژه ابزار Lint/Formatter دارد:

از همان ابزار موجود استفاده کن.

ابزار جدید غیرضروری نصب نکن.

━━━━━━━━━━━━━━━━━━━━
60. Final Report
━━━━━━━━━━━━━━━━━━━━

در پایان فقط گزارش کامل Phase 5 را بده.

گزارش شامل:

1. Admin Dashboard

2. Meal Management

3. Schedule Management

4. Reservation Management

5. Student Management

6. Reports

7. Charts

8. APIهای مصرف‌شده

9. APIهای جدید در صورت وجود

10. Backend Changes

11. Database Changes

12. Migration Changes

13. Templateهای ایجادشده

14. CSSهای ایجادشده

15. JavaScriptهای ایجادشده

16. Componentهای ایجادشده

17. تست‌های جدید

18. تعداد کل Backend Tests

19. تعداد Desktop Tests

20. Browser QA

21. Mobile QA

22. مشکلات باقی‌مانده

23. پیشنهاد Phase 6

━━━━━━━━━━━━━━━━━━━━
قانون نهایی Phase 5
━━━━━━━━━━━━━━━━━━━━

فقط Phase 5 را انجام بده.

وارد امکانات Phase 6 نشو.

در صورت کامل شدن تمام موارد، متوقف شو.

هیچ Business Logic موجود را بدون دلیل تغییر نده.

هیچ API موجود را Duplicate نکن.

هیچ Mock Data را به عنوان اطلاعات واقعی نمایش نده.

Desktop Application باید بدون تغییر رفتاری باقی بماند.
