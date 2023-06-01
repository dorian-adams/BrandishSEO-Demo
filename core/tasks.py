from django.conf import settings
from django.core.mail import send_mail

from brandishseo.celery import app


@app.task
def send_contact_form(subject, msg):
    mail = send_mail(
        subject, msg, settings.EMAIL_HOST_USER, [settings.RECIPIENT_ADDRESS]
    )
    return mail
