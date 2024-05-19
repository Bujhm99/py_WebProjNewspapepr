from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from parametrize import parametrize

from Newspaper.models import Topic, Article


class PublicLoginTest(TestCase):
    @parametrize("url, arg", [("newspaper:topics-list", ""),
                              ("newspaper:articles-list", ""),
                              ("newspaper:redactors-list", ""),
                              ("newspaper:redactor-detail", "1"),
                              ("newspaper:redactor-create", ""),
                              ("newspaper:redactor-update", "1"),
                              ("newspaper:redactor-delete", "1"),
                              ("newspaper:article-create", ""),
                              ("newspaper:article-update", "1"),
                              ("newspaper:article-delete", "1"),
                              ("newspaper:topic-create", ""),
                              ("newspaper:topic-update", "1"),
                              ("newspaper:topic-delete", "1")])
    def test_no_login_required(self, url, arg):
        res = self.client.get(reverse(url, args=arg))
        self.assertEqual(res.status_code, 302)

    def test_no_login_article_detail(self):
        res = self.client.get(
            reverse("newspaper:article-detail", args=(2515, 1)))
        self.assertEqual(res.status_code, 302)

    def test_no_login_index(self):
        res = self.client.get(reverse("newspaper:index"))
        self.assertEqual(res.status_code, 200)


class PrivateLoginTest(TestCase):
    def setUp(self) -> None:
        topic = Topic.objects.create(name="Fiat")
        self.user = get_user_model().objects.create_user(
            username="test",
            password="test123",
        )
        article = Article.objects.create(
            title="TitleTest1",
            content="ContentTest1",
            published_date="2020-10-15",
            topic=topic,
        )
        article.publishers.set([self.user])
        self.client.force_login(self.user)

    @parametrize("url, arg", [("newspaper:index", ""),
                              ("newspaper:topics-list", ""),
                              ("newspaper:articles-list", ""),
                              ("newspaper:redactors-list", ""),
                              ("newspaper:redactor-detail", "1"),
                              ("newspaper:redactor-create", ""),
                              ("newspaper:redactor-update", "1"),
                              ("newspaper:redactor-delete", "1"),
                              ("newspaper:article-create", ""),
                              ("newspaper:article-update", "1"),
                              ("newspaper:article-delete", "1"),
                              ("newspaper:topic-create", ""),
                              ("newspaper:topic-update", "1"),
                              ("newspaper:topic-delete", "1")])
    def test_login_required(self, url, arg):
        res = self.client.get(reverse(url, args=arg))
        self.assertEqual(res.status_code, 200)

    def test_article_detail(self):
        response = self.client.get(reverse("newspaper:articles-list"))
        rand_num = response.context["rand_num"]
        res = self.client.get(
            reverse("newspaper:article-detail",
                    args=(rand_num, 1))
        )
        self.assertEqual(res.status_code, 200)

    def test_index_context(self):
        response = self.client.get(reverse("newspaper:index"))
        context = {"num_articles": Article.objects.all().count(),
                   "num_redactors": get_user_model().objects.all().count(),
                   "num_topics": Topic.objects.all().count(),
                   "num_visits": 1}
        self.assertEqual(list(response.context[3].dicts[3].items()),
                         list(context.items()))


class TemplateUsedTest(TestCase):
    def setUp(self) -> None:
        topic = Topic.objects.create(name="Fiat")
        self.user = get_user_model().objects.create_user(
            username="test",
            password="test123",
        )
        article = Article.objects.create(
            title="TitleTest1",
            content="ContentTest1",
            published_date="2020-10-15",
            topic=topic,
        )
        article.publishers.set([self.user])
        self.client.force_login(self.user)

    @parametrize("url, template, arg",
                 [("newspaper:index", "newspaper/index.html", ""),
                  ("newspaper:redactors-list",
                   "newspaper/redactors_list.html", ""),
                  ("newspaper:redactor-delete",
                   "newspaper/redactor_confirm_delete.html", "1"),
                  ("newspaper:articles-list",
                   "newspaper/articles_list.html", ""),
                  ("newspaper:article-create",
                   "newspaper/article_form.html", ""),
                  ("newspaper:article-update",
                   "newspaper/article_form.html", "1"),
                  ("newspaper:article-delete",
                   "newspaper/article_confirm_delete.html", "1"),
                  ("newspaper:topics-list",
                   "newspaper/topics_list.html", ""),
                  ("newspaper:topic-create",
                   "newspaper/topic_form.html", ""),
                  ("newspaper:topic-update",
                   "newspaper/topic_form.html", "1"),
                  ("newspaper:topic-delete",
                   "newspaper/topic_confirm_delete.html", "1")],
                 )
    def test_templates_used_test(self, url, template, arg):
        response = self.client.get(reverse(url, args=arg))
        self.assertTemplateUsed(response, template)
