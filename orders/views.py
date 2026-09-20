## =========================================================
## ORDERS VIEWS
## =========================================================


## =========================================================
## IMPORTS
## =========================================================

from decimal import Decimal
from datetime import timedelta
from uuid import uuid4

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from store.models import Cart, CartItem, Product

from .models import (
    Address,
    Order,
    OrderItem,
    Payment,
)


## =========================================================
## MANAGEMENT ROLE CHECK
## =========================================================

def management_user_required(request):

    ## ## Only Super Admin and Web Admin can access
    ## ## management order pages.
    if not request.user.is_authenticated:

        return False

    return request.user.role in [
        "SUPER_ADMIN",
        "WEB_ADMIN",
    ]


## =========================================================
## SAFE MANAGEMENT RETURN
## =========================================================

def management_return_redirect(
    request,
    fallback_name,
    **kwargs,
):
    """
    Return to the Super Admin dashboard when requested;
    otherwise use the normal management page.
    """

    next_url = request.POST.get(
        "next",
        "",
    ).strip()

    if next_url.startswith("/super-admin/"):
        return redirect(next_url)

    return redirect(
        fallback_name,
        **kwargs,
    )


## =========================================================
## CUSTOMER ADDRESS LIST
## =========================================================

@login_required(login_url="login")
def address_list_view(request):

    addresses = Address.objects.filter(
        user=request.user
    ).order_by(
        "-is_default",
        "-id",
    )

    context = {
        "addresses": addresses,
    }

    return render(
        request,
        "addresses.html",
        context,
    )


## =========================================================
## ADD CUSTOMER ADDRESS
## =========================================================

@login_required(login_url="login")
def add_address_view(request):

    if request.method == "POST":

        name = request.POST.get(
            "name",
            "",
        ).strip()

        phone = request.POST.get(
            "phone",
            "",
        ).strip()

        address = request.POST.get(
            "address",
            "",
        ).strip()

        city = request.POST.get(
            "city",
            "",
        ).strip()

        state = request.POST.get(
            "state",
            "",
        ).strip()

        pincode = request.POST.get(
            "pincode",
            "",
        ).strip()


        ## =====================================================
        ## REQUIRED FIELD VALIDATION
        ## =====================================================

        if not all([
            name,
            phone,
            address,
            city,
            state,
            pincode,
        ]):

            return render(
                request,
                "address_form.html",
                {
                    "error": "All fields are required.",
                    "form_data": request.POST,
                },
            )


        ## =====================================================
        ## PHONE VALIDATION
        ## =====================================================

        if not phone.isdigit() or len(phone) != 10:

            return render(
                request,
                "address_form.html",
                {
                    "error": "Enter a valid 10-digit phone number.",
                    "form_data": request.POST,
                },
            )


        ## =====================================================
        ## PINCODE VALIDATION
        ## =====================================================

        if not pincode.isdigit() or len(pincode) != 6:

            return render(
                request,
                "address_form.html",
                {
                    "error": "Enter a valid 6-digit pincode.",
                    "form_data": request.POST,
                },
            )


        has_address = Address.objects.filter(
            user=request.user
        ).exists()


        make_default = (
            request.POST.get("is_default") == "on"
        )


        is_default = (
            not has_address
            or make_default
        )


        if is_default:

            Address.objects.filter(
                user=request.user
            ).update(
                is_default=False,
            )


        Address.objects.create(
            user=request.user,
            name=name,
            phone=phone,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
            is_default=is_default,
        )


        messages.success(
            request,
            "Address added successfully.",
        )


        return redirect("addresses")


    return render(
        request,
        "address_form.html",
    )


## =========================================================
## EDIT ADDRESS
## =========================================================

