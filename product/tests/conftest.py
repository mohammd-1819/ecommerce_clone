import pytest


@pytest.fixture(autouse=True)
def test_media_root(settings, tmp_path):
    """
    Store factory-created test images in a temporary directory.
    Prevents factory_boy ImageField files from polluting real MEDIA_ROOT.
    """
    settings.MEDIA_ROOT = tmp_path / "media"


@pytest.fixture(autouse=True)
def locmem_cache(settings):
    """
    Your views use cached category helpers.
    This keeps tests independent from Redis.
    """
    settings.CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "test-cache",
        }
    }