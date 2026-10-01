from __future__ import annotations

from django.http import HttpRequest, JsonResponse
from django.shortcuts import render


def _is_api_request(request: HttpRequest) -> bool:
    return request.path.startswith("/api/")


def _render_error_page(request: HttpRequest, *, status_code: int, title: str, message: str):
    if _is_api_request(request):
        return JsonResponse({"detail": message}, status=status_code)
    return render(
        request,
        "web/errors/error.html",
        {
            "status_code": status_code,
            "page_title": title,
            "page_message": message,
        },
        status=status_code,
    )


def bad_request(request: HttpRequest, exception):
    return _render_error_page(
        request,
        status_code=400,
        title="درخواست نامعتبر",
        message="درخواست ارسال‌شده معتبر نیست. لطفاً اطلاعات را بررسی و دوباره تلاش کنید.",
    )


def permission_denied(request: HttpRequest, exception):
    return _render_error_page(
        request,
        status_code=403,
        title="دسترسی غیرمجاز",
        message="شما اجازه دسترسی به این بخش را ندارید.",
    )


def page_not_found(request: HttpRequest, exception):
    return _render_error_page(
        request,
        status_code=404,
        title="صفحه پیدا نشد",
        message="مسیر درخواستی پیدا نشد یا دیگر در دسترس نیست.",
    )


def server_error(request: HttpRequest):
    return _render_error_page(
        request,
        status_code=500,
        title="خطای داخلی سرور",
        message="یک خطای داخلی رخ داده است. لطفاً کمی بعد دوباره تلاش کنید.",
    )


def csrf_failure(request: HttpRequest, reason: str = ""):
    detail = "اعتبارسنجی CSRF انجام نشد. لطفاً صفحه را تازه‌سازی کرده و دوباره تلاش کنید."
    return _render_error_page(
        request,
        status_code=403,
        title="نشست نامعتبر",
        message=detail,
    )
