import { init as initActivity } from "./activity.js";
import { init as initDashboard } from "./dashboard.js";
import { init as initMeals } from "./meals.js";
import { init as initReports } from "./reports.js";
import { init as initReservations } from "./reservations.js";
import { init as initSchedules } from "./schedules.js";
import { init as initStudents } from "./students.js";

const initializers = {
    activity: initActivity,
    dashboard: initDashboard,
    meals: initMeals,
    schedules: initSchedules,
    reservations: initReservations,
    students: initStudents,
    reports: initReports,
};

function bootAdminPage() {
    const pageName = document.body?.dataset?.adminPage;
    const initializer = initializers[pageName];
    if (initializer) {
        initializer();
    }
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootAdminPage, { once: true });
} else {
    bootAdminPage();
}
