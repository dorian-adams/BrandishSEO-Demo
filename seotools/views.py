from django.contrib import messages
from django.shortcuts import render

from seotools.crawler import Crawler


def seo_tools(request):
    if request.method == "POST":
        website = request.POST["website"]
        keyword = request.POST["keyword"]

        page = Crawler(url=website, keyword=keyword)
        if page.conn_error:
            messages.error(request, str(page.conn_error))
            return render(request, "seotools/seo-tools.html")

        results = page.crawl_page()
        context = {"analysis": results, "keyword": page.keyword}

        return render(request, "seotools/seo-tools.html", context)
    else:
        return render(request, "seotools/seo-tools.html")
