from django.db import models


class Lead(models.Model):
    name = models.CharField(max_length=40)
    preferred_contact = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    date_of_inquiry = models.DateTimeField(auto_now_add=True)
    converted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.preferred_contact})"


class ContactAttempt(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="contact_attempts")
    date_attempted = models.DateTimeField()
    successful = models.BooleanField(default=False)