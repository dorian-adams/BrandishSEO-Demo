"""
Models for /blog/ - handled by Wagtail CMS.
"""

from django.db import models
from django.shortcuts import render, redirect, get_list_or_404
from django.contrib import messages
from django.conf import settings
from django.core.validators import MinLengthValidator
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, path
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.search import index
from wagtail.search.models import Query
from wagtail.snippets.models import register_snippet

from .mixins import PaginationMixin


def directory_path(instance, filename):
    """
    Helper function for Profile class - creates a path to upload a user's profile image.
    :param instance: Profile instance
    :param filename: Image file name
    :return: directory path as profiles/user/filename
    """
    return "profiles/{0}/{1}".format(instance.user, filename)


class BlogIndexPage(RoutablePageMixin, PaginationMixin, Page):
    """
    Blog home.
    """
    intro = RichTextField(help_text='Brief page description used in the intro section.')

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname='full'),
    ]

    subpage_types = ['CategoryIndexPage']

    @path('search/', name='search')
    def search_results(self, request):
        """
        Records hit to query and processes the user's search request.
        :return: Live blog articles that match the query, or None.
        """
        search_query = request.GET.get("q", None)
        if search_query:
            query = Query.get(search_query)
            query.add_hit()
            results = self.paginate(
                request,
                article_filter=Page.objects.live().type(BlogPage).search(search_query)
            )
        else:
            results = Page.objects.none()

        return self.render(
            request,
            context_overrides={
                'query': search_query,
                'posts': results,
                'search': True
            },
            template='blog/search_results.html'
        )

    @path('tags/', name='tag_results')
    def tag_results(self, request):
        """
        :return: Blog articles under a given tag.
        """
        tag = request.GET.get('tag')
        results = self.paginate(
            request,
            article_filter=get_list_or_404(BlogPage, tags__name=tag)
        )

        return self.render(
            request,
            context_overrides={
                'filter': tag,
                'posts': results,
                'tag_filter': True
            },
            template='blog/tag_results.html'
        )

    def get_context(self, request, *args, **kwargs):
        """
        Get posts, organized by category.
        Used to display the three most recent posts for each category.
        :return: List of dictionaries. Each dict contains a category and the three most recent posts
        for that category.
        """
        context = super(BlogIndexPage, self).get_context(request)
        if request.path.strip('/') == self.slug:  # Only apply to the blog home, /blog/.
            context['posts_per_category'] = [
                {
                    'category': category,
                    'posts': category.get_children().live().order_by('-first_published_at')[:3]
                }
                for category in self.get_children().live()
            ]

        return context


class CategoryIndexPage(PaginationMixin, Page):
    """
    Blog category. Hosts all child pages (articles) of a particular topic/category.
    """
    intro = RichTextField(help_text='Brief page description used in the intro section.')

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname='full'),
    ]

    parent_page_types = ['BlogIndexPage']
    subpage_types = ['BlogPage']

    def get_context(self, request, *args, **kwargs):
        """
        :return: Paginated posts for the given Category.
        """
        context = super(CategoryIndexPage, self).get_context(request)
        posts = self.paginate(request)
        context["posts"] = posts
        return context

    class Meta:
        verbose_name_plural = 'Blog categories'


class BlogPageTag(TaggedItemBase):
    """
    A tag model - attaches tagging system to ``BlogPage``.
    """
    content_object = ParentalKey(
        'BlogPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )


class BlogPage(Page):
    """
    BlogPage / articles model.
    """
    date = models.DateField("Post date")
    snippet = models.CharField(max_length=250, help_text='Excerpt used in article list preview card.')
    body = RichTextField(blank=True)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    featured_image = models.ImageField(upload_to='blog_pics')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    featured_article = models.BooleanField(default=False)

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('tags'),
        ], heading='Blog Information'),
        FieldPanel('snippet'),
        FieldPanel('featured_image'),
        FieldPanel('body'),
        FieldPanel('author'),
        InlinePanel('page_comments', label='Comments')
    ]

    search_fields = Page.search_fields + [
        index.SearchField('body')
    ]

    parent_page_types = ['CategoryIndexPage']
    subpage_types = []

    def serve(self, request, *args, **kwargs):
        """
        Method override to handle POST conditions for blog comments, ``BlogComment``.
        """
        from .forms import CommentForm

        if request.method == 'POST':
            form = CommentForm(request.POST)
            if form.is_valid():
                new_comment = form.save(commit=False)
                new_comment.user = request.user
                new_comment.page = self
                new_comment.save()
                messages.success(request, 'Your message was successfully '
                                          'submitted and is awaiting moderation. '
                                          'Thank you for contributing!')
                return redirect(self.get_url())
        else:
            form = CommentForm

        return render(request, 'blog/blog_page.html', {
            'page': self,
            'form': form
        })


@register_snippet
class BlogComment(models.Model):
    """
    A model for applying article comments to ``BlogPage``.
    """
    page = ParentalKey(
        'BlogPage', on_delete=models.CASCADE, related_name='page_comments'
    )
    text = models.TextField(
        validators=[MinLengthValidator(3, "Comment must be greater than 3 characters.")]
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='comment_author'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)

    panels = [
        FieldPanel('page'),
        FieldPanel('text'),
        FieldPanel('user'),
        FieldPanel('is_approved')
    ]

    def __str__(self):
        text = self.text if len(self.text) < 15 else self.text[:15] + '...'
        return '"{0}" on Page: {1}'.format(text, self.page)


@register_snippet
class Profile(models.Model):
    """
    User profile model, used to associate a custom profile image with a user.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    profile_image = models.ImageField(upload_to=directory_path)

    panels = [
        FieldPanel('user'),
        FieldPanel('profile_image')
    ]

    def __str__(self):
        return self.user

    class Meta:
        verbose_name_plural = 'Author profiles'
