from django.urls import path

from . import views


urlpatterns = [

    ## ========================================================
    ## CUSTOMER STORE
    ## ========================================================

    path(
        "",
        views.home_view,
        name="home",
    ),

    path(
        "products/",
        views.product_list_view,
        name="products",
    ),

    path(
        "products/<int:product_id>/",
        views.product_detail_view,
        name="product-detail",
    ),


    ## ========================================================
    ## CART
    ## ========================================================

    path(
        "cart/",
        views.cart_view,
        name="cart",
    ),

    path(
        "cart/add/<int:product_id>/",
        views.add_to_cart_view,
        name="add-to-cart",
    ),

    path(
        "cart/increase/<int:item_id>/",
        views.increase_cart_quantity_view,
        name="increase-cart",
    ),

    path(
        "cart/decrease/<int:item_id>/",
        views.decrease_cart_quantity_view,
        name="decrease-cart",
    ),

    path(
        "cart/remove/<int:item_id>/",
        views.remove_cart_item_view,
        name="remove-cart-item",
    ),


    ## ========================================================
    ## WISHLIST
    ## ========================================================

    path(
        "wishlist/",
        views.wishlist_view,
        name="wishlist",
    ),

    path(
        "wishlist/add/<int:product_id>/",
        views.add_to_wishlist_view,
        name="add-to-wishlist",
    ),

    path(
        "wishlist/remove/<int:product_id>/",
        views.remove_from_wishlist_view,
        name="remove-from-wishlist",
    ),


    ## ========================================================
    ## WEB ADMIN - PRODUCTS
    ## ========================================================

    path(
        "web-admin/products/",
        views.web_admin_product_list_view,
        name="web-admin-products",
    ),

    path(
        "web-admin/products/add/",
        views.web_admin_product_add_view,
        name="web-admin-product-add",
    ),

    path(
        "web-admin/products/<int:product_id>/edit/",
        views.web_admin_product_edit_view,
        name="web-admin-product-edit",
    ),

    path(
        "web-admin/products/<int:product_id>/toggle/",
        views.web_admin_product_toggle_view,
        name="web-admin-product-toggle",
    ),

    path(
        "web-admin/products/<int:product_id>/delete/",
        views.web_admin_product_delete_view,
        name="web-admin-product-delete",
    ),


    ## ========================================================
    ## WEB ADMIN - CATEGORIES
    ## ========================================================

    path(
        "web-admin/categories/",
        views.web_admin_category_list_view,
        name="web-admin-categories",
    ),

    path(
        "web-admin/categories/add/",
        views.web_admin_category_add_view,
        name="web-admin-category-add",
    ),

    path(
        "web-admin/categories/<int:category_id>/edit/",
        views.web_admin_category_edit_view,
        name="web-admin-category-edit",
    ),

    path(
        "web-admin/categories/<int:category_id>/toggle/",
        views.web_admin_category_toggle_view,
        name="web-admin-category-toggle",
    ),

    path(
        "web-admin/categories/<int:category_id>/delete/",
        views.web_admin_category_delete_view,
        name="web-admin-category-delete",
    ),


    ## ========================================================
    ## WEB ADMIN - INVENTORY
    ## ========================================================

    path(
        "web-admin/inventory/",
        views.web_admin_inventory_view,
        name="web-admin-inventory",
    ),

    path(
        "web-admin/inventory/<int:product_id>/adjust/",
        views.web_admin_inventory_adjust_view,
        name="web-admin-inventory-adjust",
    ),

]