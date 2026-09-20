from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q

from orders.models import Review

from .models import User


## ============================================================
## ROLE HELPERS
## ============================================================

def is_super_admin(user):
    """
    Check whether the authenticated user is a Super Admin.
    """

    return (
        user.is_authenticated
        and user.role == User.Role.SUPER_ADMIN
    )


def is_management_user(user):
    """
    Check whether the authenticated user is allowed
    to access management pages.
    """

    return (
        user.is_authenticated
        and user.role in [
            User.Role.SUPER_ADMIN,
            User.Role.WEB_ADMIN,
        ]
    )


## ============================================================
## MANAGEMENT ACCESS
## ============================================================

def management_access_required(request):
    """
    Return a response when the user is not allowed
    to access management pages.

    Returns:
        None
        or
        HttpResponseForbidden
    """

    if not request.user.is_authenticated:
        return redirect("management-login")

    if not is_management_user(request.user):
        return HttpResponseForbidden(
            "You do not have permission to access this management page."
        )

    return None


def super_admin_access_required(request):
    """
    Only Super Admin can access these pages.
    """

    if not request.user.is_authenticated:
        return redirect("management-login")

    if not is_super_admin(request.user):
        return HttpResponseForbidden(
            "Only Super Admin can access this page."
        )

    return None


## ============================================================
## SAFE MANAGEMENT RETURN
## ============================================================

def management_return_redirect(request, fallback_name, **kwargs):
    """Return to Super Admin dashboard when requested, otherwise use normal management page."""
    next_url = request.POST.get("next", "").strip()

    if next_url.startswith("/super-admin/"):
        return redirect(next_url)

    return redirect(fallback_name, **kwargs)


## ============================================================
## SUPER ADMIN - WEB ADMIN LIST
## ============================================================

@login_required(login_url="management-login")
def super_admin_web_admin_list_view(request):

    ## --------------------------------------------------------
    ## SECURITY
    ## --------------------------------------------------------

    access_response = super_admin_access_required(request)

    if access_response is not None:
        return access_response


    ## --------------------------------------------------------
    ## CREATE WEB ADMIN
    ## --------------------------------------------------------

    if request.method == "POST":

        action = request.POST.get(
            "action",
            ""
        ).strip()


        ## ----------------------------------------------------
        ## ADD WEB ADMIN
        ## ----------------------------------------------------

        if action == "add":

            username = request.POST.get(
                "username",
                ""
            ).strip()

            email = request.POST.get(
                "email",
                ""
            ).strip().lower()

            phone = request.POST.get(
                "phone",
                ""
            ).strip()

            password = request.POST.get(
                "password",
                ""
            )

            confirm_password = request.POST.get(
                "confirm_password",
                ""
            )


            ## ------------------------------------------------
            ## VALIDATION
            ## ------------------------------------------------

            errors = []


            if not username:

                errors.append(
                    "Username is required."
                )

            elif len(username) < 3:

                errors.append(
                    "Username must contain at least 3 characters."
                )

            elif len(username) > 150:

                errors.append(
                    "Username must not exceed 150 characters."
                )


            if not email:

                errors.append(
                    "Email is required."
                )

            else:

                try:

                    validate_email(email)

                except ValidationError:

                    errors.append(
                        "Enter a valid email address."
                    )


            if phone:

                if not phone.isdigit():

                    errors.append(
                        "Phone number must contain numbers only."
                    )

                elif len(phone) != 10:

                    errors.append(
                        "Phone number must contain exactly 10 digits."
                    )


            if not password:

                errors.append(
                    "Password is required."
                )

            elif len(password) < 6:

                errors.append(
                    "Password must contain at least 6 characters."
                )


            if password != confirm_password:

                errors.append(
                    "Password and confirm password do not match."
                )


            ## ------------------------------------------------
            ## DUPLICATE USERNAME
            ## ------------------------------------------------

            if username:

                if User.objects.filter(
                    username__iexact=username
                ).exists():

                    errors.append(
                        "This username is already registered."
                    )


            ## ------------------------------------------------
            ## DUPLICATE EMAIL
            ## ------------------------------------------------

            if email:

                if User.objects.filter(
                    email__iexact=email
                ).exists():

                    errors.append(
                        "This email is already registered."
                    )


            ## ------------------------------------------------
            ## SHOW ERRORS
            ## ------------------------------------------------

            if errors:

                for error in errors:

                    messages.error(
                        request,
                        error
                    )

            else:

                ## --------------------------------------------
                ## CREATE WEB ADMIN
                ## --------------------------------------------

                try:

                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                    )

                    ## Never trust a submitted role.
                    ## Role is assigned by the server.

                    user.role = User.Role.WEB_ADMIN

                    user.phone = phone

                    ## Web Admin is not Django superuser.

                    user.is_superuser = False

                    user.is_staff = False

                    user.save()

                    messages.success(
                        request,
                        "Web Admin created successfully."
                    )

                except IntegrityError:

                    messages.error(
                        request,
                        "Unable to create Web Admin. "
                        "Username or email may already exist."
                    )


            return redirect(
                "super-admin-web-admin-list"
            )


        ## ----------------------------------------------------
        ## ACTIVATE / DEACTIVATE
        ## ----------------------------------------------------

        if action == "toggle":

            web_admin_id = request.POST.get(
                "web_admin_id",
                ""
            ).strip()

            try:

                web_admin = User.objects.get(
                    pk=int(web_admin_id),
                    role=User.Role.WEB_ADMIN,
                )

            except (
                ValueError,
                User.DoesNotExist,
            ):

                messages.error(
                    request,
                    "Web Admin account not found."
                )

                return redirect(
                    "super-admin-web-admin-list"
                )


            web_admin.is_active = not web_admin.is_active

            web_admin.save(
                update_fields=[
                    "is_active"
                ]
            )


            if web_admin.is_active:

                messages.success(
                    request,
                    "Web Admin activated successfully."
                )

            else:

                messages.success(
                    request,
                    "Web Admin deactivated successfully."
                )


            return redirect(
                "super-admin-web-admin-list"
            )


    ## --------------------------------------------------------
    ## GET WEB ADMINS
    ## --------------------------------------------------------

    web_admins = User.objects.filter(
        role=User.Role.WEB_ADMIN
    ).order_by(
        "-date_joined"
    )


    ## --------------------------------------------------------
    ## COUNTS
    ## --------------------------------------------------------

    total_web_admins = web_admins.count()

    active_web_admins = web_admins.filter(
        is_active=True
    ).count()

    inactive_web_admins = web_admins.filter(
        is_active=False
    ).count()


    ## --------------------------------------------------------
    ## PAGE
    ## --------------------------------------------------------

    return render(
        request,
        "web_admin_management.html",
        {
            "web_admins": web_admins,
            "total_web_admins": total_web_admins,
            "active_web_admins": active_web_admins,
            "inactive_web_admins": inactive_web_admins,
        }
    )


