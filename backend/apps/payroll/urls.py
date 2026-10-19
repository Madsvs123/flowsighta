from rest_framework.routers import DefaultRouter

from apps.payroll.views import (
    PayrollReportViewSet,
    PayrollRunViewSet,
    PayslipViewSet,
    SalaryComponentViewSet,
)

router = DefaultRouter()
router.register("payroll", PayrollRunViewSet, basename="payrollrun")
router.register("salary-components", SalaryComponentViewSet, basename="salarycomponent")
router.register("payslips", PayslipViewSet, basename="payslip")
router.register("payroll-report", PayrollReportViewSet, basename="payrollreport")

urlpatterns = router.urls
