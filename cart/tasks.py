from datetime import timedelta
from celery import shared_task
from django.db import transaction
from django.utils import timezone

from .models import Cart


@shared_task
def abandon_old_active_carts(days: int = 7) -> dict:
    cutoff = timezone.now() - timedelta(days=days)

    updated_count = Cart.objects.filter(
        status=Cart.Status.ACTIVE,
        updated_at__lt=cutoff,
    ).update(status=Cart.Status.ABANDONED)

    return {
        "abandoned_count": updated_count,
        "older_than_days": days,
    }


@shared_task
def delete_old_abandoned_carts(days: int = 30) -> dict:
    cutoff = timezone.now() - timedelta(days=days)

    deleted_count, deleted_details = Cart.objects.filter(
        status=Cart.Status.ABANDONED,
        updated_at__lt=cutoff,
    ).delete()

    return {
        "deleted_count": deleted_count,
        "deleted_details": deleted_details,
        "older_than_days": days,
    }