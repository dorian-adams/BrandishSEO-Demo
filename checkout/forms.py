from django import forms

from .models import Order


class KeywordOrderForm(forms.ModelForm):
    """Order form associated with ...."""

    class Meta:
        model = Order
        fields = ["website", "email", "additional_info"]


class AuditOrderForm(forms.ModelForm):
    """Order form associated with ...."""

    class Meta:
        model = Order
        fields = [
            "project_name",
            "website",
            "email",
            "additional_info",
            "keywords",
            "competitor",
        ]
