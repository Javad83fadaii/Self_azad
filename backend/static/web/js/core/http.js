function readCookie(name) {
    const cookieValue = document.cookie
        .split(";")
        .map((item) => item.trim())
        .find((item) => item.startsWith(`${name}=`));

    return cookieValue ? decodeURIComponent(cookieValue.split("=").slice(1).join("=")) : "";
}

function isSafeMethod(method) {
    return ["GET", "HEAD", "OPTIONS", "TRACE"].includes(String(method).toUpperCase());
}

async function parseResponseBody(response) {
    const contentType = response.headers.get("content-type") || "";
    if (!contentType.includes("application/json")) {
        return null;
    }

    try {
        return await response.json();
    } catch (error) {
        return null;
    }
}

function createApiError(response, data) {
    const error = new Error("API request failed.");
    error.status = response.status;
    error.data = data;
    error.detail = normalizeErrorDetail(data);
    return error;
}

function normalizeErrorDetail(data) {
    if (!data || typeof data !== "object") {
        return "";
    }

    if (typeof data.detail === "string" && data.detail.trim()) {
        return data.detail.trim();
    }

    for (const value of Object.values(data)) {
        if (Array.isArray(value) && value.length > 0) {
            return String(value[0]).trim();
        }

        if (typeof value === "string" && value.trim()) {
            return value.trim();
        }
    }

    return "";
}

export async function ensureCsrfToken(csrfUrl) {
    const existingToken = readCookie("csrftoken");
    if (existingToken) {
        return existingToken;
    }

    if (!csrfUrl) {
        return "";
    }

    await fetch(csrfUrl, {
        method: "GET",
        credentials: "same-origin",
        headers: {
            Accept: "application/json",
        },
    });

    return readCookie("csrftoken");
}

export async function request(url, options = {}) {
    const {
        method = "GET",
        data,
        headers = {},
        csrfUrl = "",
        withCsrf = !isSafeMethod(method),
        credentials = "same-origin",
    } = options;
    const requestHeaders = {
        Accept: "application/json",
        ...headers,
    };

    const config = {
        method,
        credentials,
        headers: requestHeaders,
    };

    if (data !== undefined) {
        requestHeaders["Content-Type"] = "application/json";
        config.body = JSON.stringify(data);
    }

    if (withCsrf) {
        const csrfToken = await ensureCsrfToken(csrfUrl);
        if (csrfToken) {
            requestHeaders["X-CSRFToken"] = csrfToken;
        }
    }

    const response = await fetch(url, config);
    const responseData = await parseResponseBody(response);

    if (!response.ok) {
        throw createApiError(response, responseData);
    }

    return responseData;
}

export function get(url, options = {}) {
    return request(url, {
        ...options,
        method: "GET",
        withCsrf: false,
    });
}

export function post(url, data, options = {}) {
    return request(url, {
        ...options,
        method: "POST",
        data,
    });
}

export function put(url, data, options = {}) {
    return request(url, {
        ...options,
        method: "PUT",
        data,
    });
}

export function patch(url, data, options = {}) {
    return request(url, {
        ...options,
        method: "PATCH",
        data,
    });
}

export function del(url, data, options = {}) {
    return request(url, {
        ...options,
        method: "DELETE",
        data,
    });
}

export async function postJson(url, payload, csrfToken) {
    const response = await fetch(url, {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify(payload),
    });
    const data = await parseResponseBody(response);

    if (!response.ok) {
        throw createApiError(response, data);
    }

    return data;
}

export function extractErrorMessage(error) {
    if (error?.status === 401 || error?.status === 403) {
        return "جلسه ورود شما منقضی شده است.";
    }

    if (typeof error?.detail === "string" && error.detail.trim()) {
        return error.detail;
    }

    const detail = normalizeErrorDetail(error?.data);
    if (detail) {
        return detail;
    }

    return "ارتباط با سرور برقرار نشد.";
}
