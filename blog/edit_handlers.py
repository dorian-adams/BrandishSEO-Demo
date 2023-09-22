"""
Custom FieldPanel.
As of Wagtail 3.0 customization of the form object must be done in
the constructor method of a subclass of BoundPanel.
See: https://docs.wagtail.org/en/latest/releases/3.0.html#api-changes-to-panels-edithandlers
"""

from wagtail.admin.panels import FieldPanel

from accounts.models import User


class AuthorPanel(FieldPanel):
    """
    Restricts ``BlogPage`` ``author`` choices to users who have an ``AuthorProfile``.
    """

    class BoundPanel(
        FieldPanel.BoundPanel
    ):  # pylint: disable=missing-class-docstring
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.form.fields["author"].queryset = User.objects.exclude(
                authorprofile__isnull=True
            )
            self.form.fields["author"].empty_label = None
