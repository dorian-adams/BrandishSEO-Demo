from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, get_list_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import FormMixin
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.contrib import messages
from django.views.generic.edit import CreateView, UpdateView
from django.http import HttpResponseRedirect

from accounts.models import User
from .models import Project, Task, TaskComment
from .forms import AccountInviteForm, TaskCreationForm, TaskUpdateForm, TaskCommentForm
from .mixins import ProjectContextMixin, ProjectAuthMixin


# pylint: disable=invalid-name

# -----------------------------------------------------------------------------
# Customer Profile Views
# -----------------------------------------------------------------------------


@login_required()
def redirect_project(request):
    """
    Redirects user to their ``Project``, or profile page if multiple or no Project exists.
    """
    projects = Project.objects.filter(members=request.user)

    if len(projects) == 1:
        return HttpResponseRedirect(
            reverse("customerportal:project", args=(projects[0].slug,))
        )
    # If user has more than one project or no projects redirect to user's profile page
    # From there, the user can complete purchase or select the project they wish to visit
    return HttpResponseRedirect(
        reverse(
            "accounts:profile",
        )
    )


# -----------------------------------------------------------------------------
# Project Views
# -----------------------------------------------------------------------------


class ProjectDetailView(ProjectAuthMixin, ProjectContextMixin, DetailView):
    """
    Serves as the main hub/landing page for all Project related content.
    """

    model = Project
    template_name = "customerportal/customer_portal.html"

    def get_context_data(self, **kwargs):
        """
        Display a brief list of the latest comments, ``TaskComment``.
        """
        context = super().get_context_data(**kwargs)
        context["comments"] = TaskComment.objects.filter(task__project=self.object.pk)[
            :5
        ]
        return context


class ProjectUpdateView(ProjectAuthMixin, ProjectContextMixin, UpdateView):
    """
    Update information related to the project.  Website name, keywords, etc.
    """

    model = Project
    fields = [
        "website",
        "description",
        "keywords",
        "competitor",
    ]
    template_name = "customerportal/project_update_form.html"

    def get_success_url(self):
        return reverse_lazy("customerportal:project", args=(self.object.slug,))


# -----------------------------------------------------------------------------
# Task Views
# -----------------------------------------------------------------------------


class TaskListView(ProjectAuthMixin, ProjectContextMixin, ListView):
    model = Task
    template_name = "customerportal/tasks.html"

    def get_queryset(self):
        return get_list_or_404(Task, project__slug=self.kwargs["slug"])


class TaskDetailView(ProjectAuthMixin, ProjectContextMixin, FormMixin, DetailView):
    """
    Display ``Task`` info and associated comments, ``TaskComment``.
    TaskComments are handled within this view's ``post`` method.
    """

    model = Task
    template_name = "customerportal/task_detail.html"
    form_class = TaskCommentForm
    slug_url_kwarg = "task_slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["comments"] = get_list_or_404(TaskComment, task=self.object.pk)
        except:
            context["comments"] = []  # If the given Task does not have comments
        context["form"] = TaskCommentForm(initial={"task": self.object})
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle creation of Task comments, ``TaskComment``.
        """
        self.object = self.get_object()
        self.object.text = request.POST.get("text", "")
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.task = self.get_object()
        obj.author = self.request.user
        obj.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "customerportal:task_detail",
            args=(
                self.object.project.slug,
                self.object.slug,
            ),
        )


class CreateTaskView(ProjectAuthMixin, ProjectContextMixin, CreateView):
    template_name = "customerportal/task_form.html"
    model = Project
    form_class = TaskCreationForm

    def get_initial(self):
        """
        Pass ``Project`` to ``TaskCreationForm`` init for custom query.
        """
        return {"project": get_object_or_404(Project, slug=self.kwargs["slug"])}

    def get_success_url(self):
        return reverse_lazy(
            "customerportal:task_detail",
            args=(
                self.object.project.slug,
                self.object.slug,
            ),
        )


class TaskUpdateView(ProjectAuthMixin, ProjectContextMixin, UpdateView):
    template_name = "customerportal/task_form.html"
    model = Task
    form_class = TaskUpdateForm

    def get_success_url(self):
        return reverse_lazy(
            "customerportal:task_detail",
            args=(
                self.object.project.slug,
                self.object.slug,
            ),
        )


# -----------------------------------------------------------------------------
# Strategy and Related Docs Views
# -----------------------------------------------------------------------------


class StrategyDetailView(ProjectAuthMixin, ProjectContextMixin, DetailView):
    """
    Display the Project's strategy and all associated documents.
    """

    template_name = "customerportal/strategy.html"
    model = Project


# -----------------------------------------------------------------------------
# Team Views
# -----------------------------------------------------------------------------


class TeamDetailView(ProjectAuthMixin, ProjectContextMixin, FormMixin, DetailView):
    """
    Display list of ``Users`` associated with the ``Project``.

    From the TeamDetailView, admins can remove, promote, or invite new members.
    ``AccountInvite`` is handled within the TeamDetailView's ``post`` method, while
    all member actions (remove, promote) are sent to their, separate, respective functions.
    """

    template_name = "customerportal/team.html"
    model = Project
    form_class = AccountInviteForm
    invite_email = (
        None  # the email for which the invite is being sent via AccountInviteForm
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = AccountInviteForm(
            initial={"project": get_object_or_404(Project, slug=self.kwargs["slug"])}
        )
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle ``Project`` invites.
        """
        self.object = self.get_object()
        form = AccountInviteForm(request.POST)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.project = self.get_object()
        self.invite_email = obj.email
        obj.save()
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(
            self.request, f"Invite successfully sent to {self.invite_email}"
        )
        return reverse_lazy("customerportal:team", args=(self.object.slug,))


