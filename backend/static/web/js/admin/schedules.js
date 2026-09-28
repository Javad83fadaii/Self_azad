import { del, extractErrorMessage, get, post, put } from "../core/http.js";
import {
    badgeToneForReservationStatus,
    clearFeedback,
    createStatusBadge,
    emptyRow,
    escapeHtml,
    formatDate,
    formatDateTime,
    humanizeActiveState,
    humanizeReservationState,
    loadingRow,
    renderPagination,
    setFeedback,
    showToast,
    slicePage,
    toDatetimeLocalValue,
} from "./components/ui.js";

const PAGE_SIZE = 8;

function buildScheduleUrl(page, scheduleId) {
    return page.dataset.detailUrlTemplate.replace("__id__", String(scheduleId));
}

function buildFormPayload(form) {
    return {
        meal_id: Number(form.querySelector("#schedule-meal-id").value),
        date: form.querySelector("#schedule-date").value,
        capacity: Number(form.querySelector("#schedule-capacity").value),
        reservation_open_at: form.querySelector("#schedule-open-at").value,
        reservation_close_at: form.querySelector("#schedule-close-at").value,
        is_active: form.querySelector("#schedule-is-active").checked,
    };
}

function getWeekdayLabel(dateValue) {
    try {
        return new Intl.DateTimeFormat("fa-IR", { weekday: "long" }).format(new Date(`${dateValue}T00:00:00`));
    } catch (error) {
        return dateValue;
    }
}

