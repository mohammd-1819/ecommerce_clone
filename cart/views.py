from django.shortcuts import render
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import TemplateView, View

from product.models import ProductVariant

from .models import Cart, CartItem



SESSION_CART_ID = "anonymous_cart_id"
MAX_CART_ITEM_QUANTITY = 20
TAX_PERCENT = 10


def _wants_json(request):
    return (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or "application/json" in request.headers.get("accept", "")
    )


def _safe_redirect_url(request, fallback_url_name="cart:cart-detail"):
    fallback = reverse(fallback_url_name)
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER")

    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url

    return fallback


def _ensure_session_key(request):
    """
    Anonymous carts need a stable session_key.
    Django may not create one until the session is saved/modified.
    """
    if not request.session.session_key:
        request.session.create()

    return request.session.session_key


def _merge_cart_items(source_cart, target_cart):
    """
    Move all items from source_cart into target_cart.
    If the same variant exists in target_cart, quantities are added.
    """
    if not source_cart or not target_cart or source_cart.pk == target_cart.pk:
        return target_cart

    source_items = source_cart.items.select_for_update().select_related("variant")

    for source_item in source_items:
        target_item, created = CartItem.objects.select_for_update().get_or_create(
            cart=target_cart,
            variant=source_item.variant,
            defaults={
                "quantity": min(source_item.quantity, MAX_CART_ITEM_QUANTITY),
            },
        )

        if not created:
            target_item.quantity = min(
                target_item.quantity + source_item.quantity,
                MAX_CART_ITEM_QUANTITY,
            )
            target_item.save(update_fields=["quantity", "updated_at"])

    source_cart.status = Cart.Status.ABANDONED
    source_cart.session_key = ""
    source_cart.save(update_fields=["status", "session_key", "updated_at"])

    return target_cart


def _get_session_cart_id(request):
    cart_id = request.session.get(SESSION_CART_ID)

    try:
        return int(cart_id)
    except (TypeError, ValueError):
        return None


def _remember_anonymous_cart(request, cart):
    request.session[SESSION_CART_ID] = cart.pk
    request.session.modified = True


def _forget_anonymous_cart(request):
    if SESSION_CART_ID in request.session:
        request.session.pop(SESSION_CART_ID, None)
        request.session.modified = True


def get_active_cart(request, *, create=False, lock=False):
    """
    Returns the current active cart for both authenticated and anonymous users.

    Why we store anonymous_cart_id in the session:
    Django may change the session_key during login, so looking up the anonymous
    cart only by session_key can fail after authentication.
    """
    cart_qs = Cart.objects
    if lock:
        cart_qs = cart_qs.select_for_update()

    session_key = request.session.session_key
    session_cart_id = _get_session_cart_id(request)

    if request.user.is_authenticated:
        anonymous_cart = None

        # First try by cart id stored in session.
        if session_cart_id:
            anonymous_cart = (
                cart_qs.filter(
                    pk=session_cart_id,
                    status=Cart.Status.ACTIVE,
                    user__isnull=True,
                )
                .prefetch_related("items")
                .first()
            )

        # Fallback for older anonymous carts created before this fix.
        if not anonymous_cart and session_key:
            anonymous_cart = (
                cart_qs.filter(
                    status=Cart.Status.ACTIVE,
                    user__isnull=True,
                    session_key=session_key,
                )
                .prefetch_related("items")
                .first()
            )

        user_cart = (
            cart_qs.filter(
                status=Cart.Status.ACTIVE,
                user=request.user,
            )
            .prefetch_related("items")
            .first()
        )

        # Existing user cart + anonymous cart: merge anonymous into user cart.
        if user_cart and anonymous_cart:
            merged_cart = _merge_cart_items(anonymous_cart, user_cart)
            _forget_anonymous_cart(request)
            return merged_cart

        # No user cart, but there is an anonymous cart: assign it to the user.
        if anonymous_cart and not user_cart:
            anonymous_cart.user = request.user
            anonymous_cart.session_key = ""
            anonymous_cart.save(update_fields=["user", "session_key", "updated_at"])
            _forget_anonymous_cart(request)
            return anonymous_cart

        # Existing user cart only.
        if user_cart:
            _forget_anonymous_cart(request)
            return user_cart

        if create:
            _forget_anonymous_cart(request)
            return Cart.objects.create(
                user=request.user,
                status=Cart.Status.ACTIVE,
            )

        return None

    # Anonymous user.
    if not session_key:
        if not create:
            return None
        session_key = _ensure_session_key(request)

    anonymous_cart = None

    # Prefer cart id from session.
    if session_cart_id:
        anonymous_cart = (
            cart_qs.filter(
                pk=session_cart_id,
                status=Cart.Status.ACTIVE,
                user__isnull=True,
            )
            .prefetch_related("items")
            .first()
        )

    # Fallback to session_key.
    if not anonymous_cart:
        anonymous_cart = (
            cart_qs.filter(
                status=Cart.Status.ACTIVE,
                user__isnull=True,
                session_key=session_key,
            )
            .prefetch_related("items")
            .first()
        )

    if anonymous_cart:
        _remember_anonymous_cart(request, anonymous_cart)
        return anonymous_cart

    if create:
        anonymous_cart = Cart.objects.create(
            user=None,
            session_key=session_key,
            status=Cart.Status.ACTIVE,
        )
        _remember_anonymous_cart(request, anonymous_cart)
        return anonymous_cart

    return None


