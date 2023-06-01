from django.urls import path

from . import views
from .views import CreateOrderView

app_name = "checkout"

urlpatterns = [
    path("strategy/<pk>/", CreateOrderView.as_view(), name="strategy-landing"),
    path("project/<pk>/", CreateOrderView.as_view(), name="checkout-project"),
    path("payment/<order_pk>/", views.checkout_payment, name="checkout-payment"),
    path("payment/", views.checkout_payment, name="checkout-payment-buy-now"),
    path("stripe-webhook/", views.stripe_webhook, name="stripe"),
    path("get-payment-intent/", views.get_payment_intent, name="get-payment-intent"),
    # path('<pk>/', views.CreateCheckout.as_view(), name='create-checkout'),
]
