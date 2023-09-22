from django.contrib import admin

from .models import Order, Service

admin.site.register(Service)
admin.site.register(Order)
