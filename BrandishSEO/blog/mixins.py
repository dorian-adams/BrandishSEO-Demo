from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


class PaginationMixin:
    """
    Pagination functionality to be used in ``CategoryIndexPage``, and ``BlogIndexPage`` via
    ``search_results``, and ``tag_results``.
    """
    def paginate(self, request, article_filter=None):
        """
        Paginate requested articles, ``BlogPage``. Each page is set to hold 9 articles.
        :param request: The requested page.
        :param article_filter: Articles, ``BlogPage``, filtered by a specific query
        or None if no filter is to be applied - article_filter is used for ``search_results``
        and ``tag_results``.
        :return: Page objects.
        """
        page = request.GET.get("page", 1)
        if not article_filter:
            paginator = Paginator(self.get_children().live(), 9)
        else:
            paginator = Paginator(article_filter, 9)
        try:
            pages = paginator.page(page)
        except PageNotAnInteger:
            pages = paginator.page(1)
        except EmptyPage:
            pages = paginator.page(paginator.num_pages)
        return pages
