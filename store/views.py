from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .models import (
    Cart,
    CartItem,
    Category,
    Product,
    Wishlist,
    WishlistItem,
)


## ============================================================
## MANAGEMENT ACCESS HELPER
## ============================================================

def management_user_required(request):
    ## Only Super Admin and Web Admin can access management pages.
    return (
        request.user.is_authenticated
        and request.user.role in ["SUPER_ADMIN", "WEB_ADMIN"]
    )


## ============================================================
## CUSTOMER HOME / PRODUCT PAGES
## ============================================================

def home_view(request):
    ## Show active categories and latest active products.
    categories = Category.objects.filter(
        is_active=True
    ).order_by("name")

    products = Product.objects.filter(
        is_active=True
    ).order_by("-created_at")[:8]

    return render(
        request,
        "home.html",
        {
            "categories": categories,
            "products": products,
        },
    )


def product_list_view(request):
    ## Show active products and active categories.
    products = Product.objects.filter(
        is_active=True
    ).select_related(
        "category"
    ).order_by("-created_at")

    categories = Category.objects.filter(
        is_active=True
    ).order_by("name")

    ## Optional category filter.
    category_id = request.GET.get("category")

    if category_id:
        products = products.filter(
            category_id=category_id
        )

    ## Optional search.
    search_query = request.GET.get(
        "q",
        "",
    ).strip()

    if search_query:
        products = products.filter(
            name__icontains=search_query
        ) | products.filter(
            brand__icontains=search_query
        )

    return render(
        request,
        "products.html",
        {
            "products": products,
            "categories": categories,
            "selected_category": category_id,
            "search_query": search_query,
        },
    )


def product_detail_view(request, product_id):
    ## Only active products are visible to customers.
    product = get_object_or_404(
        Product.objects.select_related("category"),
        id=product_id,
        is_active=True,
    )

    in_wishlist = False

    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(
            user=request.user
        ).first()

        if wishlist:
            in_wishlist = WishlistItem.objects.filter(
                wishlist=wishlist,
                product=product,
            ).exists()

    return render(
        request,
        "product_detail.html",
        {
            "product": product,
            "in_wishlist": in_wishlist,
        },
    )


## ============================================================
## CUSTOMER CART
## ============================================================

@login_required(login_url="login")
def add_to_cart_view(request, product_id):
    ## Cart changes must use POST.
    if request.method != "POST":
        return redirect(
            "product-detail",
            product_id=product_id,
        )

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
    )

    if product.stock <= 0:
        messages.error(
            request,
            "This product is currently out of stock.",
        )
        return redirect(
            "product-detail",
            product_id=product_id,
        )

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": 1},
    )

    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save(
                update_fields=["quantity"]
            )
        else:
            messages.warning(
                request,
                "You cannot add more than the available stock.",
            )
            return redirect("cart")

    messages.success(
        request,
        "Product added to cart.",
    )

    return redirect("cart")


@login_required(login_url="login")
def cart_view(request):
    cart = Cart.objects.filter(
        user=request.user
    ).first()

    if not cart:
        return render(
            request,
            "cart.html",
            {
                "cart": None,
                "items": [],
                "total": Decimal("0.00"),
            },
        )

    items = cart.items.select_related(
        "product"
    ).all()

    total = sum(
        (
            item.product.price * item.quantity
            for item in items
        ),
        Decimal("0.00"),
    )

    ## Attach subtotal to each item for template display.
    for item in items:
        item.subtotal = (
            item.product.price * item.quantity
        )

    return render(
        request,
        "cart.html",
        {
            "cart": cart,
            "items": items,
            "total": total,
        },
    )


@login_required(login_url="login")
def increase_cart_quantity_view(request, item_id):
    if request.method != "POST":
        return redirect("cart")

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user,
    )

    if cart_item.quantity < cart_item.product.stock:
        cart_item.quantity += 1

        cart_item.save(
            update_fields=["quantity"]
        )

    else:
        messages.warning(
            request,
            "You cannot exceed the available stock.",
        )

    return redirect("cart")


