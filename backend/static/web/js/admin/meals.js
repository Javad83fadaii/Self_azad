import { del, extractErrorMessage, get, post, put } from "../core/http.js";
import {
    clearFeedback,
    createStatusBadge,
    emptyRow,
    formatCurrency,
    formatDateTime,
    renderPagination,
    setFeedback,
    showToast,
    slicePage,
} from "./components/ui.js";

const PAGE_SIZE = 8;

function buildMealUrl(page, mealId) {
    return page.dataset.detailUrlTemplate.replace("__id__", String(mealId));
}

function createFormData(form) {
    const formData = new window.FormData();
    formData.set("name", form.querySelector("#meal-name").value.trim());
    formData.set("code", form.querySelector("#meal-code").value.trim());
    formData.set("description", form.querySelector("#meal-description").value.trim());
    formData.set("price", form.querySelector("#meal-price").value);
    formData.set("is_active", String(form.querySelector("#meal-is-active").checked));
    const imageInput = form.querySelector("#meal-image");
    if (imageInput.files[0]) {
        formData.set("image", imageInput.files[0]);
    }
    return formData;
}

export function init() {
    const page = document.getElementById("admin-meals-page");
    if (!page) {
        return;
    }

    const feedback = document.getElementById("admin-meals-feedback");
    const tableBody = document.getElementById("meals-table-body");
    const searchInput = document.getElementById("meal-search");
    const statusFilter = document.getElementById("meal-status-filter");
    const pagination = document.getElementById("meals-pagination");
    const form = document.getElementById("meal-form");
    const formFeedback = document.getElementById("meal-form-feedback");
    const currentImageHint = document.getElementById("meal-current-image");
    const submitButton = document.getElementById("meal-submit-button");
    const mealModal = new window.bootstrap.Modal(document.getElementById("mealFormModal"));
    const deleteModal = new window.bootstrap.Modal(document.getElementById("mealDeleteModal"));
    const createButton = document.getElementById("open-meal-create-modal");
    const confirmDeleteButton = document.getElementById("confirm-meal-delete");
    let meals = [];
    let pageNumber = 1;
    let deletingMealId = null;

    function filteredMeals() {
        const query = searchInput.value.trim().toLowerCase();
        const status = statusFilter.value;
        return meals.filter((meal) => {
            const matchesQuery =
                !query ||
                meal.name.toLowerCase().includes(query) ||
                meal.code.toLowerCase().includes(query) ||
                (meal.description || "").toLowerCase().includes(query);
            const matchesStatus =
                status === "ALL" ||
                (status === "ACTIVE" && meal.is_active) ||
                (status === "INACTIVE" && !meal.is_active);
            return matchesQuery && matchesStatus;
        });
    }

    function renderTable() {
        const rows = filteredMeals();
        const pagedRows = slicePage(rows, pageNumber, PAGE_SIZE);
        if (!pagedRows.length) {
            tableBody.innerHTML = emptyRow(6, rows.length ? "در این صفحه داده‌ای وجود ندارد." : "هنوز غذایی ثبت نشده است.");
            renderPagination(pagination, rows.length, pageNumber, PAGE_SIZE);
            return;
        }

        tableBody.innerHTML = pagedRows
            .map(
                (meal) => `
                    <tr>
                        <td>
                            <div class="fw-semibold">${meal.name}</div>
                            ${meal.description ? `<div class="small text-muted mt-1">${meal.description}</div>` : ""}
                        </td>
                        <td>${meal.code}</td>
                        <td>${formatCurrency(meal.price)}</td>
                        <td>${createStatusBadge(meal.is_active ? "فعال" : "غیرفعال", meal.is_active ? "success" : "warning")}</td>
                        <td>${formatDateTime(meal.created_at)}</td>
                        <td>
                            <div class="admin-action-group">
                                <button type="button" class="btn btn-sm btn-outline-primary" data-action="edit" data-id="${meal.id}">ویرایش</button>
                                <button type="button" class="btn btn-sm btn-outline-danger" data-action="delete" data-id="${meal.id}">حذف</button>
                            </div>
                        </td>
                    </tr>
                `
            )
            .join("");
        renderPagination(pagination, rows.length, pageNumber, PAGE_SIZE);
    }

    function resetForm() {
        form.reset();
        form.querySelector("#meal-id").value = "";
        formFeedback.classList.add("d-none");
        formFeedback.innerHTML = "";
        currentImageHint.textContent = "";
        submitButton.querySelector("span").textContent = "ذخیره غذا";
        document.getElementById("mealFormModalLabel").textContent = "افزودن غذا";
        form.querySelector("#meal-is-active").checked = true;
    }

    function openCreateModal() {
        resetForm();
        mealModal.show();
    }

    function openEditModal(mealId) {
        const meal = meals.find((item) => item.id === mealId);
        if (!meal) {
            return;
        }

        resetForm();
        form.querySelector("#meal-id").value = meal.id;
        form.querySelector("#meal-name").value = meal.name;
        form.querySelector("#meal-code").value = meal.code;
        form.querySelector("#meal-description").value = meal.description || "";
        form.querySelector("#meal-price").value = meal.price;
        form.querySelector("#meal-is-active").checked = Boolean(meal.is_active);
        currentImageHint.innerHTML = meal.image ? `تصویر فعلی ثبت شده است. برای تغییر، فایل جدید انتخاب کنید.` : "تصویری برای این غذا ثبت نشده است.";
        submitButton.querySelector("span").textContent = "ذخیره تغییرات";
        document.getElementById("mealFormModalLabel").textContent = "ویرایش غذا";
        mealModal.show();
    }

    async function loadMeals() {
        clearFeedback(feedback);
        tableBody.innerHTML = `<tr><td colspan="6" class="text-center py-4">در حال دریافت اطلاعات...</td></tr>`;
        try {
            meals = await get(page.dataset.listUrl);
            renderTable();
        } catch (error) {
            window.console.error("Failed to load meals.", error);
            tableBody.innerHTML = emptyRow(6, "دریافت اطلاعات با مشکل مواجه شد.");
            setFeedback(feedback, "danger", "خطا در دریافت غذاها", extractErrorMessage(error));
        }
    }

    async function submitForm(event) {
        event.preventDefault();
        formFeedback.classList.add("d-none");
        submitButton.disabled = true;
        const mealId = form.querySelector("#meal-id").value;
        try {
            const payload = createFormData(form);
            if (mealId) {
                await put(buildMealUrl(page, mealId), payload, { csrfUrl: page.dataset.csrfUrl });
                showToast("غذا با موفقیت به‌روزرسانی شد.", "success");
            } else {
                await post(page.dataset.createUrl, payload, { csrfUrl: page.dataset.csrfUrl });
                showToast("غذا با موفقیت ایجاد شد.", "success");
            }
            mealModal.hide();
            resetForm();
            await loadMeals();
        } catch (error) {
            window.console.error("Failed to save meal.", error);
            setFeedback(formFeedback, "danger", "خطا در ذخیره غذا", extractErrorMessage(error) || "ثبت غذا با مشکل مواجه شد.");
        } finally {
            submitButton.disabled = false;
        }
    }

    async function confirmDelete() {
        if (!deletingMealId) {
            return;
        }

        confirmDeleteButton.disabled = true;
        try {
            await del(buildMealUrl(page, deletingMealId), undefined, { csrfUrl: page.dataset.csrfUrl });
            showToast("غذا با موفقیت غیرفعال شد.", "success");
            deleteModal.hide();
            deletingMealId = null;
            await loadMeals();
        } catch (error) {
            window.console.error("Failed to delete meal.", error);
            setFeedback(feedback, "danger", "خطا در حذف غذا", extractErrorMessage(error) || "حذف غذا با مشکل مواجه شد.");
        } finally {
            confirmDeleteButton.disabled = false;
        }
    }

    tableBody.addEventListener("click", (event) => {
        const actionButton = event.target.closest("[data-action]");
        if (!actionButton) {
            return;
        }

        const mealId = Number(actionButton.dataset.id);
        if (actionButton.dataset.action === "edit") {
            openEditModal(mealId);
            return;
        }

        deletingMealId = mealId;
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

    createButton.addEventListener("click", openCreateModal);
    form.addEventListener("submit", submitForm);
    confirmDeleteButton.addEventListener("click", confirmDelete);
    searchInput.addEventListener("input", () => {
        pageNumber = 1;
        renderTable();
    });
    statusFilter.addEventListener("change", () => {
        pageNumber = 1;
        renderTable();
    });

    loadMeals();
}
