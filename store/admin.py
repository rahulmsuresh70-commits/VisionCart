## =========================================================
## STORE ADMIN
## =========================================================

from django.contrib import admin

from .models import (
    Cart,
    CartItem,
    Category,
    Product,
    Wishlist,
    WishlistItem,
)


## =========================================================
## CATEGORY ADMIN
## =========================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
    )

    list_filter = (
        "is_active",
        "created_at",
    )


## =========================================================
## PRODUCT ADMIN
## =========================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "brand",
        "category",
        "price",
        "original_price",
        "stock",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "brand",
        "description",
    )

    list_filter = (
        "category",
        "is_active",
        "created_at",
    )


## =========================================================
## WISHLIST ADMIN
## =========================================================

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
    )


## =========================================================
## WISHLIST ITEM ADMIN
## =========================================================

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):

    list_display = (
        "wishlist",
        "product",
    )

    search_fields = (
        "wishlist__user__username",
        "product__name",
    )


## =========================================================
## CART ADMIN
## =========================================================

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "user__username",
        "user__email",
    )


## =========================================================
## CART ITEM ADMIN
## =========================================================

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):

    list_display = (
        "cart",
        "product",
        "quantity",
    )

    search_fields = (
        "cart__user__username",
        "product__name",
    )

    list_filter = (
        "product",
    )