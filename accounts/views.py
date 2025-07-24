from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
    RedirectURLMixin,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import CreateView, UpdateView

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
    """
    Update customer/member information.  Name, e-mail, etc.
    """

    model = User
    fields = ["first_name", "last_name", "email"]
    template_name = "accounts/user_update_form.html"
    success_url = reverse_lazy("accounts:profile")

    def get_queryset(self):
        # Limit a user to only modifying their own data
        queryset = super().get_queryset()
        return queryset.filter(email=self.request.user.email)


class UpdatePasswordView(SuccessMessageMixin, PasswordChangeView):
    model = User
    form_class = PasswordChangeForm
    template_name = "accounts/update_password.html"
    success_message = "Password updated successfully."
    success_url = reverse_lazy("accounts:profile")


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = "accounts/reset_password.html"
    email_template_name = "accounts/password_reset_email.html"
    success_message = (
        "Instructions to reset your password will be sent "
        "to the email you provided. Thank you."
    )
    success_url = reverse_lazy("accounts:profile")


class ResetPasswordConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_message = "Password updated successfully."
    success_url = reverse_lazy("accounts:login")

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        INTERNAL_RESET_SESSION_TOKEN = "_password_reset_token"

        if "uidb64" not in kwargs or "token" not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'uidb64' and 'token' parameters."
            )
        self.validlink = False
        self.user = self.get_user(kwargs["uidb64"])
        if self.user is not None:
            token = kwargs["token"]
            if token == self.reset_url_token:
                session_token = self.request.session.get(
                    INTERNAL_RESET_SESSION_TOKEN
                )
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(
                        token, self.reset_url_token
                    )
                    return HttpResponseRedirect(redirect_url)
        # Display error message and redirect
        messages.error(
            self.request,
            "The password reset link was invalid. Please submit a new "
            "password reset request by completing the form below.",
        )
        return redirect("accounts:reset_password")


@login_required()
def profile(request):
    """
    Display ``User`` basic profile information and ``Order``.
    Provided to ease navigation of multiple Orders and Projects.
    """
    orders = Order.objects.filter(user=request.user)
    context = {"orders": orders, "user": request.user}
    return render(request, "accounts/profile.html", context)
