from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse


class AdminTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            password="testadmin"
        )
        self.client.force_login(self.admin_user)

        self.redactor = get_user_model().objects.create_user(
            username="redactorTest",
            password="testredactor",
            years_of_experience=10
        )

    def test_redactor_years_of_experience_listed(self):
        url = reverse("admin:Newspaper_redactor_changelist")
        res = self.client.get(url)
        self.assertContains(res, self.redactor.years_of_experience)

    def test_redactor_detail_years_of_experience_listed(self):
        url = reverse("admin:Newspaper_redactor_change",
                      args=[self.redactor.id])
        res = self.client.get(url)
        self.assertContains(res, self.redactor.years_of_experience)
