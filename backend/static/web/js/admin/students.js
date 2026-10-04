import { extractErrorMessage, get, post } from "../core/http.js";
import {
    badgeToneForReservationStatus,
    clearFeedback,
    createStatusBadge,
    emptyRow,
    escapeHtml,
    formatDateTime,
    humanizeActiveState,
    humanizeReservationStatus,
    loadingRow,
    renderPagination,
    setFeedback,
    showToast,
    slicePage,
} from "./components/ui.js";

const PAGE_SIZE = 10;

function buildRecentReservationsMarkup(reservations) {
    if (!reservations.length) {
        return '<p class="text-muted mb-0">برای این دانشجو رزروی ثبت نشده است.</p>';
    }

    return `
        <div class="table-responsive admin-table-shell mt-3">
            <table class="table table-sm align-middle mb-0">
                <thead>
                    <tr>
                        <th>غذا</th>
                        <th>تاریخ</th>
                        <th>کد رزرو</th>
                        <th>وضعیت</th>
                    </tr>
                </thead>
                <tbody>
                    ${reservations
                        .slice(0, 5)
                        .map(
                            (item) => `
                                <tr>
                                    <td>${escapeHtml(item.meal_name || "-")}</td>
                                    <td>${escapeHtml(item.schedule_date || "-")}</td>
                                    <td>${escapeHtml(item.reservation_code || "-")}</td>
                                    <td>${createStatusBadge(humanizeReservationStatus(item.status), badgeToneForReservationStatus(item.status))}</td>
                                </tr>
                            `
                        )
                        .join("")}
                </tbody>
            </table>
        </div>
    `;
}

function buildDetailMarkup(student, reservations) {
    return `
        <div class="admin-detail-grid">
            <div class="admin-detail-card">
                <span class="admin-detail-card__label">نام و نام خانوادگی</span>
                <strong>${escapeHtml(student.full_name || "-")}</strong>
            </div>
            <div class="admin-detail-card">
                <span class="admin-detail-card__label">کد دانشجویی</span>
                <strong>${escapeHtml(student.student_code || "-")}</strong>
            </div>
            <div class="admin-detail-card">
                <span class="admin-detail-card__label">شماره موبایل</span>
                <strong>${escapeHtml(student.phone_number || "-")}</strong>
            </div>
            <div class="admin-detail-card">
                <span class="admin-detail-card__label">نام کاربری</span>
                <strong>${escapeHtml(student.username || "-")}</strong>
            </div>
            <div class="admin-detail-card">
                <span class="admin-detail-card__label">وضعیت</span>
                <div>${createStatusBadge(humanizeActiveState(student.is_active), student.is_active ? "success" : "warning")}</div>
            </div>
            <div class="admin-detail-card">
                <span class="admin-detail-card__label">تاریخ ثبت</span>
                <strong>${escapeHtml(formatDateTime(student.created_at))}</strong>
            </div>
        </div>
        <div class="mt-4">
            <h3 class="h6 mb-3">رزروهای اخیر</h3>
            ${buildRecentReservationsMarkup(reservations)}
        </div>
    `;
}

