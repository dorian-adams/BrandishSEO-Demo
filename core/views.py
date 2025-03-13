from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic import FormView

from blog.models import BlogPage
from checkout.models import Service

from .forms import ContactForm, LeadForm


def index(request):
    services = Service.objects.all()
    recent_posts = BlogPage.objects.live().specific().order_by("-date")[:3]
    return render(request, "core/index.html", {"posts": recent_posts, "services": services})


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
    services = Service.objects.all().prefetch_related("features")
    form = LeadForm()

    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            return redirect("services")

    return render(
        request,
        "core/services.html",
        {"services": services, "form": form},
    )
