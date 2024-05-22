from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from Newspaper.models import Topic


class PrivateTopicViewTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test",
            password="test123",
        )
        self.client.force_login(self.user)

        Topic.objects.create(
            name="namewith_i",
        )
        Topic.objects.create(
            name="wethout_char",
        )
        Topic.objects.create(
            name="wethout_char2",
        )
        Topic.objects.create(
            name="namewith_i2",
        )

    def test_topic_list_search(self):

        response = self.client.get(reverse("newspaper:topics-list"),
                                   {"topic_name": "i"})
        self.assertEqual(
            list(response.context_data["topic_list"]),
            list(Topic.objects.filter(name__icontains="i"))
        )

    def test_topic_create_get_succses_redirect(self):
        url = reverse("newspaper:topic-create")
        response = self.client.post(path=url, data={
            "name": "Fuat12",
        })
        self.assertRedirects(response, reverse("newspaper:topics-list"))

    def test_topic_update_get_succses_redirect(self):
        topic = Topic.objects.first()
        url = reverse("newspaper:topic-update", args=[str(topic.id)])
        response = self.client.post(path=url, data={"name": "Fuat123"})
        self.assertRedirects(response, reverse("newspaper:topics-list"))

    def test_topic_delete_get_succses_redirect(self):
        topic = Topic.objects.first()
        url = reverse("newspaper:topic-delete", args=[str(topic.id)])
        response = self.client.post(path=url)
        self.assertRedirects(response, reverse("newspaper:topics-list"))
