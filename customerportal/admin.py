"""
This Admin section is designed to provide a quick overview of Project
and Task activity. Object creation and editing is primarily intended
to be handled on the front-end to make use of associated scripting and
other procedures.
"""

from django.contrib import admin

from .models import AccountInvite, Task, Project, TaskComment


# -----------------------------------------------------------------------------
# Default Admin
# -----------------------------------------------------------------------------

admin.site.register(AccountInvite)


# -----------------------------------------------------------------------------
# Admin Actions
# -----------------------------------------------------------------------------


@admin.action()
def export_to_xlsx():
    pass


# -----------------------------------------------------------------------------
# Inline Panels
# -----------------------------------------------------------------------------


class TaskInline(admin.StackedInline):
    """Incorporated in ProjectAdmin."""

    model = Task
    classes = ["collapse"]
    extra = 0


class TaskCommentInline(admin.StackedInline):
    """Read Only. Incorporated in TaskAdmin."""

    model = TaskComment
    classes = ["collapse"]
    ordering = ("-posted_at",)
    readonly_fields = ("text", "author")
    max_num = 0


# -----------------------------------------------------------------------------
# Project, Task, and TaskComment Admins
# -----------------------------------------------------------------------------


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = [TaskInline]
    search_fields = [
        "website",
        "project_name",
        "members__email",
        "members__first_name",
        "members__last_name",
    ]
    list_display = ("project_name", "get_service", "status")
    list_filter = ("status", "service__name")
    list_editable = ("status",)

    @admin.display(ordering="service__name", description="Service")
    def get_service(self, obj):
        return obj.service.name


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    inlines = [TaskCommentInline]
    search_fields = ["project__website", "task_description"]
    list_display = ("project", "task_title", "feedback")
    list_filter = ("feedback",)
    list_editable = ("feedback",)

    def get_form(self, request, obj=None, **kwargs):
        form = super(TaskAdmin, self).get_form(request, obj, **kwargs)
        if obj:
            form.base_fields[
                "assigned_to"
            ].queryset = (
                obj.project.members.all()
            )  # Restrict choices to Project members
            form.base_fields["project"].disabled = True
        return form


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    search_fields = [
        "text",
        "author__first_name",
        "author__last_name",
        "task__project__website",
    ]
    list_display = ("text", "posted_at")
    list_filter = ("posted_at",)
    readonly_fields = ("task",)

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super(TaskCommentAdmin, self).get_form(request, obj, **kwargs)
        if obj:
            form.base_fields["author"].queryset = obj.task.project.members.all()
        return form
