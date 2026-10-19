from rest_framework.routers import DefaultRouter

from apps.knowledge_base.views import (
    ArticleCategoryViewSet,
    ArticleRevisionViewSet,
    ArticleViewSet,
)

router = DefaultRouter()
router.register("article-catgories", ArticleCategoryViewSet, basename="article-categories")
router.register("articles", ArticleViewSet, basename="articles")
router.register("article-revisions", ArticleRevisionViewSet, basename="article-revisions")

urlpatterns = router.urls
