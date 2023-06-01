"""
Page models for Wagtail CMS.
"""

import urllib.parse
from django.db import models
from django.shortcuts import render, redirect
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

from accounts.models import UserProfile
from .paginator import paginate_posts
from .edit_handlers import AuthorPanel
from .validators import validate_twitter_handle


class BlogIndexPage(RoutablePageMixin, Page):
    """
    Root page representing the blog's home, /blog/.

    Responsible for serving search and taggable results via routable sub-URLs through
    ``search_results()`` and ``tag_results()``, respectively. On the default route, it
    gets and serves the latest three blog posts, from every ``CategoryIndexPage``.
    """

    intro = RichTextField(help_text="Brief page description used in the intro section.")

    content_panels = Page.content_panels + [
        FieldPanel("intro", classname="full"),
    ]

    max_count = 1  # Singleton class

    subpage_types = ["CategoryIndexPage"]

    @path("search/", name="search")
    def search_results(self, request):
        """
        Logs the query and processes the user's search request.
        Search results are returned as a paginator.
        """
        search_query = request.GET.get("q", None)
        if search_query:
            query = Query.get(search_query)
            query.add_hit()

        results = paginate_posts(
            request,
            queryset=BlogPage.objects.live().order_by("-date").search(search_query),
        )

        return self.render(
            request,
            context_overrides={"query": search_query, "posts": results, "search": True},
            template="blog/search_results.html",
        )

    @path("tags/", name="tag_results")
    def tag_results(self, request):
        """
        Get all posts under a given tag.
        Tag results are returned as a paginator.
        """
        tag = request.GET.get("tag")
        results = paginate_posts(
            request,
            queryset=BlogPage.objects.live().order_by("-date").filter(tags__name=tag),
        )

        return self.render(
            request,
            context_overrides={"tag": tag, "posts": results, "tag_filter": True},
            template="blog/tag_results.html",
        )

    def get_context(self, request, *args, **kwargs):
        """
        Provides additional context for the default route only, /blog/.

        Get the latest three posts from every category, returned as a list
        of dictionaries.
        """
        context = super().get_context(request)
        if request.path.strip("/") == self.slug:  # Only apply to the blog home, /blog/.
            context["posts_per_category"] = [
                {
                    "category": category,
                    "posts": category.specific.get_recent_posts(),
                }  # returns 3 posts each
                for category in self.get_children().live()
            ]

        return context


class CategoryIndexPage(Page):
    """
    Represents category pages of the blog, /blog/category/.

    Responsible for serving all posts, ``BlogPage``, associated with the category.
    """

    intro = RichTextField(help_text="Brief page description used in the intro section.")

    content_panels = Page.content_panels + [
        FieldPanel("intro", classname="full"),
    ]

    parent_page_types = ["BlogIndexPage"]
    subpage_types = ["BlogPage"]

    def get_context(self, request, *args, **kwargs):
        """
        Add all posts associated with the category to context.
        The categories posts are returned as a paginator.
        """
        context = super().get_context(request)
        posts = paginate_posts(
            request, BlogPage.objects.child_of(self).live().specific().order_by("-date")
        )
        context["posts"] = posts
        return context

    def get_recent_posts(self):
        """
        Allows ``BlogIndexPage`` to get recent posts from every category.
        :return: The three most recent posts from the category, ordered by -date.
        :rtype: queryset
        """
        return BlogPage.objects.child_of(self).live().specific().order_by("-date")[:3]

    class Meta:
        verbose_name_plural = "Blog categories"


class BlogPageTag(TaggedItemBase):
    """
    Attaches tagging to ``BlogPage``.
    """

    content_object = ParentalKey(
        "blog.BlogPage", related_name="tagged_items", on_delete=models.CASCADE
    )


