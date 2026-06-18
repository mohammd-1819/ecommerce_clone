from django.db import models

from core.models import TimeStampedModel


class ContactRequest(TimeStampedModel):
    class RequestType(models.TextChoices):
        PRODUCT_QUESTION = "product_question", "سؤال درباره محصول"
        ORDER_FOLLOWUP = "order_followup", "پیگیری سفارش"
        WHOLESALE = "wholesale", "خرید عمده"
        CONSULTATION = "consultation", "مشاوره خرید"
        OTHER = "other", "سایر"

    class Status(models.TextChoices):
        NEW = "new", "جدید"
        IN_PROGRESS = "in_progress", "در حال بررسی"
        ANSWERED = "answered", "پاسخ داده شده"
        CLOSED = "closed", "بسته شده"

    first_name = models.CharField(max_length=140, verbose_name="نام")
    last_name = models.CharField(max_length=140, verbose_name="نام خانوادگی")
    phone = models.CharField(max_length=20, verbose_name="شماره تماس")
    email = models.EmailField(blank=True, verbose_name="ایمیل")

    request_type = models.CharField(
        max_length=40,
        choices=RequestType.choices,
        default=RequestType.OTHER,
        verbose_name="نوع درخواست",
    )
    subject = models.CharField(max_length=180, verbose_name="موضوع پیام")
    message = models.TextField(verbose_name="متن پیام")

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.NEW,
        db_index=True,
        verbose_name="وضعیت",
    )

    class Meta:
        verbose_name = "درخواست تماس"
        verbose_name_plural = "درخواست‌های تماس"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.subject}"