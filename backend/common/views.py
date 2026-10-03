from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View
from django.views.decorators.csrf import ensure_csrf_cookie

from accounts.models import UserRole
from audit_logs.services import log_action


STUDENT_NAV_ITEMS = [
    {"label": "خانه", "url_name": "common:web-student-home", "icon": "fa-solid fa-house", "key": "student-home"},
    {
        "label": "برنامه غذایی",
        "url_name": "common:web-student-schedule",
        "icon": "fa-solid fa-utensils",
        "key": "student-schedule",
    },
    {
        "label": "رزروهای من",
        "url_name": "common:web-student-reservations",
        "icon": "fa-solid fa-receipt",
        "key": "student-reservations",
    },
    {
        "label": "پروفایل",
        "url_name": "common:web-student-profile",
        "icon": "fa-solid fa-user",
        "key": "student-profile",
    },
]

ADMIN_NAV_ITEMS = [
    {"label": "داشبورد", "url_name": "common:web-admin-home", "icon": "fa-solid fa-gauge", "key": "admin-dashboard"},
    {"label": "غذاها", "url_name": "common:web-admin-meals", "icon": "fa-solid fa-bowl-food", "key": "admin-meals"},
    {
        "label": "برنامه غذایی",
        "url_name": "common:web-admin-schedules",
        "icon": "fa-solid fa-calendar-days",
        "key": "admin-schedules",
    },
    {"label": "رزروها", "url_name": "common:web-admin-reservations", "icon": "fa-solid fa-clipboard-list", "key": "admin-reservations"},
    {"label": "دانشجویان", "url_name": "common:web-admin-students", "icon": "fa-solid fa-user-graduate", "key": "admin-students"},
    {"label": "گزارش‌ها", "url_name": "common:web-admin-reports", "icon": "fa-solid fa-chart-column", "key": "admin-reports"},
    {"label": "فعالیت‌ها", "url_name": "common:web-admin-activity", "icon": "fa-solid fa-clock-rotate-left", "key": "admin-activity"},
    {"label": "تنظیمات", "url_name": "common:web-admin-settings", "icon": "fa-solid fa-gear", "key": "admin-settings"},
]


def build_user_display_name(user) -> str:
    student_profile = getattr(user, "student_profile", None)
    if student_profile is not None and student_profile.full_name.strip():
        return student_profile.full_name.strip()
    full_name = user.get_full_name().strip()
    return full_name or user.username


def build_role_label(role: str | None) -> str:
    if role == UserRole.ADMIN:
        return "مدیر سامانه"
    if role == UserRole.STUDENT:
        return "دانشجو"
    return "مهمان"


def build_navigation(request, *, role: str | None, active_section: str | None) -> list[dict[str, object]]:
    items = STUDENT_NAV_ITEMS if role == UserRole.STUDENT else ADMIN_NAV_ITEMS if role == UserRole.ADMIN else []
    navigation: list[dict[str, object]] = []
    for item in items:
        navigation.append(
            {
                **item,
                "url": reverse_lazy(item["url_name"]),
                "is_active": item["key"] == active_section,
            }
        )
    return navigation


def build_placeholder_stat(*, label: str, value: str, tone: str, note: str) -> dict[str, str]:
    return {
        "label": label,
        "value": value,
        "tone": tone,
        "note": note,
    }


def build_student_page_context(*, user, heading: str, subtitle: str) -> dict[str, object]:
    student = getattr(user, "student_profile", None)
    student_name = student.full_name if student is not None else build_user_display_name(user)
    return {
        "student_name": student_name,
        "student_code": student.student_code if student is not None else None,
        "page_heading": heading,
        "page_subtitle": subtitle,
    }


def build_admin_page_context(*, heading: str, subtitle: str) -> dict[str, str]:
    return {
        "page_heading": heading,
        "page_subtitle": subtitle,
    }


