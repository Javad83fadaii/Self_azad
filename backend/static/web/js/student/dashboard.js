import { get } from "../core/http.js";
import { getReservationStatusMeta, isActiveReservation, mapReservationError } from "../reservations/reservation.js";
import { formatDateTime, formatPersianDate, getTodayIsoDate } from "../utils/date.js";

const page = document.querySelector("#student-dashboard-page");

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function showFeedback(message, level = "danger") {
    const feedback = document.querySelector("#dashboard-feedback");
    if (!feedback) {
        return;
    }

    feedback.className = `alert alert-${level} mb-4`;
    feedback.textContent = message;
}

function clearFeedback() {
    const feedback = document.querySelector("#dashboard-feedback");
    if (!feedback) {
        return;
    }

    feedback.className = "d-none mb-4";
    feedback.textContent = "";
}

function renderStats({ todayReservation, upcomingReservations, schedules }) {
    const scheduleDays = new Set((schedules || []).map((item) => item.date)).size;
    const values = {
        today: todayReservation ? "ثبت شده" : "بدون رزرو",
        upcoming: `${upcomingReservations.length} رزرو`,
        schedule: `${scheduleDays} روز`,
    };

    document.querySelectorAll("[data-stat]").forEach((element) => {
        const key = element.dataset.stat;
        if (key in values) {
            element.textContent = values[key];
        }
    });
}

function renderTodayReservation(todayReservation) {
    const container = document.querySelector("#today-reservation");
    if (!container) {
        return;
    }

    if (!todayReservation) {
        container.innerHTML = `
            <div class="empty-state empty-state--compact">
                <div class="empty-state__icon"><i class="fa-regular fa-calendar-xmark"></i></div>
                <h3 class="empty-state__title">برای امروز رزروی ثبت نشده است.</h3>
                <p class="empty-state__message">برای بررسی برنامه غذایی و ثبت رزرو جدید، برنامه روزهای آینده را مشاهده کنید.</p>
                <a href="${escapeHtml(page.dataset.schedulePageUrl)}" class="btn btn-primary">
                    <i class="fa-solid fa-calendar-days"></i>
                    <span>مشاهده برنامه غذایی</span>
                </a>
            </div>
        `;
        return;
    }

    const statusMeta = getReservationStatusMeta(todayReservation.status, todayReservation.status_label);
    container.innerHTML = `
        <div class="reservation-summary-card">
            <div class="reservation-summary-card__header">
                <div>
                    <h3 class="reservation-summary-card__title">${escapeHtml(todayReservation.meal_name)}</h3>
                    <p class="reservation-summary-card__subtitle">${escapeHtml(formatPersianDate(todayReservation.schedule_date))}</p>
                </div>
                <span class="${statusMeta.className}">${escapeHtml(statusMeta.label)}</span>
            </div>
            <dl class="detail-list">
                <div class="detail-list__item">
                    <dt>کد رزرو</dt>
                    <dd>${escapeHtml(todayReservation.reservation_code)}</dd>
                </div>
                <div class="detail-list__item">
                    <dt>کد غذا</dt>
                    <dd>${escapeHtml(todayReservation.meal_code || "-")}</dd>
                </div>
                <div class="detail-list__item">
                    <dt>زمان ثبت</dt>
                    <dd>${escapeHtml(formatDateTime(todayReservation.created_at))}</dd>
                </div>
            </dl>
        </div>
    `;
}

function renderUpcomingReservations(upcomingReservations) {
    const container = document.querySelector("#upcoming-reservations");
    if (!container) {
        return;
    }

    if (upcomingReservations.length === 0) {
        container.innerHTML = `
            <div class="empty-state empty-state--compact">
                <div class="empty-state__icon"><i class="fa-regular fa-calendar-check"></i></div>
                <h3 class="empty-state__title">رزرو آینده‌ای برای نمایش وجود ندارد.</h3>
                <p class="empty-state__message">پس از ثبت رزرو برای روزهای بعد، فهرست این بخش به‌روزرسانی می‌شود.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <div class="reservation-list">
            ${upcomingReservations
                .map((reservation) => {
                    const statusMeta = getReservationStatusMeta(reservation.status, reservation.status_label);
                    return `
                        <article class="reservation-list-item">
                            <div class="reservation-list-item__content">
                                <div class="reservation-list-item__title-row">
                                    <h3>${escapeHtml(reservation.meal_name)}</h3>
                                    <span class="${statusMeta.className}">${escapeHtml(statusMeta.label)}</span>
                                </div>
                                <p class="reservation-list-item__meta">${escapeHtml(formatPersianDate(reservation.schedule_date))}</p>
                                <p class="reservation-list-item__meta">کد رزرو: ${escapeHtml(reservation.reservation_code)}</p>
                            </div>
                        </article>
                    `;
                })
                .join("")}
        </div>
    `;
}

async function loadDashboard() {
    clearFeedback();

    try {
        const [profile, reservations, schedules] = await Promise.all([
            get(page.dataset.profileUrl),
            get(page.dataset.reservationsUrl),
            get(page.dataset.schedulesUrl),
        ]);

        const today = getTodayIsoDate();
        const activeReservations = (reservations || []).filter(isActiveReservation);
        const todayReservation = activeReservations.find((item) => item.schedule_date === today) || null;
        const upcomingReservations = activeReservations.filter((item) => item.schedule_date > today);

        renderStats({ todayReservation, upcomingReservations, schedules });
        renderTodayReservation(todayReservation);
        renderUpcomingReservations(upcomingReservations);

        const title = document.querySelector(".student-hero__title");
        if (title && profile?.full_name) {
            title.textContent = `سلام، ${profile.full_name}`;
        }
    } catch (error) {
        showFeedback(mapReservationError(error, "دریافت اطلاعات داشبورد انجام نشد."));
        renderTodayReservation(null);
        renderUpcomingReservations([]);
    }
}

if (page) {
    document.addEventListener("DOMContentLoaded", () => {
        loadDashboard();
    });
}