# -----------------------------------------------------------------------------
# Team Action Views - add / remove - members / admins - POST only
# pk represents user.pk of the user to be modified
# -----------------------------------------------------------------------------


def project_remove_admin(request, slug, pk):
    """
    Removes admin from ``Project.admin``
    Removal from admin status does not remove user as a member.
    """
    if request.method == "POST":
        min_admin = 1  # Projects must maintain at least 1 admin
        project = get_object_or_404(Project, slug=slug)
        user = get_object_or_404(User, id=pk)
        is_admin = request.user in project.admin.all()

        if not is_admin:
            messages.success(
                request, "Request failed. Only admins may perform this action."
            )
        elif len(project.admin.all()) > min_admin:
            project.admin.remove(user)
            messages.success(
                request, f"Successfully removed '{user.first_name}' from admin group."
            )
        else:
            messages.success(
                request, "Request failed. Project must maintain at least one admin."
            )

        return HttpResponseRedirect(
            reverse("customerportal:team", args=(project.slug,))
        )


def project_add_admin(request, slug, pk):
    """
    Add ``User`` via their ``pk`` to the Project's admin group.
    """
    if request.method == "POST":
        project = get_object_or_404(Project, slug=slug)
        user = get_object_or_404(User, id=pk)
        is_admin = request.user in project.admin.all()

        if is_admin:
            project.admin.add(user)
            messages.success(
                request, f"Successfully promoted '{user.first_name}' to admin."
            )
        else:
            messages.success(
                request, "Request failed. Only admins may perform this action."
            )

        return HttpResponseRedirect(
            reverse("customerportal:team", args=(project.slug,))
        )


def project_remove_member(request, slug, pk):
    """
    Entirely remove a ``User`` from the ``Project``.
    If the ``User`` is an admin, they will also be removed from
    admin.
    """
    if request.method == "POST":
        min_members = 1
        project = get_object_or_404(Project, slug=slug)
        user = get_object_or_404(User, id=pk)
        is_admin = request.user in project.admin.all()

        if not is_admin:
            messages.success(
                request, "Request failed. Only admins may perform this action."
            )
        elif len(project.members.all()) > min_members:
            project.members.remove(user)
            if user in project.admin.all():
                project.admin.remove(user)
            messages.success(
                request, f"Successfully removed '{user.first_name}' from the Project."
            )
        else:
            messages.success(
                request, "Request failed. Project must maintain at least one member."
            )
        return HttpResponseRedirect(
            reverse("customerportal:team", args=(project.slug,))
        )


"""
def invite_registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data.get('email')
            form.save()
            get_invite = get_object_or_404(AccountInvite, email=user_email)
            project = get_invite.project
            user = get_object_or_404(User, email=user_email)
            project.members.add(user)
    form = UserRegistrationForm()
    return render(request, 'customerportal/invite_registration.html', {'form': form})
"""
