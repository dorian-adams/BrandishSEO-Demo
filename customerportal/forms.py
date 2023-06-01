from django import forms
from django.shortcuts import get_object_or_404

from .models import AccountInvite, Task, TaskComment, Project


class AccountInviteForm(forms.ModelForm):
    class Meta:
        model = AccountInvite
        fields = [
            "email",
        ]


class ProjectUpdateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "website",
            "description",
            "keywords",
            "competitor",
        ]


class TaskCreationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TaskCreationForm, self).__init__(*args, **kwargs)
        project = kwargs["initial"]["project"]
        self.fields["project"].widget = forms.HiddenInput()
        self.fields["assigned_to"] = forms.ModelChoiceField(queryset=project.members)

    class Meta:
        model = Task
        fields = [
            "task_title",
            "task_description",
            "task_goal",
            "priority",
            "assigned_to",
            "project",
        ]

    def save(self, commit=True):
        instance = super(TaskCreationForm, self).save(commit=False)
        instance.status = "To-do"
        instance.progress = 0
        if commit:
            instance.save()
        return instance


class TaskUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TaskUpdateForm, self).__init__(*args, **kwargs)
        project = get_object_or_404(Project, id=kwargs["instance"].project.id)
        self.fields["assigned_to"] = forms.ModelChoiceField(queryset=project.members)

    class Meta:
        model = Task
        fields = [
            "task_title",
            "task_description",
            "task_goal",
            "priority",
            "progress",
            "assigned_to",
        ]


class TaskCommentForm(forms.ModelForm):
    class Meta:
        model = TaskComment
        fields = [
            "text",
        ]