class BlogPage(Page):
    """
    Represents blog posts, /blog/category/post.

    ``author`` must have an ``AuthorProfile``.
    """

    date = models.DateField("Post date")
    snippet = models.CharField(
        max_length=200, help_text="Excerpt used in article list preview card."
    )
    body = RichTextField(blank=True)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    featured_image = models.ForeignKey("wagtailimages.Image", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    featured_article = models.BooleanField(default=False)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("date"),
                FieldPanel("tags"),
            ],
            heading="Blog Information",
        ),
        FieldPanel("snippet"),
        FieldPanel("featured_image"),
        FieldPanel("body"),
        AuthorPanel("author"),
        InlinePanel("page_comments", label="Comments"),
    ]

    search_fields = Page.search_fields + [index.SearchField("body")]

    parent_page_types = ["CategoryIndexPage"]
    subpage_types = []

    def serve(self, request, *args, **kwargs):
        """
        Handle POST request for blog comments, ``BlogComment``.
        """
        from .forms import CommentForm

        if request.method == "POST":
            form = CommentForm(request.POST)
            if form.is_valid():
                new_comment = form.save(commit=False)
                new_comment.user = request.user
                new_comment.page = self
                new_comment.save()
                messages.success(
                    request,
                    "Your message was successfully "
                    "submitted and is awaiting moderation. "
                    "Thank you for contributing!",
                )
                return redirect(self.get_url(request))
        else:
            form = CommentForm

        return render(request, "blog/blog_page.html", {"page": self, "form": form})

    @property
    def get_tags(self):
        """
        Returns all tags related to the blog post and sets the absolute url
        for each tag.

        :return: list of tags associated with the blog post.
        :rtype: list
        """
        tags = self.tags.all()
        base_url = self.get_site().root_page.url
        for tag in tags:
            tag.url = f"{base_url}tags/?tag={tag.name}"
        return tags

    def get_twitter_share_url(self):
        """
        :return: Formatted URL to share the article on Twitter.
        """
        base_url = "https://twitter.com/share?url="
        return f"{base_url}{self.full_url}&via=BrandishSEO"

    def get_facebook_share_url(self):
        """
        :return: Formatted URL to share the article on Facebook.
        """
        base_url = "https://www.facebook.com/sharer/sharer.php?u="
        return f"{base_url}{self.full_url}"

    def get_linkedin_share_url(self):
        """
        :return: Formatted URL to share the article on LinkedIn.
        """
        base_url = "https://www.linkedin.com/shareArticle?mini=true&url="
        return f"{base_url}{self.full_url}"

    def get_email_share_url(self):
        """
        :return: Formatted URL to send an email containing the article.
        """
        base_url = "mailto:?"
        email_title = urllib.parse.quote(f"Check this out: {self.title}")
        email_body = urllib.parse.quote(f"{self.snippet}: {self.full_url} ")
        return f"{base_url}subject={email_title}&body={email_body}"


@register_snippet
class BlogComment(models.Model):
    """
    Represents comments a user can post to a corresponding ``BlogPage``.

    NOTE: By default, ``is_approved`` is set to False. Thus, all comments must be
    manually approved before they will appear on the post.
    """

    page = ParentalKey(
        "BlogPage", on_delete=models.CASCADE, related_name="page_comments"
    )
    text = models.TextField(
        validators=[MinLengthValidator(3, "Comment must be greater than 3 characters.")]
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="comment_author",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)

    panels = [
        FieldPanel("page"),
        FieldPanel("text"),
        FieldPanel("user"),
        FieldPanel("is_approved"),
    ]

    def __str__(self):
        text = self.text if len(str(self.text)) < 15 else self.text[:15] + "..."
        return f"'{text}' on Page: '{self.page}'"


@register_snippet
class AuthorProfile(UserProfile):
    """
    Add the attribute ``bio`` to ``UserProfile``.
    """

    bio = models.TextField(
        validators=[MinLengthValidator(20, "Bio must be greater than 20 characters.")]
    )
    twitter_handle = models.CharField(
        max_length=16, validators=[MinLengthValidator(5), validate_twitter_handle]
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
