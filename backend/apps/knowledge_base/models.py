from django.conf import settings
from django.db import models

from apps.core.models import AuditedModel, TenantModel


class ArticleCategory(TenantModel):
    name = models.CharField(max_length=120)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children"
    )

    class Meta:
        ordering = ["name"]
        unique_together = ("organization", "name")

    def __str__(self):
        return self.name


class Article(TenantModel, AuditedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    category = models.ForeignKey(
        ArticleCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name="articles"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="authored_articles",
    )
    views = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [models.Index(fields=["organization", "status", "category"])]

    def __str__(self):
        return self.title


class ArticleRevision(TenantModel):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="revisions"
    )
    version = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    revised_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="article_revisions",
    )

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("organization", "article", "version")

    def __str__(self):
        return f"{self.article.title} v{self.version}"
