import { extractErrorMessage, get } from "../core/http.js";
import {
    clearFeedback,
    createStatusBadge,
    emptyRow,
    escapeHtml,
    formatDate,
    formatDateTime,
    formatNumber,
    humanizeReservationStatus,
    loadingRow,
    setFeedback,
    showToast,
} from "./components/ui.js";

function toIsoDate(value) {
    return new Date(value.getTime() - value.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
}

function defaultDateRange() {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(endDate.getDate() - 6);
    return {
        start_date: toIsoDate(startDate),
        end_date: toIsoDate(endDate),
    };
}

function upsertChart(cache, key, canvasId, config, hasData = true) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !window.Chart) {
        return;
    }

    const wrapper = canvas.parentElement;
    let emptyState = wrapper?.querySelector(".chart-empty-state");
    if (!emptyState && wrapper) {
        emptyState = document.createElement("div");
        emptyState.className = "chart-empty-state d-none";
        emptyState.textContent = "داده‌ای برای نمایش وجود ندارد.";
        wrapper.appendChild(emptyState);
    }

    if (cache[key]) {
        cache[key].destroy();
    }

    if (!hasData) {
        canvas.classList.add("d-none");
        emptyState?.classList.remove("d-none");
        return;
    }

    canvas.classList.remove("d-none");
    emptyState?.classList.add("d-none");
    cache[key] = new window.Chart(canvas, config);
}

function renderDailyTable(rows) {
    const tableBody = document.getElementById("daily-report-body");
    if (!rows.length) {
        tableBody.innerHTML = emptyRow(7, "برای بازه انتخابی گزارشی ثبت نشده است.");
        return;
    }

    tableBody.innerHTML = rows
        .map(
            (item) => `
                <tr>
                    <td>${formatDate(item.date)}</td>
                    <td>${escapeHtml(item.meal_name)}</td>
                    <td>${formatNumber(item.reservation_count)}</td>
                    <td>${formatNumber(item.cancelled_count)}</td>
                    <td>${formatNumber(item.capacity)}</td>
                    <td>${formatNumber(item.remaining_capacity)}</td>
                    <td>${formatNumber(item.utilization_percentage)}%</td>
                </tr>
            `
        )
        .join("");
}

function renderStudentTable(rows) {
    const tableBody = document.getElementById("student-report-body");
    if (!rows.length) {
        tableBody.innerHTML = emptyRow(8, "گزارش دانشجویی با فیلتر فعلی خالی است.");
        return;
    }

    tableBody.innerHTML = rows
        .map(
            (item) => `
                <tr>
                    <td>${escapeHtml(item.full_name)}</td>
                    <td>${escapeHtml(item.student_code)}</td>
                    <td>${createStatusBadge(item.is_active ? "فعال" : "غیرفعال", item.is_active ? "success" : "secondary")}</td>
                    <td>${formatNumber(item.total_reservations)}</td>
                    <td>${formatNumber(item.active_reservations)}</td>
                    <td>${formatNumber(item.cancelled_count)}</td>
                    <td>${formatNumber(item.used_count)}</td>
                    <td>${formatNumber(item.no_show_count)}</td>
                </tr>
            `
        )
        .join("");
}

function renderMealTable(rows) {
    const tableBody = document.getElementById("meal-report-body");
    if (!rows.length) {
        tableBody.innerHTML = emptyRow(12, "گزارش عملکرد غذاها خالی است.");
        return;
    }

    tableBody.innerHTML = rows
        .map(
            (item) => `
                <tr>
                    <td>${escapeHtml(item.meal_name)}</td>
                    <td>${escapeHtml(item.meal_code)}</td>
                    <td>${formatNumber(item.service_count)}</td>
                    <td>${formatNumber(item.total_reservations)}</td>
                    <td>${formatNumber(item.average_reservations)}</td>
                    <td>${formatNumber(item.max_reservations)}</td>
                    <td>${formatNumber(item.min_reservations)}</td>
                    <td>${formatNumber(item.cancelled_count)}</td>
                    <td>${formatNumber(item.used_count)}</td>
                    <td>${formatNumber(item.no_show_count)}</td>
                    <td>${formatNumber(item.capacity)}</td>
                    <td>${formatNumber(item.utilization_percentage)}%</td>
                </tr>
            `
        )
        .join("");
}

