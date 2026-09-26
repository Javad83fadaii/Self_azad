document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".stat-card, .panel-card").forEach((card) => {
        card.setAttribute("tabindex", "0");
    });
});
