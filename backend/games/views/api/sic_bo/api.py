import secrets

from django.http.response import JsonResponse
from django.views.decorators.http import require_http_methods

from core.helpers import BodyContent
from core.models import get_or_none
from games import models
from games.decorators import wallet_required
from games.views.api.api import get_vault
from games.views.api.dice import get_wins

wins = {
    'small': 1,
    'big': 1,
    'double-1': 11,
    'double-2': 11,
    'double-3': 11,
    'double-4': 11,
    'double-5': 11,
    'double-6': 11,
    'triple-1': 180,
    'triple-2': 180,
    'triple-3': 180,
    'triple-4': 180,
    'triple-5': 180,
    'triple-6': 180,
    'triple-any': 30,
    'total-4': 60,
    'total-5': 20,
    'total-6': 18,
    'total-7': 12,
    'total-8': 8,
    'total-9': 6,
    'total-10': 6,
    'total-11': 6,
    'total-12': 6,
    'total-13': 8,
    'total-14': 12,
    'total-15': 18,
    'total-16': 20,
    'total-17': 60,
    'pair-1-2': 6,
    'pair-1-3': 6,
    'pair-1-4': 6,
    'pair-1-5': 6,
    'pair-1-6': 6,
    'pair-2-3': 6,
    'pair-2-4': 6,
    'pair-2-5': 6,
    'pair-2-6': 6,
    'pair-3-4': 6,
    'pair-3-5': 6,
    'pair-3-6': 6,
    'pair-4-5': 6,
    'pair-4-6': 6,
    'pair-5-6': 6,
}


def create_session(dice=None, bets=None, initial_bet=None, bet=None, possible_wins=None, session=None):
    return {
        "dice": dice if dice is not None else session["dice"],
        "bets": bets if bets is not None else session["bet"],
        "initialBet": initial_bet if initial_bet is not None else session["initial_bet"],
        "bet": bet if bet is not None else session["bet"],
        "possibleWins": possible_wins if possible_wins is not None else session["possible_wins"],
    }


def session_json(session):
    return {
        "dice": session["dice"],
        "bets": session["bets"],
        "initialBet": session["initialBet"],
        "bet": session["bet"],
        "possibleWins": session["possibleWins"],
    }


def update_wallet(wallet, bet):
    wallet.balance += bet
    wallet.save()

    vault, _ = get_vault()
    vault.balance += bet * -1
    vault.save()


@wallet_required
@require_http_methods(["POST"])
def start(request):
    wallet = get_or_none(models.Wallet, wallet_id=request.session['wallet_id'])
    post_data = BodyContent(request)

    if not wallet:
        return JsonResponse({"error": "games.game.sic_bo.errors.session_expired"}, status=400)

    if not post_data or not post_data.get('bets'):
        return JsonResponse({"error": "games.game.sic_bo.errors.invalid_request"}, status=400)

    bets = post_data.get('bets')

    if not isinstance(bets, dict) or len(bets) < 1:
        return JsonResponse({"error": "games.game.sic_bo.errors.invalid_request"}, status=400)

    total_bet = 0
    for bet, amount in bets.items():
        total_bet += amount

    if total_bet <= 0 or total_bet > wallet.balance or total_bet > 500:
        return JsonResponse({"error": "games.game.sic_bo.errors.invalid_bet"}, status=400)

    update_wallet(wallet, -total_bet)

    dice = [secrets.randbelow(6) + 1 for _ in range(3)]
    possible_wins = get_wins(dice)

    won = 0

    for bet, amount in bets.items():
        if bet in possible_wins:
            if "face" not in bet:
                won += amount + amount * wins[bet]
            else:
                amount_turn_in_wins = 0
                for win in possible_wins:
                    if bet == win:
                        amount_turn_in_wins += 1
                won += amount + amount * amount_turn_in_wins

    if won > 0:
        update_wallet(wallet, won)

    session = create_session(dice, bets, total_bet, won, possible_wins)

    return JsonResponse(session_json(session))
