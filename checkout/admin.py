from django.contrib import admin

from .models import Order, Service, ServiceFeature

admin.site.register(Order)


class FeatureInline(admin.TabularInline):
    model = ServiceFeature
    extra = 1


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "package_type")
    inlines = [FeatureInline]