def _cart_totals(cart):
    if not cart:
        return {
            "items_count": 0,
            "subtotal_toman": 0,
            "tax_toman": 0,
            "final_toman": 0,
            "is_empty": True,
        }

    items = list(cart.items.select_related("variant"))
    items_count = sum(item.quantity for item in items)
    subtotal_toman = sum(item.line_total_toman for item in items)
    tax_toman = subtotal_toman * TAX_PERCENT // 100
    final_toman = subtotal_toman + tax_toman

    return {
        "items_count": items_count,
        "subtotal_toman": subtotal_toman,
        "tax_toman": tax_toman,
        "final_toman": final_toman,
        "is_empty": items_count == 0,
    }


def _cart_json_response(cart, *, item=None, item_removed=False, status=200):
    payload = _cart_totals(cart)

    if item and not item_removed:
        payload["item"] = {
            "id": item.pk,
            "variant_id": item.variant_id,
            "quantity": item.quantity,
            "unit_price_toman": item.unit_price_toman,
            "line_total_toman": item.line_total_toman,
            "removed": False,
        }
    elif item_removed:
        payload["item"] = {
            "removed": True,
        }

    return JsonResponse(payload, status=status)


def _parse_positive_int(value, *, default=1, minimum=1, maximum=MAX_CART_ITEM_QUANTITY):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return default

    if value < minimum:
        return minimum

    if value > maximum:
        return maximum

    return value


class CartDetailView(TemplateView):
    template_name = "cart/cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        with transaction.atomic():
            cart = get_active_cart(self.request, create=False, lock=True)

        items = list(cart.items.select_related("variant")) if cart else []

        items_count = sum(item.quantity for item in items)
        subtotal_toman = sum(item.line_total_toman for item in items)
        tax_toman = subtotal_toman * TAX_PERCENT // 100
        final_toman = subtotal_toman + tax_toman

        context.update(
            {
                "cart": cart,
                "cart_items": items,
                "items_count": items_count,
                "subtotal_toman": subtotal_toman,
                "tax_toman": tax_toman,
                "final_toman": final_toman,
                "is_cart_empty": items_count == 0,
                "tax_percent": TAX_PERCENT,
            }
        )

        return context


