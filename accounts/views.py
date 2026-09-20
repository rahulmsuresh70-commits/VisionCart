## =========================================================
## VISIONCART - ACCOUNTS VIEWS
## =========================================================


## =========================================================
## DJANGO IMPORTS
## =========================================================

## Django authentication functions.
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash

## Django messages.
from django.contrib import messages

## Login protection decorator.
from django.contrib.auth.decorators import login_required

## Prevent login pages from being cached.
from django.views.decorators.cache import never_cache

## Make sure a CSRF cookie is available on the login page.
from django.views.decorators.csrf import ensure_csrf_cookie

## Render HTML pages and redirect users.
from django.shortcuts import render, redirect

## Import our custom User model.
from .models import User


## =========================================================
## CUSTOMER REGISTRATION
## =========================================================

def register_view(request):

    ## Check whether the registration form was submitted.
    if request.method == "POST":

        ## Get username from form.
        username = request.POST.get(
            "username",
            "",
        ).strip()

        ## Get email and convert it to lowercase.
        email = request.POST.get(
            "email",
            "",
        ).strip().lower()

        ## Get phone number.
        phone = request.POST.get(
            "phone",
            "",
        ).strip()

        ## Get password.
        password = request.POST.get(
            "password",
            "",
        )

        ## Get password confirmation.
        confirm_password = request.POST.get(
            "confirm_password",
            "",
        )


        ## -------------------------------------------------
        ## REQUIRED FIELD VALIDATION
        ## -------------------------------------------------

        if not username or not email or not password:

            messages.error(
                request,
                "Please fill in all required fields.",
            )

            return render(
                request,
                "register.html",
            )


        ## -------------------------------------------------
        ## PASSWORD MATCH VALIDATION
        ## -------------------------------------------------

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match.",
            )

            return render(
                request,
                "register.html",
            )


        ## -------------------------------------------------
        ## USERNAME VALIDATION
        ## -------------------------------------------------

        if User.objects.filter(
            username__iexact=username
        ).exists():

            messages.error(
                request,
                "Username already exists.",
            )

            return render(
                request,
                "register.html",
            )


        ## -------------------------------------------------
        ## EMAIL VALIDATION
        ## -------------------------------------------------

        if User.objects.filter(
            email__iexact=email
        ).exists():

            messages.error(
                request,
                "Email address is already registered.",
            )

            return render(
                request,
                "register.html",
            )


        ## -------------------------------------------------
        ## CREATE CUSTOMER
        ## -------------------------------------------------

        ## Public registration ALWAYS creates CUSTOMER.
        user = User(
            username=username,
            email=email,
            phone=phone,
            role=User.Role.CUSTOMER,
        )

        ## Hash the password securely.
        user.set_password(password)

        ## Save customer.
        user.save()


        ## -------------------------------------------------
        ## REGISTRATION SUCCESS
        ## -------------------------------------------------

        messages.success(
            request,
            "Registration successful. Please login.",
        )

        ## Go to customer login.
        return redirect(
            "login"
        )


    ## -----------------------------------------------------
    ## DISPLAY REGISTRATION PAGE
    ## -----------------------------------------------------

    return render(
        request,
        "register.html",
    )


## =========================================================
## CUSTOMER LOGIN
## =========================================================