@login_required(login_url="login")
def decrease_cart_quantity_view(request, item_id):
    if request.method != "POST":
        return redirect("cart")

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user,
    )

    if cart_item.quantity > 1:
        cart_item.quantity -= 1

        cart_item.save(
            update_fields=["quantity"]
        )

    else:
        cart_item.delete()

    return redirect("cart")


@login_required(login_url="login")
def remove_cart_item_view(request, item_id):
    if request.method != "POST":
        return redirect("cart")

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user,
    )

    cart_item.delete()

    messages.success(
        request,
        "Product removed from cart.",
    )

    return redirect("cart")


## ============================================================
## CUSTOMER WISHLIST
## ============================================================

@login_required(login_url="login")
def add_to_wishlist_view(request, product_id):
    if request.method != "POST":
        return redirect(
            "product-detail",
            product_id=product_id,
        )

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
    )

    wishlist, created = Wishlist.objects.get_or_create(
        user=request.user
    )

    WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product,
    )

    messages.success(
        request,
        "Product added to wishlist.",
    )

    return redirect(
        "product-detail",
        product_id=product_id,
    )


@login_required(login_url="login")
def wishlist_view(request):
    wishlist, created = Wishlist.objects.get_or_create(
        user=request.user
    )

    items = wishlist.items.select_related(
        "product",
        "product__category",
    ).all()

    return render(
        request,
        "wishlist.html",
        {
            "wishlist": wishlist,
            "items": items,
        },
    )


@login_required(login_url="login")
def remove_from_wishlist_view(request, product_id):
    if request.method != "POST":
        return redirect("wishlist")

    # The existing URL uses the keyword product_id, while the
    # Wishlist page sends item.id. Keep that URL unchanged and use
    # the received value as the WishlistItem primary key.
    wishlist_item = get_object_or_404(
        WishlistItem,
        id=product_id,
        wishlist__user=request.user,
    )

    wishlist_item.delete()

    messages.success(
        request,
        "Product removed from wishlist.",
    )

    return redirect("wishlist")


## ============================================================
## WEB ADMIN - PRODUCT MANAGEMENT
## ============================================================

@login_required(login_url="management-login")
def web_admin_product_list_view(request):
    ## Customers are never allowed to access Web Admin pages.
    if not management_user_required(request):
        return HttpResponseForbidden(
            "You do not have permission to access this page."
        )

    products = Product.objects.select_related(
        "category"
    ).all().order_by("-created_at")

    ## Search by product name or brand.
    search_query = request.GET.get(
        "q",
        "",
    ).strip()

    if search_query:
        products = products.filter(
            name__icontains=search_query
        ) | products.filter(
            brand__icontains=search_query
        )

    ## Optional category filter.
    category_id = request.GET.get("category")

    if category_id:
        products = products.filter(
            category_id=category_id
        )

    ## Optional status filter.
    status = request.GET.get("status")

    if status == "active":
        products = products.filter(
            is_active=True
        )

    elif status == "inactive":
        products = products.filter(
            is_active=False
        )

    categories = Category.objects.all().order_by("name")

    return render(
        request,
        "web_admin_products.html",
        {
            "products": products,
            "categories": categories,
            "search_query": search_query,
            "selected_category": category_id,
            "selected_status": status,
        },
    )