class AddToCartView(View):
    """
    POST accepted:
      - URL variant_id, or POST variant_id
      - quantity, optional, default 1
    """

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        variant_id = kwargs.get("variant_id") or request.POST.get("variant_id")
        variant = get_object_or_404(ProductVariant, pk=variant_id)

        if not variant.is_in_stock:
            if _wants_json(request):
                return JsonResponse(
                    {"detail": "This product variant is not available."},
                    status=400,
                )

            messages.error(request, "این تنوع محصول در حال حاضر موجود نیست.")
            return redirect(_safe_redirect_url(request))

        quantity = _parse_positive_int(request.POST.get("quantity"), default=1)

        cart = get_active_cart(request, create=True, lock=True)

        item, created = CartItem.objects.select_for_update().get_or_create(
            cart=cart,
            variant=variant,
            defaults={
                "quantity": quantity,
            },
        )

        if not created:
            item.quantity = min(item.quantity + quantity, MAX_CART_ITEM_QUANTITY)
            item.save(update_fields=["quantity", "updated_at"])

        if _wants_json(request):
            return _cart_json_response(cart, item=item)

        messages.success(request, "محصول به سبد خرید اضافه شد.")
        return redirect(_safe_redirect_url(request))


class UpdateCartItemQuantityView(View):
    """
    Use this for plus/minus buttons or direct quantity input.

    POST options:
      1. quantity=3       -> set exact quantity
      2. delta=1          -> increase by 1
      3. delta=-1         -> decrease by 1
      4. action=increase  -> increase by 1
      5. action=decrease  -> decrease by 1

    If final quantity <= 0, the item is automatically deleted.
    """

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        variant_id = kwargs.get("variant_id") or request.POST.get("variant_id")
        variant = get_object_or_404(ProductVariant, pk=variant_id)

        cart = get_active_cart(request, create=True, lock=True)

        item = (
            CartItem.objects.select_for_update()
            .filter(cart=cart, variant=variant)
            .first()
        )

        quantity_value = request.POST.get("quantity")
        delta_value = request.POST.get("delta")
        action = request.POST.get("action")

        if quantity_value is not None:
            try:
                new_quantity = int(quantity_value)
            except ValueError:
                new_quantity = item.quantity if item else 1

        elif delta_value is not None:
            try:
                delta = int(delta_value)
            except ValueError:
                delta = 0

            current_quantity = item.quantity if item else 0
            new_quantity = current_quantity + delta

        elif action == "increase":
            current_quantity = item.quantity if item else 0
            new_quantity = current_quantity + 1

        elif action == "decrease":
            current_quantity = item.quantity if item else 0
            new_quantity = current_quantity - 1

        else:
            if _wants_json(request):
                return JsonResponse(
                    {"detail": "quantity, delta, or action is required."},
                    status=400,
                )

            messages.error(request, "درخواست تغییر تعداد نامعتبر است.")
            return redirect(_safe_redirect_url(request))

        if new_quantity <= 0:
            if item:
                item.delete()

            if _wants_json(request):
                return _cart_json_response(cart, item_removed=True)

            messages.success(request, "محصول از سبد خرید حذف شد.")
            return redirect(_safe_redirect_url(request))

        new_quantity = min(new_quantity, MAX_CART_ITEM_QUANTITY)

        if item:
            item.quantity = new_quantity
            item.save(update_fields=["quantity", "updated_at"])
        else:
            item = CartItem.objects.create(
                cart=cart,
                variant=variant,
                quantity=new_quantity,
            )

        if _wants_json(request):
            return _cart_json_response(cart, item=item)

        messages.success(request, "تعداد محصول به‌روزرسانی شد.")
        return redirect(_safe_redirect_url(request))


class RemoveFromCartView(View):
    """
    Deletes the item completely from the cart, regardless of quantity.
    """

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        variant_id = kwargs.get("variant_id") or request.POST.get("variant_id")

        cart = get_active_cart(request, create=False, lock=True)

        if not cart:
            if _wants_json(request):
                return _cart_json_response(None, item_removed=True)

            messages.info(request, "سبد خرید شما خالی است.")
            return redirect(_safe_redirect_url(request))

        deleted_count, _ = CartItem.objects.select_for_update().filter(
            cart=cart,
            variant_id=variant_id,
        ).delete()

        if _wants_json(request):
            return _cart_json_response(cart, item_removed=True)

        if deleted_count:
            messages.success(request, "محصول از سبد خرید حذف شد.")
        else:
            messages.info(request, "این محصول در سبد خرید وجود نداشت.")

        return redirect(_safe_redirect_url(request))