## ============================================================
## SUPER ADMIN - EDIT WEB ADMIN
## ============================================================

@login_required(login_url="management-login")
def super_admin_web_admin_edit_view(
    request,
    web_admin_id,
):

    ## --------------------------------------------------------
    ## SECURITY
    ## --------------------------------------------------------

    access_response = super_admin_access_required(request)

    if access_response is not None:
        return access_response


    ## --------------------------------------------------------
    ## GET WEB ADMIN
    ## --------------------------------------------------------

    web_admin = get_object_or_404(
        User,
        pk=web_admin_id,
        role=User.Role.WEB_ADMIN,
    )


    ## --------------------------------------------------------
    ## POST
    ## --------------------------------------------------------

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip().lower()

        phone = request.POST.get(
            "phone",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )


        errors = []


        ## ----------------------------------------------------
        ## USERNAME
        ## ----------------------------------------------------

        if not username:

            errors.append(
                "Username is required."
            )

        elif len(username) < 3:

            errors.append(
                "Username must contain at least 3 characters."
            )

        elif len(username) > 150:

            errors.append(
                "Username must not exceed 150 characters."
            )


        ## ----------------------------------------------------
        ## DUPLICATE USERNAME
        ## ----------------------------------------------------

        if username:

            if User.objects.filter(
                username__iexact=username
            ).exclude(
                pk=web_admin.pk
            ).exists():

                errors.append(
                    "This username is already used by another account."
                )


        ## ----------------------------------------------------
        ## EMAIL
        ## ----------------------------------------------------

        if not email:

            errors.append(
                "Email is required."
            )

        else:

            try:

                validate_email(email)

            except ValidationError:

                errors.append(
                    "Enter a valid email address."
                )


        ## ----------------------------------------------------
        ## DUPLICATE EMAIL
        ## ----------------------------------------------------

        if email:

            if User.objects.filter(
                email__iexact=email
            ).exclude(
                pk=web_admin.pk
            ).exists():

                errors.append(
                    "This email is already used by another account."
                )


        ## ----------------------------------------------------
        ## PHONE
        ## ----------------------------------------------------

        if phone:

            if not phone.isdigit():

                errors.append(
                    "Phone number must contain numbers only."
                )

            elif len(phone) != 10:

                errors.append(
                    "Phone number must contain exactly 10 digits."
                )


        ## ----------------------------------------------------
        ## OPTIONAL PASSWORD
        ## ----------------------------------------------------

        if password:

            if len(password) < 6:

                errors.append(
                    "Password must contain at least 6 characters."
                )

            if password != confirm_password:

                errors.append(
                    "Password and confirm password do not match."
                )


        ## ----------------------------------------------------
        ## SAVE
        ## ----------------------------------------------------

        if errors:

            return render(
                request,
                "web_admin_edit.html",
                {
                    "web_admin": web_admin,
                    "errors": errors,
                    "username": username,
                    "email": email,
                    "phone": phone,
                }
            )


        web_admin.username = username

        web_admin.email = email

        web_admin.phone = phone

        ## Security:
        ## role cannot be changed through this form.

        web_admin.role = User.Role.WEB_ADMIN

        ## Password is changed only when a new password
        ## was actually supplied.

        if password:

            web_admin.set_password(
                password
            )


        web_admin.save()


        messages.success(
            request,
            "Web Admin updated successfully."
        )


        return redirect(
            "super-admin-web-admin-list"
        )


    ## --------------------------------------------------------
    ## GET
    ## --------------------------------------------------------

    return render(
        request,
        "web_admin_edit.html",
        {
            "web_admin": web_admin,
            "errors": [],
            "username": web_admin.username,
            "email": web_admin.email,
            "phone": web_admin.phone,
        }
    )