@never_cache
@ensure_csrf_cookie
def customer_login_view(request):

    ## -----------------------------------------------------
    ## AUTO LOGOUT WHEN RETURNING TO LOGIN PAGE
    ## -----------------------------------------------------

    ## If the browser Back button returns to the customer
    ## login page while a session is still authenticated,
    ## destroy that session first.
    ##
    ## This prevents the old authenticated session from
    ## remaining active after returning to the login page.
    if request.method == "GET" and request.user.is_authenticated:

        ## Destroy the existing authentication session.
        logout(request)

        ## Reload the login page as a logged-out user.
        return redirect(
            "login"
        )


    ## -----------------------------------------------------
    ## CHECK FORM SUBMISSION
    ## -----------------------------------------------------

    if request.method == "POST":

        ## Get email address.
        email = request.POST.get(
            "email",
            "",
        ).strip().lower()

        ## Get password.
        password = request.POST.get(
            "password",
            "",
        )


        ## -------------------------------------------------
        ## AUTHENTICATE USER BY EMAIL
        ## -------------------------------------------------

        user = None

        if email:
            matching_user = User.objects.filter(
                email__iexact=email,
            ).first()

            if matching_user is not None:
                user = authenticate(
                    request,
                    username=matching_user.username,
                    password=password,
                )


        ## -------------------------------------------------
        ## AUTHENTICATION SUCCESS
        ## -------------------------------------------------

        if user is not None:

            ## Customer login accepts only CUSTOMER role.
            if user.role != User.Role.CUSTOMER:

                messages.error(
                    request,
                    "Please use the management login.",
                )

                return redirect(
                    "login"
                )


            ## Check account status.
            if not user.is_active:

                messages.error(
                    request,
                    "Your account has been deactivated.",
                )

                return redirect(
                    "login"
                )


            ## Create Django session.
            login(
                request,
                user,
            )

            ## Send customer to the authenticated User Dashboard.
            return redirect(
                "profile"
            )


        ## -------------------------------------------------
        ## LOGIN FAILED
        ## -------------------------------------------------

        messages.error(
            request,
            "Invalid email or password.",
        )

        return render(
            request,
            "login.html",
        )


    ## -----------------------------------------------------
    ## DISPLAY CUSTOMER LOGIN
    ## -----------------------------------------------------

    return render(
        request,
        "login.html",
    )


## =========================================================
## CUSTOMER USER DASHBOARD
## =========================================================

@login_required(login_url="login")
def profile_view(request):

    ## Display the existing authenticated Customer User Dashboard.
    return render(
        request,
        "profile.html",
    )


## =========================================================
## CUSTOMER PROFILE MANAGEMENT
## =========================================================

@login_required(login_url="login")
def profile_management_view(request):

    ## Get the currently authenticated customer.
    user = request.user

    ## Update profile details only when the form is submitted.
    if request.method == "POST":

        new_username = request.POST.get("username", "").strip()
        new_first_name = request.POST.get("first_name", "").strip()
        new_last_name = request.POST.get("last_name", "").strip()
        new_email = request.POST.get("email", "").strip().lower()
        new_phone = request.POST.get("phone", "").strip()
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")

        ## Basic required-field validation.
        if not new_username or not new_email:
            messages.error(
                request,
                "Username and email are required.",
            )
            return render(request, "profile_management.html")

        ## Prevent another account from using the same username.
        if User.objects.filter(
            username__iexact=new_username
        ).exclude(pk=user.pk).exists():

            messages.error(
                request,
                "Username already exists.",
            )
            return render(request, "profile_management.html")

        ## Prevent another account from using the same email.
        if User.objects.filter(
            email__iexact=new_email
        ).exclude(pk=user.pk).exists():

            messages.error(
                request,
                "Email address is already registered.",
            )
            return render(request, "profile_management.html")

        ## Password fields are optional. If either is filled, both are required.
        if new_password or confirm_password:
            if not new_password or not confirm_password:
                messages.error(
                    request,
                    "Please enter and confirm the new password.",
                )
                return render(request, "profile_management.html")

            if new_password != confirm_password:
                messages.error(
                    request,
                    "New passwords do not match.",
                )
                return render(request, "profile_management.html")

        ## Update profile details.
        user.username = new_username
        user.first_name = new_first_name
        user.last_name = new_last_name
        user.email = new_email
        user.phone = new_phone

        ## Update profile image only when a new image is selected.
        profile_image = request.FILES.get("profile_image")
        if profile_image is not None:
            user.profile_image = profile_image

        ## Change password only when the optional password fields are filled.
        if new_password:
            user.set_password(new_password)

        user.save()

        ## Keep the current customer session active after a password change.
        if new_password:
            update_session_auth_hash(request, user)

        messages.success(
            request,
            "Profile updated successfully.",
        )

        return redirect(
            "profile-management"
        )

    ## Display the current customer's profile.
    return render(
        request,
        "profile_management.html",
    )


## =========================================================
## MANAGEMENT LOGIN