@login_required(login_url="login")
def edit_address_view(
    request,
    address_id,
):

    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user,
    )


    if request.method == "POST":

        name = request.POST.get(
            "name",
            "",
        ).strip()

        phone = request.POST.get(
            "phone",
            "",
        ).strip()

        address_text = request.POST.get(
            "address",
            "",
        ).strip()

        city = request.POST.get(
            "city",
            "",
        ).strip()

        state = request.POST.get(
            "state",
            "",
        ).strip()

        pincode = request.POST.get(
            "pincode",
            "",
        ).strip()


        if not all([
            name,
            phone,
            address_text,
            city,
            state,
            pincode,
        ]):

            messages.error(
                request,
                "All fields are required.",
            )

            return render(
                request,
                "address_form.html",
                {
                    "address": address,
                    "edit_mode": True,
                },
            )


        if not phone.isdigit() or len(phone) != 10:

            messages.error(
                request,
                "Enter a valid 10-digit phone number.",
            )

            return render(
                request,
                "address_form.html",
                {
                    "address": address,
                    "edit_mode": True,
                },
            )


        if not pincode.isdigit() or len(pincode) != 6:

            messages.error(
                request,
                "Enter a valid 6-digit pincode.",
            )

            return render(
                request,
                "address_form.html",
                {
                    "address": address,
                    "edit_mode": True,
                },
            )


        make_default = (
            request.POST.get("is_default") == "on"
        )


        if make_default:

            Address.objects.filter(
                user=request.user,
            ).exclude(
                id=address.id,
            ).update(
                is_default=False,
            )

            is_default = True

        else:

            is_default = address.is_default


        address.name = name
        address.phone = phone
        address.address = address_text
        address.city = city
        address.state = state
        address.pincode = pincode
        address.is_default = is_default

        address.save()


        messages.success(
            request,
            "Address updated successfully.",
        )


        return redirect("addresses")


    return render(
        request,
        "address_form.html",
        {
            "address": address,
            "edit_mode": True,
        },
    )


## =========================================================
## DELETE ADDRESS
## =========================================================

@login_required(login_url="login")
def delete_address_view(
    request,
    address_id,
):

    if request.method != "POST":

        return redirect("addresses")


    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user,
    )


    was_default = address.is_default


    address.delete()


    if was_default:

        next_address = Address.objects.filter(
            user=request.user
        ).order_by(
            "-id",
        ).first()


        if next_address:

            next_address.is_default = True

            next_address.save(
                update_fields=[
                    "is_default",
                ],
            )


    messages.success(
        request,
        "Address deleted successfully.",
    )


    return redirect("addresses")


## =========================================================
## SET DEFAULT ADDRESS
## =========================================================

@login_required(login_url="login")
def set_default_address_view(
    request,
    address_id,
):

    if request.method != "POST":

        return redirect("addresses")


    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user,
    )


    with transaction.atomic():

        Address.objects.filter(
            user=request.user
        ).update(
            is_default=False,
        )


        address.is_default = True

        address.save(
            update_fields=[
                "is_default",
            ],
        )


    messages.success(
        request,
        "Default address updated successfully.",
    )


    return redirect("addresses")


## =========================================================
## CHECKOUT
## =========================================================

@login_required(login_url="login")
def checkout_view(request):

    cart = Cart.objects.filter(
        user=request.user
    ).first()


    if not cart:

        messages.error(
            request,
            "Your cart is empty.",
        )

        return redirect("cart")


    items = cart.items.select_related(
        "product"
    ).all()


    if not items.exists():

        messages.error(
            request,
            "Your cart is empty.",
        )

        return redirect("cart")


    total = Decimal("0.00")


    for item in items:

        item.subtotal = (
            item.product.price
            * item.quantity
        )

        total += item.subtotal


    addresses = Address.objects.filter(
        user=request.user
    ).order_by(
        "-is_default",
        "-id",
    )


    if not addresses.exists():

        messages.info(
            request,
            "Please add a delivery address before checkout.",
        )

        return redirect("add-address")


    selected_address = addresses.filter(
        is_default=True
    ).first()


    if not selected_address:

        selected_address = addresses.first()


    shipping_method = (
        Order.ShippingMethod.STANDARD
    )

    shipping_charge = Decimal("0.00")


    grand_total = (
        total
        + shipping_charge
    )


    context = {
        "items": items,
        "total": total,
        "shipping_method": shipping_method,
        "shipping_charge": shipping_charge,
        "grand_total": grand_total,
        "addresses": addresses,
        "selected_address": selected_address,
    }


    return render(
        request,
        "checkout.html",
        context,
    )


## =========================================================
## ONLINE PAYMENT PAGE
## =========================================================

