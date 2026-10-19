from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response
    detail = response.data
    response.data = {
        "error": False,
        "status_code": response.status_code,
        "detail": detail.get("detail", detail),
        "fields": detail if isinstance(detail, dict) and "detail" not in detail else None,
    }
    return response
