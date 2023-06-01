from django.contrib import messages
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView

from checkout.models import Service
from .forms import ContactForm

# from blog.models import Post


def index(request):
    # context = {'posts': Post.objects.all()[:3]}
    return render(request, "core/index.html")


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


@csrf_exempt
def services(request):
    return render(
        request,
        "core/services.html",
        {"strategy_pkg": Service.objects.get(name="SEO Test Package")},
    )