@login_required(login_url="login")
def online_payment_view(request):

    if request.method != "GET":

        return redirect("checkout")


    address_id = request.GET.get(
        "address_id"
    )


    if not address_id:

        messages.error(
            request,
            "Please select a delivery address.",
        )

        return redirect("checkout")


    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user,
    )


    cart = Cart.objects.filter(
        user=request.user
    ).first()


    if not cart:

        messages.error(
            request,
            "Your cart is empty.",
        )

        return redirect("cart")


    items = cart.items.select_related(
        "product"
    ).all()


    if not items.exists():

        messages.error(
            request,
            "Your cart is empty.",
        )

        return redirect("cart")


    total = Decimal("0.00")


    for item in items:

        item.subtotal = (
            item.product.price
            * item.quantity
        )

        total += item.subtotal


    shipping_method = (
        Order.ShippingMethod.STANDARD
    )

    shipping_charge = Decimal("0.00")


    grand_total = (
        total
        + shipping_charge
    )


    context = {
        "items": items,
        "address": address,
        "total": total,
        "shipping_method": shipping_method,
        "shipping_charge": shipping_charge,
        "grand_total": grand_total,
    }


    return render(
        request,
        "online_payment.html",
        context,
    )


## =========================================================
## CONFIRM ONLINE PAYMENT
## =========================================================

@login_required(login_url="login")
def confirm_online_payment_view(request):

    if request.method != "POST":

        return redirect("checkout")


    address_id = request.POST.get(
        "address_id"
    )


    if not address_id:

        messages.error(
            request,
            "Please select a delivery address.",
        )

        return redirect("checkout")


    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user,
    )


    cart = Cart.objects.filter(
        user=request.user
    ).first()


    if not cart:

        messages.error(
            request,
            "Your cart is empty.",
        )

        return redirect("cart")


    cart_items = list(
        cart.items.select_related(
            "product"
        ).all()
    )


    if not cart_items:

        messages.error(
            request,
            "Your cart is empty.",
        )

        return redirect("cart")


    with transaction.atomic():

        total = Decimal("0.00")

        locked_items = []


        for cart_item in cart_items:

            product = Product.objects.select_for_update().get(
                id=cart_item.product.id
            )


            if not product.is_active:

                messages.error(
                    request,
                    f"{product.name} is no longer available.",
                )

                return redirect("cart")


            if cart_item.quantity <= 0:

                messages.error(
                    request,
                    f"Invalid quantity for {product.name}.",
                )

                return redirect("cart")


            if cart_item.quantity > product.stock:

                messages.error(
                    request,
                    f"Only {product.stock} unit(s) of "
                    f"{product.name} are available.",
                )

                return redirect("cart")


            subtotal = (
                product.price
                * cart_item.quantity
            )


            total += subtotal


            locked_items.append(
                (
                    cart_item,
                    product,
                )
            )


        shipping_method = (
            Order.ShippingMethod.STANDARD
        )

        shipping_charge = Decimal("0.00")


        estimated_delivery_date = (
            timezone.localdate()
            + timedelta(days=5)
        )


        grand_total = (
            total
            + shipping_charge
        )


        order_number = (
            "VC-"
            + uuid4().hex[:10].upper()
        )


        ## =================================================
        ## CREATE ORDER
        ## =================================================

        order = Order.objects.create(

            user=request.user,

            order_number=order_number,

            address=address,

            payment_method=Order.PaymentMethod.ONLINE,

            payment_status="PAID",

            status=Order.Status.PLACED,

            shipping_method=shipping_method,

            shipping_charge=shipping_charge,

            tracking_number="",

            shipped_at=None,

            delivered_at=None,

            estimated_delivery_date=(
                estimated_delivery_date
            ),

            total_amount=grand_total,
        )


        ## =================================================
        ## CREATE ORDER ITEMS
        ## =================================================

        for cart_item, product in locked_items:

            OrderItem.objects.create(

                order=order,

                product=product,

                quantity=cart_item.quantity,

                price=product.price,
            )


            product.stock -= cart_item.quantity


            product.save(
                update_fields=[
                    "stock",
                ],
            )


        ## =================================================
        ## CREATE ONLINE PAYMENT
        ## =================================================

        Payment.objects.create(

            order=order,

            method="ONLINE",

            transaction_id=(
                "ONLINE-"
                + uuid4().hex[:12].upper()
            ),

            amount=grand_total,

            status="SUCCESS",
        )


        ## =================================================
        ## CLEAR CART
        ## =================================================

        CartItem.objects.filter(
            cart=cart
        ).delete()


    messages.success(
        request,
        "Online payment successful. Your order has been placed.",
    )


    return redirect(
        "order-success",
        order_id=order.id,
    )


