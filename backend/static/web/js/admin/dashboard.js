import { extractErrorMessage, get } from "../core/http.js";
import {
    badgeToneForReservationStatus,
    createAlert,
    clearFeedback,
    createStatusBadge,
    emptyRow,
    formatDate,
    formatNumber,
    humanizeReservationState,
    humanizeReservationStatus,
    loadingRow,
    renderPagination,
    setFeedback,
    slicePage,
} from "./components/ui.js";

const PAGE_SIZE = 6;

function updateDashboardQuery(params = {}) {
    const url = new URL(window.location.href);
    ["start_date", "end_date"].forEach((key) => url.searchParams.delete(key));
    Object.entries(params).forEach(([key, value]) => {
        if (value) {
            url.searchParams.set(key, value);
        }
    });
    window.history.replaceState({}, "", url);
}

function buildUtilizationBar(item) {
    const percentage = Math.max(0, Math.min(Number(item.utilization_percentage || 0), 100));
    const tone = percentage >= 100 ? "danger" : percentage >= 75 ? "warning" : "success";
    return `
        <div class="capacity-progress">
            <div class="capacity-progress__meta">
                <span>${formatNumber(item.reservation_count)} / ${formatNumber(item.capacity)}</span>
                <strong>${formatNumber(percentage)}%</strong>
            </div>
            <div class="progress" role="progressbar" aria-label="درصد استفاده از ظرفیت" aria-valuenow="${percentage}" aria-valuemin="0" aria-valuemax="100">
                <div class="progress-bar bg-${tone}" style="width: ${percentage}%"></div>
            </div>
        </div>
    `;
}

function updateSummary(summary) {
    Object.entries(summary || {}).forEach(([key, value]) => {
        const element = document.querySelector(`[data-summary="${key}"]`);
        if (element) {
            element.textContent = formatNumber(value);
        }
    });
}

function renderTodayMeals(rows) {
    const tableBody = document.getElementById("dashboard-today-meals-body");
    if (!tableBody) {
        return;
    }

    if (!rows.length) {
        tableBody.innerHTML = emptyRow(7, "برای امروز برنامه غذایی فعالی ثبت نشده است.");
        return;
    }

    tableBody.innerHTML = rows
        .map(
            (item) => `
                <tr>
                    <td>${item.meal_name}</td>
                    <td>${formatDate(item.date)}</td>
                    <td>${formatNumber(item.capacity)}</td>
                    <td>${formatNumber(item.reservation_count)}</td>
                    <td>${formatNumber(item.remaining_capacity)}</td>
                    <td>${buildUtilizationBar(item)}</td>
                    <td>${createStatusBadge(humanizeReservationState(item.reservation_state), badgeToneForReservationStatus(item.reservation_state))}</td>
                </tr>
            `
        )
        .join("");
}

