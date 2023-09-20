import json
import stripe
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView

from projects.models import Project
from .models import Service, Order
from .forms import AuditOrderForm, KeywordOrderForm
from .tasks import order_confirmation_mail

stripe.api_key = settings.STRIPE_PRIVATE_KEY


@login_required(login_url=reverse_lazy("accounts:login"))
def checkout_payment(request, order_pk=None):
    if order_pk is None:
        # Get eligible Projects when the Project pk is not given
        # Occurs when user directly accesses the url or 'Buy Now' buttons in nav
        orders = Order.objects.filter(user=request.user, order_completed=False)

        if len(orders) > 1:
            # If the user has multiple Projects that can be checked out
            # Redirect to user's profile page, so they can select specific
            # Project to check out
            return HttpResponseRedirect(reverse("projects:profile"))
        elif len(orders) == 0:
            # If the user does not have any Projects eligible for checkout
            # Redirect to services page to initiate purchase
            return HttpResponseRedirect(reverse("core:services") + "#services")
        else:
            # Else, the user has a single Project ready for payment
            order = orders[0]
    else:
        order = get_object_or_404(Order, pk=order_pk)

    receipt_email = order.email

    context = {"order": order, "email": receipt_email}
    return render(request, "checkout/payment.html", context)


def get_payment_intent(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            order = Order.objects.get(pk=data["order"]["pk"])
            intent = stripe.PaymentIntent.create(
                amount=int(order.service.price * 100),
                currency="usd",
                automatic_payment_methods={
                    "enabled": True,
                },
                metadata={
                    "order_pk": order.pk,
                    "website": order.website,
                    "email": order.email,
                },
            )
            return JsonResponse({"clientSecret": intent["client_secret"]})
        except Exception as e:
            return JsonResponse({"error": str(e)})


@csrf_exempt
def stripe_webhook(request):
    if request.method == "POST":
        payload = request.body
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)

        session = event["data"]["object"]
        order_pk = session["metadata"]["order_pk"]
        customer_email = session["metadata"]["email"]
        order = get_object_or_404(Order, pk=order_pk)

        if event.type == "payment_intent.succeeded":
            if order.service.package_type == "SEO":
                project = Project(
                    service=order.service,
                    project_name=order.project_name,
                    website=order.website,
                    description=order.additional_info,
                    keywords=order.keywords,
                    competitor=order.competitor,
                )
                project.save()
                project.admin.add(order.user)
                project.members.add(order.user)
                project.save()

                order.project = project
                order.order_completed = True
                order.save()

                # Send success confirmation email
                order_confirmation_mail.delay(project.pk)

        elif event.type == "payment_intent.payment_failed":
            pass

        return HttpResponse(status=200)


class CreateOrderView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = None
    service = None
    template_name = "checkout/strategy_landing.html"

    def get_form_class(self):
        self.service = get_object_or_404(Service, pk=self.kwargs["pk"])
        if self.service.package_type == "SEO":
            return AuditOrderForm
        return KeywordOrderForm

    def get_initial(self):
        self.initial = {"email": self.request.user.email}
        return self.initial.copy()

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.service = self.service
        obj.user = self.request.user
        obj.save()
        return super(CreateOrderView, self).form_valid(form)

    def form_invalid(self, form):
        try:
            # If user tries to check out existing order
            order = Order.objects.get(website=form.instance.website)
            return reverse_lazy("checkout:checkout_payment", args=(order.object.pk,))
        except:
            return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy("checkout:checkout_payment", args=(self.object.pk,))