@login_required(login_url="management-login")
def web_admin_product_add_view(request):
    ## Customers cannot access product management.
    if not management_user_required(request):
        return HttpResponseForbidden(
            "You do not have permission to access this page."
        )

    categories = Category.objects.all().order_by("name")

    if request.method == "POST":
        name = request.POST.get(
            "name",
            "",
        ).strip()

        brand = request.POST.get(
            "brand",
            "",
        ).strip()

        description = request.POST.get(
            "description",
            "",
        ).strip()

        category_id = request.POST.get(
            "category"
        )

        price_value = request.POST.get(
            "price",
            "",
        ).strip()

        original_price_value = request.POST.get(
            "original_price",
            "",
        ).strip()

        stock_value = request.POST.get(
            "stock",
            "",
        ).strip()

        ## Basic required-field validation.
        if not name:
            messages.error(
                request,
                "Product name is required.",
            )

            return render(
                request,
                "web_admin_product_form.html",
                {
                    "categories": categories,
                    "form_title": "Add Product",
                    "submit_text": "Add Product",
                    "product": None,
                },
            )

        if not description:
            messages.error(
                request,
                "Product description is required.",
            )

            return render(
                request,
                "web_admin_product_form.html",
                {
                    "categories": categories,
                    "form_title": "Add Product",
                    "submit_text": "Add Product",
                    "product": None,
                },
            )

        category = get_object_or_404(
            Category,
            id=category_id,
        )

        ## Validate price.
        try:
            price = Decimal(price_value)

        except (InvalidOperation, TypeError):
            messages.error(
                request,
                "Enter a valid product price.",
            )

            return render(
                request,
                "web_admin_product_form.html",
                {
                    "categories": categories,
                    "form_title": "Add Product",
                    "submit_text": "Add Product",
                    "product": None,
                },
            )

        if price < 0:
            messages.error(
                request,
                "Price cannot be negative.",
            )

            return render(
                request,
                "web_admin_product_form.html",
                {
                    "categories": categories,
                    "form_title": "Add Product",
                    "submit_text": "Add Product",
                    "product": None,
                },
            )

        ## Validate original price when provided.
        original_price = None

        if original_price_value:
            try:
                original_price = Decimal(
                    original_price_value
                )

            except (InvalidOperation, TypeError):
                messages.error(
                    request,
                    "Enter a valid original price.",
                )

                return render(
                    request,
                    "web_admin_product_form.html",
                    {
                        "categories": categories,
                        "form_title": "Add Product",
                        "submit_text": "Add Product",
                        "product": None,
                    },
                )

            if original_price < 0:
                messages.error(
                    request,
                    "Original price cannot be negative.",
                )

                return render(
                    request,
                    "web_admin_product_form.html",
                    {
                        "categories": categories,
                        "form_title": "Add Product",
                        "submit_text": "Add Product",
                        "product": None,
                    },
                )

        ## Validate stock.
        try:
            stock = int(stock_value)

        except (ValueError, TypeError):
            messages.error(
                request,
                "Stock must be a valid whole number.",
            )

            return render(
                request,
                "web_admin_product_form.html",
                {
                    "categories": categories,
                    "form_title": "Add Product",
                    "submit_text": "Add Product",
                    "product": None,
                },
            )

        if stock < 0:
            messages.error(
                request,
                "Stock cannot be negative.",
            )

            return render(
                request,
                "web_admin_product_form.html",
                {
                    "categories": categories,
                    "form_title": "Add Product",
                    "submit_text": "Add Product",
                    "product": None,
                },
            )

        product = Product(
            category=category,
            name=name,
            brand=brand,
            description=description,
            price=price,
            original_price=original_price,
            stock=stock,
            is_active=request.POST.get(
                "is_active"
            ) == "on",
        )

        if request.FILES.get("image"):
            product.image = request.FILES["image"]

        product.save()

        messages.success(
            request,
            "Product added successfully.",
        )

        return redirect(
            "web-admin-products"
        )

    return render(
        request,
        "web_admin_product_form.html",
        {
            "categories": categories,
            "form_title": "Add Product",
            "submit_text": "Add Product",
            "product": None,
        },
    )


