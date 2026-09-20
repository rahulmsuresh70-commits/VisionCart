/* ============================================================
   VISIONCART - MAIN JAVASCRIPT
   ============================================================ */


/* ============================================================
   01. DOM READY
   ============================================================ */

document.addEventListener("DOMContentLoaded", function () {

    // Initialize all VisionCart UI interactions.

    initializeRevealAnimations();

    initializeDeleteConfirmations();

    initializeFormSubmissionProtection();

    initializeAutoDismissAlerts();

    initializeSmoothScrolling();

    initializeImageLoading();

});


/* ============================================================
   02. SCROLL REVEAL ANIMATIONS
   ============================================================ */

function initializeRevealAnimations() {

    const revealElements =
        document.querySelectorAll(".vc-reveal");


    if (!revealElements.length) {
        return;
    }


    // Use IntersectionObserver when supported.

    if ("IntersectionObserver" in window) {

        const observer =
            new IntersectionObserver(
                function (entries, observerInstance) {

                    entries.forEach(function (entry) {

                        if (entry.isIntersecting) {

                            entry.target.classList.add(
                                "is-visible"
                            );

                            observerInstance.unobserve(
                                entry.target
                            );

                        }

                    });

                },
                {
                    threshold: 0.12
                }
            );


        revealElements.forEach(function (element) {

            observer.observe(element);

        });

    } else {

        // Fallback for browsers without IntersectionObserver.

        revealElements.forEach(function (element) {

            element.classList.add("is-visible");

        });

    }

}


/* ============================================================
   03. DELETE CONFIRMATION
   ============================================================ */

function initializeDeleteConfirmations() {

    const deleteButtons =
        document.querySelectorAll(
            "[data-delete-confirm]"
        );


    if (!deleteButtons.length) {
        return;
    }


    deleteButtons.forEach(function (button) {

        button.addEventListener(
            "click",
            function (event) {

                const message =
                    button.getAttribute(
                        "data-delete-confirm"
                    );


                if (!message) {
                    return;
                }


                const confirmed =
                    window.confirm(message);


                if (!confirmed) {

                    event.preventDefault();

                }

            }
        );

    });

}


/* ============================================================
   04. FORM SUBMISSION PROTECTION
   ============================================================ */

function initializeFormSubmissionProtection() {

    const forms =
        document.querySelectorAll(
            "form[data-protect-submit]"
        );


    if (!forms.length) {
        return;
    }


    forms.forEach(function (form) {

        form.addEventListener(
            "submit",
            function () {

                // Prevent accidental double-click submissions.

                const submitButtons =
                    form.querySelectorAll(
                        "button[type='submit'], input[type='submit']"
                    );


                submitButtons.forEach(
                    function (button) {

                        button.disabled = true;

                        button.classList.add(
                            "vc-loading"
                        );


                        // Preserve the original button text.

                        if (
                            button.tagName.toLowerCase()
                            === "button"
                        ) {

                            if (
                                !button.dataset.originalText
                            ) {

                                button.dataset.originalText =
                                    button.innerHTML;

                            }


                            button.innerHTML =
                                `
                                <span
                                    class="spinner-border spinner-border-sm me-2"
                                    aria-hidden="true"
                                ></span>
                                Processing...
                                `;

                        }

                    }
                );

            }
        );

    });

}


/* ============================================================
   05. ALERT AUTO DISMISS
   ============================================================ */

function initializeAutoDismissAlerts() {

    const alerts =
        document.querySelectorAll(
            ".vc-alert[data-auto-dismiss]"
        );


    if (!alerts.length) {
        return;
    }


    alerts.forEach(function (alert) {

        const duration =
            parseInt(
                alert.getAttribute(
                    "data-auto-dismiss"
                ),
                10
            ) || 4500;


        window.setTimeout(
            function () {

                // Use Bootstrap's alert component when available.

                if (
                    window.bootstrap &&
                    window.bootstrap.Alert
                ) {

                    const bootstrapAlert =
                        bootstrap.Alert.getOrCreateInstance(
                            alert
                        );

                    bootstrapAlert.close();

                } else {

                    alert.remove();

                }

            },
            duration
        );

    });

}


/* ============================================================
   06. SMOOTH SCROLLING
   ============================================================ */

function initializeSmoothScrolling() {

    const links =
        document.querySelectorAll(
            "a[href^='#']"
        );


    if (!links.length) {
        return;
    }


    links.forEach(function (link) {

        link.addEventListener(
            "click",
            function (event) {

                const targetId =
                    link.getAttribute("href");


                if (
                    !targetId ||
                    targetId === "#"
                ) {

                    return;

                }


                const target =
                    document.querySelector(
                        targetId
                    );


                if (!target) {
                    return;
                }


                event.preventDefault();


                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            }
        );

    });

}