class WebEntryRedirectView(View):
    """Redirect the project root to the initial web login page."""

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and getattr(request.user, "role", None) == UserRole.STUDENT:
            return redirect("common:web-student-home")
        if request.user.is_authenticated and getattr(request.user, "role", None) == UserRole.ADMIN:
            return redirect("common:web-admin-home")
        return redirect("common:web-login")


@method_decorator(ensure_csrf_cookie, name="dispatch")
class StudentLoginPageView(TemplateView):
    """Render the initial student login page for the web app."""

    template_name = "web/auth/login.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and getattr(request.user, "role", None) == UserRole.STUDENT:
            return redirect("common:web-student-home")
        if request.user.is_authenticated and getattr(request.user, "role", None) == UserRole.ADMIN:
            return redirect("common:web-admin-home")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "web_app_name": "سامانه رزرو غذای دانشگاه",
                "web_brand_subtitle": "سامانه رزرو غذای دانشجویان",
                "login_title": "ورود به سامانه",
                "login_description": "دانشجویان با کد دانشجویی و موبایل و مدیران با نام کاربری و رمز عبور وارد نسخه وب می‌شوند.",
            }
        )
        return context


@method_decorator(ensure_csrf_cookie, name="dispatch")
class RoleProtectedTemplateView(LoginRequiredMixin, TemplateView):
    """Render a placeholder page only for the expected authenticated role."""

    expected_role: str | None = None
    active_section: str | None = None
    login_url = reverse_lazy("common:web-login")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if self.expected_role and getattr(request.user, "role", None) != self.expected_role:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update(
            {
                "web_app_name": "سامانه رزرو غذای دانشگاه",
                "web_brand_subtitle": "سامانه رزرو غذای دانشجویان",
                "current_role": getattr(user, "role", None),
                "current_role_label": build_role_label(getattr(user, "role", None)),
                "current_user_name": build_user_display_name(user),
                "navigation_items": build_navigation(
                    self.request,
                    role=getattr(user, "role", None),
                    active_section=self.active_section,
                ),
                "auth_me_url": reverse_lazy("accounts:me"),
                "logout_url": reverse_lazy("accounts:logout"),
                "login_url": reverse_lazy("common:web-login"),
                "student_home_url": reverse_lazy("common:web-student-home"),
                "admin_home_url": reverse_lazy("common:web-admin-home"),
            }
        )
        return context


class StudentHomePlaceholderView(RoleProtectedTemplateView):
    """Render the authenticated student dashboard shell."""

    expected_role = UserRole.STUDENT
    active_section = "student-home"
    template_name = "web/student/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = getattr(self.request.user, "student_profile", None)
        student_name = student.full_name if student is not None else build_user_display_name(self.request.user)
        context.update(
            build_student_page_context(
                user=self.request.user,
                heading=f"سلام، {student_name}",
                subtitle="نمای کلی رزرو امروز، رزروهای آینده و دسترسی سریع به برنامه غذایی و پروفایل.",
            )
        )
        return context


class StudentScheduleView(RoleProtectedTemplateView):
    """Render the student schedule page shell."""

    expected_role = UserRole.STUDENT
    active_section = "student-schedule"
    template_name = "web/student/schedule.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            build_student_page_context(
                user=self.request.user,
                heading="برنامه غذایی",
                subtitle="لیست روزهای آینده، ظرفیت باقیمانده و امکان ثبت رزرو از روی برنامه غذایی.",
            )
        )
        return context


class StudentReservationListView(RoleProtectedTemplateView):
    """Render the authenticated student's reservation list page shell."""

    expected_role = UserRole.STUDENT
    active_section = "student-reservations"
    template_name = "web/student/reservations.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            build_student_page_context(
                user=self.request.user,
                heading="رزروهای من",
                subtitle="مشاهده رزروهای ثبت‌شده، وضعیت هر رزرو و امکان لغو رزرو فعال.",
            )
        )
        return context


