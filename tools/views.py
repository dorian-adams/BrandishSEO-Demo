from django.shortcuts import render
from .utils import PageAnalyzer


def seo_tools(request):
    if request.method == "POST":
        website = request.POST["website"]
        keyword = request.POST["keyword"]

        seo = PageAnalyzer(website, keyword)
        context = {"analysis": True, "errors": seo.results}

        return render(request, "tools/seo-tools.html", context)
    else:
        return render(request, "tools/seo-tools.html")
