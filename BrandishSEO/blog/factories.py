"""
Usage:
    site = SiteFactoryWithRoot.create()
    blog_index = site.root_page
"""

import factory
import wagtail_factories

from core.models import User
from . import models


# pylint: disable=missing-function-docstring, missing-class-docstring, too-few-public-methods


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.sequence(lambda n: f"User{n}")


class BlogIndexPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = models.BlogIndexPage

    intro = "Welcome to the Blog"
    slug = "blog"


class CategoryIndexPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = models.CategoryIndexPage

    intro = factory.sequence(lambda n: f"Welcome to Category {n}")
    slug = factory.sequence(lambda n: f"category{n}")


class BlogPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = models.BlogPage

    date = factory.Faker("date_time")
    author = factory.SubFactory(UserFactory)
    slug = factory.sequence(lambda n: f"post{n}")
    snippet = factory.sequence(lambda n: f"Article {n} snippet...")
    body = "Test post..."
    featured_image = factory.SubFactory(wagtail_factories.ImageFactory)
    featured_article = False

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.tags.add(*extracted)


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.BlogComment

    page = factory.SubFactory(BlogPageFactory)
    text = "Test comment..."
    user = factory.SubFactory(UserFactory)


class SiteFactoryWithRoot(wagtail_factories.SiteFactory):
    hostname = "127.0.0.1"
    port = "8000"
    is_default_site = True
    root_page = factory.SubFactory(BlogIndexPageFactory)