@login_required(login_url="management-login")
def web_admin_product_edit_view(
    request,
    product_id,
):
    ## Customers cannot access product management.
    if not management_user_required(request):
        return HttpResponseForbidden(
            "You do not have permission to access this page."
        )

    product = get_object_or_404(
        Product,
        id=product_id,
    )

    categories = Category.objects.all().order_by("name")

    if request.method == "POST":
        name = request.POST.get(
            "name",
            "",
        ).strip()

        brand = request.POST.get(
            "brand",
            "",
        ).strip()

        description = request.POST.get(
            "description",
            "",
        ).strip()

        category_id = request.POST.get(
            "category"
        )

        price_value = request.POST.get(
            "price",
            "",
        ).strip()

        original_price_value = request.POST.get(
            "original_price",
            "",
        ).strip()

        stock_value = request.POST.get(
            "stock",
            "",
        ).strip()

        if not name:
            messages.error(
                request,
                "Product name is required.",
            )

            return render(
                request,
                "web_admin_product_form.html",
                {
                    "categories": categories,
                    "form_title": "Edit Product",
                    "submit_text": "Save Changes",
                    "product": product,
                },
            )

        if not description:
            messages.error(
                request,
                "Product description is required.",
            )

            return render(
                request,
                "web_admin_product_form.html",
                {
                    "categories": categories,
                    "form_title": "Edit Product",
                    "submit_text": "Save Changes",
                    "product": product,
                },
            )

        category = get_object_or_404(
            Category,
            id=category_id,
        )

        try:
            price = Decimal(price_value)

        except (InvalidOperation, TypeError):
            messages.error(
                request,
                "Enter a valid product price.",
            )

            return render(
                request,
                "web_admin_product_form.html",
                {
                    "categories": categories,
                    "form_title": "Edit Product",
                    "submit_text": "Save Changes",
                    "product": product,
                },
            )

        if price < 0:
            messages.error(
                request,
                "Price cannot be negative.",
            )

            return render(
                request,
                "web_admin_product_form.html",
                {
                    "categories": categories,
                    "form_title": "Edit Product",
                    "submit_text": "Save Changes",
                    "product": product,
                },
            )

        original_price = None

        if original_price_value:
            try:
                original_price = Decimal(
                    original_price_value
                )

            except (InvalidOperation, TypeError):
                messages.error(
                    request,
                    "Enter a valid original price.",
                )

                return render(
                    request,
                    "web_admin_product_form.html",
                    {
                        "categories": categories,
                        "form_title": "Edit Product",
                        "submit_text": "Save Changes",
                        "product": product,
                    },
                )

            if original_price < 0:
                messages.error(
                    request,
                    "Original price cannot be negative.",
                )

                return render(
                    request,
                    "web_admin_product_form.html",
                    {
                        "categories": categories,
                        "form_title": "Edit Product",
                        "submit_text": "Save Changes",
                        "product": product,
                    },
                )

        try:
            stock = int(stock_value)

        except (ValueError, TypeError):
            messages.error(
                request,
                "Stock must be a valid whole number.",
            )

            return render(
                request,
                "web_admin_product_form.html",
                {
                    "categories": categories,
                    "form_title": "Edit Product",
                    "submit_text": "Save Changes",
                    "product": product,
                },
            )

        if stock < 0:
            messages.error(
                request,
                "Stock cannot be negative.",
            )

            return render(
                request,
                "web_admin_product_form.html",
                {
                    "categories": categories,
                    "form_title": "Edit Product",
                    "submit_text": "Save Changes",
                    "product": product,
                },
            )

        product.category = category
        product.name = name
        product.brand = brand
        product.description = description
        product.price = price
        product.original_price = original_price
        product.stock = stock
        product.is_active = request.POST.get(
            "is_active"
        ) == "on"

        if request.FILES.get("image"):
            product.image = request.FILES["image"]

        product.save()

        messages.success(
            request,
            "Product updated successfully.",
        )

        return redirect(
            "web-admin-products"
        )

    return render(
        request,
        "web_admin_product_form.html",
        {
            "categories": categories,
            "form_title": "Edit Product",
            "submit_text": "Save Changes",
            "product": product,
        },
    )


