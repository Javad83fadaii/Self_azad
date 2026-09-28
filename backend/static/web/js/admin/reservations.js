import { extractErrorMessage, get } from "../core/http.js";
import {
    badgeToneForReservationStatus,
    clearFeedback,
    createStatusBadge,
    emptyRow,
    escapeHtml,
    formatDate,
    formatDateTime,
    humanizeReservationStatus,
    loadingRow,
    renderPagination,
    setFeedback,
    slicePage,
} from "./components/ui.js";

const PAGE_SIZE = 10;

function buildDetailMarkup(reservation) {
    return `
        <div class="admin-detail-grid">
            <div class="admin-detail-card">
                <span class="admin-detail-card__label">دانشجو</span>
                <strong>${escapeHtml(reservation.student_full_name || "-")}</strong>
            </div>
            <div class="admin-detail-card">
                <span class="admin-detail-card__label">کد دانشجویی</span>
                <strong>${escapeHtml(reservation.student_code || "-")}</strong>
            </div>
            <div class="admin-detail-card">
                <span class="admin-detail-card__label">شماره موبایل</span>
                <strong>${escapeHtml(reservation.student_phone_number || "-")}</strong>
            </div>
            <div class="admin-detail-card">
                <span class="admin-detail-card__label">غذا</span>
                <strong>${escapeHtml(reservation.meal_name || "-")}</strong>
            </div>
            <div class="admin-detail-card">
                <span class="admin-detail-card__label">تاریخ</span>
                <strong>${escapeHtml(formatDate(reservation.schedule_date))}</strong>
            </div>
            <div class="admin-detail-card">
                <span class="admin-detail-card__label">کد رزرو</span>
                <strong>${escapeHtml(reservation.reservation_code || "-")}</strong>
            </div>
            <div class="admin-detail-card">
                <span class="admin-detail-card__label">وضعیت</span>
                <div>${createStatusBadge(humanizeReservationStatus(reservation.status), badgeToneForReservationStatus(reservation.status))}</div>
            </div>
            <div class="admin-detail-card">
                <span class="admin-detail-card__label">زمان ایجاد</span>
                <strong>${escapeHtml(formatDateTime(reservation.created_at))}</strong>
            </div>
            <div class="admin-detail-card">
                <span class="admin-detail-card__label">زمان لغو</span>
                <strong>${escapeHtml(formatDateTime(reservation.cancelled_at))}</strong>
            </div>
        </div>
    `;
}