function renderReservations(rows, page, totalItems = rows.length) {
    const tableBody = document.getElementById("dashboard-reservations-body");
    if (!tableBody) {
        return;
    }

    if (!rows.length) {
        tableBody.innerHTML = emptyRow(5, "برای امروز رزروی ثبت نشده است.");
        return;
    }

    tableBody.innerHTML = rows
        .map(
            (item) => `
                <tr>
                    <td>${item.student_full_name || "-"}</td>
                    <td>${item.student_code}</td>
                    <td>${item.meal_name}</td>
                    <td>${item.reservation_code}</td>
                    <td>${createStatusBadge(humanizeReservationStatus(item.status), badgeToneForReservationStatus(item.status))}</td>
                </tr>
            `
        )
        .join("");

    renderPagination(
        document.getElementById("dashboard-reservations-pagination"),
        totalItems,
        page,
        PAGE_SIZE
    );
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

function renderAlerts(alerts) {
    const container = document.getElementById("dashboard-alerts");
    if (!container) {
        return;
    }

    if (!alerts?.length) {
        container.innerHTML = "";
        return;
    }

    container.innerHTML = alerts
        .map((item) => createAlert(item.tone || "info", item.title, item.message))
        .join("");
}

function renderCharts(cache, charts) {
    upsertChart(cache, "popularMeals", "popular-meals-chart", {
        type: "bar",
        data: {
            labels: charts.popular_meals.map((item) => item.meal_name),
            datasets: [
                {
                    label: "تعداد رزرو",
                    data: charts.popular_meals.map((item) => item.total_reservations),
                    backgroundColor: "rgba(31, 75, 153, 0.75)",
                    borderRadius: 10,
                },
            ],
        },
        options: { responsive: true, maintainAspectRatio: false },
    }, charts.popular_meals.length > 0);

    upsertChart(cache, "dailyReservations", "daily-reservations-chart", {
        type: "line",
        data: {
            labels: charts.daily_reservations.map((item) => formatDate(item.date)),
            datasets: [
                {
                    label: "رزروهای روزانه",
                    data: charts.daily_reservations.map((item) => item.reservation_count),
                    borderColor: "#1f4b99",
                    backgroundColor: "rgba(31, 75, 153, 0.18)",
                    fill: true,
                    tension: 0.35,
                },
            ],
        },
        options: { responsive: true, maintainAspectRatio: false },
    }, charts.daily_reservations.length > 0);

    upsertChart(cache, "reservationStatus", "reservation-status-chart", {
        type: "doughnut",
        data: {
            labels: charts.status_distribution.map((item) => humanizeReservationStatus(item.status)),
            datasets: [
                {
                    data: charts.status_distribution.map((item) => item.count),
                    backgroundColor: ["#1f4b99", "#b63c3c", "#1f7a52", "#b7791f"],
                },
            ],
        },
        options: { responsive: true, maintainAspectRatio: false },
    }, charts.status_distribution.some((item) => Number(item.count) > 0));
}

export function init() {
    const page = document.getElementById("admin-dashboard-page");
    if (!page) {
        return;
    }

    const feedback = document.getElementById("admin-dashboard-feedback");
    const form = document.getElementById("dashboard-range-form");
    const resetButton = document.getElementById("dashboard-reset-range");
    const startInput = document.getElementById("dashboard-start-date");
    const endInput = document.getElementById("dashboard-end-date");
    const chartCache = {};
    const reservationsPagination = document.getElementById("dashboard-reservations-pagination");
    let reservationRows = [];
    let reservationPage = 1;
    const currentUrl = new URL(window.location.href);

    startInput.value = currentUrl.searchParams.get("start_date") || "";
    endInput.value = currentUrl.searchParams.get("end_date") || "";

    function renderReservationPage() {
        renderReservations(
            slicePage(reservationRows, reservationPage, PAGE_SIZE),
            reservationPage,
            reservationRows.length
        );
    }

    async function loadDashboard(params = {}) {
        clearFeedback(feedback);
        document.getElementById("dashboard-today-meals-body").innerHTML = loadingRow(7);
        document.getElementById("dashboard-reservations-body").innerHTML = loadingRow(5);

        try {
            const query = new URLSearchParams(params);
            const dashboardUrl = query.size ? `${page.dataset.dashboardUrl}?${query.toString()}` : page.dataset.dashboardUrl;
            const dashboardData = await get(dashboardUrl);
            const reservationsData = await get(`${page.dataset.byDateUrl}?date=${dashboardData.current_date}`);

            updateSummary(dashboardData.summary);
            renderTodayMeals(dashboardData.today_meals || []);
            renderAlerts(dashboardData.alerts || []);
            reservationRows = reservationsData || [];
            reservationPage = 1;
            renderReservationPage();
            renderCharts(chartCache, dashboardData.charts);

            if (dashboardData.start_date) {
                startInput.value = dashboardData.start_date;
            }
            if (dashboardData.end_date) {
                endInput.value = dashboardData.end_date;
            }
            updateDashboardQuery({
                start_date: startInput.value,
                end_date: endInput.value,
            });
        } catch (error) {
            window.console.error("Failed to load admin dashboard.", error);
            setFeedback(feedback, "danger", "خطا در دریافت اطلاعات", extractErrorMessage(error) || "دریافت اطلاعات داشبورد با مشکل مواجه شد.");
            renderAlerts([]);
        }
    }

    form?.addEventListener("submit", (event) => {
        event.preventDefault();
        loadDashboard({
            start_date: startInput.value,
            end_date: endInput.value,
        });
    });

    resetButton?.addEventListener("click", () => {
        startInput.value = "";
        endInput.value = "";
        loadDashboard();
    });

    reservationsPagination?.addEventListener("click", (event) => {
        const button = event.target.closest("[data-page]");
        if (!button) {
            return;
        }

        reservationPage = Number(button.dataset.page);
        renderReservationPage();
    });

    loadDashboard({
        start_date: startInput.value,
        end_date: endInput.value,
    });
}
