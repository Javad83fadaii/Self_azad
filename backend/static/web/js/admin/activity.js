import { extractErrorMessage, get } from "../core/http.js";
import {
    clearFeedback,
    emptyRow,
    escapeHtml,
    formatDateTime,
    formatNumber,
    loadingRow,
    renderPagination,
    setFeedback,
    slicePage,
} from "./components/ui.js";

const PAGE_SIZE = 15;

function buildQuery(form) {
    const params = new URLSearchParams();
    ["username", "action", "start_date", "end_date"].forEach((fieldName) => {
        const value = form.elements[fieldName]?.value?.trim?.() ?? form.elements[fieldName]?.value ?? "";
        if (value) {
            params.set(fieldName, value);
        }
    });
    return params;
}

function updateUrlQuery(form) {
    const url = new URL(window.location.href);
    url.search = "";
    buildQuery(form).forEach((value, key) => url.searchParams.set(key, value));
    window.history.replaceState({}, "", url);
}

function hydrateFormFromUrl(form) {
    const currentUrl = new URL(window.location.href);
    ["username", "action", "start_date", "end_date"].forEach((fieldName) => {
        form.elements[fieldName].value = currentUrl.searchParams.get(fieldName) || "";
    });
}

function renderActivityRows(rows) {
    const tableBody = document.getElementById("activity-table-body");
    if (!tableBody) {
        return;
    }

    if (!rows.length) {
        tableBody.innerHTML = emptyRow(4, "برای فیلتر فعلی فعالیتی ثبت نشده است.");
        return;
    }

    tableBody.innerHTML = rows
        .map(
            (item) => `
                <tr>
                    <td>${escapeHtml(item.full_name || item.username || "-")}</td>
                    <td><code>${escapeHtml(item.action)}</code></td>
                    <td>${escapeHtml(item.description)}</td>
                    <td>${formatDateTime(item.created_at)}</td>
                </tr>
            `
        )
        .join("");
}

export function init() {
    const page = document.getElementById("admin-activity-page");
    if (!page) {
        return;
    }

    const feedback = document.getElementById("admin-activity-feedback");
    const form = document.getElementById("activity-filter-form");
    const resetButton = document.getElementById("activity-reset-filters");
    const pagination = document.getElementById("activity-pagination");
    const totalCountElement = document.getElementById("activity-total-count");
    let activityRows = [];
    let currentPage = 1;

    function renderPage() {
        renderActivityRows(slicePage(activityRows, currentPage, PAGE_SIZE));
        renderPagination(pagination, activityRows.length, currentPage, PAGE_SIZE);
    }

    async function loadActivity() {
        clearFeedback(feedback);
        document.getElementById("activity-table-body").innerHTML = loadingRow(4, "در حال دریافت رخدادها...");

        try {
            const query = buildQuery(form);
            const targetUrl = query.size ? `${page.dataset.activityUrl}?${query.toString()}` : page.dataset.activityUrl;
            const response = await get(targetUrl);
            activityRows = response.results || [];
            currentPage = 1;
            if (totalCountElement) {
                totalCountElement.textContent = formatNumber(response.count || 0);
            }
            renderPage();
            updateUrlQuery(form);
        } catch (error) {
            window.console.error("Failed to load audit logs.", error);
            activityRows = [];
            currentPage = 1;
            if (totalCountElement) {
                totalCountElement.textContent = "۰";
            }
            renderPage();
            setFeedback(feedback, "danger", "خطا در دریافت فعالیت‌ها", extractErrorMessage(error) || "دریافت رخدادهای ثبت‌شده با مشکل مواجه شد.");
        }
    }

    form?.addEventListener("submit", async (event) => {
        event.preventDefault();
        await loadActivity();
    });

    resetButton?.addEventListener("click", async () => {
        form.reset();
        await loadActivity();
    });

    pagination?.addEventListener("click", (event) => {
        const button = event.target.closest("[data-page]");
        if (!button) {
            return;
        }
        currentPage = Number(button.dataset.page);
        renderPage();
    });

    hydrateFormFromUrl(form);
    loadActivity();
}