@login_required(login_url="management-login")
def web_admin_product_toggle_view(
    request,
    product_id,
):
    ## Customers cannot access product management.
    if not management_user_required(request):
        return HttpResponseForbidden(
            "You do not have permission to access this page."
        )

    if request.method != "POST":
        return redirect(
            "web-admin-products"
        )

    product = get_object_or_404(
        Product,
        id=product_id,
    )

    product.is_active = not product.is_active

    product.save(
        update_fields=[
            "is_active",
            "updated_at",
        ]
    )

    if product.is_active:
        messages.success(
            request,
            f"{product.name} has been activated.",
        )
    else:
        messages.success(
            request,
            f"{product.name} has been deactivated.",
        )

    return redirect(
        "web-admin-products"
    )


@login_required(login_url="management-login")
def web_admin_product_delete_view(
    request,
    product_id,
):
    ## Customers cannot access product management.
    if not management_user_required(request):
        return HttpResponseForbidden(
            "You do not have permission to access this page."
        )

    if request.method != "POST":
        return redirect(
            "web-admin-products"
        )

    product = get_object_or_404(
        Product,
        id=product_id,
    )

    try:
        product_name = product.name

        product.delete()

        messages.success(
            request,
            f"{product_name} was deleted successfully.",
        )

    except ProtectedError:
        ## Preserve products that are referenced by historical orders.
        messages.error(
            request,
            "This product cannot be deleted because it is used in an existing order. Deactivate it instead.",
        )

    return redirect(
        "web-admin-products"
    )


## ============================================================
## WEB ADMIN - CATEGORY MANAGEMENT
## ============================================================

@login_required(login_url="management-login")
def web_admin_category_list_view(request):
    ## Customers cannot access category management.
    if not management_user_required(request):
        return HttpResponseForbidden(
            "You do not have permission to access this page."
        )

    categories = Category.objects.all().order_by("name")

    search_query = request.GET.get(
        "q",
        "",
    ).strip()

    if search_query:
        categories = categories.filter(
            name__icontains=search_query
        )

    status = request.GET.get("status")

    if status == "active":
        categories = categories.filter(
            is_active=True
        )

    elif status == "inactive":
        categories = categories.filter(
            is_active=False
        )

    return render(
        request,
        "web_admin_categories.html",
        {
            "categories": categories,
            "search_query": search_query,
            "selected_status": status,
        },
    )


@login_required(login_url="management-login")
def web_admin_category_add_view(request):
    ## Customers cannot access category management.
    if not management_user_required(request):
        return HttpResponseForbidden(
            "You do not have permission to access this page."
        )

    if request.method == "POST":
        name = request.POST.get(
            "name",
            "",
        ).strip()

        description = request.POST.get(
            "description",
            "",
        ).strip()

        if not name:
            messages.error(
                request,
                "Category name is required.",
            )

            return render(
                request,
                "web_admin_category_form.html",
                {
                    "form_title": "Add Category",
                    "submit_text": "Add Category",
                    "category": None,
                },
            )

        ## Prevent duplicate category names.
        if Category.objects.filter(
            name__iexact=name
        ).exists():
            messages.error(
                request,
                "A category with this name already exists.",
            )

            return render(
                request,
                "web_admin_category_form.html",
                {
                    "form_title": "Add Category",
                    "submit_text": "Add Category",
                    "category": None,
                },
            )

        category = Category(
            name=name,
            description=description,
            is_active=request.POST.get(
                "is_active"
            ) == "on",
        )

        if request.FILES.get("image"):
            category.image = request.FILES["image"]

        category.save()

        messages.success(
            request,
            "Category added successfully.",
        )

        return redirect(
            "web-admin-categories"
        )

    return render(
        request,
        "web_admin_category_form.html",
        {
            "form_title": "Add Category",
            "submit_text": "Add Category",
            "category": None,
        },
    )


