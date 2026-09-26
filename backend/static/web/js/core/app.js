import { extractErrorMessage, get, post } from "./http.js";

function getRoleLabel(role) {
    if (role === "ADMIN") {
        return "مدیر سامانه";
    }

    if (role === "STUDENT") {
        return "دانشجو";
    }

    return "مهمان";
}

function updateAuthUi(user) {
    const displayName = [user?.first_name, user?.last_name].filter(Boolean).join(" ").trim() || user?.username || "";
    document.querySelectorAll("[data-auth-user-name]").forEach((element) => {
        element.textContent = displayName;
    });
    document.querySelectorAll("[data-auth-role-label]").forEach((element) => {
        element.textContent = getRoleLabel(user?.role);
    });
}

function redirectToResolvedHome(user) {
    const { adminHomeUrl, studentHomeUrl, loginUrl } = document.body.dataset;

    if (user?.role === "ADMIN" && adminHomeUrl) {
        window.location.assign(adminHomeUrl);
        return;
    }

    if (user?.role === "STUDENT" && studentHomeUrl) {
        window.location.assign(studentHomeUrl);
        return;
    }

    if (loginUrl) {
        window.location.assign(loginUrl);
    }
}

async function ensureAuthenticatedSession() {
    if (document.body.dataset.requiresAuth !== "true") {
        return null;
    }

    try {
        const user = await get(document.body.dataset.authMeUrl);
        updateAuthUi(user);

        const requiredRole = document.body.dataset.requiredRole;
        if (requiredRole && user?.role !== requiredRole) {
            redirectToResolvedHome(user);
            return null;
        }

        return user;
    } catch (error) {
        if (error?.status === 401 || error?.status === 403) {
            redirectToResolvedHome(null);
            return null;
        }

        throw error;
    }
}

function bindLogoutActions() {
    const triggers = document.querySelectorAll("[data-logout-trigger]");
    if (triggers.length === 0) {
        return;
    }

    triggers.forEach((button) => {
        button.addEventListener("click", async () => {
            const initialContent = button.innerHTML;
            button.disabled = true;
            button.innerHTML = '<i class="fa-solid fa-spinner fa-spin" aria-hidden="true"></i><span>در حال خروج...</span>';

            try {
                await post(document.body.dataset.logoutUrl, {});
                window.location.assign(document.body.dataset.loginUrl);
            } catch (error) {
                window.alert(extractErrorMessage(error));
                button.disabled = false;
                button.innerHTML = initialContent;
            }
        });
    });
}

document.addEventListener("DOMContentLoaded", async () => {
    bindLogoutActions();

    try {
        await ensureAuthenticatedSession();
    } catch (error) {
        window.console.error("Failed to resolve authentication state.", error);
    }
});
