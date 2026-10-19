from celery import shared_task

from apps.dashboards.models import WidgetDataSource


@shared_task
def refresh_dashboard_widgets()
    """Touch every widget data source so dashboards re-fetch their data."""
    count = WidgetDataSource.objects.count()
    for source in WidgetDataSource.objects.all().iterator():
        source.save(update_fields=["updated_at"])
    return {"data_sources_refreshed": count}


@shared_task
def reset_dashboard_defaults():
    """Clear the is_default flag on dashboards that have no widgets."""
    from apps.dashboards.models import Dashboard

    cleared = 0
    for dashboard in Dashboard.objects.filter(is_default=True):
        if not dashboard.widgets.exists():
            dashboard.is_default = False
            dashboard.save(update_fields=["is_default", "updated_at"])
            cleared += 1
    return {"defaults_cleared": cleared}