export function init() {
    const page = document.getElementById("admin-reservations-page");
    if (!page) {
        return;
    }

    const feedback = document.getElementById("admin-reservations-feedback");
    const tableBody = document.getElementById("reservations-table-body");
    const pagination = document.getElementById("reservations-pagination");
    const dateFilter = document.getElementById("reservation-date-filter");
    const mealFilter = document.getElementById("reservation-meal-filter");
    const statusFilter = document.getElementById("reservation-status-filter");
    const studentSearch = document.getElementById("reservation-student-search");
    const detailBody = document.getElementById("reservation-detail-body");
    const detailModal = new window.bootstrap.Modal(document.getElementById("reservationDetailModal"));

    let reservations = [];
    let meals = [];
    let pageNumber = 1;

    function renderMealOptions() {
        mealFilter.innerHTML = ['<option value="ALL">همه غذاها</option>']
            .concat(meals.map((meal) => `<option value="${meal.id}">${escapeHtml(meal.name)}</option>`))
            .join("");
    }

    function filteredReservations() {
        const query = studentSearch.value.trim().toLowerCase();
        return reservations.filter((item) => {
            const matchesStatus = statusFilter.value === "ALL" || item.status === statusFilter.value;
            const matchesStudent =
                !query ||
                (item.student_full_name || "").toLowerCase().includes(query) ||
                (item.student_code || "").toLowerCase().includes(query) ||
                (item.student_phone_number || "").toLowerCase().includes(query);
            const matchesMeal = mealFilter.value === "ALL" || item.meal_id === Number(mealFilter.value);
            return matchesStatus && matchesStudent && matchesMeal;
        });
    }

    function renderTable() {
        const rows = filteredReservations();
        const pagedRows = slicePage(rows, pageNumber, PAGE_SIZE);
        if (!pagedRows.length) {
            tableBody.innerHTML = emptyRow(9, rows.length ? "در این صفحه رزروی وجود ندارد." : "رزروی برای نمایش وجود ندارد.");
            renderPagination(pagination, rows.length, pageNumber, PAGE_SIZE);
            return;
        }

        tableBody.innerHTML = pagedRows
            .map(
                (item) => `
                    <tr>
                        <td>${escapeHtml(item.student_full_name || "-")}</td>
                        <td>${escapeHtml(item.student_code || "-")}</td>
                        <td>${escapeHtml(item.student_phone_number || "-")}</td>
                        <td>${escapeHtml(item.meal_name || "-")}</td>
                        <td>${escapeHtml(formatDate(item.schedule_date))}</td>
                        <td>${escapeHtml(item.reservation_code || "-")}</td>
                        <td>${createStatusBadge(humanizeReservationStatus(item.status), badgeToneForReservationStatus(item.status))}</td>
                        <td>${escapeHtml(formatDateTime(item.created_at))}</td>
                        <td><button type="button" class="btn btn-sm btn-outline-secondary" data-action="detail" data-id="${item.id}">مشاهده</button></td>
                    </tr>
                `
            )
            .join("");

        renderPagination(pagination, rows.length, pageNumber, PAGE_SIZE);
    }

    async function fetchReservationRows() {
        if (dateFilter.value) {
            return get(`${page.dataset.byDateUrl}?date=${encodeURIComponent(dateFilter.value)}`);
        }
        if (mealFilter.value !== "ALL") {
            return get(`${page.dataset.byMealUrl}?meal_id=${encodeURIComponent(mealFilter.value)}`);
        }
        return get(page.dataset.listUrl);
    }

    async function loadData() {
        clearFeedback(feedback);
        tableBody.innerHTML = loadingRow(9);

        try {
            const selectedMeal = mealFilter.value || "ALL";
            const [mealRows, reservationRows] = await Promise.all([get(page.dataset.mealsUrl), fetchReservationRows()]);
            meals = mealRows || [];
            reservations = reservationRows || [];
            renderMealOptions();
            if (selectedMeal !== "ALL" && meals.some((meal) => String(meal.id) === selectedMeal)) {
                mealFilter.value = selectedMeal;
            }
            renderTable();
        } catch (error) {
            window.console.error("Failed to load reservations.", error);
            tableBody.innerHTML = emptyRow(9, "دریافت اطلاعات با مشکل مواجه شد.");
            setFeedback(feedback, "danger", "خطا در دریافت رزروها", extractErrorMessage(error) || "رزروها دریافت نشد.");
        }
    }

    tableBody.addEventListener("click", (event) => {
        const button = event.target.closest("[data-action='detail']");
        if (!button) {
            return;
        }

        const reservation = reservations.find((item) => item.id === Number(button.dataset.id));
        if (!reservation) {
            return;
        }

        detailBody.innerHTML = buildDetailMarkup(reservation);
        detailModal.show();
    });

    pagination.addEventListener("click", (event) => {
        const button = event.target.closest("[data-page]");
        if (!button) {
            return;
        }

        pageNumber = Number(button.dataset.page);
        renderTable();
    });

    dateFilter.addEventListener("change", async () => {
        pageNumber = 1;
        await loadData();
    });
    mealFilter.addEventListener("change", async () => {
        pageNumber = 1;
        await loadData();
    });
    statusFilter.addEventListener("change", () => {
        pageNumber = 1;
        renderTable();
    });
    studentSearch.addEventListener("input", () => {
        pageNumber = 1;
        renderTable();
    });

    loadData();
}
