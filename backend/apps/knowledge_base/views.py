from django.db import models
from django.db.models import Sum
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.knowledge_base.models import Article, ArticleCategory, ArticleRevision
from apps.knowledge_base.serializers import (
    ArticleCategorySerializer,
    ArticleRevisionSerializer,
    ArticleSerializer,
)


class ArticleCategoryViewSet(TenantViewSet):
    queryset = ArticleCategory.objects.select_related("parent").prefetch_related("articles")
    serializer_class = ArticleCategorySerializer
    required_permission = "knowledge_base.view"
    write_permission = "knowledge_base.manage"
    search_fields = ["name"]
    filterset_fields = ["parent"]


class ArticleViewSet(TenantViewSet):
    queryset = Article.objects.select_related("category", "author").prefetch_related("revisions")
    serializer_class = ArticleSerializer
    required_permission = "knowledge_base.view"
    write_permission = "knowledge_base.manage"
    search_fields = ["title", "body", "author__email"]
    filterset_fields = ["status", "category", "author"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        top = list(
            qs.filter(status=Article.Status.PUBLISHED)
            .order_by("views")[:5]
            .values_list("title", "views")
        )
        return Response(
            {
                "articles": qs.count(),
                "draft": qs.filter(status=Article.Status.DRAFT).count(),
                "published": qs.filter(status=Article.Status.PUBLISHED).count(),
                "archived": qs.filter(status=Article.Status.ARCHIVED).count(),
                "categories": ArticleCategory.objects.filter(organization=request.organization).count(),
                "total_views": float(
                    qs.aggregate(total=Sum("views"))["total"] or 0
                ),
                "top_articles": [{"title": t, "views": v} for t, v in top],
            }
        )

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        article = self.get_object()
        if article.status != Article.Status.DRAFT:
            raise ValidationError("Only draft articles can be published.")
        article.status = Article.Status.PUBLISHED
        article.updated_by = request.user
        article.save(update_fields=["status", "updated_at", "updated_by"])
        return Response(self.get_serializer(article).data)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None)
        article = self.get_object()
        if article.status != Article.Status.PUBLISHED:
            raise ValidationError("Only published articles can be archived.")
        article.status = Article.Status.ARCHIVED
        article.updated_by = request.user
        article.save(update_fields=["status", "updated_at", "updated_by"])
        return Response(self.get_serializer(article).data)

    @action(detail=True, methods=["post"])
    def record_view(self, request, pk=None):
        article = self.get_object()
        Article.objects.filter(pk=article.pk).update(views=models.F("views") + 1)
        article.refresh_from_db(fields=["views"])
        return Response(self.get_serializer(article).data)


class ArticleRevisionViewSet(TenantViewSet):
    queryset = ArticleRevision.objects.select_related("article", "revised_by")
    serializer_class = ArticleRevisionSerializer
    required_permission = "knowledge_base.view"
    write_permission = "knowledge_base.manage"
    search_fields = ["article__title", "version", "notes"]
    filterset_fields = ["article", "revised_by"]

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization, revised_by=self.request.user)
