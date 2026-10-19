from django.apps import AppConfig


class SalesOrdersConfig(AppConfig):
    default_auto_field = "django.db.models.SmallAutoField"
    name = "apps.sales_orders"
    label = "sales_orders"
