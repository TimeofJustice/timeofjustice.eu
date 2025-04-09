import uuid
from random import shuffle

from django.http.response import JsonResponse

from core.models import get_or_none
from .... import models
from ....decorators import wallet_required

CARD_SET = [
    "2_of_clubs",
    "3_of_clubs",
    "4_of_clubs",
    "5_of_clubs",
    "6_of_clubs",
    "7_of_clubs",
    "8_of_clubs",
    "9_of_clubs",
    "10_of_clubs",
    "jack_of_clubs",
    "queen_of_clubs",
    "king_of_clubs",
    "ace_of_clubs",
    "2_of_diamonds",
    "3_of_diamonds",
    "4_of_diamonds",
    "5_of_diamonds",
    "6_of_diamonds",
    "7_of_diamonds",
    "8_of_diamonds",
    "9_of_diamonds",
    "10_of_diamonds",
    "jack_of_diamonds",
    "queen_of_diamonds",
    "king_of_diamonds",
    "ace_of_diamonds",
    "2_of_hearts",
    "3_of_hearts",
    "4_of_hearts",
    "5_of_hearts",
    "6_of_hearts",
    "7_of_hearts",
    "8_of_hearts",
    "9_of_hearts",
    "10_of_hearts",
    "jack_of_hearts",
    "queen_of_hearts",
    "king_of_hearts",
    "ace_of_hearts",
    "2_of_spades",
    "3_of_spades",
    "4_of_spades",
    "5_of_spades",
    "6_of_spades",
    "7_of_spades",
    "8_of_spades",
    "9_of_spades",
    "10_of_spades",
    "jack_of_spades",
    "queen_of_spades",
    "king_of_spades",
    "ace_of_spades",
]

RANK_ORDER = [
    "2", "3", "4", "5", "6", "7", "8", "9", "10",
    "jack", "queen", "king", "ace"
]

def get_rank(card_name):
    return card_name.split("_of_")[0]

def compare_cards(old_card, new_card):
    old_rank = get_rank(old_card)
    new_rank = get_rank(new_card)

    old_value = RANK_ORDER.index(old_rank)
    new_value = RANK_ORDER.index(new_rank)

    if new_value > old_value:
        return "higher"
    elif new_value < old_value:
        return "lower"
    else:
        return "draw"

def draw_card(deck):
    if deck and len(deck) > 0:
        card = deck.pop(0)
        return card, deck
    return None

def create_session(id=None, deck=None, card=None, bet=None, initial_bet=None, session=None):
    return {
        "session_id": id if id is not None else session["session_id"],
        "deck": deck if deck is not None else session["deck"],
        "card": card if card is not None else session["card"],
        "bet": bet if bet is not None else session["bet"],
        "initial_bet": initial_bet if initial_bet is not None else session["initial_bet"],
    }

def session_json(session):
    return {
        "session_id": session["session_id"],
        "cards_left": len(session["deck"]) if session["deck"] else 0,
        "card": session["card"],
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

    left_over_cards = CARD_SET.copy()
    shuffle(left_over_cards)

    result = draw_card(left_over_cards)
    if result is None:
        return JsonResponse({"error": "casino.game.higher_lower.errors.deck_empty"}, status=400)
    card, left_over_cards = result

    request.session['higher_lower_session'] = create_session(uuid.uuid4().hex, left_over_cards, card, bet, bet)

    return JsonResponse(session_json(request.session['higher_lower_session']))


@wallet_required
def higher(request, session_id):
    session = request.session.get('higher_lower_session', None)

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "casino.game.higher_lower.errors.session_expired"}, status=400)

    result = draw_card(session['deck'])
    if result is None:
        return JsonResponse({"error": "casino.game.higher_lower.errors.deck_empty"}, status=400)
    card, left_over_cards = result

    bet = session['bet'] + session['initial_bet'] if compare_cards(session['card'], card) == "higher" else 0

    request.session['higher_lower_session'] = create_session(deck=left_over_cards, card=card, bet=bet, session=session)

    if bet <= 0:
        return end(request)

    return JsonResponse(session_json(request.session['higher_lower_session']))


@wallet_required
def lower(request, session_id):
    session = request.session.get('higher_lower_session', None)

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "casino.game.higher_lower.errors.session_expired"}, status=400)

    result = draw_card(session['deck'])
    if result is None:
        return JsonResponse({"error": "casino.game.higher_lower.errors.deck_empty"}, status=400)
    card, left_over_cards = result

    bet = session['bet'] + session['initial_bet'] if compare_cards(session['card'], card) == "lower" else 0

    request.session['higher_lower_session'] = create_session(deck=left_over_cards, card=card, bet=bet, session=session)

    if bet <= 0:
        return end(request)

    return JsonResponse(session_json(request.session['higher_lower_session']))


@wallet_required
def draw(request, session_id):
    session = request.session.get('higher_lower_session', None)

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "casino.game.higher_lower.errors.session_expired"}, status=400)

    result = draw_card(session['deck'])
    if result is None:
        return JsonResponse({"error": "casino.game.higher_lower.errors.deck_empty"}, status=400)
    card, left_over_cards = result

    bet = session['bet'] + session['initial_bet'] * 8 if compare_cards(session['card'], card) == "draw" else 0

    request.session['higher_lower_session'] = create_session(deck=left_over_cards, card=card, bet=bet, session=session)

    if bet <= 0:
        return end(request)

    return JsonResponse(session_json(request.session['higher_lower_session']))


@wallet_required
def leave(request, session_id):
    session = request.session.get('higher_lower_session', None)

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "casino.game.higher_lower.errors.session_expired"}, status=400)

    if session['bet'] == session['initial_bet']:
        return JsonResponse({"error": "casino.game.higher_lower.errors.invalid_round"}, status=400)

    return end(request)


def end(request):
    session = request.session.get('higher_lower_session', None)
    wallet = get_or_none(models.Wallet, wallet_id=request.session['wallet_id'])

    if not session:
        return JsonResponse({"error": "casino.game.higher_lower.errors.session_expired"}, status=400)

    if session['bet'] > 0:
        update_wallet(wallet, session['bet'] if len(session['deck']) > 0 else session['bet'] + session['initial_bet'] * 100000)

    del request.session['higher_lower_session']

    return JsonResponse(session_json(session))