function updateSummaryCards(studentReport, mealReport, reservationReport) {
    const summary = {
        active_students: studentReport.summary?.active_students || 0,
        students_with_reservations: studentReport.summary?.students_with_reservations || 0,
        total_reservations: reservationReport.summary?.total_reservations || 0,
        participation_rate: `${formatNumber(studentReport.summary?.participation_rate || 0)}%`,
        scheduled_meals: mealReport.summary?.scheduled_meals || 0,
        total_capacity: mealReport.summary?.total_capacity || 0,
    };

    Object.entries(summary).forEach(([key, value]) => {
        const element = document.querySelector(`[data-report-summary="${key}"]`);
        if (element) {
            element.textContent = typeof value === "string" ? value : formatNumber(value);
        }
    });
}

function updateReservationSummary(summary) {
    Object.entries(summary || {}).forEach(([key, value]) => {
        const element = document.querySelector(`[data-reservation-summary="${key}"]`);
        if (element) {
            element.textContent = formatNumber(value);
        }
    });
}

function renderCharts(chartCache, dailyReport, reservationReport, mealRows) {
    upsertChart(chartCache, "mealReport", "reports-meals-chart", {
        type: "bar",
        data: {
            labels: mealRows.map((item) => item.meal_name),
            datasets: [
                {
                    label: "کل رزرو",
                    data: mealRows.map((item) => item.total_reservations),
                    backgroundColor: "rgba(31, 75, 153, 0.75)",
                    borderRadius: 10,
                },
            ],
        },
        options: { responsive: true, maintainAspectRatio: false },
    }, mealRows.length > 0);

    upsertChart(chartCache, "dailyReport", "reports-daily-chart", {
        type: "line",
        data: {
            labels: reservationReport.daily_reservations.map((item) => formatDate(item.date)),
            datasets: [
                {
                    label: "رزرو",
                    data: reservationReport.daily_reservations.map((item) => item.reservation_count),
                    borderColor: "#1f4b99",
                    backgroundColor: "rgba(31, 75, 153, 0.16)",
                    fill: true,
                    tension: 0.35,
                },
            ],
        },
        options: { responsive: true, maintainAspectRatio: false },
    }, reservationReport.daily_reservations.length > 0 || dailyReport.results?.length > 0);

    upsertChart(chartCache, "reservationReport", "reports-reservations-chart", {
        type: "doughnut",
        data: {
            labels: reservationReport.status_breakdown.map((item) => humanizeReservationStatus(item.status)),
            datasets: [
                {
                    data: reservationReport.status_breakdown.map((item) => item.count),
                    backgroundColor: ["#1f4b99", "#b63c3c", "#1f7a52", "#b7791f"],
                },
            ],
        },
        options: { responsive: true, maintainAspectRatio: false },
    }, reservationReport.status_breakdown.some((item) => Number(item.count) > 0));
}

function buildStudentFilterParams(form) {
    const params = new URLSearchParams();
    ["first_name", "last_name", "student_code", "phone_number"].forEach((fieldName) => {
        const value = form.elements[fieldName].value.trim();
        if (value) {
            params.set(fieldName, value);
        }
    });
    return params;
}

function buildRangeParams(form) {
    const params = new URLSearchParams();
    ["start_date", "end_date"].forEach((fieldName) => {
        const value = form.elements[fieldName].value;
        if (value) {
            params.set(fieldName, value);
        }
    });
    return params;
}

function updateReportQuery(form) {
    const url = new URL(window.location.href);
    url.search = "";
    buildRangeParams(form).forEach((value, key) => url.searchParams.set(key, value));
    buildStudentFilterParams(form).forEach((value, key) => url.searchParams.set(key, value));
    window.history.replaceState({}, "", url);
}

function hydrateFormFromUrl(form) {
    const currentUrl = new URL(window.location.href);
    const defaults = defaultDateRange();

    form.elements.start_date.value = currentUrl.searchParams.get("start_date") || defaults.start_date;
    form.elements.end_date.value = currentUrl.searchParams.get("end_date") || defaults.end_date;
    ["first_name", "last_name", "student_code", "phone_number"].forEach((fieldName) => {
        form.elements[fieldName].value = currentUrl.searchParams.get(fieldName) || "";
    });
}

function updatePrintHeader(startDate, endDate) {
    const generatedAt = document.getElementById("print-generated-at");
    const rangeLabel = document.getElementById("print-range-label");
    if (generatedAt) {
        generatedAt.textContent = formatDateTime(new Date().toISOString());
    }
    if (rangeLabel) {
        rangeLabel.textContent = `${formatDate(startDate)} تا ${formatDate(endDate)}`;
    }
}

