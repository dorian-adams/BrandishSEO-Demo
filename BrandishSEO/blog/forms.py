from django import forms

from .models import BlogComment


class CommentForm(forms.ModelForm):
    """
    Form allows users to submit comments ``BlogComment`` to an article ``BlogPage``.
    """
    text = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control border-0 px-1',
            'placeholder': 'Leave a comment...'
        })
    )

    class Meta:
        model = BlogComment
        fields = ['text', ]
