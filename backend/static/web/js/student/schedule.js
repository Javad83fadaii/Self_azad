import { get } from "../core/http.js";
import {
    createReservation,
    getReservationStatusMeta,
    getScheduleStateMeta,
    isActiveReservation,
    mapReservationError,
} from "../reservations/reservation.js";
import { formatPersianDate, formatPersianWeekday, formatTime } from "../utils/date.js";

const page = document.querySelector("#student-schedule-page");

let selectedSchedule = null;
let isSubmitting = false;
let reservationsCache = [];
let schedulesCache = [];

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function getActiveReservationByDate() {
    const map = new Map();
    reservationsCache.filter(isActiveReservation).forEach((reservation) => {
        map.set(reservation.schedule_date, reservation);
    });
    return map;
}

function showFeedback(message, level = "danger") {
    const feedback = document.querySelector("#schedule-feedback");
    if (!feedback) {
        return;
    }

    feedback.className = `alert alert-${level} mb-4`;
    feedback.textContent = message;
}

function clearFeedback() {
    const feedback = document.querySelector("#schedule-feedback");
    if (!feedback) {
        return;
    }

    feedback.className = "d-none mb-4";
    feedback.textContent = "";
}

function getMealVisual(schedule) {
    if (schedule.meal_image_url) {
        return `
            <img
                src="${escapeHtml(schedule.meal_image_url)}"
                alt="${escapeHtml(schedule.meal_name)}"
                class="meal-card__image"
                loading="lazy"
            >
        `;
    }

    return `
        <div class="meal-card__placeholder" aria-hidden="true">
            <i class="fa-solid fa-bowl-rice"></i>
        </div>
    `;
}

function getReservationWindowText(schedule, reservedForDay) {
    if (reservedForDay) {
        const statusMeta = getReservationStatusMeta(reservedForDay.status, reservedForDay.status_label);
        return {
            tone: "info",
            message: `برای این روز قبلاً رزرو ثبت شده است. وضعیت فعلی: ${statusMeta.label}`,
        };
    }

    if (schedule.reservation_state === "FULL") {
        return {
            tone: "danger",
            message: "ظرفیت تکمیل است.",
        };
    }

    if (schedule.reservation_state === "NOT_OPEN") {
        return {
            tone: "warning",
            message: `رزرو هنوز فعال نشده است. شروع رزرو: ${formatTime(schedule.reservation_open_at)}`,
        };
    }

    if (schedule.reservation_state === "CLOSED") {
        return {
            tone: "secondary",
            message: "مهلت رزرو به پایان رسیده است.",
        };
    }

    return {
        tone: "success",
        message: "امکان ثبت رزرو برای این غذا فعال است.",
    };
}

function groupSchedulesByDate(schedules) {
    const groups = new Map();
    (schedules || []).forEach((schedule) => {
        const items = groups.get(schedule.date) || [];
        items.push(schedule);
        groups.set(schedule.date, items);
    });
    return groups;
}

