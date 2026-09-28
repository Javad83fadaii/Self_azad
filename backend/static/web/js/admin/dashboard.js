import { extractErrorMessage, get } from "../core/http.js";
import {
    badgeToneForReservationStatus,
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
        tableBody.innerHTML = emptyRow(6, "برای امروز برنامه غذایی فعالی ثبت نشده است.");
        return;
    }

    tableBody.innerHTML = rows
        .map(
            (item) => `
                <tr>
                    <td>${item.meal_name}</td>
                    <td>${formatDate(item.date)}</td>
                    <td>${formatNumber(item.reservation_count)}</td>
                    <td>${formatNumber(item.capacity)}</td>
                    <td>${formatNumber(item.remaining_capacity)}</td>
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
    });

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
    });

    const totalReservations = charts.daily_reservations.reduce((sum, item) => sum + item.reservation_count, 0);
    const totalCancelled = charts.cancelled_reservations.reduce((sum, item) => sum + item.cancelled_count, 0);
    upsertChart(cache, "reservationStatus", "reservation-status-chart", {
        type: "doughnut",
        data: {
            labels: ["رزرو شده", "لغوشده"],
            datasets: [
                {
                    data: [totalReservations, totalCancelled],
                    backgroundColor: ["#1f7a52", "#b63c3c"],
                },
            ],
        },
        options: { responsive: true, maintainAspectRatio: false },
    });
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

    function renderReservationPage() {
        renderReservations(
            slicePage(reservationRows, reservationPage, PAGE_SIZE),
            reservationPage,
            reservationRows.length
        );
    }

    async function loadDashboard(params = {}) {
        clearFeedback(feedback);
        document.getElementById("dashboard-today-meals-body").innerHTML = loadingRow(6);
        document.getElementById("dashboard-reservations-body").innerHTML = loadingRow(5);

        try {
            const query = new URLSearchParams(params);
            const dashboardUrl = query.size ? `${page.dataset.dashboardUrl}?${query.toString()}` : page.dataset.dashboardUrl;
            const dashboardData = await get(dashboardUrl);
            const reservationsData = await get(`${page.dataset.byDateUrl}?date=${dashboardData.current_date}`);

            updateSummary(dashboardData.summary);
            renderTodayMeals(dashboardData.today_meals || []);
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
        } catch (error) {
            window.console.error("Failed to load admin dashboard.", error);
            setFeedback(feedback, "danger", "خطا در دریافت اطلاعات", extractErrorMessage(error) || "دریافت اطلاعات داشبورد با مشکل مواجه شد.");
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

    loadDashboard();
}
