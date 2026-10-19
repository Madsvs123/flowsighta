from rest_framework.routers import DefaultRouter

from apps.employees.views import DepartmentViewSet, EmployeeViewSet, EmploymentHistoryViewSet

router = DefaultRouter()
router.register("employees", EmployeeViewSet, basename="employee")
router.register("departments", DepartmentViewSet, basename="departments")
router.register("employment-histories", EmploymentHistoryViewSet, basename="employmenthistory")

urlpatterns = router.urls