export function init() {
    const page = document.getElementById("admin-schedules-page");
    if (!page) {
        return;
    }

    const feedback = document.getElementById("admin-schedules-feedback");
    const tableBody = document.getElementById("schedules-table-body");
    const weeklyView = document.getElementById("schedule-weekly-view");
    const dateFilter = document.getElementById("schedule-date-filter");
    const mealFilter = document.getElementById("schedule-meal-filter");
    const statusFilter = document.getElementById("schedule-status-filter");
    const pagination = document.getElementById("schedules-pagination");
    const form = document.getElementById("schedule-form");
    const formFeedback = document.getElementById("schedule-form-feedback");
    const submitButton = document.getElementById("schedule-submit-button");
    const createButton = document.getElementById("open-schedule-create-modal");
    const formModal = new window.bootstrap.Modal(document.getElementById("scheduleFormModal"));
    const deleteModal = new window.bootstrap.Modal(document.getElementById("scheduleDeleteModal"));
    const confirmDeleteButton = document.getElementById("confirm-schedule-delete");

    let schedules = [];
    let meals = [];
    let pageNumber = 1;
    let deletingScheduleId = null;

    function renderMealOptions() {
        const filterOptions = ['<option value="ALL">همه غذاها</option>']
            .concat(
                meals.map(
                    (meal) =>
                        `<option value="${meal.id}">${escapeHtml(meal.name)}${meal.is_active ? "" : " (غیرفعال)"}</option>`
                )
            )
            .join("");
        mealFilter.innerHTML = filterOptions;

        form.querySelector("#schedule-meal-id").innerHTML = meals.length
            ? meals
                  .map(
                      (meal) =>
                          `<option value="${meal.id}">${escapeHtml(meal.name)}${meal.is_active ? "" : " (غیرفعال)"}</option>`
                  )
                  .join("")
            : '<option value="">غذایی یافت نشد</option>';
    }

    function filteredSchedules() {
        return schedules.filter((schedule) => {
            const matchesDate = !dateFilter.value || schedule.date === dateFilter.value;
            const matchesMeal = mealFilter.value === "ALL" || schedule.meal_id === Number(mealFilter.value);
            const matchesStatus =
                statusFilter.value === "ALL" ||
                (statusFilter.value === "ACTIVE" && schedule.is_active) ||
                (statusFilter.value === "INACTIVE" && !schedule.is_active);
            return matchesDate && matchesMeal && matchesStatus;
        });
    }

    function renderWeeklyView(rows) {
        if (!rows.length) {
            weeklyView.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state__icon" aria-hidden="true"><i class="fa-solid fa-calendar-xmark"></i></div>
                    <h3 class="empty-state__title">برنامه‌ای برای نمایش وجود ندارد.</h3>
                    <p class="empty-state__message">برای بازه و فیلتر فعلی برنامه غذایی ثبت نشده است.</p>
                </div>
            `;
            return;
        }

        const groupedRows = new Map();
        rows.forEach((schedule) => {
            if (!groupedRows.has(schedule.date)) {
                groupedRows.set(schedule.date, []);
            }
            groupedRows.get(schedule.date).push(schedule);
        });

        weeklyView.innerHTML = Array.from(groupedRows.entries())
            .slice(0, 7)
            .map(
                ([date, items]) => `
                    <article class="weekly-board__day">
                        <div class="weekly-board__day-header">
                            <strong>${escapeHtml(getWeekdayLabel(date))}</strong>
                            <span>${escapeHtml(formatDate(date))}</span>
                        </div>
                        <div class="weekly-board__items">
                            ${items
                                .map(
                                    (item) => `
                                        <div class="weekly-board__item">
                                            <div class="fw-semibold">${escapeHtml(item.meal_name)}</div>
                                            <div class="small text-muted mt-1">ظرفیت ${item.capacity} | رزرو ${item.reserved_count}</div>
                                            <div class="mt-2">${createStatusBadge(humanizeReservationState(item.reservation_state), badgeToneForReservationStatus(item.reservation_state))}</div>
                                        </div>
                                    `
                                )
                                .join("")}
                        </div>
                    </article>
                `
            )
            .join("");
    }

    function renderTable() {
        const rows = filteredSchedules();
        const pagedRows = slicePage(rows, pageNumber, PAGE_SIZE);
        if (!pagedRows.length) {
            tableBody.innerHTML = emptyRow(9, rows.length ? "در این صفحه موردی وجود ندارد." : "هنوز برنامه غذایی ثبت نشده است.");
            renderPagination(pagination, rows.length, pageNumber, PAGE_SIZE);
            renderWeeklyView(rows);
            return;
        }

        tableBody.innerHTML = pagedRows
            .map(
                (schedule) => `
                    <tr>
                        <td>${formatDate(schedule.date)}</td>
                        <td>${escapeHtml(schedule.meal_name)}</td>
                        <td>${escapeHtml(String(schedule.capacity))}</td>
                        <td>${escapeHtml(String(schedule.reserved_count ?? 0))}</td>
                        <td>${escapeHtml(String(schedule.remaining_capacity ?? 0))}</td>
                        <td>${formatDateTime(schedule.reservation_open_at)}</td>
                        <td>${formatDateTime(schedule.reservation_close_at)}</td>
                        <td>${createStatusBadge(humanizeActiveState(schedule.is_active), schedule.is_active ? "success" : "warning")}</td>
                        <td>
                            <div class="admin-action-group">
                                <button type="button" class="btn btn-sm btn-outline-primary" data-action="edit" data-id="${schedule.id}">ویرایش</button>
                                <button type="button" class="btn btn-sm btn-outline-danger" data-action="delete" data-id="${schedule.id}">حذف</button>
                            </div>
                        </td>
                    </tr>
                `
            )
            .join("");

        renderPagination(pagination, rows.length, pageNumber, PAGE_SIZE);
        renderWeeklyView(rows);
    }

    function resetForm() {
        form.reset();
        form.querySelector("#schedule-id").value = "";
        clearFeedback(formFeedback);
        submitButton.querySelector("span").textContent = "ذخیره برنامه";
        document.getElementById("scheduleFormModalLabel").textContent = "افزودن برنامه غذایی";
        form.querySelector("#schedule-is-active").checked = true;
        if (meals.length) {
            form.querySelector("#schedule-meal-id").value = String(meals[0].id);
        }
    }

    function openCreateModal() {
        resetForm();
        formModal.show();
    }

    function openEditModal(scheduleId) {
        const schedule = schedules.find((item) => item.id === scheduleId);
        if (!schedule) {
            return;
        }

        resetForm();
        form.querySelector("#schedule-id").value = schedule.id;
        form.querySelector("#schedule-meal-id").value = String(schedule.meal_id);
        form.querySelector("#schedule-date").value = schedule.date;
        form.querySelector("#schedule-capacity").value = schedule.capacity;
        form.querySelector("#schedule-open-at").value = toDatetimeLocalValue(schedule.reservation_open_at);
        form.querySelector("#schedule-close-at").value = toDatetimeLocalValue(schedule.reservation_close_at);
        form.querySelector("#schedule-is-active").checked = Boolean(schedule.is_active);
        submitButton.querySelector("span").textContent = "ذخیره تغییرات";
        document.getElementById("scheduleFormModalLabel").textContent = "ویرایش برنامه غذایی";
        formModal.show();
    }

    async function loadData() {
        clearFeedback(feedback);
        tableBody.innerHTML = loadingRow(9);
        weeklyView.innerHTML = '<div class="loading-state">در حال دریافت اطلاعات...</div>';

        try {
            const [scheduleRows, mealRows] = await Promise.all([get(page.dataset.listUrl), get(page.dataset.mealsUrl)]);
            schedules = scheduleRows || [];
            meals = mealRows || [];
            renderMealOptions();
            renderTable();
        } catch (error) {
            window.console.error("Failed to load schedules.", error);
            tableBody.innerHTML = emptyRow(9, "دریافت اطلاعات با مشکل مواجه شد.");
            weeklyView.innerHTML = '<div class="empty-state"><p class="empty-state__message">نمای هفتگی بارگذاری نشد.</p></div>';
            setFeedback(feedback, "danger", "خطا در دریافت برنامه غذایی", extractErrorMessage(error) || "برنامه غذایی دریافت نشد.");
        }
    }

    async function submitForm(event) {
        event.preventDefault();
        clearFeedback(formFeedback);
        submitButton.disabled = true;

        const scheduleId = form.querySelector("#schedule-id").value;
        try {
            const payload = buildFormPayload(form);
            if (scheduleId) {
                await put(buildScheduleUrl(page, scheduleId), payload, { csrfUrl: page.dataset.csrfUrl });
                showToast("برنامه غذایی با موفقیت به‌روزرسانی شد.", "success");
            } else {
                await post(page.dataset.createUrl, payload, { csrfUrl: page.dataset.csrfUrl });
                showToast("برنامه غذایی با موفقیت ایجاد شد.", "success");
            }

            formModal.hide();
            resetForm();
            await loadData();
        } catch (error) {
            window.console.error("Failed to save schedule.", error);
            setFeedback(formFeedback, "danger", "خطا در ذخیره برنامه غذایی", extractErrorMessage(error) || "برنامه غذایی ذخیره نشد.");
        } finally {
            submitButton.disabled = false;
        }
    }

    async function confirmDelete() {
        if (!deletingScheduleId) {
            return;
        }

        confirmDeleteButton.disabled = true;
        try {
            await del(buildScheduleUrl(page, deletingScheduleId), undefined, { csrfUrl: page.dataset.csrfUrl });
            deleteModal.hide();
            deletingScheduleId = null;
            showToast("برنامه غذایی با موفقیت غیرفعال شد.", "success");
            await loadData();
        } catch (error) {
            window.console.error("Failed to delete schedule.", error);
            setFeedback(feedback, "danger", "خطا در حذف برنامه غذایی", extractErrorMessage(error) || "حذف برنامه غذایی با مشکل مواجه شد.");
        } finally {
            confirmDeleteButton.disabled = false;
        }
    }

    tableBody.addEventListener("click", (event) => {
        const actionButton = event.target.closest("[data-action]");
        if (!actionButton) {
            return;
        }

        const scheduleId = Number(actionButton.dataset.id);
        if (actionButton.dataset.action === "edit") {
            openEditModal(scheduleId);
            return;
        }

        deletingScheduleId = scheduleId;
        deleteModal.show();
    });

    pagination.addEventListener("click", (event) => {
        const button = event.target.closest("[data-page]");
        if (!button) {
            return;
        }

        pageNumber = Number(button.dataset.page);
        renderTable();
    });

    [dateFilter, mealFilter, statusFilter].forEach((element) => {
        element.addEventListener("input", () => {
            pageNumber = 1;
            renderTable();
        });
        element.addEventListener("change", () => {
            pageNumber = 1;
            renderTable();
        });
    });

    createButton.addEventListener("click", openCreateModal);
    form.addEventListener("submit", submitForm);
    confirmDeleteButton.addEventListener("click", confirmDelete);

    loadData();
}
