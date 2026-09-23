# University Food Reservation System (UFRS)

UFRS یک سیستم رزرو غذای سلف دانشگاه با معماری `Backend-First` است. در فاز ۳، بخش Backend و REST API پروژه پیاده‌سازی شده و شامل احراز هویت، Roleها، APIهای دانشجو و مدیر، قوانین رزرو و تست‌های API است.

## معماری

```text
PySide6 Desktop Application
        |
        v
Django REST API
        |
        v
Service Layer / Business Rules
        |
        v
Django ORM
        |
        v
MySQL
```

## تکنولوژی‌ها

- Python 3.12+
- Django 5
- Django REST Framework
- DRF Token Authentication
- MySQL
- PySide6

## نصب و اجرا

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

فایل `.env` را در ریشه پروژه بسازید:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=ufrs_db
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=127.0.0.1
DB_PORT=3306
ALLOWED_HOSTS=127.0.0.1,localhost
```

سپس:

```powershell
python backend\manage.py migrate
python backend\manage.py runserver
```

## احراز هویت و Roleها

احراز هویت API با `TokenAuthentication` انجام می‌شود.

Roleهای سیستم:

- `ADMIN`
- `STUDENT`

پس از لاگین، توکن را در هدر زیر بفرستید:

```http
Authorization: Token <token>
```

## مستندات API

Schema استاندارد OpenAPI از این آدرس در دسترس است و endpointهای فاز ۳ را پوشش می‌دهد:

```text
/api/schema/
```

## Business Rules

Backend این قوانین را enforce می‌کند:

- هر دانشجو در هر روز فقط یک رزرو فعال دارد.
- رزرو تکراری ممنوع است.
- ظرفیت بیشتر از ظرفیت Schedule ثبت نمی‌شود.
- غذای غیرفعال قابل رزرو نیست.
- Schedule غیرفعال قابل رزرو نیست.
- تاریخ گذشته قابل رزرو نیست.
- رزرو خارج از بازه `reservation_open_at` تا `reservation_close_at` ممنوع است.
- ایجاد رزرو با `transaction.atomic()` و `select_for_update()` انجام می‌شود تا Race Condition برای ظرفیت و رزرو هم‌زمان کنترل شود.

## Endpointها

### Authentication

- `POST /api/auth/student/register/`
- `POST /api/auth/login/`

### Student API

- `GET /api/students/me/profile/`
- `GET /api/schedules/upcoming/`
- `GET /api/meals/`
- `GET /api/meals/active/`
- `GET /api/reservations/my/`
- `POST /api/reservations/`
- `DELETE /api/reservations/{id}/cancel/`

### Meal API

- `GET /api/meals/`
- `GET /api/meals/active/`
- `POST /api/meals/` `ADMIN`
- `PUT /api/meals/{id}/` `ADMIN`
- `DELETE /api/meals/{id}/` `ADMIN`  -> soft deactivate

### Schedule API

- `GET /api/schedules/upcoming/` `STUDENT`
- `POST /api/schedules/` `ADMIN`
- `PUT /api/schedules/{id}/` `ADMIN`
- `DELETE /api/schedules/{id}/` `ADMIN` -> soft deactivate

### Reservation API

- `POST /api/reservations/` `STUDENT`
- `GET /api/reservations/my/` `STUDENT`
- `DELETE /api/reservations/{id}/cancel/` `STUDENT`
- `GET /api/admin/reservations/` `ADMIN`
- `GET /api/admin/reservations/by-date/?date=YYYY-MM-DD` `ADMIN`
- `GET /api/admin/reservations/by-meal/?meal_id=<id>` `ADMIN`

## نمونه Request/Response

### 1. ثبت دانشجو

```http
POST /api/auth/student/register/
Content-Type: application/json
```

```json
{
  "student_code": "40110001",
  "first_name": "Ali",
  "last_name": "Ahmadi",
  "phone_number": "09120000000",
  "password": "StrongPass123"
}
```

```json
{
  "id": 1,
  "student_code": "40110001",
  "first_name": "Ali",
  "last_name": "Ahmadi",
  "phone_number": "09120000000",
  "is_active": true,
  "user": {
    "id": 1,
    "username": "40110001",
    "role": "STUDENT"
  }
}
```

### 2. لاگین

```http
POST /api/auth/login/
Content-Type: application/json
```

```json
{
  "username": "40110001",
  "password": "StrongPass123"
}
```

```json
{
  "token": "9b0f....",
  "user": {
    "id": 1,
    "username": "40110001",
    "role": "STUDENT"
  }
}
```

### 3. ایجاد رزرو

```http
POST /api/reservations/
Authorization: Token <token>
Content-Type: application/json
```

```json
{
  "meal_schedule_id": 12
}
```

```json
{
  "id": 25,
  "reservation_code": "RSV-AB12CD34EF56",
  "student_id": 1,
  "student_code": "40110001",
  "meal_schedule_id": 12,
  "meal_id": 4,
  "meal_name": "Ghormeh Sabzi",
  "schedule_date": "2026-09-30",
  "reservation_date": "2026-09-30",
  "status": "RESERVED",
  "created_at": "2026-09-23T11:00:00+03:30",
  "cancelled_at": null
}
```

### 4. مشاهده پروفایل دانشجو

```http
GET /api/students/me/profile/
Authorization: Token <token>
```

```json
{
  "id": 1,
  "student_code": "40110001",
  "first_name": "Ali",
  "last_name": "Ahmadi",
  "full_name": "Ali Ahmadi",
  "phone_number": "09120000000",
  "is_active": true,
  "username": "40110001",
  "role": "STUDENT"
}
```

### 5. مشاهده برنامه غذایی آینده

```http
GET /api/schedules/upcoming/
Authorization: Token <token>
```

```json
[
  {
    "id": 12,
    "meal": {
      "id": 4,
      "name": "Ghormeh Sabzi",
      "code": "GHORMEH",
      "description": "Persian stew",
      "image": null,
      "price": "85000.00",
      "is_active": true,
      "created_at": "2026-09-23T10:00:00+03:30",
      "updated_at": "2026-09-23T10:00:00+03:30"
    },
    "date": "2026-09-30",
    "capacity": 100,
    "reserved_count": 28,
    "remaining_capacity": 72,
    "reservation_open_at": "2026-09-25T08:00:00+03:30",
    "reservation_close_at": "2026-09-29T18:00:00+03:30",
    "is_active": true,
    "created_at": "2026-09-23T10:00:00+03:30",
    "updated_at": "2026-09-23T10:00:00+03:30"
  }
]
```

### 6. فیلتر رزروها برای مدیر بر اساس تاریخ

```http
GET /api/admin/reservations/by-date/?date=2026-09-30
Authorization: Token <admin-token>
```

### 7. فیلتر رزروها برای مدیر بر اساس غذا

```http
GET /api/admin/reservations/by-meal/?meal_id=4
Authorization: Token <admin-token>
```

### 8. خطای رزرو تکراری

```json
{
  "detail": "Duplicate reservation for this day is not allowed."
}
```

### 9. خطای ظرفیت پر

```json
{
  "detail": "Schedule capacity is full."
}
```

## اجرای تست‌ها

برای اجرای تست‌های فاز ۳:

```powershell
python backend\manage.py test accounts students meals reservations --settings=config.settings.test
```

## وضعیت فاز ۳

در این فاز این موارد انجام شده‌اند:

- پیاده‌سازی Custom User و Roleهای `ADMIN` و `STUDENT`
- پیاده‌سازی Token Authentication برای API
- پیاده‌سازی Permissionهای جداگانه برای Student و Admin
- پیاده‌سازی APIهای دانشجو، غذا، برنامه غذایی و رزرو
- پیاده‌سازی Service Layer برای منطق رزرو
- اعمال Business Ruleها در Backend
- مستندسازی API در README و `/api/schema/`
- نوشتن و اجرای تست‌های API
- تکمیل تست‌های permission، scope داده‌های دانشجو و فیلترهای مدیریتی رزرو
