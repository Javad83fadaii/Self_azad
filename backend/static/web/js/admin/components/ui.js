const numberFormatter = new Intl.NumberFormat("fa-IR");

export function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

export function formatNumber(value) {
    const numericValue = Number(value ?? 0);
    return numberFormatter.format(Number.isFinite(numericValue) ? numericValue : 0);
}

export function formatCurrency(value) {
    return `${formatNumber(value)} ریال`;
}

export function formatDate(value) {
    if (!value) {
        return "-";
    }

    try {
        return new Intl.DateTimeFormat("fa-IR", {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
        }).format(new Date(`${value}T00:00:00`));
    } catch (error) {
        return value;
    }
}

export function formatDateTime(value) {
    if (!value) {
        return "-";
    }

    try {
        return new Intl.DateTimeFormat("fa-IR", {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
        }).format(new Date(value));
    } catch (error) {
        return value;
    }
}

export function toDatetimeLocalValue(value) {
    if (!value) {
        return "";
    }

    const date = new Date(value);
    const offset = date.getTimezoneOffset();
    const localDate = new Date(date.getTime() - offset * 60 * 1000);
    return localDate.toISOString().slice(0, 16);
}

export function createStatusBadge(label, tone = "secondary") {
    return `<span class="status-badge status-badge--${escapeHtml(tone)}">${escapeHtml(label)}</span>`;
}

export function humanizeReservationStatus(status) {
    const mapping = {
        RESERVED: "رزرو شده",
        CANCELLED: "لغوشده",
        USED: "استفاده‌شده",
        NO_SHOW: "عدم مراجعه",
    };
    return mapping[status] || status || "-";
}

export function humanizeReservationState(state) {
    const mapping = {
        AVAILABLE: "قابل رزرو",
        FULL: "تکمیل ظرفیت",
        CLOSED: "بسته",
        NOT_OPEN: "هنوز باز نشده",
        INACTIVE: "غیرفعال",
    };
    return mapping[state] || state || "-";
}

export function humanizeActiveState(isActive) {
    return isActive ? "فعال" : "غیرفعال";
}

export function loadingRow(colspan, message = "در حال دریافت اطلاعات...") {
    return `<tr><td colspan="${colspan}" class="text-center py-4">${escapeHtml(message)}</td></tr>`;
}

export function emptyRow(colspan, message = "موردی برای نمایش وجود ندارد.") {
    return `<tr><td colspan="${colspan}" class="text-center py-4 text-muted">${escapeHtml(message)}</td></tr>`;
}

export function createAlert(level, title, message) {
    return `
        <div class="alert alert-${escapeHtml(level)}" role="alert">
            ${title ? `<div class="fw-semibold mb-1">${escapeHtml(title)}</div>` : ""}
            <div>${escapeHtml(message)}</div>
        </div>
    `;
}

export function setFeedback(container, level, title, message) {
    if (!container) {
        return;
    }

    container.classList.remove("d-none");
    container.innerHTML = createAlert(level, title, message);
}

export function clearFeedback(container) {
    if (!container) {
        return;
    }

    container.classList.add("d-none");
    container.innerHTML = "";
}

export function ensureToastContainer() {
    let container = document.getElementById("admin-toast-container");
    if (container) {
        return container;
    }

    container = document.createElement("div");
    container.id = "admin-toast-container";
    container.className = "toast-container position-fixed top-0 start-0 p-3";
    document.body.appendChild(container);
    return container;
}

export function showToast(message, tone = "primary") {
    const container = ensureToastContainer();
    const toast = document.createElement("div");
    toast.className = `toast align-items-center border-0 text-bg-${tone}`;
    toast.setAttribute("role", "status");
    toast.setAttribute("aria-live", "polite");
    toast.setAttribute("aria-atomic", "true");
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${escapeHtml(message)}</div>
            <button type="button" class="btn-close btn-close-white ms-2 me-auto m-2" data-bs-dismiss="toast" aria-label="بستن"></button>
        </div>
    `;
    container.appendChild(toast);
    const instance = new window.bootstrap.Toast(toast, { delay: 3000 });
    toast.addEventListener("hidden.bs.toast", () => toast.remove(), { once: true });
    instance.show();
}

export function buildPagination(totalItems, page, pageSize) {
    const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
    return {
        totalPages,
        startIndex: (page - 1) * pageSize,
        endIndex: page * pageSize,
    };
}

export function renderPagination(container, totalItems, page, pageSize) {
    if (!container) {
        return;
    }

    const { totalPages } = buildPagination(totalItems, page, pageSize);
    if (totalPages <= 1) {
        container.innerHTML = "";
        return;
    }

    const items = Array.from({ length: totalPages }, (_, index) => {
        const pageNumber = index + 1;
        const activeClass = pageNumber === page ? " is-active" : "";
        return `<button type="button" class="pagination-placeholder__item${activeClass}" data-page="${pageNumber}">${formatNumber(pageNumber)}</button>`;
    }).join("");

    container.innerHTML = `
        <nav aria-label="صفحه‌بندی" class="pagination-placeholder">
            <span class="pagination-placeholder__label">صفحه ${formatNumber(page)} از ${formatNumber(totalPages)}</span>
            <div class="pagination-placeholder__items">${items}</div>
        </nav>
    `;
}

export function slicePage(items, page, pageSize) {
    const { startIndex, endIndex } = buildPagination(items.length, page, pageSize);
    return items.slice(startIndex, endIndex);
}

export function badgeToneForReservationStatus(status) {
    const mapping = {
        RESERVED: "primary",
        USED: "success",
        CANCELLED: "danger",
        NO_SHOW: "warning",
        AVAILABLE: "success",
        FULL: "danger",
        CLOSED: "secondary",
        NOT_OPEN: "info",
        INACTIVE: "warning",
    };
    return mapping[status] || "secondary";
}
