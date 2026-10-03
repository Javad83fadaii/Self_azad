# راهنمای Backup و Restore دیتابیس Production

این سند فقط strategy و commandهای پیشنهادی برای MySQL را مستند می‌کند. در این فاز هیچ backup واقعی اجرا نشده است.

## هدف

- داشتن backup منظم از دیتابیس Production
- امکان restore سریع و کنترل‌شده
- نگه‌داری نسخه‌های روزانه و هفتگی

## پیش‌فرض‌ها

- دیتابیس Production از MySQL استفاده می‌کند.
- نام دیتابیس و credentialها از Environment خوانده می‌شوند.
- نمونه‌های زیر را باید با مقادیر واقعی سرور جایگزین کنید.

## مسیر پیشنهادی Backup

```text
/var/backups/self_food/mysql/
```

ساختار پیشنهادی فایل‌ها:

```text
/var/backups/self_food/mysql/ufrs_2026-10-03_010000.sql.gz
```

## Command پیشنهادی Backup

نمونه backup فشرده:

```bash
mysqldump \
  --single-transaction \
  --quick \
  --default-character-set=utf8mb4 \
  --host=127.0.0.1 \
  --port=3306 \
  --user=ufrs_user \
  --password \
  ufrs_db | gzip > /var/backups/self_food/mysql/ufrs_$(date +%F_%H%M%S).sql.gz
```

نکات:

- `--single-transaction` برای InnoDB مناسب است و downtime ایجاد نمی‌کند.
- بهتر است پسورد در command line hard-code نشود.
- برای اجرای زمان‌بندی‌شده می‌توان از user محدود backup استفاده کرد.

## زمان‌بندی پیشنهادی

- backup روزانه: هر روز ساعت `01:00`
- backup هفتگی: جمعه ساعت `02:00`
- backup ماهانه: روز اول ماه

نمونه cron:

```cron
0 1 * * * /usr/local/bin/self_food_backup.sh
```

## Retention پیشنهادی

- روزانه: 7 نسخه
- هفتگی: 4 نسخه
- ماهانه: 3 نسخه

قانون نمونه:

- فایل‌های روزانه قدیمی‌تر از 7 روز حذف شوند.
- فایل‌های هفتگی قدیمی‌تر از 30 روز حذف شوند.
- فایل‌های ماهانه قدیمی‌تر از 90 روز حذف شوند.

## اعتبارسنجی Backup

صرف داشتن فایل backup کافی نیست. حداقل این موارد باید بررسی شوند:

1. فایل خروجی خالی نباشد.
2. gzip سالم باشد.
3. restore آزمایشی روی یک دیتابیس staging یا local انجام شود.
4. تعداد جدول‌ها و حجم منطقی backup بررسی شود.

نمونه بررسی سریع:

```bash
gzip -t /var/backups/self_food/mysql/ufrs_2026-10-03_010000.sql.gz
```

## Restore Procedure

1. سرویس application را در بازه نگه‌داری مناسب متوقف یا از دسترس خارج کنید.
2. از دیتابیس فعلی نیز قبل از restore یک backup جدید بگیرید.
3. در صورت restore روی دیتابیس خالی:

```bash
gunzip -c /var/backups/self_food/mysql/ufrs_2026-10-03_010000.sql.gz | mysql \
  --host=127.0.0.1 \
  --port=3306 \
  --user=ufrs_user \
  --password \
  ufrs_db
```

اگر فایل backup بدون gzip باشد:

```bash
mysql --host=127.0.0.1 --port=3306 --user=ufrs_user --password ufrs_db < backup.sql
```

## Restore روی دیتابیس جدید

برای کاهش ریسک، restore اولیه بهتر است روی دیتابیس جدید انجام شود:

```sql
CREATE DATABASE ufrs_restore CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

سپس:

```bash
gunzip -c backup.sql.gz | mysql --host=127.0.0.1 --port=3306 --user=ufrs_user --password ufrs_restore
```

بعد از restore بررسی کنید:

- تعداد جدول‌ها
- وجود داده‌های کلیدی
- صحت login مدیر
- گزارش‌ها و reservationها

## اقلام خارج از Backup دیتابیس

این موارد جدا از MySQL باید بررسی شوند:

- فایل env production
- لاگ‌های مهم در صورت نیاز قانونی/عملیاتی
- فایل‌های media در صورت استفاده واقعی
- snapshot از تنظیمات Nginx/systemd

## سناریوی Incident

در رخداد عملیاتی:

1. زمان خرابی را ثبت کنید.
2. آخرین backup سالم را شناسایی کنید.
3. restore را ابتدا روی staging یا دیتابیس جدید آزمایش کنید.
4. بعد از تأیید، restore production را انجام دهید.
5. سلامت login، dashboard، reservation و reports را smoke test کنید.

## حداقل بازبینی دوره‌ای

- ماهی یک‌بار restore آزمایشی
- بازبینی فضای دیسک backup
- بازبینی retention policy
- بازبینی دسترسی فایل‌های backup
