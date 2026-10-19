from django.contrib import admin

from apps.organizations.models import Customer, Membership, Organization, Region, Role, Team, Warehouse

admin.site.register(Organization)
admin.site.register(Region)
admin.site.register(Team)
admin.site.register(Role)
admin.site.register(Membership)
admin.site.register(Region)
