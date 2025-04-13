import random
import uuid
from django.http.response import JsonResponse
from django.views.decorators.http import require_http_methods

from core.helpers import BodyContent
from core.models import get_or_none
from ..dice import get_wins
from ..user import get_vault
from .... import models
from ....decorators import wallet_required


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
    'pair-5-6': 6
}


def create_session(session_id=None, dice=None, bet=None, initial_bet=None, session=None):
    return {
        "session_id": session_id if session_id is not None else session["session_id"],
        "dice": dice if dice is not None else session["dice"],
        "bet": bet if bet is not None else session["bet"],
        "initial_bet": initial_bet if initial_bet is not None else session["initial_bet"],
    }


def session_json(session):
    return {
        "session_id": session["session_id"],
        "dice": session["dice"],
        "bet": session["bet"],
        "initial_bet": session["initial_bet"],
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
        return JsonResponse({"error": "casino.game.sic_bo.errors.session_expired"}, status=400)

    if not post_data or not post_data.get('bet'):
        return JsonResponse({"error": "casino.game.sic_bo.errors.invalid_request"}, status=400)

    bet = post_data.get('bet')

    if bet <= 0 or bet > wallet.balance or 100 < bet:
        return JsonResponse({"error": "casino.game.sic_bo.errors.invalid_bet"}, status=400)

    update_wallet(wallet, -bet)

    request.session['sic_bo_session'] = create_session(uuid.uuid4().hex, [], bet, bet)

    return JsonResponse(session_json(request.session['sic_bo_session']))


@wallet_required
@require_http_methods(["POST"])
def process_turn(request, turn):
    session = request.session.get('sic_bo_session', None)
    post_data = BodyContent(request)
    turn = turn.lower()

    if not post_data or not post_data.get('session'):
        return JsonResponse({"error": "casino.game.sic_bo.errors.invalid_request"}, status=400)

    session_id = post_data.get('session')

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "casino.game.sic_bo.errors.session_expired"}, status=400)

    dices = [ random.randint(1, 6) for _ in range(3) ]
    possible_wins = get_wins(dices)

    if turn in possible_wins:
        if "face" not in turn:
            bet = session['bet'] + session['initial_bet'] * wins[turn]
        else:
            amount_turn_in_wins = 0
            for win in possible_wins:
                if turn == win:
                    amount_turn_in_wins += 1
            bet = session['bet'] + session['initial_bet'] * amount_turn_in_wins
    else:
        bet = 0

    request.session['sic_bo_session'] = create_session(session=request.session['sic_bo_session'], dice=dices, bet=bet)

    return end(request)


def end(request):
    session = request.session.get('sic_bo_session', None)
    wallet = get_or_none(models.Wallet, wallet_id=request.session['wallet_id'])

    if not session:
        return JsonResponse({"error": "casino.game.sic_bo.errors.session_expired"}, status=400)

    if session['bet'] > 0:
        update_wallet(wallet, session['bet'])

    del request.session['sic_bo_session']

    return JsonResponse(session_json(session))