/* ============================================================
   07. IMAGE LOADING
   ============================================================ */

function initializeImageLoading() {

    const images =
        document.querySelectorAll(
            "img[data-vc-image]"
        );


    if (!images.length) {
        return;
    }


    images.forEach(function (image) {

        // Mark successfully loaded images.

        if (image.complete) {

            image.classList.add(
                "vc-image-loaded"
            );

            return;

        }


        image.addEventListener(
            "load",
            function () {

                image.classList.add(
                    "vc-image-loaded"
                );

            }
        );


        // Gracefully handle broken images.

        image.addEventListener(
            "error",
            function () {

                image.classList.add(
                    "vc-image-error"
                );

            }
        );

    });

}


/* ============================================================
   08. NAVBAR SHADOW ON SCROLL
   ============================================================ */

window.addEventListener(
    "scroll",
    function () {

        const header =
            document.querySelector(
                ".vc-header"
            );


        if (!header) {
            return;
        }


        if (window.scrollY > 10) {

            header.classList.add(
                "vc-header-scrolled"
            );

        } else {

            header.classList.remove(
                "vc-header-scrolled"
            );

        }

    },
    {
        passive: true
    }
);


/* ============================================================
   09. BACK/FORWARD CACHE PROTECTION
   ============================================================ */

window.addEventListener(
    "pageshow",
    function (event) {

        // If the browser restores an old page from BFCache,
        // reload so Django can re-check authentication.

        if (event.persisted) {

            window.location.reload();

        }

    }
);


/* ============================================================
   10. PREVENT ACCIDENTAL FORM RESUBMISSION
   ============================================================ */

window.addEventListener(
    "pageshow",
    function () {

        // Re-enable protected forms when a page is restored
        // normally by the browser.

        const forms =
            document.querySelectorAll(
                "form[data-protect-submit]"
            );


        forms.forEach(function (form) {

            const submitButtons =
                form.querySelectorAll(
                    "button[type='submit'], input[type='submit']"
                );


            submitButtons.forEach(
                function (button) {

                    button.disabled = false;

                    button.classList.remove(
                        "vc-loading"
                    );


                    if (
                        button.dataset.originalText
                    ) {

                        button.innerHTML =
                            button.dataset.originalText;

                    }

                }
            );

        });

    }
);


/* ============================================================
   11. MOBILE MENU CLEANUP
   ============================================================ */

document.addEventListener(
    "click",
    function (event) {

        const clickedLink =
            event.target.closest(
                ".vc-main-nav .vc-nav-link"
            );


        if (!clickedLink) {
            return;
        }


        // Close Bootstrap mobile navbar after navigation.

        const navbar =
            document.querySelector(
                ".vc-navbar .navbar-collapse"
            );


        if (
            navbar &&
            navbar.classList.contains("show") &&
            window.bootstrap
        ) {

            const collapse =
                bootstrap.Collapse.getInstance(
                    navbar
                );


            if (collapse) {

                collapse.hide();

            }

        }

    }
);


/* ============================================================
   12. KEYBOARD ESCAPE SUPPORT
   ============================================================ */

document.addEventListener(
    "keydown",
    function (event) {

        if (event.key !== "Escape") {
            return;
        }


        // Close open Bootstrap modals.

        const modal =
            document.querySelector(
                ".modal.show"
            );


        if (
            modal &&
            window.bootstrap
        ) {

            const modalInstance =
                bootstrap.Modal.getInstance(
                    modal
                );


            if (modalInstance) {

                modalInstance.hide();

            }

        }

    }
);


/* ============================================================
   13. GLOBAL BUTTON FEEDBACK
   ============================================================ */

document.addEventListener(
    "click",
    function (event) {

        const button =
            event.target.closest(
                "[data-vc-click-feedback]"
            );


        if (!button) {
            return;
        }


        button.classList.add(
            "vc-button-clicked"
        );


        window.setTimeout(
            function () {

                button.classList.remove(
                    "vc-button-clicked"
                );

            },
            180
        );

    }
);


/* ============================================================
   14. REDUCED MOTION SUPPORT
   ============================================================ */

const reducedMotionQuery =
    window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    );


if (reducedMotionQuery.matches) {

    document.documentElement.classList.add(
        "vc-reduced-motion"
    );

}


/* ============================================================
   15. CONSOLE INFORMATION
   ============================================================ */

console.info(
    "VisionCart UI initialized successfully."
);