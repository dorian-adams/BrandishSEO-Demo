from django.db import models
from django.conf import settings


PACKAGE_CHOICES = (("SEO", "SEO"), ("Keyword", "Keyword"))


class Service(models.Model):
    name = models.CharField(max_length=80)
    price = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    package_type = models.CharField(choices=PACKAGE_CHOICES, max_length=7)

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email = models.EmailField()
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    project_name = models.CharField(max_length=20)
    project = models.ForeignKey(
        "projects.Project", blank=True, null=True, on_delete=models.CASCADE
    )
    order_completed = models.BooleanField(default=False)
    website = models.CharField(max_length=200)
    additional_info = models.TextField(blank=True)
    keywords = models.CharField(max_length=200, blank=True)
    competitor = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-order_completed"]

    def __str__(self):
        return self.project_name
