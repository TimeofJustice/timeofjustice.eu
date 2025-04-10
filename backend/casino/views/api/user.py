from django.http.response import JsonResponse

from casino import models
from casino.decorators import wallet_required
from core.helpers import BodyContent
from core.models import get_or_none


@wallet_required
def update(request):
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
