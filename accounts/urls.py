from django.urls import path

from . import management_views
from . import views


urlpatterns = [

    ## ========================================================
    ## CUSTOMER AUTHENTICATION
    ## ========================================================

    path(
        "register/",
        views.register_view,
        name="register",
    ),

    path(
        "login/",
        views.customer_login_view,
        name="login",
    ),

    path(
        "profile/",
        views.profile_view,
        name="profile",
    ),

    path(
        "profile/manage/",
        views.profile_management_view,
        name="profile-management",
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),


    ## ========================================================
    ## MANAGEMENT AUTHENTICATION
    ## ========================================================

    path(
        "management/login/",
        views.management_login_view,
        name="management-login",
    ),

    path(
        "management/logout/",
        views.management_logout_view,
        name="management-logout",
    ),


    ## ========================================================
    ## SUPER ADMIN DASHBOARD
    ## ========================================================

    path(
        "super-admin/",
        views.super_admin_dashboard,
        name="super-admin-dashboard",
    ),


    ## ========================================================
    ## WEB ADMIN DASHBOARD
    ## ========================================================

    path(
        "web-admin/",
        views.web_admin_dashboard,
        name="web-admin-dashboard",
    ),


    ## ========================================================
    ## WEB ADMIN - CUSTOMER MANAGEMENT
    ## ========================================================

    path(
        "web-admin/customers/",
        management_views.web_admin_customer_list_view,
        name="web-admin-customers",
    ),


    ## ========================================================
    ## WEB ADMIN - REVIEW MANAGEMENT
    ## ========================================================

    path(
        "web-admin/reviews/",
        management_views.web_admin_review_list_view,
        name="web-admin-reviews",
    ),

    path(
        "web-admin/reviews/<int:review_id>/",
        management_views.web_admin_review_detail_view,
        name="web-admin-review-detail",
    ),

    path(
        "web-admin/reviews/<int:review_id>/delete/",
        management_views.web_admin_review_delete_view,
        name="web-admin-review-delete",
    ),


    ## ========================================================
    ## SUPER ADMIN - WEB ADMIN MANAGEMENT
    ## ========================================================

    path(
        "super-admin/web-admins/",
        management_views.super_admin_web_admin_list_view,
        name="super-admin-web-admin-list",
    ),

    ## Compatibility alias for templates that used the older name.
    path(
        "super-admin/web-admins/",
        management_views.super_admin_web_admin_list_view,
        name="super-admin-web-admins",
    ),

    path(
        "super-admin/web-admins/<int:web_admin_id>/edit/",
        management_views.super_admin_web_admin_edit_view,
        name="super-admin-web-admin-edit",
    ),

    path(
        "super-admin/web-admins/<int:web_admin_id>/delete/",
        management_views.super_admin_web_admin_delete_view,
        name="super-admin-web-admin-delete",
    ),
]