@login_required(login_url="management-login")
def web_admin_category_edit_view(
    request,
    category_id,
):
    ## Customers cannot access category management.
    if not management_user_required(request):
        return HttpResponseForbidden(
            "You do not have permission to access this page."
        )

    category = get_object_or_404(
        Category,
        id=category_id,
    )

    if request.method == "POST":
        name = request.POST.get(
            "name",
            "",
        ).strip()

        description = request.POST.get(
            "description",
            "",
        ).strip()

        if not name:
            messages.error(
                request,
                "Category name is required.",
            )

            return render(
                request,
                "web_admin_category_form.html",
                {
                    "form_title": "Edit Category",
                    "submit_text": "Save Changes",
                    "category": category,
                },
            )

        ## Prevent duplicate names except current category.
        duplicate_exists = Category.objects.filter(
            name__iexact=name
        ).exclude(
            id=category.id
        ).exists()

        if duplicate_exists:
            messages.error(
                request,
                "A category with this name already exists.",
            )

            return render(
                request,
                "web_admin_category_form.html",
                {
                    "form_title": "Edit Category",
                    "submit_text": "Save Changes",
                    "category": category,
                },
            )

        category.name = name
        category.description = description
        category.is_active = request.POST.get(
            "is_active"
        ) == "on"

        if request.FILES.get("image"):
            category.image = request.FILES["image"]

        category.save()

        messages.success(
            request,
            "Category updated successfully.",
        )

        return redirect(
            "web-admin-categories"
        )

    return render(
        request,
        "web_admin_category_form.html",
        {
            "form_title": "Edit Category",
            "submit_text": "Save Changes",
            "category": category,
        },
    )


@login_required(login_url="management-login")
def web_admin_category_toggle_view(
    request,
    category_id,
):
    ## Customers cannot access category management.
    if not management_user_required(request):
        return HttpResponseForbidden(
            "You do not have permission to access this page."
        )

    if request.method != "POST":
        return redirect(
            "web-admin-categories"
        )

    category = get_object_or_404(
        Category,
        id=category_id,
    )

    category.is_active = not category.is_active

    category.save(
        update_fields=["is_active"]
    )

    if category.is_active:
        messages.success(
            request,
            f"{category.name} has been activated.",
        )
    else:
        messages.success(
            request,
            f"{category.name} has been deactivated.",
        )

    return redirect(
        "web-admin-categories"
    )


@login_required(login_url="management-login")
def web_admin_category_delete_view(
    request,
    category_id,
):
    ## Customers cannot access category management.
    if not management_user_required(request):
        return HttpResponseForbidden(
            "You do not have permission to access this page."
        )

    if request.method != "POST":
        return redirect(
            "web-admin-categories"
        )

    category = get_object_or_404(
        Category,
        id=category_id,
    )

    ## Never delete a category containing products.
    if category.products.exists():
        messages.error(
            request,
            "This category cannot be deleted because it contains products. Move or delete the products first, or deactivate the category.",
        )

        return redirect(
            "web-admin-categories"
        )

    category_name = category.name

    category.delete()

    messages.success(
        request,
        f"{category_name} was deleted successfully.",
    )

    return redirect(
        "web-admin-categories"
    )


## ============================================================
## WEB ADMIN - INVENTORY MANAGEMENT
## ============================================================

