"""
Test form functionality.
"""

# pylint: disable=missing-function-docstring

from django.test import SimpleTestCase

from blog.forms import CommentForm


class CommentFormTest(SimpleTestCase):
    """
    Tests ``CommentForm``, ensures form is valid under appropriate conditions,
    and placeholder and label have expected values.
    """

    def test_comment_form_placeholder(self):
        form = CommentForm()
        text_field_placeholder = form.fields["text"].widget.attrs["placeholder"]
        self.assertEqual(text_field_placeholder, "Leave a comment...")

    def test_comment_form_label(self):
        form = CommentForm()
        self.assertEqual(form.fields["text"].label, "")

    def test_comment_form_valid(self):
        form = CommentForm(data={"text": "Valid"})
        self.assertTrue(form.is_valid())

    def test_comment_form_invalid(self):
        form = CommentForm(data={"text": ""})
        self.assertFalse(form.is_valid())