async function downloadReport(url, label) {
    showToast("در حال آماده‌سازی گزارش...", "info");
    const response = await fetch(url, {
        credentials: "same-origin",
        headers: {
            Accept: "*/*",
        },
    });
    if (!response.ok) {
        throw new Error("download-failed");
    }
    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    const contentDisposition = response.headers.get("content-disposition") || "";
    const filenameMatch = contentDisposition.match(/filename="([^"]+)"/);
    link.href = downloadUrl;
    link.download = filenameMatch?.[1] || label;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(downloadUrl);
    showToast("گزارش آماده شد.", "success");
}

export function init() {
    const page = document.getElementById("admin-reports-page");
    if (!page) {
        return;
    }

    const feedback = document.getElementById("admin-reports-feedback");
    const form = document.getElementById("reports-filter-form");
    const resetButton = document.getElementById("reports-reset-filters");
    const printButton = document.getElementById("reports-print-trigger");
    const chartCache = {};

    async function loadReports() {
        clearFeedback(feedback);
        document.getElementById("daily-report-body").innerHTML = loadingRow(7, "در حال دریافت گزارش روزانه...");
        document.getElementById("student-report-body").innerHTML = loadingRow(8, "در حال دریافت گزارش دانشجویان...");
        document.getElementById("meal-report-body").innerHTML = loadingRow(12, "در حال دریافت گزارش غذاها...");

        const studentQuery = buildStudentFilterParams(form);
        const rangeQuery = buildRangeParams(form);
        const mealQuery = new URLSearchParams(rangeQuery);
        const reservationQuery = new URLSearchParams(rangeQuery);
        const studentRequestQuery = new URLSearchParams(rangeQuery);
        studentQuery.forEach((value, key) => studentRequestQuery.set(key, value));

        try {
            const [dailyReport, studentReport, mealReport, reservationReport] = await Promise.all([
                get(`${page.dataset.dailyUrl}?${rangeQuery.toString()}`),
                get(studentRequestQuery.size ? `${page.dataset.studentsUrl}?${studentRequestQuery.toString()}` : page.dataset.studentsUrl),
                get(mealQuery.size ? `${page.dataset.mealsUrl}?${mealQuery.toString()}` : page.dataset.mealsUrl),
                get(reservationQuery.size ? `${page.dataset.reservationsUrl}?${reservationQuery.toString()}` : page.dataset.reservationsUrl),
            ]);

            const dailyRows = dailyReport.results || [];
            const studentRows = studentReport.results || [];
            const mealRows = mealReport.results || [];

            renderDailyTable(dailyRows);
            renderStudentTable(studentRows);
            renderMealTable(mealRows);
            renderCharts(chartCache, dailyReport, reservationReport, mealRows);
            updateSummaryCards(studentReport, mealReport, reservationReport);
            updateReservationSummary(reservationReport.summary);
            updatePrintHeader(form.elements.start_date.value, form.elements.end_date.value);
            updateReportQuery(form);
        } catch (error) {
            window.console.error("Failed to load reports.", error);
            setFeedback(feedback, "danger", "خطا در دریافت گزارش‌ها", extractErrorMessage(error) || "گزارش‌ها دریافت نشد.");
            renderDailyTable([]);
            renderStudentTable([]);
            renderMealTable([]);
        }
    }

    async function handleExportClick(button) {
        const params = buildRangeParams(form);
        params.set("export", button.dataset.exportFormat);
        let targetUrl = "";
        if (button.dataset.exportReport === "daily") {
            targetUrl = `${page.dataset.dailyUrl}?${params.toString()}`;
        } else if (button.dataset.exportReport === "students") {
            buildStudentFilterParams(form).forEach((value, key) => params.set(key, value));
            targetUrl = `${page.dataset.studentsUrl}?${params.toString()}`;
        } else {
            targetUrl = `${page.dataset.mealsUrl}?${params.toString()}`;
        }

        try {
            await downloadReport(targetUrl, `report-${button.dataset.exportReport}.${button.dataset.exportFormat}`);
        } catch (error) {
            window.console.error("Failed to export report.", error);
            showToast("آماده‌سازی گزارش با مشکل مواجه شد.", "danger");
        }
    }

    page.querySelectorAll("[data-export-report]").forEach((button) => {
        button.addEventListener("click", async () => handleExportClick(button));
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        await loadReports();
    });

    resetButton?.addEventListener("click", async () => {
        const defaults = defaultDateRange();
        form.reset();
        form.elements.start_date.value = defaults.start_date;
        form.elements.end_date.value = defaults.end_date;
        await loadReports();
    });

    printButton?.addEventListener("click", () => window.print());

    hydrateFormFromUrl(form);
    loadReports();
}
