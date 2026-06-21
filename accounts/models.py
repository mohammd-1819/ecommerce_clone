from django.db.models import TextChoices
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from core.models import TimeStampedModel

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number is required")
        user = self.model(phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = PhoneNumberField(
        unique=True, region="IR")  # store E.164 (+98...)
    username = models.CharField(_('username'), max_length=150, blank=True, default="")
    password = models.CharField(_("password"), max_length=200, blank=True, default="")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    otp_code = models.CharField(max_length=5, null=True, blank=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)
    otp_max_try = models.IntegerField(default=3)
    otp_max_out = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []  # prompts only for phone + password in createsuperuser

    objects = UserManager()

    def __str__(self):
        return str(self.phone_number)

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'


class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر', related_name='addresses')
    title = models.CharField(max_length=255, verbose_name='نام انتخابی', null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='نام و نام خانوادگی تحویل گیرنده')
    phone_number = models.CharField(max_length=11, null=True, blank=True, verbose_name='شماره تلفن تحویل گیرنده')
    zip_code = models.CharField(max_length=10, verbose_name='کد پستی', null=True, blank=True)
    province = models.CharField(max_length=255, blank=True, null=True, verbose_name='استان')
    city = models.CharField(max_length=255, blank=True, null=True, verbose_name='شهر')
    postal_address = models.CharField(max_length=255, blank=True, null=True, verbose_name='آدرس پستی')
    plaque_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='پلاک')
    unit = models.CharField(max_length=100, blank=True, null=True, verbose_name='واحد')

    def __str__(self):
        return f"{self.user.phone_number} - آدرس"

    class Meta:
        verbose_name = 'آدرس کاربر'
        verbose_name_plural = 'آدرس های کاربر'



class UserProfile(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("کاربر")
    )

    first_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name=_("نام")
    )

    last_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name=_("نام خانوادگی")
    )

    email = models.EmailField(
        max_length=254,
        blank=True,
        default="",
        verbose_name=_("ایمیل")
    )


    def __str__(self):
        full_name = self.get_full_name()
        return full_name or str(self.user.phone_number)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    class Meta:
        verbose_name = _("پروفایل کاربر")
        verbose_name_plural = _("پروفایل کاربران")