## ============================================================
## SUPER ADMIN - DELETE WEB ADMIN
## ============================================================

@login_required(login_url="management-login")
def super_admin_web_admin_delete_view(
    request,
    web_admin_id,
):

    ## --------------------------------------------------------
    ## SECURITY
    ## --------------------------------------------------------

    access_response = super_admin_access_required(request)

    if access_response is not None:
        return access_response


    ## --------------------------------------------------------
    ## ONLY POST CAN DELETE
    ## --------------------------------------------------------

    if request.method != "POST":

        return redirect(
            "super-admin-web-admin-list"
        )


    ## --------------------------------------------------------
    ## FIND WEB ADMIN
    ## --------------------------------------------------------

    web_admin = get_object_or_404(
        User,
        pk=web_admin_id,
        role=User.Role.WEB_ADMIN,
    )


    ## --------------------------------------------------------
    ## DELETE
    ## --------------------------------------------------------

    web_admin.delete()


    messages.success(
        request,
        "Web Admin deleted successfully."
    )


    return redirect(
        "super-admin-web-admin-list"
    )


## ============================================================
## WEB ADMIN - CUSTOMER MANAGEMENT
## ============================================================

@login_required(login_url="management-login")
def web_admin_customer_list_view(request):

    ## --------------------------------------------------------
    ## SECURITY
    ## --------------------------------------------------------

    access_response = management_access_required(request)

    if access_response is not None:
        return access_response


    ## --------------------------------------------------------
    ## ACTIVATE / DEACTIVATE CUSTOMER
    ## --------------------------------------------------------

    if request.method == "POST":

        action = request.POST.get(
            "action",
            ""
        ).strip()

        if action == "toggle":

            customer_id = request.POST.get(
                "customer_id",
                ""
            ).strip()

            try:

                customer = User.objects.get(
                    pk=int(customer_id),
                    role=User.Role.CUSTOMER,
                )

            except (
                ValueError,
                User.DoesNotExist,
            ):

                messages.error(
                    request,
                    "Customer account not found."
                )

                return redirect(
                    "web-admin-customers"
                )


            # Explicitly calculate the new account state and persist it.
            # This keeps the Activate / Deactivate action tied to the
            # exact customer selected in the submitted form.
            new_is_active = not bool(customer.is_active)

            customer.is_active = new_is_active

            customer.save(
                update_fields=[
                    "is_active"
                ]
            )

            # Read the saved value back before redirecting so the next
            # page render always reflects the database state.
            customer.refresh_from_db(
                fields=["is_active"]
            )


            if customer.is_active:

                messages.success(
                    request,
                    "Customer account activated successfully."
                )

            else:

                messages.success(
                    request,
                    "Customer account deactivated successfully."
                )


            return redirect(
                "web-admin-customers"
            )


    ## --------------------------------------------------------
    ## ONLY CUSTOMER ACCOUNTS
    ## --------------------------------------------------------

    customers = User.objects.filter(
        role=User.Role.CUSTOMER
    ).order_by(
        "-date_joined"
    )


    ## --------------------------------------------------------
    ## SEARCH
    ## --------------------------------------------------------

    search_query = request.GET.get(
        "q",
        ""
    ).strip()


    if search_query:

        customers = customers.filter(
            username__icontains=search_query
        ) | customers.filter(
            email__icontains=search_query
        ) | customers.filter(
            phone__icontains=search_query
        )


    ## --------------------------------------------------------
    ## STATUS FILTER
    ## --------------------------------------------------------

    selected_status = request.GET.get(
        "status",
        ""
    ).strip()


    if selected_status == "active":

        customers = customers.filter(
            is_active=True
        )


    elif selected_status == "inactive":

        customers = customers.filter(
            is_active=False
        )


    ## --------------------------------------------------------
    ## CUSTOMER COUNTS
    ## --------------------------------------------------------

    all_customers = User.objects.filter(
        role=User.Role.CUSTOMER
    )


    total_customers = all_customers.count()


    active_customers = all_customers.filter(
        is_active=True
    ).count()


    inactive_customers = all_customers.filter(
        is_active=False
    ).count()


    ## --------------------------------------------------------
    ## PAGE
    ## --------------------------------------------------------

    return render(
        request,
        "web_admin_customers.html",
        {
            "customers": customers,
            "search_query": search_query,
            "selected_status": selected_status,
            "total_customers": total_customers,
            "active_customers": active_customers,
            "inactive_customers": inactive_customers,
        }
    )

