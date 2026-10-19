from django.contrib import admin

from apps.knowledge_base.models import Article, ArticleCategory, ArticleRevisions

admin.site.register(ArticleCategory)
admin.site.register(Article)
admin.site.register(ArticleRevision)
