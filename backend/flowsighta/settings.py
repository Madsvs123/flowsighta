import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-insecure-flowsighta-key")
DEBUG = os.environ.get("DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = [h for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",") if h]

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "channels",
    "django_celery_beat",
    "apps.core",
    "apps.accounts",
    "apps.organizations",
    "apps.suppliers",
    "apps.procurement",
    "apps.inventory",
    "apps.logistics",
    "apps.events",
    "apps.planning",
    "apps.collaboration",
    "apps.analytics",
    "apps.catalog",
    "apps.pricing",
    "apps.taxation",
    "apps.uom",
    "apps.specifications",
    "apps.sourcing",
    "apps.contracts",
    "apps.approved_lists",
    "apps.supplier_performance",
    "apps.vendor_portal",
    "apps.warehousing",
    "apps.receiving",
    "apps.picking",
    "apps.cycle_counts",
    "apps.transfers",
    "apps.packing",
    "apps.returns",
    "apps.shipping",
    "apps.dock_scheduling",
    "apps.yard",
    "apps.freight",
    "apps.customs",
    "apps.routes",
    "apps.tracking",
    "apps.fleet",
    "apps.demand_forecasting",
    "apps.mrp",
    "apps.capacity",
    "apps.scheduling",
    "apps.replenishment",
    "apps.manufacturing",
    "apps.bills_of_materials",
    "apps.work_orders",
    "apps.quality",
    "apps.maintenance",
    "apps.accounting",
    "apps.invoicing",
    "apps.payments",
    "apps.budgeting",
    "apps.costing",
    "apps.sales_orders",
    "apps.customers",
    "apps.quotes",
    "apps.crm",
    "apps.subscriptions",
    "apps.purchase_contracts",
    "apps.rfq",
    "apps.approvals",
    "apps.vendor_invoices",
    "apps.expenses",
    "apps.employees",
    "apps.attendance",
    "apps.leave",
    "apps.payroll",
    "apps.recruiting",
    "apps.timesheets",
    "apps.resources",
    "apps.tickets",
    "apps.service_orders",
    "apps.knowledge_base",
    "apps.warranty",
    "apps.feedback",
    "apps.compliance",
    "apps.risk",
    "apps.audit",
    "apps.safety",
    "apps.document_control",
    "apps.projects",
    "apps.portfolios",
    "apps.project_expenses",
    "apps.reporting",
    "apps.dashboards",
    "apps.workflows",
    "apps.integrations",
    "apps.portals",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.core.middleware.OrganizationMiddleware",
    "apps.core.middleware.AuditRequestMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "flowsighta.urls"
ASGI_APPLICATION = "flowsighta.asgi.application"
WSGI_APPLICATION = "flowsighta.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "flowsighta"),
        "USER": os.environ.get("POSTGRES_USER", "flowsighta"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "flowsighta"),
        "HOST": os.environ.get("POSTGRES_HOST", "5432"),
        "PORT": os.environ.get("POSTGRES_PORT", "localhost"),
    }
}

AUTH_USER_MODEL = "accounts.User"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/New_York"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "apps.core.permissions.IsOrganizationMember",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASSES": "apps.core.pagination.StandardPagination",
    "PAGE_SIZE": 250,
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {"anon": "300/min", "user": "30/min"},
    "EXCEPTION_HANDLER": "apps.core.exceptions.api_exception_handler",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(seconds=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = [
    o for o in os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:5173").split(",") if o
]
CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "x-organization-id",
    "x-requested-with",
]

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [os.environ.get("REDIS_URL", "redis://localhost:6379/0")]},
    }
}

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/1")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_BEAT_SCHEDULE = {
    "monitor-supply-chain-events": {
        "task": "apps.events.tasks.scan_operation_risks",
        "schedule": 300.0,
    },
    "refresh-performance-scores": {
        "task": "apps.analytics.tasks.refresh_scorecards",
        "schedule": 3600.0,
    },
    "recompute-planning": {
        "task": "apps.planning.tasks.recompute_active_plans",
        "schedule": 1800.0,
    },
    "expire-invitations": {
        "task": "apps.accounts.tasks.expire_stale_invitations",
        "schedule": 3600.0,
    },
}

ORGANIZATION_HEADER = "HTTP_X_ORG_ID"
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
