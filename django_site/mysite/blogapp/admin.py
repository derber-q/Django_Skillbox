from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest


from .models import Author, Category, Tag, Article
from django.contrib import admin

# Register your models here.


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):

    list_display = 'pk', 'title', 'content', 'pub_date', 'author'



@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):

    list_display = 'pk', 'name', 'bio'
@admin.register(Category)

class CategoryAdmin(admin.ModelAdmin):

    list_display = 'pk', 'name'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = 'pk', 'name'

