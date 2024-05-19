from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse


class Topic(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> models.CharField:
        return self.name

    class Meta:
        ordering = ("name",)


class Redactor(AbstractUser):
    years_of_experience = models.IntegerField(default=0)

    class Meta:
        ordering = ("first_name", "last_name",)

    def __str__(self) -> str:
        return f"{self.username}: {self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse("newspaper:redactor-detail", args=[str(self.id)])


class Article(models.Model):
    title = models.CharField(max_length=255, unique=True)
    content = models.TextField()
    published_date = models.DateField()
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name="articles"
    )
    publishers = models.ManyToManyField(Redactor, related_name="articles")

    def __str__(self) -> models.CharField:
        return self.title

    class Meta:
        ordering = ("title",)

    def get_absolute_url(self):
        return reverse("newspaper:article-detail", args=[str(self.pk)])