## =========================================================
## ORDER SUCCESS
## =========================================================

@login_required(login_url="login")
def order_success_view(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
    )

    return render(
        request,
        "order_success.html",
        {
            "order": order,
        },
    )


## =========================================================
## PLACE ORDER
## =========================================================

@login_required(login_url="login")
def place_order_view(request):

    if request.method != "POST":

        return redirect("checkout")


    address_id = request.POST.get(
        "address_id"
    )


    payment_method = request.POST.get(
        "payment_method"
    )


    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user,
    )


    valid_methods = [
        Order.PaymentMethod.COD,
        Order.PaymentMethod.ONLINE,
    ]


    if payment_method not in valid_methods:

        messages.error(
            request,
            "Please select a valid payment method.",
        )

        return redirect("checkout")


    ## =====================================================
    ## ONLINE PAYMENT
    ## =====================================================

    if payment_method == Order.PaymentMethod.ONLINE:

        payment_url = (
            reverse("online-payment")
            + "?address_id="
            + str(address.id)
        )


        return redirect(
            payment_url
        )


    ## =====================================================
    ## COD
    ## =====================================================

    cart = Cart.objects.filter(
        user=request.user
    ).first()


    if not cart:

        messages.error(
            request,
            "Your cart is empty.",
        )

        return redirect("cart")


    cart_items = list(
        cart.items.select_related(
            "product"
        ).all()
    )


    if not cart_items:

        messages.error(
            request,
            "Your cart is empty.",
        )

        return redirect("cart")


    with transaction.atomic():

        total = Decimal("0.00")

        locked_items = []


        for cart_item in cart_items:

            product = Product.objects.select_for_update().get(
                id=cart_item.product.id
            )


            if not product.is_active:

                messages.error(
                    request,
                    f"{product.name} is no longer available.",
                )

                return redirect("cart")


            if cart_item.quantity <= 0:

                messages.error(
                    request,
                    f"Invalid quantity for {product.name}.",
                )

                return redirect("cart")


            if cart_item.quantity > product.stock:

                messages.error(
                    request,
                    f"Only {product.stock} unit(s) of "
                    f"{product.name} are available.",
                )

                return redirect("cart")


            subtotal = (
                product.price
                * cart_item.quantity
            )


            total += subtotal


            locked_items.append(
                (
                    cart_item,
                    product,
                )
            )


        shipping_method = (
            Order.ShippingMethod.STANDARD
        )

        shipping_charge = Decimal("0.00")


        estimated_delivery_date = (
            timezone.localdate()
            + timedelta(days=5)
        )


        grand_total = (
            total
            + shipping_charge
        )


        order_number = (
            "VC-"
            + uuid4().hex[:10].upper()
        )


        ## =================================================
        ## CREATE COD ORDER
        ## =================================================

        order = Order.objects.create(

            user=request.user,

            order_number=order_number,

            address=address,

            payment_method=Order.PaymentMethod.COD,

            payment_status="PENDING",

            status=Order.Status.PLACED,

            shipping_method=shipping_method,

            shipping_charge=shipping_charge,

            tracking_number="",

            shipped_at=None,

            delivered_at=None,

            estimated_delivery_date=(
                estimated_delivery_date
            ),

            total_amount=grand_total,
        )


        ## =================================================
        ## ORDER ITEMS
        ## =================================================

        for cart_item, product in locked_items:

            OrderItem.objects.create(

                order=order,

                product=product,

                quantity=cart_item.quantity,

                price=product.price,
            )


            product.stock -= cart_item.quantity


            product.save(
                update_fields=[
                    "stock",
                ],
            )


        ## =================================================
        ## COD PAYMENT
        ## =================================================

        Payment.objects.create(

            order=order,

            method="COD",

            transaction_id="",

            amount=grand_total,

            status="PENDING",
        )


        ## =================================================
        ## CLEAR CART
        ## =================================================

        CartItem.objects.filter(
            cart=cart
        ).delete()


    messages.success(
        request,
        "Your order has been placed successfully.",
    )


    return redirect(
        "order-detail",
        order_id=order.id,
    )


## =========================================================
## CUSTOMER ORDERS
## =========================================================

