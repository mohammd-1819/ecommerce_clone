from django.db.models import Sum
from .models import Cart


def cart_counter(request):
    count = 0

    if request.user.is_authenticated:
        count = (
            Cart.objects
            .filter(user=request.user, status=Cart.Status.ACTIVE)
            .aggregate(total=Sum("items__quantity"))
            .get("total")
            or 0
        )
    else:
        session_key = request.session.session_key

        if session_key:
            count = (
                Cart.objects
                .filter(session_key=session_key, status=Cart.Status.ACTIVE)
                .aggregate(total=Sum("items__quantity"))
                .get("total")
                or 0
            )

    return {
        "cart_items_count": count
    }