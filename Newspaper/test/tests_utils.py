from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from parametrize import parametrize

from Newspaper.config import (PRICE_FOR_TITLE,
                              PRICE_FOR_CONTENT,
                              PRICE_FOR_TOPIC)
from Newspaper.models import Article, Topic
from Newspaper.utils import search_split


class PrivateSearchUtilsTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test",
            password="test123",
        )
        self.client.force_login(self.user)
        self.serch_str = "sagg.apple,video,water.dsagf-hjj.-filtr-fger"

    def test_split_search(self):
        self.assertEqual(
            search_split(self.serch_str),
            {
                "sagg": {"or_part": ["sagg"]},
                "apple,video,water": {"or_part": ["apple", "video", "water"]},
                "dsagf-hjj": {"or_part": ["dsagf"], "exept": ["hjj"]},
                "-filtr-fger": {"or_part": [], "exept": ["filtr", "fger"]}
            }
        )

    @parametrize(
        "title, content, topic, res_return,relevance",
        [
            ("With sagg", "sagg.apple,video,water.dsagf-hjj", "Sagg",
             Article.objects.all(),
             (PRICE_FOR_TOPIC
              + PRICE_FOR_TITLE + 5 * PRICE_FOR_CONTENT)),
            ("With sa1gg", "sagg.apple,video,water.dsagf-hjj", "Sagg",
             Article.objects.all(), PRICE_FOR_TOPIC + 5 * PRICE_FOR_CONTENT),
            ("With sagg", "sagg.apple,video,water.dsagf-hjj", "Sa1gg",
             Article.objects.all(), PRICE_FOR_TITLE + 5 * PRICE_FOR_CONTENT),
            ("With sagg", "sagg.ap1ple,video,water.dsagf-hjj", "Sagg",
             Article.objects.all(),
             (PRICE_FOR_TOPIC
              + PRICE_FOR_TITLE + 4 * PRICE_FOR_CONTENT)),
            ("With sagg", "sagg.apple,video,water.dsa1gf-h1jj", "Sagg",
             Article.objects.all(),
             (PRICE_FOR_TOPIC
              + PRICE_FOR_TITLE + 4 * PRICE_FOR_CONTENT)),
            ("With sa1gg", "sa1gg.apple,video,water.dsagf-hjj", "Sa1gg",
             "", PRICE_FOR_TOPIC + PRICE_FOR_TITLE + 5 * PRICE_FOR_CONTENT),
            ("With sagg",
             "sagg.apple,video,water.dsagf-hjjfiltr-fger",
             "Sagg",
             "", PRICE_FOR_TOPIC + PRICE_FOR_TITLE + 5 * PRICE_FOR_CONTENT),
            ("With sagg",
             "sagg.apple,video,water.dsagf-hjjfi1ltr-fger",
             "Sagg",
             Article.objects.all(),
             (PRICE_FOR_TOPIC
              + PRICE_FOR_TITLE + 5 * PRICE_FOR_CONTENT)),
            ("With sagg video",
             "sagg.apple,video,water.dsagf-hjj",
             "Sagg",
             Article.objects.all(),
             (PRICE_FOR_TOPIC
              + 2 * PRICE_FOR_TITLE + 5 * PRICE_FOR_CONTENT)),
            ("With sagg video",
             "sagg.apple,video,water.dsagf-hjj",
             "Sagg dsagf",
             Article.objects.all(),
             (2 * PRICE_FOR_TOPIC
              + 2 * PRICE_FOR_TITLE + 5 * PRICE_FOR_CONTENT)),

        ]
    )
    def test_articles_list_search_not_null(
            self,
            title,
            content,
            topic,
            res_return,
            relevance
    ):
        Article.objects.create(
            title=title,
            content=content,
            published_date="2020-10-15",
            topic=Topic.objects.create(name=topic)
        )
        response = self.client.get(
            reverse("newspaper:articles-list"),
            {"relevant_search": self.serch_str}
        )
        self.assertEqual(
            response.context_data["article_list"],
            list(res_return)
        )
        if res_return:
            self.assertEqual(
                response.context_data["article_list"][0].relevance,
                relevance
            )