export function init() {
    const page = document.getElementById("admin-students-page");
    if (!page) {
        return;
    }

    const feedback = document.getElementById("admin-students-feedback");
    const tableBody = document.getElementById("students-table-body");
    const pagination = document.getElementById("students-pagination");
    const searchInput = document.getElementById("student-search");
    const statusFilter = document.getElementById("student-status-filter");
    const detailBody = document.getElementById("student-detail-body");
    const detailModal = new window.bootstrap.Modal(document.getElementById("studentDetailModal"));
    const createSection = document.getElementById("student-create-section");
    const form = document.getElementById("student-form");
    const formFeedback = document.getElementById("student-form-feedback");
    const submitButton = document.getElementById("student-submit-button");
    const createButton = document.getElementById("open-student-create-modal");
    const resetButton = document.getElementById("student-reset-button");

    let students = [];
    let reservations = [];
    let pageNumber = 1;

    function createPayload() {
        return {
            first_name: form.querySelector("#student-form-first-name").value.trim(),
            last_name: form.querySelector("#student-form-last-name").value.trim(),
            student_code: form.querySelector("#student-form-student-code").value.trim(),
            phone_number: form.querySelector("#student-form-phone-number").value.trim(),
            password: form.querySelector("#student-form-password").value,
            is_active: form.querySelector("#student-form-is-active").checked,
        };
    }

    function resetForm() {
        form.reset();
        form.querySelector("#student-form-is-active").checked = true;
        clearFeedback(formFeedback);
    }

    function openCreateSection() {
        resetForm();
        createSection?.scrollIntoView({ behavior: "smooth", block: "start" });
        form.querySelector("#student-form-first-name")?.focus();
    }

    function filteredStudents() {
        const query = searchInput.value.trim().toLowerCase();
        return students.filter((student) => {
            const matchesStatus =
                statusFilter.value === "ALL" ||
                (statusFilter.value === "ACTIVE" && student.is_active) ||
                (statusFilter.value === "INACTIVE" && !student.is_active);
            const matchesSearch =
                !query ||
                (student.full_name || "").toLowerCase().includes(query) ||
                (student.first_name || "").toLowerCase().includes(query) ||
                (student.last_name || "").toLowerCase().includes(query) ||
                (student.student_code || "").toLowerCase().includes(query) ||
                (student.phone_number || "").toLowerCase().includes(query);
            return matchesStatus && matchesSearch;
        });
    }

    function renderTable() {
        const rows = filteredStudents();
        const pagedRows = slicePage(rows, pageNumber, PAGE_SIZE);
        if (!pagedRows.length) {
            tableBody.innerHTML = emptyRow(7, rows.length ? "در این صفحه دانشجویی وجود ندارد." : "دانشجویی برای نمایش وجود ندارد.");
            renderPagination(pagination, rows.length, pageNumber, PAGE_SIZE);
            return;
        }

        tableBody.innerHTML = pagedRows
            .map(
                (student) => `
                    <tr>
                        <td>${escapeHtml(student.full_name || "-")}</td>
                        <td>${escapeHtml(student.student_code || "-")}</td>
                        <td>${escapeHtml(student.phone_number || "-")}</td>
                        <td>${createStatusBadge(humanizeActiveState(student.is_active), student.is_active ? "success" : "warning")}</td>
                        <td>${escapeHtml(student.username || "-")}</td>
                        <td>${escapeHtml(formatDateTime(student.created_at))}</td>
                        <td><button type="button" class="btn btn-sm btn-outline-secondary" data-action="detail" data-id="${student.id}">مشاهده</button></td>
                    </tr>
                `
            )
            .join("");

        renderPagination(pagination, rows.length, pageNumber, PAGE_SIZE);
    }

    async function loadData() {
        clearFeedback(feedback);
        tableBody.innerHTML = loadingRow(7);

        try {
            const [studentRows, reservationRows] = await Promise.all([get(page.dataset.listUrl), get(page.dataset.reservationsUrl)]);
            students = studentRows || [];
            reservations = reservationRows || [];
            renderTable();
        } catch (error) {
            window.console.error("Failed to load students.", error);
            tableBody.innerHTML = emptyRow(7, "دریافت اطلاعات با مشکل مواجه شد.");
            setFeedback(feedback, "danger", "خطا در دریافت دانشجویان", extractErrorMessage(error) || "لیست دانشجویان دریافت نشد.");
        }
    }

    async function submitForm(event) {
        event.preventDefault();
        clearFeedback(formFeedback);
        submitButton.disabled = true;

        try {
            await post(page.dataset.createUrl, createPayload(), { csrfUrl: page.dataset.csrfUrl });
            resetForm();
            showToast("دانشجو با موفقیت ایجاد شد.", "success");
            pageNumber = 1;
            await loadData();
            createSection?.scrollIntoView({ behavior: "smooth", block: "start" });
        } catch (error) {
            window.console.error("Failed to create student.", error);
            setFeedback(formFeedback, "danger", "خطا در ایجاد دانشجو", extractErrorMessage(error) || "ثبت دانشجو با مشکل مواجه شد.");
        } finally {
            submitButton.disabled = false;
        }
    }

    tableBody.addEventListener("click", (event) => {
        const button = event.target.closest("[data-action='detail']");
        if (!button) {
            return;
        }

        const student = students.find((item) => item.id === Number(button.dataset.id));
        if (!student) {
            return;
        }

        const studentReservations = reservations.filter((item) => item.student_id === student.id);
        detailBody.innerHTML = buildDetailMarkup(student, studentReservations);
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

    searchInput.addEventListener("input", () => {
        pageNumber = 1;
        renderTable();
    });
    statusFilter.addEventListener("change", () => {
        pageNumber = 1;
        renderTable();
    });
    createButton.addEventListener("click", openCreateSection);
    resetButton?.addEventListener("click", () => {
        clearFeedback(formFeedback);
    });
    form.addEventListener("submit", submitForm);

    loadData();
}
