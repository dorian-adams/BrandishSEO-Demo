from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.views import (
    RedirectURLMixin,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView,
)

from checkout.models import Order
from .forms import UserRegistrationForm
from .models import User


class RegisterUserView(RedirectURLMixin, CreateView):
    template_name = "accounts/register.html"
    model = User
    form_class = UserRegistrationForm
    redirect_field_name = "next"
    next_page = "/"

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return HttpResponseRedirect(self.get_success_url())


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """Update customer/member information.  Name, e-mail, etc."""

    model = User
    fields = ["first_name", "last_name", "email"]
    template_name = "accounts/user_update_form.html"
    success_url = reverse_lazy("accounts:profile")

    def get_queryset(self):
        # Limit a user to only modifying their own data
        queryset = super(UserUpdateView, self).get_queryset()
        return queryset.filter(email=self.request.user.email)

    def get_context_data(self, **kwargs):
        # Get user id to pass as url argument for post request
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        context["pk"] = self.request.user.id
        return context


class UpdatePasswordView(SuccessMessageMixin, PasswordChangeView):
    model = User
    form_class = PasswordChangeForm
    template_name = "accounts/update_password.html"
    success_message = "Password changed successfully."
    success_url = reverse_lazy("accounts:profile")


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = "accounts/reset_password.html"
    email_template_name = "accounts/password_reset_email.html"
    success_message = "Instructions to reset your password will be sent to the email you provided. Thank you."
    success_url = reverse_lazy("accounts:profile")


class ResetPasswordConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_message = "Password updated successfully."
    success_url = reverse_lazy("accounts:profile")


@login_required()
def profile(request):
    """
    Display ``User`` basic profile information and ``Order``.
    Provided to ease navigation of multiple Orders and Projects.
    """
    orders = Order.objects.filter(user=request.user)
    context = {"orders": orders, "user": request.user}
    return render(request, "accounts/profile.html", context)
