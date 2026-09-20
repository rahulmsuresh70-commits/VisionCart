## =========================================================
## VISIONCART MAIN URL CONFIGURATION
## =========================================================
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.views.static import serve
from django.urls import include, path, re_path


## =========================================================
## MAIN URL PATTERNS
## =========================================================

urlpatterns = [

    ## ## Django administration
    path(
        "admin/",
        admin.site.urls,
    ),

    ## ## Accounts
    path(
        "",
        include("accounts.urls"),
    ),

    ## ## Store
    path(
        "",
        include("store.urls"),
    ),

    ## ## Orders and customer addresses
    path(
        "",
        include("orders.urls"),
    ),
]


## =========================================================
## MEDIA FILES
## =========================================================


urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {
            "document_root": settings.MEDIA_ROOT,
        },
    ),
]