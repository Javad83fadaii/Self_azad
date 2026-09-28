import { extractErrorMessage, get } from "../core/http.js";
import {
    clearFeedback,
    createStatusBadge,
    emptyRow,
    escapeHtml,
    formatDate,
    formatNumber,
    loadingRow,
    setFeedback,
} from "./components/ui.js";

function upsertChart(cache, key, canvasId, config) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !window.Chart) {
        return;
    }

    if (cache[key]) {
        cache[key].destroy();
    }

    cache[key] = new window.Chart(canvas, config);
}

function renderDailyTable(rows) {
    const tableBody = document.getElementById("daily-report-body");
    if (!rows.length) {
        tableBody.innerHTML = emptyRow(6, "برای تاریخ انتخابی گزارشی ثبت نشده است.");
        return;
    }

    tableBody.innerHTML = rows
        .map(
            (item) => `
                <tr>
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
        tableBody.innerHTML = emptyRow(7, "گزارش دانشجویی با فیلتر فعلی خالی است.");
        return;
    }

    tableBody.innerHTML = rows
        .map(
            (item) => `
                <tr>
                    <td>${escapeHtml(item.full_name)}</td>
                    <td>${escapeHtml(item.student_code)}</td>
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
        tableBody.innerHTML = emptyRow(8, "گزارش عملکرد غذاها خالی است.");
        return;
    }

    tableBody.innerHTML = rows
        .map(
            (item) => `
                <tr>
                    <td>${escapeHtml(item.meal_name)}</td>
                    <td>${escapeHtml(item.meal_code)}</td>
                    <td>${formatNumber(item.total_reservations)}</td>
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

function renderCharts(chartCache, dailyRows, studentRows, mealRows) {
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
    });

    upsertChart(chartCache, "dailyReport", "reports-daily-chart", {
        type: "line",
        data: {
            labels: dailyRows.map((item) => item.meal_name),
            datasets: [
                {
                    label: "رزرو",
                    data: dailyRows.map((item) => item.reservation_count),
                    borderColor: "#1f4b99",
                    backgroundColor: "rgba(31, 75, 153, 0.16)",
                    fill: true,
                    tension: 0.35,
                },
                {
                    label: "ظرفیت",
                    data: dailyRows.map((item) => item.capacity),
                    borderColor: "#1f7a52",
                    backgroundColor: "rgba(31, 122, 82, 0.08)",
                    fill: false,
                    tension: 0.35,
                },
            ],
        },
        options: { responsive: true, maintainAspectRatio: false },
    });

    const totals = studentRows.reduce(
        (accumulator, item) => {
            accumulator.active += item.active_reservations;
            accumulator.cancelled += item.cancelled_count;
            accumulator.used += item.used_count;
            accumulator.noShow += item.no_show_count;
            return accumulator;
        },
        { active: 0, cancelled: 0, used: 0, noShow: 0 }
    );

    upsertChart(chartCache, "studentReport", "reports-students-chart", {
        type: "doughnut",
        data: {
            labels: ["فعال", "لغوشده", "استفاده‌شده", "عدم مراجعه"],
            datasets: [
                {
                    data: [totals.active, totals.cancelled, totals.used, totals.noShow],
                    backgroundColor: ["#1f4b99", "#b63c3c", "#1f7a52", "#b7791f"],
                },
            ],
        },
        options: { responsive: true, maintainAspectRatio: false },
    });
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

function triggerReportDownload(url) {
    const link = document.createElement("a");
    link.href = url;
    link.rel = "noopener";
    document.body.appendChild(link);
    link.click();
    link.remove();
}

export function init() {
    const page = document.getElementById("admin-reports-page");
    if (!page) {
        return;
    }

    const feedback = document.getElementById("admin-reports-feedback");
    const form = document.getElementById("reports-filter-form");
    const dailyDateInput = document.getElementById("daily-report-date");
    const chartCache = {};

    async function loadReports() {
        clearFeedback(feedback);
        document.getElementById("daily-report-body").innerHTML = loadingRow(6);
        document.getElementById("student-report-body").innerHTML = loadingRow(7);
        document.getElementById("meal-report-body").innerHTML = loadingRow(8);

        const studentQuery = buildStudentFilterParams(form);

        try {
            const [dailyReport, studentReport, mealReport] = await Promise.all([
                get(`${page.dataset.dailyUrl}?date=${encodeURIComponent(dailyDateInput.value)}`),
                get(studentQuery.size ? `${page.dataset.studentsUrl}?${studentQuery.toString()}` : page.dataset.studentsUrl),
                get(page.dataset.mealsUrl),
            ]);

            const dailyRows = dailyReport.results || [];
            const studentRows = studentReport.results || [];
            const mealRows = mealReport.results || [];

            renderDailyTable(dailyRows);
            renderStudentTable(studentRows);
            renderMealTable(mealRows);
            renderCharts(chartCache, dailyRows, studentRows, mealRows);
        } catch (error) {
            window.console.error("Failed to load reports.", error);
            setFeedback(feedback, "danger", "خطا در دریافت گزارش‌ها", extractErrorMessage(error) || "گزارش‌ها دریافت نشد.");
            renderDailyTable([]);
            renderStudentTable([]);
            renderMealTable([]);
        }
    }

    function handleExportClick(button) {
        const params = new URLSearchParams();
        params.set("export", button.dataset.exportFormat);

        if (button.dataset.exportReport === "daily") {
            params.set("date", dailyDateInput.value || new Date().toISOString().slice(0, 10));
            triggerReportDownload(`${page.dataset.dailyUrl}?${params.toString()}`);
            return;
        }

        if (button.dataset.exportReport === "students") {
            buildStudentFilterParams(form).forEach((value, key) => params.set(key, value));
            triggerReportDownload(`${page.dataset.studentsUrl}?${params.toString()}`);
            return;
        }

        triggerReportDownload(`${page.dataset.mealsUrl}?${params.toString()}`);
    }

    page.querySelectorAll("[data-export-report]").forEach((button) => {
        button.addEventListener("click", () => handleExportClick(button));
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        await loadReports();
    });

    if (!dailyDateInput.value) {
        dailyDateInput.value = new Date().toISOString().slice(0, 10);
    }

    loadReports();
}
