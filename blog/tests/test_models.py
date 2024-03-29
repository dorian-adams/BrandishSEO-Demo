"""
Test model methods (non-view), pagination, and parent-child relationships.
"""

# pylint: disable=missing-function-docstring

import operator

from django.test import TestCase
from wagtail.test.utils import WagtailPageTestCase

from blog.factories import (
    BlogIndexPageFactory,
    BlogPageFactory,
    CategoryIndexPageFactory,
    CommentFactory,
    SiteFactoryWithRoot,
)
from blog.models import BlogIndexPage, BlogPage, CategoryIndexPage
from blog.paginator import paginate_posts


class BlogIndexPageModelTest(WagtailPageTestCase):
    """
    Tests hierarchy of ``BlogIndexPage``.
    """

    def test_can_create_child_at_blog_index(self):
        self.assertCanCreateAt(BlogIndexPage, CategoryIndexPage)


class CategoryIndexPageModelTest(WagtailPageTestCase):
    """
    Tests method ``get_recent_posts`` and hierarchy.
    Expected to return 3 posts from the category in reverse chronological order "-date".
    """

    def test_can_create_child_at_category_index(self):
        self.assertCanCreateAt(CategoryIndexPage, BlogPage)

    def test_get_recent_posts(self):
        category = CategoryIndexPageFactory.create(
            parent=BlogIndexPageFactory.create()
        )
        BlogPageFactory.create_batch(4, parent=category)
        queryset = category.get_recent_posts()
        expected_num_results = 3  # get_recent_posts() slices at [:3]
        expected_order = sorted(
            queryset,
            key=operator.attrgetter("specific.date"),
            reverse=True,
        )  # get_recent_posts() is expected to order by "-date"

        self.assertEqual(queryset.count(), expected_num_results)
        self.assertQuerysetEqual(
            queryset, expected_order, transform=lambda x: x
        )


class BlogCommentModelTest(TestCase):
    """
    Tests ``BlogComment`` for proper object name and that the attribute, ``is_approved``,
    remains False by default.
    """

    def test_object_name(self):
        blog_page = BlogPageFactory.build()
        comment_text = "Ensure comment text is properly truncated"
        truncated_comment_text = "Ensure comment ..."
        expected_object_name = (
            f"'{truncated_comment_text}' on Page: '{blog_page}'"
        )

        comment_obj = CommentFactory.build(page=blog_page, text=comment_text)
        self.assertEqual(str(comment_obj), expected_object_name)

    def test_is_approved_default_is_false(self):
        comment_obj = CommentFactory.build()
        self.assertFalse(comment_obj.is_approved)


class TestPagination(TestCase):
    """
    Tests pagination function holds 9 blog posts per page and returns the correct
    number of pages.

    paginate() takes a Django request object and queryset.
    """

    @classmethod
    def setUpTestData(cls):
        cls.site = SiteFactoryWithRoot.create()
        cls.blog_index = cls.site.root_page
        cls.category = CategoryIndexPageFactory.create(parent=cls.blog_index)
        cls.posts = BlogPageFactory.build_batch(10, parent=cls.category)

    def setUp(self):
        self.response = self.client.get(self.category.url)
        self.paginator = paginate_posts(self.response.wsgi_request, self.posts)

    def test_pagination_returns_correct_num_pages(self):
        self.assertEqual(self.paginator.paginator.num_pages, 2)

    def test_pagination_is_nine(self):
        page_one = self.paginator.paginator.page(1)
        self.assertEqual(len(page_one.object_list), 9)

    def test_has_next_page(self):
        page_one = self.paginator.paginator.page(1)
        self.assertTrue(page_one.has_next())

    def test_has_previous_page(self):
        page_two = self.paginator.paginator.page(2)
        self.assertTrue(page_two.has_previous())


class BlogPageModelTest(TestCase):
    """
    Tests ``get_tags`` and all methods related to generating URLs
    for sharing blog posts on social media.
    """

    @classmethod
    def setUpTestData(cls):
        cls.site = SiteFactoryWithRoot.create()
        cls.blog_index = cls.site.root_page
        cls.category = CategoryIndexPageFactory.create(
            parent=cls.blog_index, slug="test-category"
        )
        cls.post = BlogPageFactory.create(
            parent=cls.category, slug="test-post"
        )

    def test_get_tags_properly_formats_tag_urls(self):
        post = BlogPageFactory.create(parent=self.category, tags=["test"])
        tag = post.get_tags[0]
        page = "/blog/tags/?tag=test"
        expected_url = f"http://{self.site.hostname}:{self.site.port}{page}"

        self.assertEqual(tag.url, expected_url)

    def test_get_tags_returns_all_tags_associated_with_post(self):
        create_tags = ["test1", "test2", "test3", "test4"]
        expected_tag_count = len(create_tags)
        post = BlogPageFactory.create(parent=self.category, tags=create_tags)
        tags = post.get_tags

        self.assertEqual(len(tags), expected_tag_count)

    def test_get_twitter_share_url(self):
        twitter = "https://twitter.com/share?url="
        page = "/blog/test-category/test-post/&via=BrandishSEO"
        expected_url = (
            f"{twitter}http://{self.site.hostname}:{self.site.port}{page}"
        )

        self.assertEqual(self.post.get_twitter_share_url(), expected_url)

    def test_get_facebook_share_url(self):
        facebook = "https://www.facebook.com/sharer/sharer.php?u="
        page = "/blog/test-category/test-post/"
        expected_url = (
            f"{facebook}http://{self.site.hostname}:{self.site.port}{page}"
        )

        self.assertEqual(self.post.get_facebook_share_url(), expected_url)

    def test_get_linkedin_share_url(self):
        linkedin = "https://www.linkedin.com/shareArticle?mini=true&url="
        page = "/blog/test-category/test-post/"
        expected_url = (
            f"{linkedin}http://{self.site.hostname}:{self.site.port}{page}"
        )

        self.assertEqual(self.post.get_linkedin_share_url(), expected_url)

    def test_get_email_share_url(self):
        subject = "subject=Check%20this%20out%3A%20Test%20page&"
        body = f"body=Article%20snippet...%3A%20"
        page = "/blog/test-category/test-post/%20"
        expected_url = f"mailto:?{subject}{body}http%3A//{self.site.hostname}%3A{self.site.port}{page}"

        self.assertEqual(self.post.get_email_share_url(), expected_url)
