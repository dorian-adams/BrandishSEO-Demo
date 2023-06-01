from django.contrib import messages
from django.shortcuts import render
from django.views.generic import FormView

from checkout.models import Service
from blog.models import BlogPage
from .forms import ContactForm


def index(request):
    recent_posts = BlogPage.objects.live().specific().order_by("-date")[:3]
    return render(request, "core/index.html", {"posts": recent_posts})


class ContactView(FormView):
    template_name = "core/contact.html"
    form_class = ContactForm
    success_url = "/contact/"

    def form_valid(self, form):
        form.send()
        messages.success(self.request, "Email sent successfully!")
        return super().form_valid(form)


def about(request):
    return render(request, "core/about.html")


def services(request):
    return render(
        request,
        "core/services.html",
        {"strategy_pkg": Service.objects.get(package_type="SEO")},
    )
