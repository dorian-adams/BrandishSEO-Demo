from django.conf import settings


def test_stripe_keys():
    stripe_secret_key = settings.STRIPE_PRIVATE_KEY
    stripe_pub_key = settings.STRIPE_PUBLIC_KEY
    assert stripe_secret_key.startswith("sk_")
    assert stripe_pub_key.startswith("pk_")
