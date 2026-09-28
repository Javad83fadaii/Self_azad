import { consumeLoginMessage, ensureCsrfToken, extractErrorMessage, post } from "../core/http.js";

function showFeedback(feedback, message, level = "danger") {
    feedback.className = `alert alert-${level}`;
    feedback.textContent = message;
}

function setLoading(submitButton, isLoading, idleLabel, loadingLabel) {
    submitButton.disabled = isLoading;
    const label = submitButton.querySelector(".login-submit__label");
    if (label) {
        label.textContent = isLoading ? loadingLabel : idleLabel;
    }
}

function validateField(field) {
    const isValid = Boolean(field.value.trim());
    field.classList.toggle("is-invalid", !isValid);
    return isValid;
}

function validateForm(form) {
    return Array.from(form.querySelectorAll("input[required]")).every(validateField);
}

function bindLoginForm(form) {
    const feedback = form.parentElement.querySelector("[data-login-feedback]");
    const submitButton = form.querySelector("button[type='submit']");
    if (!feedback || !submitButton) {
        return;
    }

    const idleLabel = submitButton.querySelector(".login-submit__label")?.textContent?.trim() || "ورود";
    const loadingLabel = "در حال ورود...";

    form.querySelectorAll("input[required]").forEach((field) => {
        field.addEventListener("input", () => {
            validateField(field);
        });
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        if (!validateForm(form)) {
            showFeedback(feedback, "لطفاً همه فیلدهای ضروری را تکمیل کنید.", "warning");
            return;
        }

        setLoading(submitButton, true, idleLabel, loadingLabel);
        feedback.className = "alert d-none";
        feedback.textContent = "";

        try {
            await ensureCsrfToken(form.dataset.csrfUrl);
            const payload = Object.fromEntries(new window.FormData(form).entries());
            await post(form.dataset.loginUrl, payload, { csrfUrl: form.dataset.csrfUrl });
            window.location.assign(form.dataset.successUrl);
        } catch (error) {
            showFeedback(feedback, extractErrorMessage(error));
        } finally {
            setLoading(submitButton, false, idleLabel, loadingLabel);
        }
    });
}

const forms = document.querySelectorAll("[data-web-login-form]");

if (forms.length) {
    const loginMessage = consumeLoginMessage();
    if (loginMessage) {
        const firstFeedback = document.querySelector("[data-login-feedback]");
        if (firstFeedback) {
            showFeedback(firstFeedback, loginMessage, "warning");
        }
    }

    forms.forEach(bindLoginForm);
}
