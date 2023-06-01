from django.db.models.signals import post_save
from django.dispatch import receiver

from customerportal.models import Project, Task
from customerportal.parser import extract_tasks


@receiver(post_save, sender=Project)
def create_tasks(sender, instance, **kwargs):
    # Get Tasks associated with the instance (Project)
    project_tasks = Task.objects.filter(project=instance)
    # Create Project Tasks only if Tasks haven't already been created.
    if instance.strategy_doc and len(project_tasks) == 0:
        tasks = extract_tasks(instance)
        for task in tasks:
            new_task = Task.create(
                project=instance,
                title=task["title"],
                description=task["description"],
                priority=task["priority"].split()[1],
            )
            new_task.save()
