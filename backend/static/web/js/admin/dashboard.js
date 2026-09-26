document.addEventListener("DOMContentLoaded", () => {
    const offcanvasLinks = document.querySelectorAll(".admin-sidebar-canvas .admin-sidebar__link");
    offcanvasLinks.forEach((link) => {
        link.addEventListener("click", () => {
            const toggle = document.querySelector(".admin-sidebar-canvas.show");
            if (!toggle || !window.bootstrap?.Offcanvas) {
                return;
            }

            const instance = window.bootstrap.Offcanvas.getInstance(toggle);
            instance?.hide();
        });
    });
});
