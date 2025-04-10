import uuid
from django.http.response import JsonResponse
from core.models import get_or_none
from ..cards import CardDeck, is_higher, is_lower, is_equal, card_to_string
from .... import models
from ....decorators import wallet_required


def create_session(session_id=None, deck=None, card=None, bet=None, initial_bet=None, session=None):
    return {
        "session_id": session_id if session_id is not None else session["session_id"],
        "deck": deck if deck is not None else session["deck"],
        "card": card if card is not None else session["card"],
        "bet": bet if bet is not None else session["bet"],
        "initial_bet": initial_bet if initial_bet is not None else session["initial_bet"],
    }


def session_json(session):
    return {
        "session_id": session["session_id"],
        "cards_left": len(session["deck"]) if session["deck"] else 0,
        "card": card_to_string(session["card"]),
        "bet": session["bet"],
        "initial_bet": session["initial_bet"],
    }


def update_wallet(wallet, bet):
    wallet.balance += bet
    wallet.save()


@wallet_required
def start(request, bet):
    wallet = get_or_none(models.Wallet, wallet_id=request.session['wallet_id'])

    if not wallet:
        return JsonResponse({"error": "casino.game.higher_lower.errors.session_expired"}, status=400)

    if bet <= 0 or bet > wallet.balance or 100 < bet:
        return JsonResponse({"error": "casino.game.higher_lower.errors.invalid_bet"}, status=400)

    update_wallet(wallet, -bet)

    deck = CardDeck()
    card = deck.draw()

    if card is None:
        return JsonResponse({"error": "casino.game.higher_lower.errors.deck_empty"}, status=400)

    request.session['higher_lower_session'] = create_session(uuid.uuid4().hex, deck.remaining(), card, bet, bet)

    return JsonResponse(session_json(request.session['higher_lower_session']))


def process_turn(request, session_id, comparison_function, multiplier):
    session = request.session.get('higher_lower_session', None)

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "casino.game.higher_lower.errors.session_expired"}, status=400)

    deck = CardDeck(session['deck'])
    card = deck.draw()

    if card is None:
        return JsonResponse({"error": "casino.game.higher_lower.errors.deck_empty"}, status=400)

    if len(deck.remaining()) == 0:
        bet = session['bet'] + session['initial_bet'] * 100000 if comparison_function(card, session['card']) else 0
    else:
        bet = session['bet'] + session['initial_bet'] * multiplier if comparison_function(card, session['card']) else 0

    request.session['higher_lower_session'] = create_session(deck=deck.remaining(), card=card, bet=bet, session=session)

    if bet <= 0:
        return end(request)

    return JsonResponse(session_json(request.session['higher_lower_session']))


@wallet_required
def higher(request, session_id):
    return process_turn(request, session_id, is_higher, 1)


@wallet_required
def lower(request, session_id):
    return process_turn(request, session_id, is_lower, 1)


@wallet_required
def draw(request, session_id):
    return process_turn(request, session_id, is_equal, 8)


@wallet_required
def leave(request, session_id):
    session = request.session.get('higher_lower_session', None)

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "casino.game.higher_lower.errors.session_expired"}, status=400)

    if session['bet'] == session['initial_bet']:
        return JsonResponse({"error": "casino.game.higher_lower.errors.invalid_round"}, status=400)

    deck = CardDeck(session['deck'])
    card = deck.draw()

    if card is None:
        card = session['card']

    request.session['higher_lower_session'] = create_session(deck=deck.remaining(), card=card, session=session)

    return end(request)


def end(request):
    session = request.session.get('higher_lower_session', None)
    wallet = get_or_none(models.Wallet, wallet_id=request.session['wallet_id'])

    if not session:
        return JsonResponse({"error": "casino.game.higher_lower.errors.session_expired"}, status=400)

    if session['bet'] > 0:
        update_wallet(wallet, session['bet'])

    del request.session['higher_lower_session']

    return JsonResponse(session_json(session))
