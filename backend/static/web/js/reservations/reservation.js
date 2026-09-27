import { del, post } from "../core/http.js";

const RESERVATION_ERROR_MAP = new Map([
    ["Schedule capacity is full.", "ظرفیت تکمیل شده است."],
    ["Reservation is outside the allowed window.", "مهلت رزرو به پایان رسیده است یا هنوز فعال نشده است."],
    ["Inactive schedules cannot be reserved.", "این برنامه غذایی غیرفعال است و قابل رزرو نیست."],
    ["Inactive meals cannot be reserved.", "این غذا غیرفعال است و قابل رزرو نیست."],
    ["Past schedules cannot be reserved.", "رزرو برای تاریخ گذشته مجاز نیست."],
    ["Duplicate reservation for this day is not allowed.", "شما برای این روز قبلاً رزرو کرده‌اید."],
    ["Only active reservations can be cancelled.", "فقط رزرو فعال قابل لغو است."],
]);

const RESERVATION_STATUS_META = {
    RESERVED: { label: "فعال", className: "status-badge status-badge--success" },
    CANCELLED: { label: "لغوشده", className: "status-badge status-badge--danger" },
    USED: { label: "استفاده‌شده", className: "status-badge status-badge--primary" },
    NO_SHOW: { label: "عدم مراجعه", className: "status-badge status-badge--warning" },
};

const SCHEDULE_STATE_META = {
    AVAILABLE: { label: "قابل رزرو", className: "status-badge status-badge--success" },
    FULL: { label: "ظرفیت تکمیل است", className: "status-badge status-badge--danger" },
    NOT_OPEN: { label: "رزرو هنوز فعال نشده است", className: "status-badge status-badge--warning" },
    CLOSED: { label: "مهلت رزرو به پایان رسیده است", className: "status-badge status-badge--secondary" },
};

function normalizeMessage(message) {
    return String(message || "").trim();
}

export function mapReservationError(error, fallbackMessage = "امکان انجام عملیات رزرو وجود ندارد.") {
    if (error?.status === 401 || error?.status === 403) {
        return "جلسه ورود شما منقضی شده است.";
    }

    const detail = normalizeMessage(error?.detail);
    if (RESERVATION_ERROR_MAP.has(detail)) {
        return RESERVATION_ERROR_MAP.get(detail);
    }

    for (const [apiMessage, translatedMessage] of RESERVATION_ERROR_MAP.entries()) {
        if (detail.includes(apiMessage)) {
            return translatedMessage;
        }
    }

    if (detail) {
        return detail;
    }

    return fallbackMessage;
}

export function getReservationStatusMeta(status, statusLabel = "") {
    return RESERVATION_STATUS_META[status] || {
        label: statusLabel || status || "نامشخص",
        className: "status-badge status-badge--soft",
    };
}

export function getScheduleStateMeta(state) {
    return SCHEDULE_STATE_META[state] || {
        label: "نامشخص",
        className: "status-badge status-badge--soft",
    };
}

export function isActiveReservation(reservation) {
    return reservation?.status === "RESERVED";
}

export function buildCancelUrl(template, reservationId) {
    return String(template || "").replace("__id__", String(reservationId));
}

export async function createReservation({ url, mealScheduleId, csrfUrl }) {
    return post(
        url,
        {
            meal_schedule_id: mealScheduleId,
        },
        {
            csrfUrl,
        },
    );
}

export async function cancelReservation({ url, csrfUrl }) {
    return del(url, undefined, { csrfUrl });
}
