"""
Provides pagination for Page models.
"""

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


def paginate_posts(request, queryset):
    """
    Paginate blog posts, ``BlogPage``. Each page is set to hold 9 posts.

    NOTE: Meta class ordering is not supported in Wagtail. Thus, the queryset should
    be ordered as desired prior to pagination.

    :param request: Django request object.
    :param queryset: An ordered queryset of blog posts, ``BlogPage``, to be paginated.
    :return: Paginated queryset.
    :rtype: paginator
    """
    page = request.GET.get("page", 1)
    paginator = Paginator(queryset, 9)

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return posts