@login_required(login_url="management-login")
def web_admin_inventory_view(request):
    ## Only Super Admin and Web Admin can manage inventory.
    if not management_user_required(request):
        return HttpResponseForbidden(
            "You do not have permission to access this page."
        )

    products = Product.objects.select_related(
        "category"
    ).all().order_by("name")

    ## Search by product name or brand.
    search_query = request.GET.get(
        "q",
        "",
    ).strip()

    if search_query:
        products = products.filter(
            name__icontains=search_query
        ) | products.filter(
            brand__icontains=search_query
        )

    ## Stock status filter.
    stock_status = request.GET.get(
        "stock_status",
        "",
    )

    if stock_status == "in_stock":
        products = products.filter(
            stock__gt=5
        )

    elif stock_status == "low_stock":
        products = products.filter(
            stock__gt=0,
            stock__lte=5,
        )

    elif stock_status == "out_of_stock":
        products = products.filter(
            stock=0
        )

    ## Calculate inventory summary.
    all_products = Product.objects.all()

    total_products = all_products.count()

    in_stock_count = all_products.filter(
        stock__gt=5
    ).count()

    low_stock_count = all_products.filter(
        stock__gt=0,
        stock__lte=5,
    ).count()

    out_of_stock_count = all_products.filter(
        stock=0
    ).count()

    return render(
        request,
        "web_admin_inventory.html",
        {
            "products": products,
            "search_query": search_query,
            "selected_stock_status": stock_status,
            "total_products": total_products,
            "in_stock_count": in_stock_count,
            "low_stock_count": low_stock_count,
            "out_of_stock_count": out_of_stock_count,
        },
    )


@login_required(login_url="management-login")
def web_admin_inventory_adjust_view(
    request,
    product_id,
):
    ## Only Super Admin and Web Admin can modify inventory.
    if not management_user_required(request):
        return HttpResponseForbidden(
            "You do not have permission to access this page."
        )

    if request.method != "POST":
        return redirect(
            "web-admin-inventory"
        )

    adjustment_type = request.POST.get(
        "adjustment_type"
    )

    quantity_value = request.POST.get(
        "quantity",
        "",
    ).strip()

    ## Only two adjustment types are accepted.
    if adjustment_type not in [
        "add",
        "remove",
    ]:
        messages.error(
            request,
            "Invalid inventory adjustment.",
        )

        return redirect(
            "web-admin-inventory"
        )

    ## Quantity must be a positive whole number.
    try:
        quantity = int(quantity_value)

    except (ValueError, TypeError):
        messages.error(
            request,
            "Enter a valid whole number for the stock quantity.",
        )

        return redirect(
            "web-admin-inventory"
        )

    if quantity <= 0:
        messages.error(
            request,
            "Stock adjustment quantity must be greater than zero.",
        )

        return redirect(
            "web-admin-inventory"
        )

    ## Lock the product row during the stock update.
    with transaction.atomic():

        product = get_object_or_404(
            Product.objects.select_for_update(),
            id=product_id,
        )

        ## --------------------------------------------------------
        ## ADD STOCK
        ## --------------------------------------------------------

        if adjustment_type == "add":

            ## Read the locked database value and calculate the new
            ## stock from that value. This guarantees that an Add +N
            ## operation is persisted as current stock + N.
            current_stock = int(product.stock)
            new_stock = current_stock + quantity

            product.stock = new_stock

            product.save(
                update_fields=[
                    "stock",
                    "updated_at",
                ]
            )

            ## Refresh after saving so the success message and the
            ## next page load use the value actually stored in DB.
            product.refresh_from_db(fields=["stock"])

            messages.success(
                request,
                f"{quantity} unit(s) added to {product.name}. Current stock: {product.stock}.",
            )

        ## --------------------------------------------------------
        ## REMOVE STOCK
        ## --------------------------------------------------------

        else:

            ## Never allow inventory to become negative.
            if quantity > int(product.stock):

                messages.error(
                    request,
                    f"Cannot remove {quantity} unit(s). {product.name} currently has only {product.stock} unit(s) in stock.",
                )

            else:

                current_stock = int(product.stock)
                new_stock = current_stock - quantity

                product.stock = new_stock

                product.save(
                    update_fields=[
                        "stock",
                        "updated_at",
                    ]
                )

                product.refresh_from_db(fields=["stock"])

                messages.success(
                    request,
                    f"{quantity} unit(s) removed from {product.name}. Current stock: {product.stock}.",
                )

    return redirect(
        "web-admin-inventory"
    )