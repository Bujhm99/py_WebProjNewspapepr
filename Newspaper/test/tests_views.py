from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from parametrize import parametrize

from Newspaper.models import Topic, Article


class PublicLoginTest(TestCase):
    @parametrize("url, arg", [("newspaper:topics-list", ""),
                              ("newspaper:articles-list", ""),
                              ("newspaper:redactors-list", ""),
                              ("newspaper:redactor-detail",
                               "1"),
                              ("newspaper:redactor-create", ""),
                              ("newspaper:redactor-update",
                               "1"),
                              ("newspaper:redactor-delete",
                               "1"),
                              ("newspaper:article-create", ""),
                              ("newspaper:article-update",
                               "1"),
                              ("newspaper:article-delete",
                               "1"),
                              ("newspaper:topic-create", ""),
                              ("newspaper:topic-update",
                              "1"),
                              ("newspaper:topic-delete",
                               "1")])
    def test_no_login_required(self, url, arg):
        res = self.client.get(reverse(url, args=str(arg)))
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

        print(topic.pk)

    @parametrize("url, arg", [
                              ("newspaper:redactor-detail",
                               get_user_model().objects),
                              ("newspaper:redactor-update",
                               get_user_model().objects),
                              ("newspaper:redactor-delete",
                               get_user_model().objects),
                              ("newspaper:article-update",
                               Article.objects),
                              ("newspaper:article-delete",
                               Article.objects),
                              ("newspaper:topic-update",
                               Topic.objects),
                              ("newspaper:topic-delete",
                               Topic.objects)])
    def test_login_required_with_args(self, url, arg):
        res = self.client.get(reverse(url, args=[str(arg.first().id)]))
        self.assertEqual(res.status_code, 200)

    @parametrize("url", [("newspaper:index"),
                         ("newspaper:topics-list"),
                         ("newspaper:articles-list"),
                         ("newspaper:redactors-list"),
                         ("newspaper:redactor-create"),
                         ("newspaper:article-create"),
                         ("newspaper:topic-create"),
                         ])
    def test_login_required_without_args(self, url):
        res = self.client.get(reverse(url))
        self.assertEqual(res.status_code, 200)

    def test_article_detail(self):
        response = self.client.get(reverse("newspaper:articles-list"))
        rand_num = response.context["rand_num"]
        articl = Article.objects.first().id
        res = self.client.get(
            reverse("newspaper:article-detail",
                    args=(rand_num, articl))
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
        print(topic.pk)

    @parametrize("order, url, template, arg",
                 [("001", "newspaper:index", "newspaper/index.html", ""),
                  ("002", "newspaper:redactors-list",
                   "newspaper/redactors_list.html", ""),
                  ("003", "newspaper:redactor-delete",
                   "newspaper/redactor_confirm_delete.html",
                   get_user_model().objects),
                  ("004", "newspaper:articles-list",
                   "newspaper/articles_list.html", ""),
                  ("005", "newspaper:article-create",
                   "newspaper/article_form.html", ""),
                  ("006", "newspaper:article-update",
                   "newspaper/article_form.html",
                   Article.objects),
                  ("007", "newspaper:article-delete",
                   "newspaper/article_confirm_delete.html",
                   Article.objects),
                  ("010", "newspaper:topics-list",
                   "newspaper/topics_list.html", ""),
                  ("011", "newspaper:topic-create",
                   "newspaper/topic_form.html", ""),
                  ("008", "newspaper:topic-update",
                   "newspaper/topic_form.html",
                   Topic.objects),
                  ("009", "newspaper:topic-delete",
                   "newspaper/topic_confirm_delete.html",
                   Topic.objects)],
                 )
    def test_templates_used_test(self, order, url, template, arg):
        if arg:
            response = self.client.get(reverse(url, args=[str(arg.first().id)]))
        else:
            response = self.client.get(reverse(url))
        self.assertTemplateUsed(response, template)
