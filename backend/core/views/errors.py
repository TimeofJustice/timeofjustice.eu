from core.views import pages


def bad_request(request, *args, **kwargs):
    return pages.error(request, 400)

def permission_denied(request, *args, **kwargs):
    return pages.error(request, 403)

def page_not_found(request, *args, **kwargs):
    return pages.error(request, 404)

def server_error(request, *args, **kwargs):
    return pages.error(request, 500)
