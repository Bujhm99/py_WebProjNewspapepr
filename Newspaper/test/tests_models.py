from django.contrib.auth import get_user_model
from django.test import TestCase

from Newspaper.models import Topic, Article


class ModelTests(TestCase):
    def test_topic_str(self):
        topic = Topic.objects.create(name="test")
        self.assertEqual(str(topic), topic.name)

    def test_redactor_str(self):
        redactor_test = get_user_model().objects.create(
            username="test",
            password="test123",
            first_name="test_first",
            last_name="test_last",

        )
        self.assertEqual(
            str(redactor_test),
            f"{redactor_test.username}: "
            f"{redactor_test.first_name} {redactor_test.last_name}"
        )

    def test_article_str(self):
        topic = Topic.objects.create(name="test")
        article = Article.objects.create(
            title="TitleTest1",
            content="ContentTest1",
            published_date="2020-10-15",
            topic=topic
        )
        self.assertEqual(str(article), article.title)
