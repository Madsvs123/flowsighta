from django.contrib import admin

from apps.budgeting.models import Budget, BudgetActual, BudgetLine, CostCenter

admin.site.register(CostCenter)
admin.site.register(Budget)
admin.site.register(BudgetActual)
admin.site.register(BudgetActual)
