from django.urls import path

from . import views
from .views import CreateOrderView

app_name = "checkout"

urlpatterns = [
    path("strategy/<pk>/", CreateOrderView.as_view(), name="strategy_landing"),
    path("project/<pk>/", CreateOrderView.as_view(), name="checkout_project"),
    path(
        "payment/<order_pk>/", views.checkout_payment, name="checkout_payment"
    ),
    path("payment/", views.checkout_payment, name="checkout_payment_buy_now"),
    path("stripe-webhook/", views.stripe_webhook, name="stripe"),
    path(
        "get-payment-intent/",
        views.get_payment_intent,
        name="get_payment_intent",
    ),
    # path('<pk>/', views.CreateCheckout.as_view(), name='create-checkout'),
]
