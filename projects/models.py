from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
)
from django.db import models, transaction
from django.template.defaultfilters import slugify
from django.urls import reverse

from checkout.models import Service
from projects.utils.file_parsers import extract_tasks_docx, extract_tasks_xlsx

STRATEGY_STATUS_CHOICES = (
    ("Researching", "Researching"),
    ("In Progress", "In Progress"),
    ("Final Touches", "Final Touches"),
    ("Review", "Review"),
    ("Complete", "Complete"),
)

TASK_PRIORITY_CHOICES = (
    ("Low", "Low"),
    ("Medium", "Medium"),
    ("High", "High"),
)

TASK_STATUS_CHOICES = (
    ("To-do", "To-do"),
    ("In progress", "In progress"),
    ("Completed", "Completed"),
)


def directory_path(instance, filename):
    return "{0}/{1}".format(instance.project_name, filename)


class Project(models.Model):
    admin = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="admins"
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="members"
    )
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    project_name = models.CharField(max_length=40, unique=True)
    slug = models.SlugField(max_length=50)
    website = models.CharField(max_length=200)
    description = models.TextField()
    keywords = models.CharField(max_length=200)
    competitor = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20,
        choices=STRATEGY_STATUS_CHOICES,
        default="Payment Pending",
    )
    strategy_doc = models.FileField(
        upload_to=directory_path,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["docx"])],
    )
    strategy_xlsx = models.FileField(
        upload_to=directory_path,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["xlsx"])],
    )
    strategy_pdf = models.FileField(
        upload_to=directory_path,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
    )

    def get_absolute_url(self):
        return reverse("projects:project", args=[self.slug])

    @transaction.atomic
    def create_tasks(self):
        """
        Creates Task instances from extracted task data stored in self._tasks.

        Ensures all tasks are created atomically. Deletes self._tasks after 
        creation.
        """
        for data in self._tasks:
            Task.objects.create(
                project=self,
                task_title=data["title"],
                task_description=data["description"],
                priority=data["priority"],
            )
        del self._tasks

    def clean(self):
        """
        Validates that a strategy document is only uploaded after the project 
        exists, and parses the document for validation and task creation if 
        none exist yet.
        """
        super().clean()

        if self.pk is None and (self.strategy_doc or self.strategy_xlsx):
            raise ValidationError(
                {
                    "strategy_doc": "You must create the project before "
                    "uploading a strategy.",
                    "strategy_xlsx": "You must create the project before "
                    "uploading a strategy.",
                }
            )

        if not self.tasks.exists():
            if self.strategy_xlsx:
                try:
                    self._tasks = extract_tasks_xlsx(self.strategy_xlsx)
                except ValidationError as e:
                    raise ValidationError({"strategy_xlsx": e})
            if self.strategy_doc:
                try:
                    self._tasks = extract_tasks_docx(self.strategy_doc)
                except ValidationError as e:
                    raise ValidationError({"strategy_doc": e})

    def save(self, *args, **kwargs):
        """
        Generates slug from project name if not set, then saves the instance.

        If task data exists (via ``self._tasks``), triggers task creation 
        after saving.
        """
        if not self.slug:
            self.slug = slugify(self.project_name)

        super().save(*args, **kwargs)

        if getattr(self, "_tasks", None):
            self.create_tasks()

    def __str__(self):
        return self.website


class Task(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="tasks"
    )
    task_title = models.CharField(max_length=100)
    task_description = models.TextField()
    task_goal = models.CharField(max_length=100, blank=True)
    progress = models.IntegerField(
        default=0, validators=[MaxValueValidator(100), MinValueValidator(0)]
    )
    priority = models.CharField(choices=TASK_PRIORITY_CHOICES, max_length=10)
    status = models.CharField(
        choices=TASK_STATUS_CHOICES, max_length=15, default="To-do"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField()
    feedback = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse(
            "projects:task_detail", args=[self.project.slug, self.slug]
        )

    @classmethod
    def create(cls, project, title, description, priority):
        task = cls(
            project=project,
            task_title=title,
            task_description=description,
            priority=priority,
        )
        return task

    def __str__(self):
        if len(self.task_title) < 16:
            return self.task_title
        return self.task_title[:14] + "..."

    def save(self, *args, **kwargs):
        self.slug = slugify(self.task_title)
        super(Task, self).save(*args, **kwargs)


class TaskComment(models.Model):
    task = models.ForeignKey(
        Task, related_name="comments", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=1000)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT
    )
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("posted_at",)

    def __str__(self):
        if len(self.text) < 15:
            return self.text
        return self.text[:11] + " ..."


class DirectMessage(models.Model):
    text = models.TextField(
        max_length=300,
        validators=[
            MinLengthValidator(3, "Comment must be greater than 3 characters.")
        ],
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="sent_to",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="sent_from",
    )
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("sent_at",)

    def __str__(self):
        if len(self.text) < 15:
            return self.text
        return self.text[:11] + " ..."


class AccountInvite(models.Model):
    email = models.EmailField(max_length=300)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.email
