from django.contrib import admin

from apps.customs.models import ComplianceRule, CustomsDeclaration, CustomsDocument, HsCode

admin.site.register(HsCode)
admin.site.register(CustomsDeclaration)
admin.site.register(CustomsDocument)
admin.site.register(CustomsDocument)