@never_cache
@ensure_csrf_cookie
def management_login_view(request):

    ## -----------------------------------------------------
    ## AUTO LOGOUT WHEN RETURNING TO MANAGEMENT LOGIN PAGE
    ## -----------------------------------------------------

    ## If the browser Back button returns to the management
    ## login page while a management session is still active,
    ## destroy that session first.
    ##
    ## This prevents Super Admin/Web Admin sessions from
    ## remaining active after returning to the login page.
    if request.method == "GET" and request.user.is_authenticated:

        ## Destroy the existing authentication session.
        logout(request)

        ## Reload the management login page as logged out.
        return redirect(
            "management-login"
        )


    ## -----------------------------------------------------
    ## CHECK FORM SUBMISSION
    ## -----------------------------------------------------

    if request.method == "POST":

        ## Get username.
        username = request.POST.get(
            "username",
            "",
        ).strip()

        ## Get password.
        password = request.POST.get(
            "password",
            "",
        )


        ## -------------------------------------------------
        ## AUTHENTICATE AGAINST DJANGO
        ## -------------------------------------------------

        user = authenticate(
            request,
            username=username,
            password=password,
        )


        ## -------------------------------------------------
        ## AUTHENTICATION SUCCESS
        ## -------------------------------------------------

        if user is not None:

            ## Only these roles can enter management.
            allowed_roles = (
                User.Role.SUPER_ADMIN,
                User.Role.WEB_ADMIN,
            )


            ## -------------------------------------------------
            ## REJECT CUSTOMERS
            ## -------------------------------------------------

            if user.role not in allowed_roles:

                messages.error(
                    request,
                    "You do not have management access.",
                )

                return redirect(
                    "management-login"
                )


            ## -------------------------------------------------
            ## REJECT INACTIVE ACCOUNTS
            ## -------------------------------------------------

            if not user.is_active:

                messages.error(
                    request,
                    "Your account has been deactivated.",
                )

                return redirect(
                    "management-login"
                )


            ## -------------------------------------------------
            ## CREATE DJANGO SESSION
            ## -------------------------------------------------

            login(
                request,
                user,
            )


            ## -------------------------------------------------
            ## SUPER ADMIN
            ## -------------------------------------------------

            if user.role == User.Role.SUPER_ADMIN:

                return redirect(
                    "super-admin-dashboard"
                )


            ## -------------------------------------------------
            ## WEB ADMIN
            ## -------------------------------------------------

            if user.role == User.Role.WEB_ADMIN:

                return redirect(
                    "web-admin-dashboard"
                )


        ## -------------------------------------------------
        ## MANAGEMENT LOGIN FAILED
        ## -------------------------------------------------

        messages.error(
            request,
            "Invalid management credentials.",
        )

        return render(
            request,
            "management/login.html",
        )


    ## -----------------------------------------------------
    ## DISPLAY MANAGEMENT LOGIN PAGE
    ## -----------------------------------------------------

    return render(
        request,
        "management/login.html",
    )


## =========================================================
## CUSTOMER LOGOUT
## =========================================================

def logout_view(request):

    ## Destroy current authentication session.
    logout(request)

    ## Return to customer login.
    return redirect(
        "login"
    )


## =========================================================
## MANAGEMENT LOGOUT
## =========================================================

def management_logout_view(request):

    ## Destroy current authentication session.
    logout(request)

    ## Return to management login.
    return redirect(
        "management-login"
    )


## =========================================================
## SUPER ADMIN DASHBOARD
## =========================================================

@login_required
def super_admin_dashboard(request):

    ## Only SUPER_ADMIN can access this page.
    if request.user.role != User.Role.SUPER_ADMIN:

        messages.error(
            request,
            "You do not have permission to access this page.",
        )

        return redirect(
            "home"
        )


    ## Display Super Admin dashboard.
    return render(
        request,
        "super_admin_dashboard.html",
    )


## =========================================================
## WEB ADMIN DASHBOARD
## =========================================================

@login_required
def web_admin_dashboard(request):

    ## Only WEB_ADMIN can access this page.
    if request.user.role != User.Role.WEB_ADMIN:

        messages.error(
            request,
            "You do not have permission to access this page.",
        )

        return redirect(
            "home"
        )


    ## Display Web Admin dashboard.
    return render(
        request,
        "admin_dashboard.html",
    )