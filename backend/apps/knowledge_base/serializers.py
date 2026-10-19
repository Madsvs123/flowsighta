from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.knowledge_base.models import Article, ArticleCategory, ArticleRevision


class ArticleCategorySerializer(TenantSerializer):
    parent_name = serializers.CharField(source="parent.name", read_only=True)
    article_count = serializers.SerializerMethodField()

    class Meta:
        model = ArticleCategory
        fields = ("id", "name", "parent", "parent_name", "article_count", "created_at")
        read_only_fields = ("id", "created_at")

    def get_article_count(self, obj):
        return obj.articles.count()


class ArticleSerializer(TenantSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    author_name = serializers.CharField(source="author.first_name", read_only=True)
    revision_count = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            "id",
            "title",
            "body",
            "category",
            "category_name",
            "status",
            "author",
            "author_name",
            "views",
            "revision_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "views", "created_at", "updated_at")

    def get_revision_count(self, obj):
        return obj.revisions.count()


class ArticleRevisionSerializer(TenantSerializer):
    article_title = serializers.CharField(source="article.title", read_only=True)
    revised_by_name = serializers.CharField(source="revised_by.email", read_only=True)

    class Meta:
        model = ArticleRevision
        fields = (
            "id",
            "article",
            "article_title",
            "version",
            "notes",
            "revised_by",
            "revised_by_name",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
