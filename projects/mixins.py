from django.shortcuts import get_object_or_404

from .models import Project
from django.contrib.auth.mixins import UserPassesTestMixin


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
    Sets context that's used across all ``Project``.

    context['slug'] is used in the sub-nav, 'projects_nav.html'.
    Passing the slug to context ensures it can be accessed in a consistent manner.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["demo"] = True if self.kwargs["slug"] == "demo" else False
        context["slug"] = self.kwargs["slug"]
        context["project"] = get_object_or_404(Project, slug=context["slug"])
        context["admin"] = self.request.user in context["project"].admin.all()
        return context
