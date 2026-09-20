## =========================================================
## ORDERS MODELS
## =========================================================

from django.conf import settings
from django.db import models

from store.models import Product


## =========================================================
## CUSTOMER ADDRESS
## =========================================================

class Address(models.Model):

    ## ## Customer who owns this address.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
    )

    ## ## Customer name.
    name = models.CharField(
        max_length=100,
    )

    ## ## Phone number.
    phone = models.CharField(
        max_length=15,
    )

    ## ## Complete address.
    address = models.TextField()

    ## ## City.
    city = models.CharField(
        max_length=100,
    )

    ## ## State.
    state = models.CharField(
        max_length=100,
    )

    ## ## PIN code.
    pincode = models.CharField(
        max_length=10,
    )

    ## ## Default address.
    is_default = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return f"{self.name} - {self.city}"


## =========================================================
## ORDER
## =========================================================

class Order(models.Model):

    ## =====================================================
    ## ORDER STATUS
    ## =====================================================

    class Status(models.TextChoices):

        PLACED = (
            "PLACED",
            "Order Placed",
        )

        CONFIRMED = (
            "CONFIRMED",
            "Confirmed",
        )

        PROCESSING = (
            "PROCESSING",
            "Processing",
        )

        SHIPPED = (
            "SHIPPED",
            "Shipped",
        )

        OUT_FOR_DELIVERY = (
            "OUT_FOR_DELIVERY",
            "Out for Delivery",
        )

        DELIVERED = (
            "DELIVERED",
            "Delivered",
        )

        CANCELLED = (
            "CANCELLED",
            "Cancelled",
        )


    ## =====================================================
    ## PAYMENT METHODS
    ## =====================================================

    class PaymentMethod(models.TextChoices):

        ## ## Cash payment.
        COD = (
            "COD",
            "Cash on Delivery",
        )

        ## ## Customer-facing name is only Online Payment.
        ONLINE = (
            "ONLINE",
            "Online Payment",
        )


    ## =====================================================
    ## SHIPPING METHODS
    ## =====================================================

    class ShippingMethod(models.TextChoices):

        ## ## Simple shipping option for this project.
        STANDARD = (
            "STANDARD",
            "Standard Delivery",
        )


    ## =====================================================
    ## CUSTOMER
    ## =====================================================

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )


    ## =====================================================
    ## ORDER NUMBER
    ## =====================================================

    order_number = models.CharField(
        max_length=30,
        unique=True,
    )


    ## =====================================================
    ## DELIVERY ADDRESS
    ## =====================================================

    address = models.ForeignKey(
        Address,
        on_delete=models.PROTECT,
    )


    ## =====================================================
    ## PAYMENT
    ## =====================================================

    payment_method = models.CharField(
        max_length=10,
        choices=PaymentMethod.choices,
    )

    payment_status = models.CharField(
        max_length=20,
        default="PENDING",
    )


    ## =====================================================
    ## ORDER STATUS
    ## =====================================================

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PLACED,
    )


    ## =====================================================
    ## SHIPPING
    ## =====================================================

    shipping_method = models.CharField(
        max_length=20,
        choices=ShippingMethod.choices,
        default=ShippingMethod.STANDARD,
    )

    shipping_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    tracking_number = models.CharField(
        max_length=50,
        blank=True,
    )

    shipped_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    delivered_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    estimated_delivery_date = models.DateField(
        blank=True,
        null=True,
    )


    ## =====================================================
    ## ORDER TOTAL
    ## =====================================================

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )


    ## =====================================================
    ## TIMESTAMPS
    ## =====================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )


    def __str__(self):
        return self.order_number


## =========================================================
## ORDER ITEM
## =========================================================

class OrderItem(models.Model):

    ## ## Parent order.
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    ## ## Purchased product.
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
    )

    ## ## Quantity purchased.
    quantity = models.PositiveIntegerField()

    ## ## Price when order was placed.
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


## =========================================================
## PAYMENT
## =========================================================

class Payment(models.Model):

    ## ## One payment per order.
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment",
    )

    ## ## Payment method.
    method = models.CharField(
        max_length=20,
    )

    ## ## Example transaction/reference ID.
    ## ## This is NOT a real payment transaction.
    transaction_id = models.CharField(
        max_length=200,
        blank=True,
    )

    ## ## Payment amount.
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    ## ## Payment status.
    status = models.CharField(
        max_length=30,
        default="PENDING",
    )

    ## ## Payment creation time.
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.order.order_number} - {self.status}"


## =========================================================
## REVIEW
## =========================================================

class Review(models.Model):

    ## ## Product being reviewed.
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    ## ## Customer who wrote review.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    ## ## Rating.
    rating = models.PositiveIntegerField()

    ## ## Review text.
    comment = models.TextField()

    ## ## Created time.
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.product.name} - {self.rating}/5"