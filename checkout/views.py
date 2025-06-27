import json
import logging

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, UpdateView

from checkout.services import fulfill_checkout

from .forms import AuditOrderForm, KeywordOrderForm
from .models import Order, Service

stripe.api_key = settings.STRIPE_PRIVATE_KEY
logger = logging.getLogger(__name__)

PACKAGE_FORM_MAPPING = {
    Service.PackageType.KEYWORD: KeywordOrderForm,
    Service.PackageType.SEO_STRATEGY: AuditOrderForm,
}


@login_required(login_url=reverse_lazy("accounts:login"))
def checkout_payment(request, order_pk):
    """
    Display Stripe payment form, if the Order has not already beeen processed.
    """
    order = get_object_or_404(Order, pk=order_pk, user=request.user)

    if order.order_processed:
        logger.info(
            f"User, {request.user.id}, attempted to access a processed order, "
            f"{order.pk}."
        )
        messages.error(
            request,
            "Order already placed, please navigate to your projects to access "
            "it or create a new order.",
        )
        return redirect("core:services")

    context = {
        "order_pk": order_pk,
        "price_id": order.service.price_id,
        "stripe_pk": settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, "checkout/payment_form.html", context)


@login_required(login_url=reverse_lazy("accounts:login"))
def create_checkout_session(request):
    """
    Creates a Stripe Checkout session for an Order.

    Triggered via a POST request from the frontend (/checkout/payment_form/).
    If the provided `price_id` and user match the associated Order, this view
    creates a Stripe Checkout session required to embed Stripe's payment form.

    The `return_url` includes a placeholder ({CHECKOUT_SESSION_ID}) that Stripe
    replaces with the actual checkout session ID after a successful payment.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            price_id = data.get("price_id")
            order_pk = data.get("order_pk")

            # Ensure ownership
            order = get_object_or_404(Order, pk=order_pk, user=request.user)

            # Ensure price_id matches and hasn't been manipulated
            if price_id != order.service.price_id:
                return JsonResponse(
                    {
                        "error": "Invalid price_id. Please try again or contact "
                        "support."
                    }
                )

            absolute_url = request.build_absolute_uri(
                reverse("checkout:order_success")
            )
            session = stripe.checkout.Session.create(
                metadata={
                    "order_pk": order_pk,
                    "user_id": request.user.id,
                    "email": request.user.email,
                },
                ui_mode="embedded",
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                mode="payment",
                return_url=f"{absolute_url}?session_id={{CHECKOUT_SESSION_ID}}",
                automatic_tax={"enabled": True},
            )

        except (stripe.StripeError, json.JSONDecodeError, KeyError) as e:
            logger.error(
                f"Checkout session creation error (client secret). "
                f"Order: {order_pk}. Error: {e}"
            )
            return JsonResponse({"error": str(e)})

        return JsonResponse({"clientSecret": session.client_secret})


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handles incoming Stripe webhook events.

    Verifies the Stripe signature and processes successful checkout sessions by
    calling `fulfill_checkout`.

    Returns:
        HttpResponse:
            200 OK on successful processing,
            400 Bad Request on verification failure or processing error.
    """
    if request.method == "POST":
        payload = request.body
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            logger.error(f"Stripe webhook error (Invalid payload). Error: {e}")
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            logger.error(
                f"Stripe webhook error (Invalid signature). Error: {e}"
            )
            return HttpResponse(status=400)

        if (
            event["type"] == "checkout.session.completed"
            or event["type"] == "checkout.session.async_payment_succeeded"
        ):
            project = fulfill_checkout(event["data"]["object"]["id"])
            if not project:
                return HttpResponse(status=400)

        return HttpResponse(status=200)


@login_required(login_url=reverse_lazy("accounts:login"))
def start_order(request, package_type=None):
    """
    Redirects the user to the appropriate view to start a new Order or continue
    an existing one.

    This view is triggered when a user clicks "Buy Now" from the navigation bar
    or selects a specific service package. If an unprocessed Order already exists
    for the user, they are redirected to update it. Otherwise, a new Order flow
    is initiated.
    """
    # User selects 'buy now' from the main nav
    if not package_type:
        existing = Order.objects.filter(
            user=request.user, order_processed=False
        ).first()
        if existing:
            return redirect("checkout:update_order", existing.pk)
        return redirect(reverse("core:services") + "#services")

    # User selects a package from /services/
    service = get_object_or_404(Service, package_type=package_type)
    existing = Order.objects.filter(
        user=request.user,
        service=service,
        order_processed=False,
    ).first()

    if existing:
        return redirect("checkout:update_order", existing.pk)
    else:
        return redirect("checkout:create_order", package_type)


class OrderCreateView(LoginRequiredMixin, CreateView):
    """
    Creates a new Order.

    Redirects to the payment form after successfully saving the Order.
    """

    model = Order
    form_class = None
    service = None
    template_name = "checkout/order_form.html"

    def get_form_class(self):
        self.service = get_object_or_404(
            Service, package_type=self.kwargs["package_type"]
        )
        return PACKAGE_FORM_MAPPING.get(self.service.package_type)

    def get_initial(self):
        self.initial = {"email": self.request.user.email}
        return self.initial.copy()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["package_type"] = self.kwargs["package_type"]
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.service = self.service
        obj.user = self.request.user
        obj.save()
        return super(OrderCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "checkout:checkout_payment", args=(self.object.pk,)
        )


class OrderUpdateView(LoginRequiredMixin, UpdateView):
    """
    Updates an existing Order.

    Redirects to the payment form after successfully updating the Order.
    """

    model = Order
    form_class = None
    template_name = "checkout/order_form.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

    def get_form_class(self):
        return PACKAGE_FORM_MAPPING.get(self.object.service.package_type)

    def get_success_url(self):
        return reverse_lazy(
            "checkout:checkout_payment", args=(self.object.pk,)
        )


def order_success_view(request):
    """
    Handles the post checkout success page.

    Retrieves the Stripe session ID from the query parameters and attempts to
    fulfill the order via `fulfill_checkout`. If successful, passes the created
    Project and related context to the template.
    """
    session_id = request.GET.get("session_id")
    context = {}

    if not session_id:
        raise Http404("Session id not found.")

    project = fulfill_checkout(session_id)

    if not project:
        context["processing_payment"] = True
        return render(request, "checkout/success.html", context)

    context["project"] = project
    context["completion_date"] = project.order.expected_completion_date()
    context["project_email"] = project.admin.first().email

    return render(request, "checkout/success.html", context)
