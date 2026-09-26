import { ensureCsrfToken, extractErrorMessage, post } from "../core/http.js";

const form = document.querySelector("#student-login-form");
const feedback = document.querySelector("#login-feedback");
const submitButton = document.querySelector("#login-submit");

function showFeedback(message, level = "danger") {
    feedback.className = `alert alert-${level}`;
    feedback.textContent = message;
}

function setLoading(isLoading) {
    submitButton.disabled = isLoading;
    const label = submitButton.querySelector(".login-submit__label");
    if (label) {
        label.textContent = isLoading ? "در حال ورود..." : "ورود به سامانه";
    }
}

function validateField(field) {
    const isValid = Boolean(field.value.trim());
    field.classList.toggle("is-invalid", !isValid);
    return isValid;
}

function validateForm() {
    return [form.student_code, form.phone_number].every(validateField);
}

if (form && feedback && submitButton) {
    [form.student_code, form.phone_number].forEach((field) => {
        field.addEventListener("input", () => {
            validateField(field);
        });
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        if (!validateForm()) {
            showFeedback("کد دانشجویی و شماره موبایل را وارد کنید.", "warning");
            return;
        }

        setLoading(true);
        feedback.className = "d-none";
        feedback.textContent = "";

        try {
            await ensureCsrfToken(form.dataset.csrfUrl);
            await post(
                form.dataset.loginUrl,
                {
                    student_code: form.student_code.value.trim(),
                    phone_number: form.phone_number.value.trim(),
                },
                {
                    csrfUrl: form.dataset.csrfUrl,
                },
            );
            window.location.assign(form.dataset.successUrl);
        } catch (error) {
            showFeedback(extractErrorMessage(error));
        } finally {
            setLoading(false);
        }
    });
}
