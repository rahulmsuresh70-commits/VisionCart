## =========================================================
## ORDERS ADMIN
## =========================================================

from django.contrib import admin

from .models import (
    Address,
    Order,
    OrderItem,
    Payment,
    Review,
)


## =========================================================
## ADDRESS ADMIN
## =========================================================

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "user",
        "phone",
        "city",
        "state",
        "pincode",
        "is_default",
    )

    search_fields = (
        "name",
        "phone",
        "city",
        "state",
        "pincode",
        "user__username",
        "user__email",
    )

    list_filter = (
        "is_default",
        "state",
        "city",
    )


## =========================================================
## ORDER ADMIN
## =========================================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "order_number",
        "user",
        "payment_method",
        "payment_status",
        "status",
        "shipping_method",
        "tracking_number",
        "estimated_delivery_date",
        "total_amount",
        "created_at",
    )

    search_fields = (
        "order_number",
        "user__username",
        "user__email",
        "tracking_number",
    )

    list_filter = (
        "status",
        "payment_method",
        "payment_status",
        "shipping_method",
        "created_at",
    )

    readonly_fields = (
        "order_number",
        "created_at",
        "updated_at",
    )

    list_per_page = 25


## =========================================================
## ORDER ITEM ADMIN
## =========================================================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "product",
        "quantity",
        "price",
    )

    search_fields = (
        "order__order_number",
        "product__name",
    )

    list_filter = (
        "product",
    )


## =========================================================
## PAYMENT ADMIN
## =========================================================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "method",
        "transaction_id",
        "amount",
        "status",
        "created_at",
    )

    search_fields = (
        "order__order_number",
        "transaction_id",
    )

    list_filter = (
        "method",
        "status",
        "created_at",
    )

    readonly_fields = (
        "created_at",
    )


## =========================================================
## REVIEW ADMIN
## =========================================================

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "user",
        "rating",
        "created_at",
    )

    search_fields = (
        "product__name",
        "user__username",
        "user__email",
        "comment",
    )

    list_filter = (
        "rating",
        "created_at",
    )