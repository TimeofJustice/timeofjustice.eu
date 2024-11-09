from django.http import HttpResponseRedirect


def page_not_found(request, *args, **kwargs):
    return HttpResponseRedirect(f'/error/404')


def server_error(request, *args, **kwargs):
    return HttpResponseRedirect(f'/error/500')


def permission_denied(request, *args, **kwargs):
    return HttpResponseRedirect(f'/error/403')


def bad_request(request, *args, **kwargs):
    return HttpResponseRedirect(f'/error/400')