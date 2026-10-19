from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.approved_lists.views import ApprovedListViewSet, ApprovedSupplierViewSet

router = DefaultRouter()
router.register("lists", ApprovedListViewSet, basename="approved-list")
router.register("approved-suppliers", ApprovedListViewSet, basename="approved-supplier")

urlpatterns = [
    path("approved-lists/", include(router.urls)),
]
