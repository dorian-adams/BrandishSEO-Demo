"""
Test functionality related to default and sub-routes of all Page models.

NOTE: Will refactor to pytest in the future to reduce boilerplate and the amount of objects
that need to be recreated. As is, the current implementation is necessary due to Wagtail's
parent-child relationships.
See: https://pytest-django.readthedocs.io/en/latest/database.html#populate-the-test-database-if-you-don-t-use-transactional-or-live-server
See: https://pytest-django.readthedocs.io/en/latest/database.html#django-db-setup
"""

# pylint: disable=missing-function-docstring

import operator
from wagtail.test.utils import WagtailPageTestCase

from blog.factories import (
    CategoryIndexPageFactory,
    BlogPageFactory,
    SiteFactoryWithRoot,
    UserFactory,
    CommentFactory,
    AuthorProfileFactory,
)

TOTAL_CATEGORIES = 2
CATEGORY_POST_COUNT = 4


class BlogIndexPageTest(WagtailPageTestCase):
    """
    Tests ``get_context()`` associated with the default route.
    Tests ``search_results()``, and ``tag_results()`` sub-routes.

    NOTE: ``context["posts"]`` is a paginator object containing the three most recent posts
    from a category.
    ``context["posts_per_category"]`` is a list of dictionaries containing a category and its posts
    in every dict.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        cls.site = SiteFactoryWithRoot.create()
        cls.blog_index = cls.site.root_page
        cls.categories = CategoryIndexPageFactory.create_batch(
            TOTAL_CATEGORIES, parent=cls.blog_index
        )
        BlogPageFactory.create_batch(
            CATEGORY_POST_COUNT,
            parent=cls.categories[0],
            body="Posts for category 1",
            author=cls.user,
        )
        BlogPageFactory.create_batch(
            CATEGORY_POST_COUNT,
            parent=cls.categories[1],
            body="Posts for category 2",
            author=cls.user,
        )

    def test_default_route(self):
        response = self.client.get(self.blog_index.url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "blog/blog_index_page.html")

    def test_search_empty_string(self):
        # /blog/?q=
        response = self.client.get(
            self.blog_index.url + self.blog_index.reverse_subpage("search"),
            data={"q": ""},
        )
        expected_num_results = 0

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            response.context["posts"].paginator.count, expected_num_results
        )

    def test_search_with_results(self):
        # /blog/?q=find+me
        BlogPageFactory.create(parent=self.categories[0], body="find me")
        response = self.client.get(
            self.blog_index.url + self.blog_index.reverse_subpage("search"),
            data={"q": "find me"},
        )
        expected_num_results = 1

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            response.context["posts"].paginator.count, expected_num_results
        )

    def test_search_with_no_results(self):
        # /blog/?q=no+results
        BlogPageFactory.create(parent=self.categories[0], body="blank")
        response = self.client.get(
            self.blog_index.url + self.blog_index.reverse_subpage("search"),
            data={"q": "no results"},
        )
        expected_num_results = 0

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            response.context["posts"].paginator.count, expected_num_results
        )

    def test_tags_with_results(self):
        # /blog/tags/?tag=test
        BlogPageFactory.create(parent=self.categories[0], tags=["test"])
        response = self.client.get(
            self.blog_index.url + self.blog_index.reverse_subpage("tag_results"),
            data={"tag": "test"},
        )
        expected_num_results = 1

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            response.context["posts"].paginator.count, expected_num_results
        )

    def test_get_context_gets_all_categories(self):
        response = self.client.get(self.blog_index.url)
        self.assertEqual(len(response.context["posts_per_category"]), TOTAL_CATEGORIES)

    def test_get_context_filters_posts_by_category(self):
        response = self.client.get(self.blog_index.url)
        for post in response.context["posts_per_category"][0]["posts"]:
            self.assertEqual(post.specific.body, "Posts for category 1")


class CategoryIndexPageTest(WagtailPageTestCase):
    """
    Tests default route and ensures blog posts are filtered by category and
    in reverse chronological order.

    NOTE: ``context["posts"]`` is a paginator object.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        cls.site = SiteFactoryWithRoot.create()
        cls.blog_index = cls.site.root_page
        cls.categories = CategoryIndexPageFactory.create_batch(
            TOTAL_CATEGORIES, parent=cls.blog_index
        )
        cls.category = cls.categories[0]
        BlogPageFactory.create_batch(
            CATEGORY_POST_COUNT, parent=cls.categories[0], author=cls.user
        )
        BlogPageFactory.create_batch(
            CATEGORY_POST_COUNT, parent=cls.categories[1], author=cls.user
        )

    def test_default_route(self):
        response = self.client.get(self.category.url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "blog/category_index_page.html")

    def test_get_context_returns_posts_filtered_by_category(self):
        response = self.client.get(self.category.url)
        self.assertEqual(response.context["posts"].paginator.count, CATEGORY_POST_COUNT)

    def test_get_context_orders_posts_in_reverse_chronological_order(self):
        response = self.client.get(self.category.url)
        posts = response.context["posts"].object_list
        expected_order = sorted(
            posts, key=operator.attrgetter("specific.date"), reverse=True
        )

        self.assertEqual(posts, expected_order)


class BlogPageTest(WagtailPageTestCase):
    """
    Tests default route, AuthorProfile integration with the template,
    and ensures POST requests for blog comments are handled successfully.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        cls.site = SiteFactoryWithRoot.create()
        cls.blog_index = cls.site.root_page
        cls.blog_page = BlogPageFactory.create(
            author=cls.user,
            parent=CategoryIndexPageFactory.create(parent=cls.blog_index),
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_default_route(self):
        response = self.client.get(self.blog_page.url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "blog/blog_page.html")

    def test_serve_successful_post_request_for_blog_comments(self):
        response = self.client.post(
            self.blog_page.url, data={"text": "test comment..."}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Success!"
        )  # via messages.success on successful POST

    def test_comment_is_not_shown_when_is_approved_is_false(self):
        comment = CommentFactory.create(page=self.blog_page, user=self.user)
        response = self.client.get(self.blog_page.url)
        self.assertNotContains(response, comment.text)

    def test_comment_is_shown_when_is_approved_is_true(self):
        comment = CommentFactory.create(
            page=self.blog_page, is_approved=True, user=self.user
        )
        response = self.client.get(self.blog_page.url)
        self.assertContains(response, comment.text)

    def test_template_displays_author_bio(self):
        author_profile = AuthorProfileFactory.create(user=self.user)
        response = self.client.get(self.blog_page.url)
        self.assertContains(response, author_profile.bio)
