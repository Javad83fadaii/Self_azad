from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View
from django.views.decorators.csrf import ensure_csrf_cookie

from accounts.models import UserRole


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
    {"label": "غذاها", "url_name": "common:web-admin-home", "icon": "fa-solid fa-bowl-food", "key": "admin-meals"},
    {
        "label": "برنامه غذایی",
        "url_name": "common:web-admin-home",
        "icon": "fa-solid fa-calendar-days",
        "key": "admin-schedules",
    },
    {"label": "رزروها", "url_name": "common:web-admin-home", "icon": "fa-solid fa-clipboard-list", "key": "admin-reservations"},
    {"label": "دانشجویان", "url_name": "common:web-admin-home", "icon": "fa-solid fa-user-graduate", "key": "admin-students"},
    {"label": "گزارش‌ها", "url_name": "common:web-admin-home", "icon": "fa-solid fa-chart-column", "key": "admin-reports"},
    {"label": "تنظیمات", "url_name": "common:web-admin-home", "icon": "fa-solid fa-gear", "key": "admin-settings"},
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
                "login_title": "ورود دانشجو",
                "login_description": "برای ورود به نسخه وب، کد دانشجویی و شماره موبایل خود را وارد کنید.",
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
            return HttpResponseForbidden("You do not have permission to access this page.")
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


class AdminHomePlaceholderView(RoleProtectedTemplateView):
    """Render the admin placeholder page until the admin panel is built."""

    expected_role = UserRole.ADMIN
    active_section = "admin-dashboard"
    template_name = "web/admin/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_heading": "داشبورد مدیریت",
                "page_subtitle": "این صفحه در فاز ۳ برای نمایش shell مدیریتی، sidebar، table و stateها آماده شده است.",
                "admin_notice": "برای جلوگیری از نمایش اطلاعات نادرست، آمار این صفحه به‌صورت Placeholder علامت‌گذاری شده‌اند.",
                "admin_recent_reservations": [
                    {
                        "student": "نمونه رابط کاربری",
                        "meal": "اطلاعات بعداً از API",
                        "status": "Placeholder",
                        "date": "فاز بعد",
                    },
                    {
                        "student": "نمونه جدول",
                        "meal": "بدون داده واقعی",
                        "status": "UI آماده است",
                        "date": "فاز بعد",
                    },
                ],
                "admin_stats": [
                    build_placeholder_stat(
                        label="تعداد دانشجویان",
                        value="Placeholder",
                        tone="primary",
                        note="اطلاعات در فاز بعد از API دریافت خواهد شد.",
                    ),
                    build_placeholder_stat(
                        label="رزروهای امروز",
                        value="Placeholder",
                        tone="success",
                        note="در این فاز آمار واقعی به UI متصل نشده است.",
                    ),
                    build_placeholder_stat(
                        label="غذاهای امروز",
                        value="Placeholder",
                        tone="warning",
                        note="این کارت فقط برای تست UI و spacing ایجاد شده است.",
                    ),
                    build_placeholder_stat(
                        label="رزروهای پیش‌رو",
                        value="Placeholder",
                        tone="info",
                        note="گزارش و جزئیات واقعی در فاز بعد تکمیل می‌شود.",
                    ),
                ],
            }
        )
        return context
