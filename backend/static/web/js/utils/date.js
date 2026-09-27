const dateFormatter = new Intl.DateTimeFormat("fa-IR-u-ca-persian", {
    year: "numeric",
    month: "long",
    day: "numeric",
});

const weekdayDateFormatter = new Intl.DateTimeFormat("fa-IR-u-ca-persian", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
});

const weekdayFormatter = new Intl.DateTimeFormat("fa-IR-u-ca-persian", {
    weekday: "long",
});

const dateTimeFormatter = new Intl.DateTimeFormat("fa-IR-u-ca-persian", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
});

const timeFormatter = new Intl.DateTimeFormat("fa-IR", {
    hour: "2-digit",
    minute: "2-digit",
});

export function parseIsoDate(dateString) {
    if (!dateString) {
        return null;
    }

    const [year, month, day] = String(dateString).split("-").map(Number);
    if (!year || !month || !day) {
        return null;
    }

    return new Date(year, month - 1, day);
}

export function getTodayIsoDate() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
}

export function formatPersianDate(dateString, options = {}) {
    const { withWeekday = true } = options;
    const date = parseIsoDate(dateString);
    if (!date) {
        return "-";
    }

    return withWeekday ? weekdayDateFormatter.format(date) : dateFormatter.format(date);
}

export function formatPersianWeekday(dateString) {
    const date = parseIsoDate(dateString);
    if (!date) {
        return "-";
    }

    return weekdayFormatter.format(date);
}

export function formatDateTime(dateTimeString) {
    if (!dateTimeString) {
        return "-";
    }

    return dateTimeFormatter.format(new Date(dateTimeString));
}

export function formatTime(dateTimeString) {
    if (!dateTimeString) {
        return "-";
    }

    return timeFormatter.format(new Date(dateTimeString));
}
