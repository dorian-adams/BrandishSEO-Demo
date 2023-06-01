from django import forms
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox

from .tasks import send_contact_form


class ContactForm(forms.Form):
    form_class = {"class": "form-control form-control-lg"}
    name = forms.CharField(
        max_length=75,
        widget=forms.TextInput(attrs={"placeholder": "Your name", **form_class}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"placeholder": "email@example.com", **form_class}
        )
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "data-toggle": "autosize",
                "placeholder": "Tell us a few words ...",
                "rows": "3",
                **form_class,
            }
        )
    )
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    def send(self):
        cleaned_data = super().clean()
        subject = "Contact Form, from: " + cleaned_data.get("name")
        msg = "Email: " + cleaned_data.get("email") + "\n" + cleaned_data.get("message")
        send_contact_form.delay(subject, msg)