@login_required(login_url="login")
def order_list_view(request):

    orders = Order.objects.filter(
        user=request.user
    ).select_related(
        "address",
    ).order_by(
        "-created_at",
    )


    context = {
        "orders": orders,
    }


    return render(
        request,
        "orders.html",
        context,
    )


## =========================================================
## CUSTOMER ORDER DETAIL
## =========================================================

@login_required(login_url="login")
def order_detail_view(
    request,
    order_id,
):

    order = get_object_or_404(
        Order.objects.select_related(
            "address",
            "payment",
        ).prefetch_related(
            "items__product",
        ),
        id=order_id,
        user=request.user,
    )


    context = {
        "order": order,
    }


    return render(
        request,
        "order_detail.html",
        context,
    )


## =========================================================
## CUSTOMER CANCEL ORDER
## =========================================================

@login_required(login_url="login")
@transaction.atomic
def cancel_order_view(
    request,
    order_id,
):

    if request.method != "POST":

        return redirect(
            "order-detail",
            order_id=order_id,
        )


    order = get_object_or_404(
        Order.objects.select_for_update(),
        id=order_id,
        user=request.user,
    )


    ## ## Customers may cancel orders while they are PLACED
    ## ## or CONFIRMED.
    cancellable_statuses = {
        Order.Status.PLACED,
        Order.Status.CONFIRMED,
    }


    if order.status not in cancellable_statuses:

        messages.error(
            request,
            "This order can no longer be cancelled.",
        )

        return redirect(
            "order-detail",
            order_id=order.id,
        )


    ## ## Restore stock reserved when the order was created.
    for item in order.items.select_related(
        "product"
    ).all():

        item.product.stock += item.quantity

        item.product.save(
            update_fields=[
                "stock",
            ]
        )


    order.status = Order.Status.CANCELLED

    order.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )


    messages.success(
        request,
        f"Order {order.order_number} was cancelled successfully.",
    )


    return redirect(
        "order-detail",
        order_id=order.id,
    )


## =========================================================
## WEB ADMIN ORDER LIST
## =========================================================

@login_required(login_url="management-login")
def web_admin_order_list_view(request):

    ## ## Customer must never access management orders.
    if not management_user_required(request):

        messages.error(
            request,
            "You do not have permission to access management orders.",
        )

        return redirect("home")


    ## ## Get all orders for management.
    orders = Order.objects.select_related(
        "user",
        "address",
    ).order_by(
        "-created_at",
    )


    ## ## Optional status filter.
    selected_status = request.GET.get(
        "status",
        "",
    ).strip()


    if selected_status:

        valid_statuses = [
            choice[0]
            for choice in Order.Status.choices
        ]


        if selected_status in valid_statuses:

            orders = orders.filter(
                status=selected_status
            )

        else:

            selected_status = ""


    context = {
        "orders": orders,
        "selected_status": selected_status,
        "status_choices": Order.Status.choices,
    }


    return render(
        request,
        "web_admin_orders.html",
        context,
    )


## =========================================================
## WEB ADMIN ORDER DETAIL
## =========================================================

@login_required(login_url="management-login")
def web_admin_order_detail_view(
    request,
    order_id,
):

    ## ## Customer must never access this page.
    if not management_user_required(request):

        messages.error(
            request,
            "You do not have permission to access management orders.",
        )

        return redirect("home")


    ## ## Get complete order information.
    order = get_object_or_404(
        Order.objects.select_related(
            "user",
            "address",
            "payment",
        ).prefetch_related(
            "items__product",
        ),
        id=order_id,
    )


    context = {
        "order": order,
        "status_choices": Order.Status.choices,
    }


    return render(
        request,
        "web_admin_order_detail.html",
        context,
    )


## =========================================================
## WEB ADMIN UPDATE ORDER
## =========================================================

