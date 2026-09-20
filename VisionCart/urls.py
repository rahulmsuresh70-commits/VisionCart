## =========================================================
## VISIONCART MAIN URL CONFIGURATION
## =========================================================

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


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

if settings.DEBUG:

    urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)