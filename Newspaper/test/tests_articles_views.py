from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from Newspaper.models import Article, Topic


class PrivateArticleViewTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test",
            password="test123",
        )
        self.client.force_login(self.user)

        Article.objects.create(
            title="TitleTest1",
            content="ContentTest1",
            published_date="2020-10-15",
            topic=Topic.objects.create(name="wethout_char_0")
        )
        Article.objects.create(
            title="TytleTest2",
            content="ContentTest2",
            published_date="2020-10-15",
            topic=Topic.objects.create(name="with_char_i_1")
        )
        Article.objects.create(
            title="TitleTest3",
            content="ContentTest3",
            published_date="2020-10-15",
            topic=Topic.objects.create(name="with_char_i_2")
        )
        Article.objects.create(
            title="TytleTest4",
            content="ContentTest4",
            published_date="2020-10-15",
            topic=Topic.objects.create(name="wethout_char_3")
        )

    def test_article_create_get_succses_redirect(self):
        url = reverse("newspaper:article-create")
        response = self.client.post(
            path=url,
            data={
                "title": "TytleTest5",
                "content": "ContentTest5",
                "published_date": "2020-10-15",
                "topic": 1}
        )
        self.assertRedirects(response, reverse("newspaper:articles-list"))

    def test_article_update_get_succses_redirect(self):
        url = reverse("newspaper:article-update", args=["1"])
        response = self.client.post(
            path=url,
            data={
                "title": "TytleTest6",
                "content": "ContentTest6",
                "published_date": "2020-10-15",
                "topic": 2,
                "publishers": 1}
        )
        self.assertRedirects(response, reverse("newspaper:articles-list"))

    def test_article_delete_get_succses_redirect(self):
        url = reverse("newspaper:article-delete", args=["1"])
        response = self.client.post(path=url)
        self.assertRedirects(response, reverse("newspaper:articles-list"))
