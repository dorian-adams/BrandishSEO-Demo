from django.urls import path

from .views import (
    CreateTaskView,
    ProjectDetailView,
    ProjectUpdateView,
    StrategyDetailView,
    TaskDetailView,
    TaskListView,
    TaskUpdateView,
    TeamDetailView,
    project_add_admin,
    project_remove_admin,
    project_remove_member,
    redirect_project,
)

app_name = "projects"

urlpatterns = [
    path(
        "<slug:slug>/team/add-admin/<int:pk>/",
        project_add_admin,
        name="add_admin",
    ),
    path(
        "<slug:slug>/team/remove-admin/<int:pk>/",
        project_remove_admin,
        name="remove_admin",
    ),
    path(
        "<slug:slug>/team/remove-member/<int:pk>/",
        project_remove_member,
        name="remove_member",
    ),
    path(
        "<slug:slug>/tasks/update/<int:pk>",
        TaskUpdateView.as_view(),
        name="task_update",
    ),
    path(
        "<slug:slug>/tasks/create-task/",
        CreateTaskView.as_view(),
        name="task_creation",
    ),
    path(
        "<slug:slug>/tasks/<slug:task_slug>/",
        TaskDetailView.as_view(),
        name="task_detail",
    ),
    path(
        "<slug:slug>/project-update/",
        ProjectUpdateView.as_view(),
        name="project_update",
    ),
    path(
        "<slug:slug>/strategy/", StrategyDetailView.as_view(), name="strategy"
    ),
    path("<slug:slug>/team/", TeamDetailView.as_view(), name="team"),
    path("<slug:slug>/tasks/", TaskListView.as_view(), name="tasks"),
    path("<slug:slug>/", ProjectDetailView.as_view(), name="project"),
    path("", redirect_project, name="redirect_to_project"),
]
