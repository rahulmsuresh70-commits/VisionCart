## =========================================================
## VISIONCART - SECURITY MIDDLEWARE
## =========================================================

import uuid

from django.http import HttpResponseRedirect


## Unique ID for every fresh server process.
SERVER_RUN_ID = uuid.uuid4().hex


class VisionCartSecurityMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        ## =====================================================
        ## SERVER RESTART SESSION CHECK
        ## =====================================================

        current_run_id = request.session.get(
            "_visioncart_server_run_id"
        )

        ## If an old session belongs to a previous server run,
        ## completely destroy that session.
        if current_run_id is not None:

            if current_run_id != SERVER_RUN_ID:

                request.session.flush()

                ## Always send old URLs to Home after
                ## a fresh server start.
                if request.path != "/":
                    return HttpResponseRedirect("/")

        ## Store the current server-run ID.
        request.session["_visioncart_server_run_id"] = (
            SERVER_RUN_ID
        )

        ## =====================================================
        ## PROCESS REQUEST
        ## =====================================================

        response = self.get_response(request)

        ## =====================================================
        ## PREVENT BROWSER CACHE / BACK BUTTON ACCESS
        ## =====================================================

        ## Do not allow protected pages to remain in the
        ## browser cache after logout.
        response["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, "
            "max-age=0, private"
        )

        response["Pragma"] = "no-cache"

        response["Expires"] = "0"

        return response