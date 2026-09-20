from django.urls import path

from . import review_views
from . import views


urlpatterns = [
    ## ========================================================
    ## CUSTOMER ADDRESSES
    ## ========================================================

    path(
        "addresses/",
        views.address_list_view,
        name="addresses",
    ),

    path(
        "addresses/add/",
        views.add_address_view,
        name="add-address",
    ),

    path(
        "addresses/edit/<int:address_id>/",
        views.edit_address_view,
        name="edit-address",
    ),

    path(
        "addresses/delete/<int:address_id>/",
        views.delete_address_view,
        name="delete-address",
    ),

    path(
        "addresses/default/<int:address_id>/",
        views.set_default_address_view,
        name="set-default-address",
    ),


    ## ========================================================
    ## CHECKOUT
    ## ========================================================

    path(
        "checkout/",
        views.checkout_view,
        name="checkout",
    ),

    path(
        "checkout/place-order/",
        views.place_order_view,
        name="place-order",
    ),

    ## Online Payment
    path(
        "checkout/online-payment/",
        views.online_payment_view,
        name="online-payment",
    ),

    path(
        "checkout/online-payment/confirm/",
        views.confirm_online_payment_view,
        name="confirm-online-payment",
    ),


    ## ========================================================
    ## CUSTOMER ORDERS
    ## ========================================================

    path(
        "orders/",
        views.order_list_view,
        name="orders",
    ),

    path(
        "orders/<int:order_id>/",
        views.order_detail_view,
        name="order-detail",
    ),

    path(
        "orders/<int:order_id>/success/",
        views.order_success_view,
        name="order-success",
    ),

    path(
        "orders/<int:order_id>/cancel/",
        views.cancel_order_view,
        name="cancel-order",
    ),


    ## ========================================================
    ## CUSTOMER REVIEWS
    ## ========================================================

    path(
        "products/<int:product_id>/review/",
        review_views.add_review_view,
        name="add-review",
    ),


    ## ========================================================
    ## WEB ADMIN - ORDER MANAGEMENT
    ## ========================================================

    path(
        "web-admin/orders/",
        views.web_admin_order_list_view,
        name="web-admin-orders",
    ),

    path(
        "web-admin/orders/<int:order_id>/",
        views.web_admin_order_detail_view,
        name="web-admin-order-detail",
    ),

    path(
        "web-admin/orders/<int:order_id>/update/",
        views.web_admin_update_order_view,
        name="web-admin-update-order",
    ),
]