function renderSchedules() {
    const container = document.querySelector("#schedule-groups");
    if (!container) {
        return;
    }

    if (!schedulesCache.length) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state__icon"><i class="fa-regular fa-calendar-xmark"></i></div>
                <h3 class="empty-state__title">برنامه غذایی برای روزهای آینده ثبت نشده است.</h3>
                <p class="empty-state__message">در حال حاضر هیچ برنامه غذایی فعالی برای رزرو در روزهای آینده وجود ندارد.</p>
            </div>
        `;
        return;
    }

    const activeReservationByDate = getActiveReservationByDate();
    const groupedSchedules = groupSchedulesByDate(schedulesCache);

    container.innerHTML = `
        <div class="schedule-groups">
            ${Array.from(groupedSchedules.entries())
                .map(([date, items]) => {
                    return `
                        <section class="schedule-day-group">
                            <header class="schedule-day-group__header">
                                <div>
                                    <span class="schedule-day-group__weekday">${escapeHtml(formatPersianWeekday(date))}</span>
                                    <h3 class="schedule-day-group__date">${escapeHtml(formatPersianDate(date, { withWeekday: false }))}</h3>
                                </div>
                                <span class="status-badge status-badge--soft">${items.length} غذا</span>
                            </header>
                            <div class="meal-card-grid">
                                ${items
                                    .map((schedule) => {
                                        const reservedForDay = activeReservationByDate.get(schedule.date);
                                        const stateMeta = getScheduleStateMeta(schedule.reservation_state);
                                        const windowText = getReservationWindowText(schedule, reservedForDay);
                                        const isReservedThisSchedule = reservedForDay?.meal_schedule_id === schedule.id;
                                        const disableReserve = !schedule.is_reservable || Boolean(reservedForDay) || isSubmitting;
                                        const buttonLabel = isReservedThisSchedule
                                            ? "رزرو شده"
                                            : reservedForDay
                                              ? "رزرو این روز ثبت شده"
                                              : schedule.reservation_state === "FULL"
                                                ? "ظرفیت تکمیل است"
                                                : "رزرو غذا";

                                        return `
                                            <article class="meal-card">
                                                <div class="meal-card__media">
                                                    ${getMealVisual(schedule)}
                                                </div>
                                                <div class="meal-card__body">
                                                    <div class="meal-card__header">
                                                        <div>
                                                            <h4 class="meal-card__title">${escapeHtml(schedule.meal_name)}</h4>
                                                            <p class="meal-card__subtitle">کد غذا: ${escapeHtml(schedule.meal_code)}</p>
                                                        </div>
                                                        <span class="${stateMeta.className}">${escapeHtml(stateMeta.label)}</span>
                                                    </div>
                                                    <p class="meal-card__description">${escapeHtml(schedule.meal_description || "توضیحی برای این غذا ثبت نشده است.")}</p>
                                                    <dl class="detail-list">
                                                        <div class="detail-list__item">
                                                            <dt>تاریخ</dt>
                                                            <dd>${escapeHtml(formatPersianDate(schedule.date))}</dd>
                                                        </div>
                                                        <div class="detail-list__item">
                                                            <dt>ظرفیت کل</dt>
                                                            <dd>${escapeHtml(schedule.capacity)}</dd>
                                                        </div>
                                                        <div class="detail-list__item">
                                                            <dt>رزرو شده</dt>
                                                            <dd>${escapeHtml(schedule.reserved_count)}</dd>
                                                        </div>
                                                        <div class="detail-list__item">
                                                            <dt>باقی‌مانده</dt>
                                                            <dd>${escapeHtml(schedule.remaining_capacity)}</dd>
                                                        </div>
                                                    </dl>
                                                    <div class="meal-card__footer">
                                                        <p class="state-note state-note--${windowText.tone}">${escapeHtml(windowText.message)}</p>
                                                        <button
                                                            type="button"
                                                            class="btn btn-primary w-100"
                                                            data-reserve-schedule="${schedule.id}"
                                                            ${disableReserve ? "disabled" : ""}
                                                        >
                                                            <i class="fa-solid fa-bowl-food"></i>
                                                            <span>${escapeHtml(buttonLabel)}</span>
                                                        </button>
                                                    </div>
                                                </div>
                                            </article>
                                        `;
                                    })
                                    .join("")}
                            </div>
                        </section>
                    `;
                })
                .join("")}
        </div>
    `;
}

async function loadSchedules() {
    const container = document.querySelector("#schedule-groups");
    if (container) {
        container.textContent = "در حال دریافت برنامه غذایی...";
    }

    try {
        const [schedules, reservations] = await Promise.all([
            get(page.dataset.schedulesUrl),
            get(page.dataset.reservationsUrl),
        ]);
        schedulesCache = schedules || [];
        reservationsCache = reservations || [];
        renderSchedules();
    } catch (error) {
        schedulesCache = [];
        reservationsCache = [];
        renderSchedules();
        showFeedback(mapReservationError(error, "دریافت برنامه غذایی انجام نشد."));
    }
}

function setSubmitLoading(isLoading) {
    isSubmitting = isLoading;
    const confirmButton = document.querySelector("#confirm-reserve-button");
    if (confirmButton) {
        confirmButton.disabled = isLoading;
        confirmButton.textContent = isLoading ? "در حال ثبت رزرو..." : "تأیید رزرو";
    }
}

function populateModal(schedule) {
    document.querySelector('[data-confirm="meal-name"]').textContent = schedule.meal_name;
    document.querySelector('[data-confirm="schedule-date"]').textContent = formatPersianDate(schedule.date);
    document.querySelector('[data-confirm="meal-code"]').textContent = schedule.meal_code;
}

function getModalInstance() {
    const modalElement = document.querySelector("#reserveMealModal");
    if (!modalElement || !window.bootstrap) {
        return null;
    }

    return window.bootstrap.Modal.getOrCreateInstance(modalElement);
}

async function handleReservationConfirm() {
    if (!selectedSchedule || isSubmitting) {
        return;
    }

    setSubmitLoading(true);
    clearFeedback();

    try {
        const reservation = await createReservation({
            url: page.dataset.createReservationUrl,
            mealScheduleId: selectedSchedule.id,
            csrfUrl: page.dataset.csrfUrl,
        });

        const modal = getModalInstance();
        if (modal) {
            modal.hide();
        }

        showFeedback(
            reservation?.reservation_code
                ? `رزرو غذا با موفقیت ثبت شد. کد رزرو: ${reservation.reservation_code}`
                : "رزرو غذا با موفقیت ثبت شد.",
            "success",
        );
        selectedSchedule = null;
        await loadSchedules();
    } catch (error) {
        showFeedback(mapReservationError(error));
    } finally {
        setSubmitLoading(false);
    }
}

function bindActions() {
    document.addEventListener("click", (event) => {
        const refreshButton = event.target.closest('[data-action="refresh-schedules"]');
        if (refreshButton) {
            clearFeedback();
            loadSchedules();
            return;
        }

        const reserveButton = event.target.closest("[data-reserve-schedule]");
        if (!reserveButton) {
            return;
        }

        const scheduleId = Number(reserveButton.dataset.reserveSchedule);
        selectedSchedule = schedulesCache.find((item) => item.id === scheduleId) || null;
        if (!selectedSchedule) {
            return;
        }

        populateModal(selectedSchedule);
        const modal = getModalInstance();
        if (modal) {
            modal.show();
        }
    });

    const confirmButton = document.querySelector("#confirm-reserve-button");
    if (confirmButton) {
        confirmButton.addEventListener("click", () => {
            handleReservationConfirm();
        });
    }
}

if (page) {
    document.addEventListener("DOMContentLoaded", () => {
        bindActions();
        loadSchedules();
    });
}
