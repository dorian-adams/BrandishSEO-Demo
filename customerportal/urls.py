from django.urls import path

from .views import (
    ProjectUpdateView,
    ProjectDetailView,
    TaskListView,
    CreateTaskView,
    TaskUpdateView,
    TaskDetailView,
    TeamDetailView,
    StrategyDetailView,
    redirect_project,
    project_add_admin,
    project_remove_admin,
    project_remove_member,
)


app_name = "customerportal"

urlpatterns = [
    path("<slug:slug>/team/add-admin/<int:pk>/", project_add_admin, name="add-admin"),
    path(
        "<slug:slug>/team/remove-admin/<int:pk>/",
        project_remove_admin,
        name="remove-admin",
    ),
    path(
        "<slug:slug>/team/remove-member/<int:pk>/",
        project_remove_member,
        name="remove-member",
    ),
    path(
        "<slug:slug>/tasks/update/<int:pk>",
        TaskUpdateView.as_view(),
        name="task-update",
    ),
    path(
        "<slug:slug>/tasks/create-task/", CreateTaskView.as_view(), name="task-creation"
    ),
    path(
        "<slug:slug>/tasks/<slug:task_slug>/",
        TaskDetailView.as_view(),
        name="task-detail",
    ),
    path(
        "<slug:slug>/project-update/",
        ProjectUpdateView.as_view(),
        name="project-update",
    ),
    path("<slug:slug>/strategy/", StrategyDetailView.as_view(), name="strategy"),
    path("<slug:slug>/team/", TeamDetailView.as_view(), name="team"),
    path("<slug:slug>/tasks/", TaskListView.as_view(), name="tasks"),
    path("<slug:slug>/", ProjectDetailView.as_view(), name="project"),
    path("", redirect_project, name="redirect-to-project"),
]