## ============================================================
## REVIEW MANAGEMENT
## ============================================================

@login_required(login_url="management-login")
def web_admin_review_list_view(request):
    """
    Review management for Super Admin and Web Admin.
    """

    ## --------------------------------------------------------
    ## SECURITY
    ## --------------------------------------------------------

    access_response = management_access_required(request)

    if access_response is not None:
        return access_response


    ## --------------------------------------------------------
    ## GET REVIEWS
    ## --------------------------------------------------------

    reviews = Review.objects.select_related(
        "product",
        "user",
    ).order_by(
        "-created_at"
    )


    ## --------------------------------------------------------
    ## SEARCH
    ## --------------------------------------------------------

    search_query = request.GET.get(
        "q",
        "",
    ).strip()


    if search_query:

        reviews = reviews.filter(
            Q(product__name__icontains=search_query)
            | Q(user__username__icontains=search_query)
            | Q(user__email__icontains=search_query)
            | Q(comment__icontains=search_query)
        )


    ## --------------------------------------------------------
    ## RATING FILTER
    ## --------------------------------------------------------

    selected_rating = request.GET.get(
        "rating",
        "",
    ).strip()


    if selected_rating in [
        "1",
        "2",
        "3",
        "4",
        "5",
    ]:

        reviews = reviews.filter(
            rating=int(selected_rating)
        )


    ## --------------------------------------------------------
    ## SUMMARY COUNTS
    ## --------------------------------------------------------

    all_reviews = Review.objects.all()

    total_reviews = all_reviews.count()

    five_star_reviews = all_reviews.filter(
        rating=5
    ).count()

    four_star_reviews = all_reviews.filter(
        rating=4
    ).count()

    low_rating_reviews = all_reviews.filter(
        rating__lte=2
    ).count()


    ## --------------------------------------------------------
    ## PAGE
    ## --------------------------------------------------------

    return render(
        request,
        "web_admin_reviews.html",
        {
            "reviews": reviews,
            "search_query": search_query,
            "selected_rating": selected_rating,
            "total_reviews": total_reviews,
            "five_star_reviews": five_star_reviews,
            "four_star_reviews": four_star_reviews,
            "low_rating_reviews": low_rating_reviews,
        },
    )


## ============================================================
## REVIEW DETAIL
## ============================================================

@login_required(login_url="management-login")
def web_admin_review_detail_view(
    request,
    review_id,
):

    ## --------------------------------------------------------
    ## SECURITY
    ## --------------------------------------------------------

    access_response = management_access_required(request)

    if access_response is not None:
        return access_response


    ## --------------------------------------------------------
    ## GET REVIEW
    ## --------------------------------------------------------

    review = get_object_or_404(
        Review.objects.select_related(
            "product",
            "user",
        ),
        pk=review_id,
    )


    ## --------------------------------------------------------
    ## PAGE
    ## --------------------------------------------------------

    return render(
        request,
        "web_admin_review_detail.html",
        {
            "review": review,
        },
    )


## ============================================================
## DELETE REVIEW
## ============================================================

@login_required(login_url="management-login")
def web_admin_review_delete_view(
    request,
    review_id,
):

    ## --------------------------------------------------------
    ## SECURITY
    ## --------------------------------------------------------

    access_response = management_access_required(request)

    if access_response is not None:
        return access_response


    ## --------------------------------------------------------
    ## ONLY POST
    ## --------------------------------------------------------

    if request.method != "POST":

        return redirect(
            "web-admin-reviews"
        )


    ## --------------------------------------------------------
    ## FIND REVIEW
    ## --------------------------------------------------------

    review = get_object_or_404(
        Review,
        pk=review_id,
    )


    ## --------------------------------------------------------
    ## DELETE
    ## --------------------------------------------------------

    review.delete()


    messages.success(
        request,
        "Review deleted successfully.",
    )


    return management_return_redirect(
        request,
        "web-admin-reviews"
    )
