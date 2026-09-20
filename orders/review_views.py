from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .models import Review
from store.models import Product
from accounts.models import User


## ============================================================
## CUSTOMER ACCESS HELPER
## ============================================================

def customer_required(request):
    ## Only logged-in customers can submit reviews.
    return (
        request.user.is_authenticated
        and request.user.role == User.Role.CUSTOMER
    )


## ============================================================
## CUSTOMER - ADD REVIEW
## ============================================================

@login_required(login_url="login")
def add_review_view(request, product_id):

    ## --------------------------------------------------------
    ## Check customer access.
    ## --------------------------------------------------------

    if not customer_required(request):

        return HttpResponseForbidden(
            "Only customers can submit product reviews."
        )


    ## --------------------------------------------------------
    ## Get active product.
    ## --------------------------------------------------------

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
    )


    ## --------------------------------------------------------
    ## Check whether the customer already reviewed
    ## this product.
    ## --------------------------------------------------------

    existing_review = Review.objects.filter(
        product=product,
        user=request.user,
    ).first()


    ## --------------------------------------------------------
    ## Prevent duplicate review.
    ## --------------------------------------------------------

    if existing_review:

        messages.info(
            request,
            "You have already reviewed this product.",
        )

        return redirect(
            "product-detail",
            product_id=product.id,
        )


    ## ========================================================
    ## POST - SUBMIT REVIEW
    ## ========================================================

    if request.method == "POST":

        ## ----------------------------------------------------
        ## Get submitted rating.
        ## ----------------------------------------------------

        rating = request.POST.get(
            "rating",
            "",
        ).strip()


        ## ----------------------------------------------------
        ## Get submitted comment.
        ## ----------------------------------------------------

        comment = request.POST.get(
            "comment",
            "",
        ).strip()


        ## ----------------------------------------------------
        ## Validate rating.
        ## ----------------------------------------------------

        if rating not in [
            "1",
            "2",
            "3",
            "4",
            "5",
        ]:

            messages.error(
                request,
                "Please select a rating from 1 to 5.",
            )

            return render(
                request,
                "review_form.html",
                {
                    "product": product,
                    "rating": rating,
                    "comment": comment,
                },
            )


        ## ----------------------------------------------------
        ## Validate comment.
        ## ----------------------------------------------------

        if not comment:

            messages.error(
                request,
                "Please write a review comment.",
            )

            return render(
                request,
                "review_form.html",
                {
                    "product": product,
                    "rating": rating,
                    "comment": comment,
                },
            )


        ## ----------------------------------------------------
        ## Maximum comment length.
        ## ----------------------------------------------------

        if len(comment) > 1000:

            messages.error(
                request,
                "Review comment cannot exceed 1000 characters.",
            )

            return render(
                request,
                "review_form.html",
                {
                    "product": product,
                    "rating": rating,
                    "comment": comment,
                },
            )


        ## ----------------------------------------------------
        ## Create review.
        ## ----------------------------------------------------

        Review.objects.create(
            product=product,
            user=request.user,
            rating=int(rating),
            comment=comment,
        )


        ## ----------------------------------------------------
        ## Success message.
        ## ----------------------------------------------------

        messages.success(
            request,
            "Your review has been submitted successfully.",
        )


        ## ----------------------------------------------------
        ## Return to product detail.
        ## ----------------------------------------------------

        return redirect(
            "product-detail",
            product_id=product.id,
        )


    ## ========================================================
    ## GET - SHOW REVIEW FORM
    ## ========================================================

    return render(
        request,
        "review_form.html",
        {
            "product": product,
            "rating": "",
            "comment": "",
        },
    )