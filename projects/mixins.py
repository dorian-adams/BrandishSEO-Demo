from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404

from .models import Project


class ProjectAuthMixin(UserPassesTestMixin):
    """
    Handles authentication for ``Project`` views.

    Ensures user requesting access is a member of the ``Project``.
    """

    def test_func(self):
        project_slug = self.request.resolver_match.kwargs["slug"]
        if project_slug == "demo":  # Demo is accessible to everyone
            return True
        project = get_object_or_404(Project, slug=project_slug)
        return self.request.user in project.members.all()


class ProjectContextMixin:
    """
    Sets context that's used across all Project views.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs["slug"]
        project = get_object_or_404(Project, slug=slug)

        context.update(
            {
                "demo": slug == "demo",
                "slug": slug,
                "project": project,
                "admin": self.request.user.is_authenticated
                and self.request.user in project.admin.all(),
            }
        )
        return context