class StudentProfilePageView(RoleProtectedTemplateView):
    """Render the authenticated student's profile page shell."""

    expected_role = UserRole.STUDENT
    active_section = "student-profile"
    template_name = "web/student/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            build_student_page_context(
                user=self.request.user,
                heading="پروفایل دانشجو",
                subtitle="اطلاعات هویتی و دانشگاهی ثبت‌شده برای حساب کاربری شما.",
            )
        )
        return context


class AdminTemplateView(RoleProtectedTemplateView):
    expected_role = UserRole.ADMIN

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        if response.status_code == 200:
            log_action(
                user=self.request.user,
                action="ADMIN_PAGE_VIEW",
                description=f"نمایش صفحه {context.get('page_heading', 'مدیریت')}",
            )
        return response


class AdminHomeView(AdminTemplateView):
    """Render the admin dashboard page."""

    active_section = "admin-dashboard"
    template_name = "web/admin/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                **build_admin_page_context(heading="داشبورد مدیریت", subtitle="آمار زنده، خلاصه غذاهای امروز و نمودارهای مدیریتی سامانه."),
                "admin_page": "dashboard",
            }
        )
        return context


class AdminMealsView(AdminTemplateView):
    """Render the admin meal management page."""

    active_section = "admin-meals"
    template_name = "web/admin/meals.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                **build_admin_page_context(heading="مدیریت غذاها", subtitle="مشاهده، جستجو، ایجاد، ویرایش و غیرفعال‌سازی غذاها از طریق APIهای موجود."),
                "admin_page": "meals",
            }
        )
        return context


class AdminSchedulesView(AdminTemplateView):
    """Render the admin schedule management page."""

    active_section = "admin-schedules"
    template_name = "web/admin/schedules.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                **build_admin_page_context(heading="مدیریت برنامه غذایی", subtitle="بررسی برنامه روزانه و هفتگی، ظرفیت‌ها و بازه‌های رزرو غذاها."),
                "admin_page": "schedules",
            }
        )
        return context


class AdminReservationsView(AdminTemplateView):
    """Render the admin reservation page."""

    active_section = "admin-reservations"
    template_name = "web/admin/reservations.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                **build_admin_page_context(heading="مدیریت رزروها", subtitle="مشاهده رزروهای دانشجویان، فیلتر بر اساس تاریخ و غذا و بررسی جزئیات هر رزرو."),
                "admin_page": "reservations",
            }
        )
        return context


class AdminStudentsView(AdminTemplateView):
    """Render the admin student page."""

    active_section = "admin-students"
    template_name = "web/admin/students.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                **build_admin_page_context(heading="مدیریت دانشجویان", subtitle="فهرست دانشجویان، جستجوی مدیریتی و مشاهده رزروهای اخیر هر دانشجو."),
                "admin_page": "students",
            }
        )
        return context


class AdminReportsView(AdminTemplateView):
    """Render the admin reports page."""

    active_section = "admin-reports"
    template_name = "web/admin/reports.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                **build_admin_page_context(heading="گزارش‌ها", subtitle="گزارش روزانه غذاها، گزارش دانشجویان و عملکرد غذاها همراه با نمودارهای پویا."),
                "admin_page": "reports",
            }
        )
        return context


class AdminActivityView(AdminTemplateView):
    """Render the admin activity page."""

    active_section = "admin-activity"
    template_name = "web/admin/activity.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                **build_admin_page_context(heading="گزارش فعالیت‌ها", subtitle="مشاهده رخدادهای مدیریتی ثبت‌شده با فیلتر کاربر، عمل و تاریخ."),
                "admin_page": "activity",
            }
        )
        return context


class AdminSettingsPlaceholderView(AdminTemplateView):
    """Render the admin settings placeholder page."""

    active_section = "admin-settings"
    template_name = "web/admin/settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                **build_admin_page_context(heading="تنظیمات", subtitle="این بخش فعلاً به‌صورت placeholder نگه داشته شده و در فاز بعد تکمیل می‌شود."),
                "admin_page": "settings",
            }
        )
        return context
