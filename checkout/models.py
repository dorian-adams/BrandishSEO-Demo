from datetime import timedelta

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Service(models.Model):
    class PackageType(models.IntegerChoices):
        KEYWORD = 1, "Keyword Strategy"
        SEO_STRATEGY = 2, "SEO Strategy"
        LINK_BUILDING_STRATEGY = 3, "Link Building Strategy"

    name = models.CharField(max_length=80)
    price = models.DecimalField(
        default=0.00,
        max_digits=7,
        decimal_places=2,
        verbose_name="Price (USD)",
        validators=[MinValueValidator(0.00)],
    )
    price_id = models.CharField(max_length=35, help_text="The Stripe price id")
    package_type = models.PositiveSmallIntegerField(
        choices=PackageType.choices, unique=True
    )
    featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["package_type"]


class ServiceFeature(models.Model):
    service = models.ForeignKey(
        Service, related_name="features", on_delete=models.CASCADE
    )
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.description


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    email = models.EmailField()
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    project_name = models.CharField(max_length=20)
    project = models.OneToOneField(
        "projects.Project",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="order",
    )
    order_processed = models.BooleanField(default=False)
    order_processed_date = models.DateField(blank=True, null=True)
    order_abandoned = models.BooleanField(default=False)
    website = models.CharField(max_length=200)
    additional_info = models.TextField(blank=True)
    keywords = models.CharField(max_length=200, blank=True)
    competitor = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-order_processed_date"]

    def expected_completion_date(self):
        weeks_to_add = (
            timedelta(weeks=4)
            if self.service.package_type == Service.PackageType.SEO_STRATEGY
            else timedelta(weeks=2)
        )

        return weeks_to_add + self.order_processed_date

    def __str__(self):
        return self.project_name
