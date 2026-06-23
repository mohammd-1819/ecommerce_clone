from itertools import count

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from cart.models import Cart, CartItem
from product.tests.factories import ProductVariantFactory


_user_counter = count(1)


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", "testpass123")

        sequence = next(_user_counter)
        fields = {field.name for field in model_class._meta.fields}
        username_field = getattr(model_class, "USERNAME_FIELD", "username")

        if username_field == "phone_number":
            kwargs.setdefault("phone_number", f"091{sequence:08d}")

        elif username_field == "email":
            kwargs.setdefault("email", f"user{sequence}@example.com")

        elif username_field == "username":
            kwargs.setdefault("username", f"user{sequence}")

        else:
            kwargs.setdefault(username_field, f"user-{sequence}")

        # Fill common optional fields if your custom user model has them.
        if "phone_number" in fields:
            kwargs.setdefault("phone_number", f"092{sequence:08d}")

        if "email" in fields:
            kwargs.setdefault("email", f"user{sequence}@example.com")

        if "username" in fields:
            kwargs.setdefault("username", f"user{sequence}")

        manager = model_class._default_manager

        if hasattr(manager, "create_user"):
            try:
                return manager.create_user(*args, password=password, **kwargs)
            except TypeError:
                pass

        user = model_class(*args, **kwargs)
        user.set_password(password)
        user.save()
        return user


class CartFactory(DjangoModelFactory):
    class Meta:
        model = Cart

    user = None
    session_key = factory.Sequence(lambda n: f"test-session-{n}")
    status = Cart.Status.ACTIVE


class CartItemFactory(DjangoModelFactory):
    class Meta:
        model = CartItem

    cart = factory.SubFactory(CartFactory)
    variant = factory.SubFactory(ProductVariantFactory)
    quantity = 1