from django.conf import settings


def base_url(request):
    """
    Return a BASE_URL template context for the current request.
    """
    if hasattr(settings, "BASE_URL"):
        return {"BASE_URL": settings.BASE_URL}
    scheme = "https://" if request.is_secure() else "http://"
    return {"BASE_URL": scheme + request.get_host()}
