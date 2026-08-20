from django.http.response import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from core.helpers import BodyContent, get_or_none
from games import models
from games.decorators import wallet_required
from games.vault import get_vault
from games.wallet import get_wallet, revealable_phrase, stop_revealing_phrase


@wallet_required
@require_http_methods(["POST"])
def update(request):
    """Updates the name, the avatar, or both — whichever the body contains."""
    wallet = get_wallet(request)
    post_data = BodyContent(request)

    if not post_data:
        return JsonResponse({"error": "games.main.errors.invalid_request"}, status=400)

    name = post_data.get("name")
    avatar_id = post_data.get("avatarId", False)

    if name is None and avatar_id is False:
        return JsonResponse({"error": "games.main.errors.invalid_request"}, status=400)

    if name is not None:
        if not (isinstance(name, str) and 3 <= len(name) <= 32 and name.isalnum()):
            return JsonResponse({"error": "games.main.errors.name_invalid"}, status=400)

        wallet.name = name

    if avatar_id is not False:
        # An explicit null clears the avatar again.
        if avatar_id is None:
            wallet.avatar = None
        else:
            avatar = get_or_none(models.Avatar, id=avatar_id)

            if not avatar:
                return JsonResponse({"error": "games.main.errors.avatar_invalid"}, status=400)

            wallet.avatar = avatar

    wallet.save()

    # Saving the settings is the end of first-time setup, so the phrase stops
    # being offered from here on.
    stop_revealing_phrase(request)

    return JsonResponse({"name": wallet.name, "avatar": wallet.avatar.json() if wallet.avatar else None})


@wallet_required
def recovery_phrase(request):
    """
    The phrase, but only while it is still new. It is the only credential, so it
    is shown once during setup and never served again.
    """
    reveal = revealable_phrase(request)

    return JsonResponse({"recoveryPhrase": reveal.get("phrase"), "reason": reveal.get("reason")})


@wallet_required
def avatars(request):
    """The avatars players can choose from, for the picker."""
    return JsonResponse({"avatars": [avatar.json() for avatar in models.Avatar.objects.all()]})


@wallet_required
@require_http_methods(["POST"])
def redeem(request):
    wallet = get_wallet(request)

    if wallet.refresh_streak() >= 1:
        wallet.days_played += 1
        wallet.last_visit = timezone.now().date()
        reward = 50

        if wallet.days_played in [3, 4]:
            reward = 100
        elif wallet.days_played > 4:
            reward = 200

        wallet.balance += reward
        wallet.save()

        last_visit = timezone.datetime.combine(wallet.last_visit, timezone.datetime.min.time()) if wallet.last_visit else timezone.now()
        next_bonus = last_visit + timezone.timedelta(days=1)

        return JsonResponse({"reward": reward, "nextBonus": next_bonus.strftime("%Y-%m-%dT%H:%M:%SZ")})

    return JsonResponse({"error": "games.main.errors.already_claimed"}, status=400)


def get_leaderboard(wallet):
    leaderboard = models.Wallet.objects.order_by("-balance")
    leaderboard = list(leaderboard)
    own_index = leaderboard.index(wallet)

    return leaderboard, own_index


@wallet_required
def leaderboard(request):
    wallet = get_wallet(request)

    leaderboard, own_index = get_leaderboard(wallet)

    return JsonResponse(
        {
            "leaderboard": [wallet.public_json() for wallet in leaderboard[:5]],
            "ownPosition": own_index + 1,
        }
    )


@wallet_required
def vault(request):
    vault, vault_reset = get_vault()

    return JsonResponse(
        {
            "vault": vault.balance,
            "vaultReset": vault_reset.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
    )
