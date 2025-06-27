from django.urls import path

from . import views
from .views import OrderCreateView, OrderUpdateView

app_name = "checkout"

urlpatterns = [
    path(
        "create-order/<int:package_type>/",
        OrderCreateView.as_view(),
        name="create_order",
    ),
    path(
        "update-order/<int:pk>/",
        OrderUpdateView.as_view(),
        name="update_order",
    ),
    path(
        "start-order/", views.start_order, name="start_order_unknown_package"
    ),
    path(
        "start-order/<int:package_type>/",
        views.start_order,
        name="start_order_with_package",
    ),
    path(
        "payment/<int:order_pk>/",
        views.checkout_payment,
        name="checkout_payment",
    ),
    path("stripe-webhook/", views.stripe_webhook, name="stripe"),
    path(
        "checkout-session/",
        views.create_checkout_session,
        name="create_checkout_session",
    ),
    path("success/", views.order_success_view, name="order_success"),
]
