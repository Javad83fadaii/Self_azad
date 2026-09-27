import { get } from "../core/http.js";
import { mapReservationError } from "../reservations/reservation.js";

const page = document.querySelector("#student-profile-page");

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function showFeedback(message, level = "danger") {
    const feedback = document.querySelector("#profile-feedback");
    if (!feedback) {
        return;
    }

    feedback.className = `alert alert-${level} mb-4`;
    feedback.textContent = message;
}

function renderProfileErrorState() {
    const container = document.querySelector("#profile-card");
    if (!container) {
        return;
    }

    container.innerHTML = `
        <div class="empty-state">
            <div class="empty-state__icon"><i class="fa-regular fa-circle-xmark"></i></div>
            <h3 class="empty-state__title">اطلاعات پروفایل در دسترس نیست.</h3>
            <p class="empty-state__message">در حال حاضر دریافت اطلاعات پروفایل انجام نشد. صفحه را دوباره به‌روزرسانی کنید.</p>
        </div>
    `;
}

function renderProfile(profile) {
    const container = document.querySelector("#profile-card");
    if (!container) {
        return;
    }

    container.innerHTML = `
        <div class="profile-card">
            <div class="profile-card__hero">
                <span class="profile-card__avatar" aria-hidden="true">
                    <i class="fa-solid fa-user-graduate"></i>
                </span>
                <div>
                    <h3 class="profile-card__title">${escapeHtml(profile.full_name || "-")}</h3>
                    <p class="profile-card__subtitle">اطلاعات ثبت‌شده برای حساب دانشجویی شما</p>
                </div>
            </div>
            <div class="profile-card__grid">
                <article class="profile-card__item">
                    <span class="profile-card__label">نام</span>
                    <strong>${escapeHtml(profile.first_name || "-")}</strong>
                </article>
                <article class="profile-card__item">
                    <span class="profile-card__label">نام خانوادگی</span>
                    <strong>${escapeHtml(profile.last_name || "-")}</strong>
                </article>
                <article class="profile-card__item">
                    <span class="profile-card__label">کد دانشجویی</span>
                    <strong>${escapeHtml(profile.student_code || "-")}</strong>
                </article>
                <article class="profile-card__item">
                    <span class="profile-card__label">شماره موبایل</span>
                    <strong>${escapeHtml(profile.phone_number || "-")}</strong>
                </article>
            </div>
        </div>
    `;
}

async function loadProfile() {
    try {
        const profile = await get(page.dataset.profileUrl);
        renderProfile(profile);
    } catch (error) {
        renderProfileErrorState();
        showFeedback(mapReservationError(error, "دریافت اطلاعات پروفایل انجام نشد."));
    }
}

if (page) {
    document.addEventListener("DOMContentLoaded", () => {
        loadProfile();
    });
}
