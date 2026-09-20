from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from orders.models import Review
from .models import User


## ============================================================
## MANAGEMENT ACCESS HELPER
## ============================================================

def management_user_required(request):
    ## Only Super Admin and Web Admin can access management pages.
    return (
        request.user.is_authenticated
        and request.user.role in [
            User.Role.SUPER_ADMIN,
            User.Role.WEB_ADMIN,
        ]
    )


## ============================================================
## WEB ADMIN - REVIEW MANAGEMENT
## ============================================================

@login_required(login_url="management-login")
def web_admin_review_list_view(request):
    ## Customers cannot access management review pages.
    if not management_user_required(request):
        return HttpResponseForbidden(
            "You do not have permission to access this page."
        )

    ## Get all reviews with related product and customer information.
    reviews = Review.objects.select_related(
        "product",
        "user",
    ).order_by(
        "-created_at"
    )

    ## --------------------------------------------------------
    ## Search
    ## --------------------------------------------------------

    search_query = request.GET.get(
        "q",
        "",
    ).strip()

    if search_query:
        reviews = reviews.filter(
            Q(product__name__icontains=search_query)
            | Q(user__username__icontains=search_query)
            | Q(user__email__icontains=search_query)
            | Q(comment__icontains=search_query)
        )

    ## --------------------------------------------------------
    ## Rating Filter
    ## --------------------------------------------------------

    rating = request.GET.get(
        "rating",
        "",
    )

    if rating in ["1", "2", "3", "4", "5"]:
        reviews = reviews.filter(
            rating=int(rating)
        )

    ## --------------------------------------------------------
    ## Review Summary
    ## --------------------------------------------------------

    all_reviews = Review.objects.all()

    total_reviews = all_reviews.count()

    five_star_reviews = all_reviews.filter(
        rating=5
    ).count()

    one_star_reviews = all_reviews.filter(
        rating=1
    ).count()

    return render(
        request,
        "web_admin_reviews.html",
        {
            "reviews": reviews,
            "search_query": search_query,
            "selected_rating": rating,
            "total_reviews": total_reviews,
            "five_star_reviews": five_star_reviews,
            "one_star_reviews": one_star_reviews,
        },
    )


@login_required(login_url="management-login")
def web_admin_review_detail_view(
    request,
    review_id,
):
    ## Customers cannot access management review pages.
    if not management_user_required(request):
        return HttpResponseForbidden(
            "You do not have permission to access this page."
        )

    ## Load the requested review.
    review = get_object_or_404(
        Review.objects.select_related(
            "product",
            "user",
        ),
        id=review_id,
    )

    return render(
        request,
        "web_admin_review_detail.html",
        {
            "review": review,
        },
    )


@login_required(login_url="management-login")
def web_admin_review_delete_view(
    request,
    review_id,
):
    ## Customers cannot access management review pages.
    if not management_user_required(request):
        return HttpResponseForbidden(
            "You do not have permission to access this page."
        )

    ## Review deletion must use POST.
    if request.method != "POST":
        return redirect(
            "web-admin-reviews"
        )

    review = get_object_or_404(
        Review,
        id=review_id,
    )

    ## Store the information before deleting the record.
    product_name = review.product.name

    review.delete()

    messages.success(
        request,
        f"Review for {product_name} was deleted successfully.",
    )

    return redirect(
        "web-admin-reviews"
    )