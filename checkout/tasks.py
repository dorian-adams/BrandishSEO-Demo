from celery import shared_task, task
from django.conf import settings
from django.core.mail import send_mail

from brandishseo.celery import app
from projects.models import Project


@app.task
def order_confirmation_mail(project_pk):
    project = Project.objects.get(pk=project_pk)
    user_email = project.admin.first().email
    subject = "Payment Successful. You're 4 Weeks Away from Organic Success!"
    msg = (
        "Thank you for your recent purchase at https://brandishseo.com. "
        "This e-mail is to inform you that your payment completed successfully.\n"
        "To access your project and track its status please visit: "
        "https://brandishseo.com/customer/" + str(project.slug)
    )
    mail = send_mail(subject, msg, settings.EMAIL_HOST_USER, [user_email])
    return mail
