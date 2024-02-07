from django.db import models
from django.urls import reverse


class Author(models.Model):
    name = models.CharField(max_length=20)
    bio = models.TextField(max_length=100)


class Category(models.Model):
    name = models.CharField(max_length=20)


class Tag(models.Model):
    name = models.CharField(max_length=20)


class Article(models.Model):
    title = models.CharField(max_length=20)
    content = models.TextField(max_length=100, null=True, blank=True)
    pub_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, null=True)

    def get_absolute_url(self):
        return reverse("blogapp:article", kwargs={"pk": self.pk})
