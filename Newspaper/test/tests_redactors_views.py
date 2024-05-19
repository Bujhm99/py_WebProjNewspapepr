from django.contrib.auth import get_user_model
from django.db.models import Q
from django.test import TestCase, RequestFactory
from django.urls import reverse
from Newspaper.models import Redactor
from Newspaper.views import RedactorDetailView


class PrivateRedactorViewTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test",
            password="test123",
        )
        self.client.force_login(self.user)

        Redactor.objects.create(
            username="namewith_i",
            first_name="Fordi",
            last_name="Harg",
            years_of_experience=10
        )
        Redactor.objects.create(
            username="namewith_i1",
            first_name="Ford",
            last_name="Hargi",
            years_of_experience=11
        )
        Redactor.objects.create(
            username="namewith_i2",
            first_name="Ford",
            last_name="Harg",
            years_of_experience=12
        )
        Redactor.objects.create(
            username="namewith_i3",
            first_name="Fordi",
            last_name="Hargi",
            years_of_experience=13
        )

    def test_redactors_list_search(self):

        response = self.client.get(reverse("newspaper:redactors-list"),
                                   {"redactor_name": "i"})
        self.assertEqual(
            list(response.context_data["redactor_list"]),
            list(Redactor.objects.filter(Q(first_name__icontains="i")
                 | Q(last_name__icontains="i"))
                 )
        )

    def test_redactor_queryset_detail_view(self):
        request = RequestFactory().get("newspaper:redactor-detail")
        view = RedactorDetailView()
        view.request = request
        qeryset = view.get_queryset()
        self.assertQuerysetEqual(
            qeryset,
            get_user_model().objects.prefetch_related("articles__publishers")
        )

    def test_redactor_delete_get_succses_redirect(self):
        path = reverse("newspaper:redactor-delete", args=["5"])
        response = self.client.post(path=path)
        self.assertRedirects(response, reverse("newspaper:redactors-list"))
