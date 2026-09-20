## ============================================================
## VISIONCART - DJANGO ADMIN CONFIGURATION
## ============================================================

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


## ============================================================
## MANAGEMENT USERS PROXY
## ============================================================

class ManagementUser(User):
    """
    Proxy model used to display VisionCart management users
    inside Django's Authentication and Authorization section.
    """

    class Meta:
        proxy = True

        ## Place this proxy inside Django's auth admin section.
        app_label = "auth"

        verbose_name = "User"
        verbose_name_plural = "Users"


## ============================================================
## MANAGEMENT USERS ADMIN
## ============================================================

@admin.register(ManagementUser)
class ManagementUserAdmin(UserAdmin):

    ## --------------------------------------------------------
    ## Show only Super Admin and Web Admin accounts.
    ## --------------------------------------------------------

    def get_queryset(self, request):

        queryset = super().get_queryset(request)

        return queryset.filter(
            role__in=[
                User.Role.SUPER_ADMIN,
                User.Role.WEB_ADMIN,
            ]
        )

    ## --------------------------------------------------------
    ## User list columns.
    ## --------------------------------------------------------

    list_display = (
        "username",
        "email",
        "role",
        "is_active",
        "is_staff",
        "date_joined",
    )

    ## --------------------------------------------------------
    ## User filters.
    ## --------------------------------------------------------

    list_filter = (
        "role",
        "is_active",
    )

    ## --------------------------------------------------------
    ## Search fields.
    ## --------------------------------------------------------

    search_fields = (
        "username",
        "email",
        "phone",
    )

    ## --------------------------------------------------------
    ## Fields shown while editing a user.
    ## --------------------------------------------------------

    fieldsets = (
        (
            "Account Information",
            {
                "fields": (
                    "username",
                    "password",
                )
            },
        ),

        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                )
            },
        ),

        (
            "VisionCart Role",
            {
                "fields": (
                    "role",
                )
            },
        ),

        (
            "Account Status",
            {
                "fields": (
                    "is_active",
                )
            },
        ),

        (
            "Important Dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )

    ## --------------------------------------------------------
    ## Fields shown while creating a management user.
    ## --------------------------------------------------------

    add_fieldsets = (
        (
            "Create Management User",
            {
                "classes": (
                    "wide",
                ),
                "fields": (
                    "username",
                    "email",
                    "phone",
                    "role",
                    "password1",
                    "password2",
                    "is_active",
                ),
            },
        ),
    )

    ## --------------------------------------------------------
    ## Only management roles can be selected here.
    ## --------------------------------------------------------

    def get_form(
        self,
        request,
        obj=None,
        **kwargs
    ):

        form = super().get_form(
            request,
            obj,
            **kwargs,
        )

        if "role" in form.base_fields:

            form.base_fields["role"].choices = [
                (
                    User.Role.SUPER_ADMIN,
                    "Super Admin",
                ),
                (
                    User.Role.WEB_ADMIN,
                    "Web Admin",
                ),
            ]

        return form

    ## --------------------------------------------------------
    ## Save management user safely.
    ## --------------------------------------------------------

    def save_model(
        self,
        request,
        obj,
        form,
        change
    ):

        ## Keep this section restricted to management roles.
        if obj.role not in [
            User.Role.SUPER_ADMIN,
            User.Role.WEB_ADMIN,
        ]:

            obj.role = User.Role.WEB_ADMIN

        ## Management users require Django Admin access.
        obj.is_staff = True

        ## Only Super Admin gets superuser permission.
        if obj.role == User.Role.SUPER_ADMIN:

            obj.is_superuser = True

        else:

            obj.is_superuser = False

        super().save_model(
            request,
            obj,
            form,
            change,
        )


## ============================================================
## CUSTOMER PROXY MODEL
## ============================================================

class Customer(User):
    """
    Proxy model used to display CUSTOMER accounts separately
    under the VisionCart Accounts section.
    """

    class Meta:
        proxy = True
        app_label = "accounts"

        verbose_name = "Customer"
        verbose_name_plural = "Customers"


## ============================================================
## CUSTOMER ADMIN
## ============================================================

@admin.register(Customer)
class CustomerAdmin(UserAdmin):

    ## --------------------------------------------------------
    ## Show only CUSTOMER accounts.
    ## --------------------------------------------------------

    def get_queryset(self, request):

        queryset = super().get_queryset(request)

        return queryset.filter(
            role=User.Role.CUSTOMER
        )

    ## --------------------------------------------------------
    ## Customer list columns.
    ## --------------------------------------------------------

    list_display = (
        "username",
        "email",
        "phone",
        "is_active",
        "date_joined",
    )

    ## --------------------------------------------------------
    ## Customer filters.
    ## --------------------------------------------------------

    list_filter = (
        "is_active",
        "date_joined",
    )

    ## --------------------------------------------------------
    ## Customer search.
    ## --------------------------------------------------------

    search_fields = (
        "username",
        "email",
        "phone",
    )

    ## --------------------------------------------------------
    ## Customer editing fields.
    ## --------------------------------------------------------

    fieldsets = (
        (
            "Customer Account",
            {
                "fields": (
                    "username",
                    "password",
                )
            },
        ),

        (
            "Customer Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                )
            },
        ),

        (
            "Account Status",
            {
                "fields": (
                    "is_active",
                )
            },
        ),

        (
            "Account Date",
            {
                "fields": (
                    "date_joined",
                    "last_login",
                )
            },
        ),
    )

    ## --------------------------------------------------------
    ## Customer creation fields.
    ## --------------------------------------------------------

    add_fieldsets = (
        (
            "Create Customer",
            {
                "classes": (
                    "wide",
                ),
                "fields": (
                    "username",
                    "email",
                    "phone",
                    "password1",
                    "password2",
                    "is_active",
                ),
            },
        ),
    )

    ## --------------------------------------------------------
    ## Always keep this account as CUSTOMER.
    ## --------------------------------------------------------

    def save_model(
        self,
        request,
        obj,
        form,
        change
    ):

        ## Customer cannot become a management user here.
        obj.role = User.Role.CUSTOMER

        ## Customer has no Django Admin staff permission.
        obj.is_staff = False

        ## Customer has no superuser permission.
        obj.is_superuser = False

        super().save_model(
            request,
            obj,
            form,
            change,
        )