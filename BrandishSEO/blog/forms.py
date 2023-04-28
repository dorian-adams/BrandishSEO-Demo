from django import forms

from .models import BlogComment


class CommentForm(forms.ModelForm):
    """
    Form for blog comments used within ``BlogPage``.
    """

    class Meta:
        model = BlogComment
        fields = [
            "text",
        ]

    text = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "form-control border-0 px-1",
                "placeholder": "Leave a comment...",
            }
        ),
    )
