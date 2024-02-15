from django.contrib.syndication.views import Feed
from django.urls import reverse, reverse_lazy
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Article
class ArticleListView(ListView):
    template_name = 'blogapp/blog-list.html'
    queryset = (
        Article.objects
        .defer('content')
        .select_related('author')
        .select_related('category')
        .prefetch_related('tags')
    )
    context_object_name = 'blogs'

class ArticleDetailView(DetailView):
    model = Article


class LatestArticlesFeed(Feed):
    title = "Blog articles (latest)"
    description = "Updates on changes and addition blog articles"
    link = reverse_lazy("blogapp:article-list")

    def items(self):
        return (
        Article.objects
        .defer('content')
        .select_related('author')
        .select_related('category')
        .prefetch_related('tags')[:5]
    )

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content[:20]

