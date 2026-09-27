import { get } from "../core/http.js";
import {
    buildCancelUrl,
    cancelReservation,
    getReservationStatusMeta,
    mapReservationError,
} from "../reservations/reservation.js";
import { formatDateTime, formatPersianDate } from "../utils/date.js";

const page = document.querySelector("#student-reservations-page");

let reservationsCache = [];
let selectedReservation = null;
let isCancelling = false;

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function showFeedback(message, level = "danger") {
    const feedback = document.querySelector("#reservations-feedback");
    if (!feedback) {
        return;
    }

    feedback.className = `alert alert-${level} mb-4`;
    feedback.textContent = message;
}

function clearFeedback() {
    const feedback = document.querySelector("#reservations-feedback");
    if (!feedback) {
        return;
    }

    feedback.className = "d-none mb-4";
    feedback.textContent = "";
}

function renderReservations() {
    const container = document.querySelector("#reservations-list");
    if (!container) {
        return;
    }

    if (!reservationsCache.length) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state__icon"><i class="fa-regular fa-rectangle-list"></i></div>
                <h3 class="empty-state__title">هنوز رزروی ثبت نکرده‌اید.</h3>
                <p class="empty-state__message">پس از ثبت اولین رزرو، جزئیات آن در این صفحه نمایش داده می‌شود.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <div class="reservation-table-wrapper">
            <table class="table reservation-table align-middle">
                <thead>
                    <tr>
                        <th>غذا</th>
                        <th>تاریخ</th>
                        <th>کد رزرو</th>
                        <th>وضعیت</th>
                        <th>زمان ثبت</th>
                        <th>عملیات</th>
                    </tr>
                </thead>
                <tbody>
                    ${reservationsCache
                        .map((reservation) => {
                            const statusMeta = getReservationStatusMeta(reservation.status, reservation.status_label);
                            return `
                                <tr>
                                    <td>
                                        <div class="table-title-cell">
                                            <strong>${escapeHtml(reservation.meal_name)}</strong>
                                            <span>${escapeHtml(reservation.meal_code || "-")}</span>
                                        </div>
                                    </td>
                                    <td>${escapeHtml(formatPersianDate(reservation.schedule_date))}</td>
                                    <td>${escapeHtml(reservation.reservation_code)}</td>
                                    <td><span class="${statusMeta.className}">${escapeHtml(statusMeta.label)}</span></td>
                                    <td>${escapeHtml(formatDateTime(reservation.created_at))}</td>
                                    <td>
                                        ${
                                            reservation.can_cancel
                                                ? `
                                                    <button
                                                        type="button"
                                                        class="btn btn-outline-danger btn-sm"
                                                        data-cancel-reservation="${reservation.id}"
                                                        ${isCancelling ? "disabled" : ""}
                                                    >
                                                        <i class="fa-solid fa-ban"></i>
                                                        <span>لغو رزرو</span>
                                                    </button>
                                                `
                                                : '<span class="text-muted small">بدون عملیات</span>'
                                        }
                                    </td>
                                </tr>
                            `;
                        })
                        .join("")}
                </tbody>
            </table>
        </div>
        <div class="reservation-mobile-list">
            ${reservationsCache
                .map((reservation) => {
                    const statusMeta = getReservationStatusMeta(reservation.status, reservation.status_label);
                    return `
                        <article class="reservation-mobile-card">
                            <div class="reservation-mobile-card__header">
                                <div>
                                    <h3>${escapeHtml(reservation.meal_name)}</h3>
                                    <p>${escapeHtml(formatPersianDate(reservation.schedule_date))}</p>
                                </div>
                                <span class="${statusMeta.className}">${escapeHtml(statusMeta.label)}</span>
                            </div>
                            <dl class="detail-list">
                                <div class="detail-list__item">
                                    <dt>کد رزرو</dt>
                                    <dd>${escapeHtml(reservation.reservation_code)}</dd>
                                </div>
                                <div class="detail-list__item">
                                    <dt>زمان ثبت</dt>
                                    <dd>${escapeHtml(formatDateTime(reservation.created_at))}</dd>
                                </div>
                            </dl>
                            ${
                                reservation.can_cancel
                                    ? `
                                        <button
                                            type="button"
                                            class="btn btn-outline-danger w-100"
                                            data-cancel-reservation="${reservation.id}"
                                            ${isCancelling ? "disabled" : ""}
                                        >
                                            <i class="fa-solid fa-ban"></i>
                                            <span>لغو رزرو</span>
                                        </button>
                                    `
                                    : ""
                            }
                        </article>
                    `;
                })
                .join("")}
        </div>
    `;
}

async function loadReservations() {
    const container = document.querySelector("#reservations-list");
    if (container) {
        container.textContent = "در حال دریافت رزروها...";
    }

    try {
        reservationsCache = await get(page.dataset.reservationsUrl);
        renderReservations();
    } catch (error) {
        reservationsCache = [];
        renderReservations();
        showFeedback(mapReservationError(error, "دریافت رزروهای شما انجام نشد."));
    }
}

function populateModal(reservation) {
    document.querySelector('[data-confirm="meal-name"]').textContent = reservation.meal_name;
    document.querySelector('[data-confirm="schedule-date"]').textContent = formatPersianDate(reservation.schedule_date);
    document.querySelector('[data-confirm="reservation-code"]').textContent = reservation.reservation_code;
}

function getModalInstance() {
    const modalElement = document.querySelector("#cancelReservationModal");
    if (!modalElement || !window.bootstrap) {
        return null;
    }

    return window.bootstrap.Modal.getOrCreateInstance(modalElement);
}

function setCancelLoading(isLoading) {
    isCancelling = isLoading;
    const button = document.querySelector("#confirm-cancel-button");
    if (button) {
        button.disabled = isLoading;
        button.textContent = isLoading ? "در حال لغو..." : "لغو رزرو";
    }
}

async function handleCancelConfirm() {
    if (!selectedReservation || isCancelling) {
        return;
    }

    clearFeedback();
    setCancelLoading(true);

    try {
        await cancelReservation({
            url: buildCancelUrl(page.dataset.cancelUrlTemplate, selectedReservation.id),
            csrfUrl: page.dataset.csrfUrl,
        });
        const modal = getModalInstance();
        if (modal) {
            modal.hide();
        }
        showFeedback("رزرو با موفقیت لغو شد.", "success");
        selectedReservation = null;
        await loadReservations();
    } catch (error) {
        showFeedback(mapReservationError(error, "لغو رزرو انجام نشد."));
    } finally {
        setCancelLoading(false);
    }
}

function bindActions() {
    document.addEventListener("click", (event) => {
        const refreshButton = event.target.closest('[data-action="refresh-reservations"]');
        if (refreshButton) {
            clearFeedback();
            loadReservations();
            return;
        }

        const cancelButton = event.target.closest("[data-cancel-reservation]");
        if (!cancelButton) {
            return;
        }

        const reservationId = Number(cancelButton.dataset.cancelReservation);
        selectedReservation = reservationsCache.find((item) => item.id === reservationId) || null;
        if (!selectedReservation) {
            return;
        }

        populateModal(selectedReservation);
        const modal = getModalInstance();
        if (modal) {
            modal.show();
        }
    });

    const confirmButton = document.querySelector("#confirm-cancel-button");
    if (confirmButton) {
        confirmButton.addEventListener("click", () => {
            handleCancelConfirm();
        });
    }
}

if (page) {
    document.addEventListener("DOMContentLoaded", () => {
        bindActions();
        loadReservations();
    });
}
