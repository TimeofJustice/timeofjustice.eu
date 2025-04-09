import json

from django.conf import settings
from django.http.response import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie

from casino import models
from casino.decorators import wallet_required
from core.models import get_or_none


class BodyContent:
    def __init__(self, request):
        body_unicode = request.body.decode('utf-8')

        self.body = None

        try:
            self.body = json.loads(body_unicode)
        except:
            pass

    def get(self, key):
        if self.body is None:
            return None

        return self.body.get(key)


@ensure_csrf_cookie
@wallet_required
def change(request):
    wallet = get_or_none(models.Wallet, wallet_id=request.session['wallet_id'])

    if not wallet:
        return JsonResponse({"error": "casino.main.errors.wallet_not_found"}, status=404)

    post_data = BodyContent(request)

    if post_data:
        name = post_data.get('name')

        if name and 3 <= len(name) <= 32 and name.isalnum():
            wallet.name = name
            wallet.save()
        else:
            return JsonResponse({"error": "casino.main.errors.name_invalid"}, status=400)
    else:
        return JsonResponse({"error": "casino.main.errors.invalid_request"}, status=400)

    return JsonResponse({"name": wallet.name})