@login_required(login_url="management-login")
def web_admin_update_order_view(
    request,
    order_id,
):

    ## ## Customer must never access this page.
    if not management_user_required(request):

        messages.error(
            request,
            "You do not have permission to update orders.",
        )

        return redirect("home")


    ## ## Only POST can update an order.
    if request.method != "POST":

        return redirect(
            "web-admin-order-detail",
            order_id=order_id,
        )


    ## ## Get order.
    order = get_object_or_404(
        Order,
        id=order_id,
    )


    ## =====================================================
    ## GET FORM DATA
    ## =====================================================

    new_status = request.POST.get(
        "status",
        "",
    ).strip()

    tracking_number = request.POST.get(
        "tracking_number",
        "",
    ).strip()

    shipping_datetime = request.POST.get(
        "shipping_datetime",
        "",
    ).strip()

    delivery_datetime = request.POST.get(
        "delivery_datetime",
        "",
    ).strip()

    estimated_delivery_date = request.POST.get(
        "estimated_delivery_date",
        "",
    ).strip()

    estimated_delivery_time = request.POST.get(
        "estimated_delivery_time",
        "",
    ).strip()


    ## =====================================================
    ## VALIDATE STATUS
    ## =====================================================

    valid_statuses = [
        choice[0]
        for choice in Order.Status.choices
    ]

    if new_status not in valid_statuses:

        messages.error(
            request,
            "Please select a valid order status.",
        )

        return management_return_redirect(
            request,
            "web-admin-order-detail",
            order_id=order.id,
        )


    ## =====================================================
    ## PARSE OPTIONAL DATE / TIME VALUES
    ## =====================================================

    from datetime import datetime

    parsed_shipping_datetime = None
    parsed_delivery_datetime = None
    parsed_estimated_date = None
    parsed_estimated_time = None


    if shipping_datetime:

        try:

            parsed_shipping_datetime = timezone.make_aware(
                datetime.strptime(
                    shipping_datetime,
                    "%Y-%m-%dT%H:%M",
                ),
                timezone.get_current_timezone(),
            )

        except ValueError:

            messages.error(
                request,
                "Enter a valid shipping date and time.",
            )

            return management_return_redirect(
                request,
                "web-admin-order-detail",
                order_id=order.id,
            )


    if delivery_datetime:

        try:

            parsed_delivery_datetime = timezone.make_aware(
                datetime.strptime(
                    delivery_datetime,
                    "%Y-%m-%dT%H:%M",
                ),
                timezone.get_current_timezone(),
            )

        except ValueError:

            messages.error(
                request,
                "Enter a valid delivery date and time.",
            )

            return management_return_redirect(
                request,
                "web-admin-order-detail",
                order_id=order.id,
            )


    if bool(estimated_delivery_date) != bool(estimated_delivery_time):

        messages.error(
            request,
            "Enter both the estimated delivery date and time.",
        )

        return management_return_redirect(
            request,
            "web-admin-order-detail",
            order_id=order.id,
        )


    if estimated_delivery_date:

        try:

            parsed_estimated_date = datetime.strptime(
                estimated_delivery_date,
                "%Y-%m-%d",
            ).date()

            parsed_estimated_time = datetime.strptime(
                estimated_delivery_time,
                "%H:%M",
            ).time()

        except ValueError:

            messages.error(
                request,
                "Enter a valid estimated delivery date and time.",
            )

            return management_return_redirect(
                request,
                "web-admin-order-detail",
                order_id=order.id,
            )


    ## =====================================================
    ## UPDATE ORDER
    ## =====================================================

    with transaction.atomic():

        old_status = order.status

        order.status = new_status


        ## =================================================
        ## TRACKING NUMBER
        ## =================================================

        order.tracking_number = tracking_number


        ## =================================================
        ## SHIPPING DATE / TIME
        ## =================================================

        if parsed_shipping_datetime is not None:

            order.shipped_at = parsed_shipping_datetime

        elif (
            new_status == Order.Status.SHIPPED
            and old_status != Order.Status.SHIPPED
            and not order.shipped_at
        ):

            order.shipped_at = timezone.now()


        ## =================================================
        ## DELIVERY DATE / TIME
        ## =================================================

        if parsed_delivery_datetime is not None:

            order.delivered_at = parsed_delivery_datetime

        elif (
            new_status == Order.Status.DELIVERED
            and old_status != Order.Status.DELIVERED
            and not order.delivered_at
        ):

            order.delivered_at = timezone.now()


        ## =================================================
        ## ESTIMATED DELIVERY DATE / TIME
        ## =====================================================

        if parsed_estimated_date is not None:

            order.estimated_delivery_date = parsed_estimated_date
            order.estimated_delivery_time = parsed_estimated_time


        ## =================================================
        ## SAVE
        ## =================================================

        order.save()


    messages.success(
        request,
        "Order updated successfully.",
    )


    return management_return_redirect(
        request,
        "web-admin-order-detail",
        order_id=order.id,
    )
