from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse

from accounts.models import User
from projects.forms import AccountInviteForm, ProjectUpdateForm
from projects.models import (
    AccountInvite,
    Project,
    Task,
    TaskComment,
)


class TestAuthUser(TestCase):
    fixtures = ["project-test.json"]

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = User.objects.get(username="user")

    def setUp(self):
        self.client.force_login(self.user)
        self.project = Project.objects.get(slug="test-project")
        self.slug_dict = {"slug": self.project.slug}
        self.task = Task.objects.get(slug="test-task")

    def test_project_view(self):
        response = self.client.get(
            reverse("projects:project", kwargs=self.slug_dict)
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects/projects.html")
        self.assertEqual(response.context["project"], self.project)
        self.assertContains(
            response, "Welcome, Auth"
        )  # Contains welcome msg w/ user's name
        self.assertContains(
            response, "Test Project"
        )  # Contains project's name
        self.assertContains(response, "www.test.com")  # Contains project's url
        self.assertContains(
            response, "Test comment."
        )  # Contains message snippet
        self.assertContains(response, "Pending")  # Contains order status

    def test_create_task_view_GET(self):
        response = self.client.get(
            reverse("projects:task_creation", kwargs=self.slug_dict)
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects/task_form.html")

        # Test view's get_initial()
        self.assertContains(
            response,
            '<input type="hidden" name="project" value="1" id="id_project">',  # Ensures correct Project was passed
        )

    def test_create_task_view_POST(self):
        prior_objects_count = Task.objects.count()
        response = self.client.post(
            reverse("projects:task_creation", kwargs=self.slug_dict),
            data={
                "task_title": "Post test",
                "task_description": "a new task",
                "task_goal": "testing",
                "priority": "High",
                "assigned_to": self.user.pk,
                "project": self.project.pk,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.count(), prior_objects_count + 1)

    def test_invite_registration_view_GET(self):
        response = self.client.get(
            reverse("projects:invite-registration", kwargs=self.slug_dict)
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects/invite_registration.html")

        # Test view's get_initial()
        self.assertContains(
            response,
            '<input type="hidden" name="project" value="1" id="id_project">',  # Ensures correct Project was passed
        )

    def test_invite_registration_view_POST(self):
        prior_objects_count = AccountInvite.objects.count()
        response = self.client.post(
            reverse("projects:invite-registration", kwargs=self.slug_dict),
            data={"email": "invite@email.com", "project": self.project.pk},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            AccountInvite.objects.count(), prior_objects_count + 1
        )

    def test_task_list_view(self):
        response = self.client.get(
            reverse("projects:tasks", kwargs=self.slug_dict)
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects/tasks.html")

        # Test get_queryset - correctly filters the right project
        self.assertIn("object_list", response.context)
        self.assertEqual(len(response.context["object_list"]), 1)
        self.assertEqual(
            response.context["object_list"][0].project, self.project
        )

    def test_task_detail_view_GET(self):
        response = self.client.get(
            reverse(
                "projects:task_detail",
                kwargs={"task_slug": self.task.slug, **self.slug_dict},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects/task_detail.html")
        self.assertContains(response, "Test Task")
        self.assertContains(response, "Testing")
        self.assertContains(response, "Test task description.")  #
        self.assertContains(response, "Auth User")
        self.assertContains(response, "Low")
        self.assertContains(response, "90%")
        self.assertContains(response, "Test comment.")

        # Test context
        self.assertIn("form", response.context)
        self.assertIn("comments", response.context)
        self.assertEqual(len(response.context["comments"]), 1)
        self.assertEqual(
            response.context["comments"][
                0
            ].task,  # Filter check - Comment belongs to correct Task
            self.task,
        )
        self.assertEqual(
            response.context["comments"][
                0
            ].task.project,  # Task belongs to correct Project
            self.project,
        )

    def test_task_detail_view_POST(self):
        """Handles TaskComment"""
        prior_objects_count = TaskComment.objects.count()
        response = self.client.post(
            reverse(
                "projects:task_detail",
                kwargs={"task_slug": self.task.slug, **self.slug_dict},
            ),
            data={"text": "Test comment POST."},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(TaskComment.objects.count(), prior_objects_count + 1)

    def test_task_update_view_GET(self):
        response = self.client.get(
            reverse(
                "projects:task_update",
                kwargs={"pk": self.task.pk, **self.slug_dict},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects/task_form.html")

    def test_task_update_view_POST(self):
        task_to_update = Task.objects.create(
            task_title="Initial Title", project=self.project
        )
        response = self.client.post(
            reverse(
                "projects:task_update",
                kwargs={"pk": task_to_update.pk, **self.slug_dict},
            ),
            data={
                "task_title": "Updated",
                "task_description": "Update",
                "task_goal": "Update",
                "priority": "High",
                "progress": 95,
                "assigned_to": self.user.pk,
                "project": self.project,
            },
        )

        self.assertEqual(response.status_code, 302)
        task_to_update.refresh_from_db()
        self.assertEqual(task_to_update.task_title, "Updated")

    def test_team_detail_view(self):
        response = self.client.get(
            reverse("projects:team", kwargs=self.slug_dict)
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects/team.html")
        self.assertContains(response, "Auth User")
        self.assertNotContains(response, "Unauth User")

    def test_team_update_view_POST(self):
        new_user = User.objects.create_user(
            username="new", password="abc12345"
        )
        self.project.members.add(new_user)
        response = self.client.post(
            reverse(
                "projects:team-edit",
                kwargs={
                    "edit": "remove_member",
                    "pk": new_user.pk,
                    **self.slug_dict,
                },
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_project_update_view_GET(self):
        response = self.client.get(
            reverse("projects:project-update", kwargs=self.slug_dict)
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects/project_update_form.html")
        self.assertIn("form", response.context)

    def test_project_update_view_POST(self):
        response = self.client.post(
            reverse("projects:project-update", kwargs=self.slug_dict),
            data={
                "website": "Updated",
                "description": "test",
                "keywords": "testing",
                "competitor": "everyone",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.project.refresh_from_db()
        self.assertEqual(self.project.website, "Updated")


class TestUnauthUser(TestCase):
    fixtures = ["project.json"]

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.unauth_user = User.objects.get(username="unauth_user")
        cls.project = Project.objects.get(slug="test-project")
        cls.slug_dict = {"slug": cls.project.slug}
        cls.task = Task.objects.get(slug="test-task")

    def setUp(self):
        self.client.force_login(self.unauth_user)

    def test_project_view(self):
        # Project Main
        response = self.client.get(
            reverse("projects:project", kwargs=self.slug_dict)
        )
        self.assertEqual(response.status_code, 403)

    def test_task_creation(self):
        response = self.client.get(
            reverse("projects:task_creation", kwargs=self.slug_dict)
        )
        self.assertEqual(response.status_code, 403)

    def test_invite_registration(self):
        response = self.client.get(
            reverse("projects:invite-registration", kwargs=self.slug_dict)
        )
        self.assertEqual(response.status_code, 403)

    def test_tasks(self):
        response = self.client.get(
            reverse("projects:tasks", kwargs=self.slug_dict)
        )
        self.assertEqual(response.status_code, 403)

    def test_task_detail(self):
        response = self.client.get(
            reverse(
                "projects:task_detail",
                kwargs={"task_slug": self.task.slug, **self.slug_dict},
            )
        )
        self.assertEqual(response.status_code, 403)

    def test_task_update(self):
        response = self.client.get(
            reverse(
                "projects:task_update",
                kwargs={"pk": self.task.pk, **self.slug_dict},
            )
        )
        self.assertEqual(response.status_code, 403)

    def test_team(self):
        response = self.client.get(
            reverse("projects:team", kwargs=self.slug_dict)
        )
        self.assertEqual(response.status_code, 403)

    def test_project_update(self):
        response = self.client.get(
            reverse("projects:project-update", kwargs=self.slug_dict)
        )
        self.assertEqual(response.status_code, 403)


class TestAccountInviteForm(TestCase):
    fixtures = ["project.json"]

    @classmethod
    def setUpTestData(cls):
        cls.project = Project.objects.get(slug="test-project")

    def test_act_invite_form_valid(self):
        form = AccountInviteForm(
            data={"email": "testing@gmail.com", "project": self.project}
        )
        self.assertTrue(form.is_valid())

    def test_act_invite_form_invalid(self):
        form = AccountInviteForm(
            data={"email": "invalid", "project": self.project}
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)

        form_blank = AccountInviteForm(data={})
        self.assertFalse(form_blank.is_valid())
        self.assertEqual(len(form_blank.errors), 2)


class TestProjectUpdateForm(TestCase):
    fixtures = ["project.json"]


"""
    @classmethod
    def setUpTestData(cls):
        cls.project = Project.objects.get(slug='test-project')

    def test_project_update_valid(self):
        form = ProjectUpdateForm(instance=self.project).initial
        self.assertEqual(form['website'], 'www.test.com')
        self.assertTrue(form.is_valid())
        form['website'] = 'www.newtest.com'

    def test_project_update_invalid(self):
        pass
"""
