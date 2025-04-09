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

def get_suit(card_name):
    return card_name.split("_of_")[1]

def get_color(card_name):
    color = get_suit(card_name)
    if color == "clubs" or color == "spades":
        return "black"
    else:
        return "red"

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

def is_card_inside(card, card1, card2):
    rank1 = get_rank(card1)
    rank2 = get_rank(card2)

    value1 = RANK_ORDER.index(rank1)
    value2 = RANK_ORDER.index(rank2)

    card_value = RANK_ORDER.index(get_rank(card))

    return value1 < card_value < value2 or value2 < card_value < value1

def draw_card(deck):
    if deck and len(deck) > 0:
        card = deck.pop(0)
        return card, deck
    return None

def create_session(id=None, deck=None, cards=None, bet=None, initial_bet=None, session=None):
    return {
        "session_id": id if id is not None else session["session_id"],
        "deck": deck if deck is not None else session["deck"],
        "cards": cards if cards is not None else session["cards"],
        "bet": bet if bet is not None else session["bet"],
        "initial_bet": initial_bet if initial_bet is not None else session["initial_bet"],
    }

def session_json(session):
    return {
        "session_id": session["session_id"],
        "card": session["cards"][-1] if session["cards"] else None,
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
        return JsonResponse({"error": "casino.game.ride_the_bus.errors.session_expired"}, status=400)

    if bet <= 0 or bet > wallet.balance or 500 < bet:
        return JsonResponse({"error": "casino.game.ride_the_bus.errors.invalid_bet"}, status=400)

    update_wallet(wallet, -bet)

    left_over_cards = CARD_SET.copy()
    shuffle(left_over_cards)

    request.session['ride_the_bus_session'] = create_session(uuid.uuid4().hex, left_over_cards, [], bet, bet)

    return JsonResponse(session_json(request.session['ride_the_bus_session']))


@wallet_required
def red(request, session_id):
    session = request.session.get('ride_the_bus_session', None)

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "casino.game.ride_the_bus.errors.session_expired"}, status=400)

    result = draw_card(session['deck'])
    if result is None:
        return JsonResponse({"error": "casino.game.ride_the_bus.errors.deck_empty"}, status=400)
    card, left_over_cards = result

    bet = session['bet'] * 2 if get_color(card) == "red" else 0

    request.session['ride_the_bus_session'] = create_session(deck=left_over_cards, cards=[card], bet=bet, session=session)

    if bet <= 0:
        return end(request)

    return JsonResponse(session_json(request.session['ride_the_bus_session']))


@wallet_required
def black(request, session_id):
    session = request.session.get('ride_the_bus_session', None)

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "casino.game.ride_the_bus.errors.session_expired"}, status=400)

    result = draw_card(session['deck'])
    if result is None:
        return JsonResponse({"error": "casino.game.ride_the_bus.errors.deck_empty"}, status=400)
    card, left_over_cards = result

    bet = session['bet'] * 2 if get_color(card) == "black" else 0

    request.session['ride_the_bus_session'] = create_session(deck=left_over_cards, cards=[card], bet=bet, session=session)

    if bet <= 0:
        return end(request)

    return JsonResponse(session_json(request.session['ride_the_bus_session']))

@wallet_required
def higher(request, session_id):
    session = request.session.get('ride_the_bus_session', None)

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "casino.game.ride_the_bus.errors.session_expired"}, status=400)

    result = draw_card(session['deck'])
    if result is None:
        return JsonResponse({"error": "casino.game.ride_the_bus.errors.deck_empty"}, status=400)
    card, left_over_cards = result

    bet = session['initial_bet'] * 3 if compare_cards(session['cards'][0], card) == "higher" else 0

    cards = session['cards'] + [card] if session['cards'] else [card]

    request.session['ride_the_bus_session'] = create_session(deck=left_over_cards, cards=cards, bet=bet, session=session)

    if bet <= 0:
        return end(request)

    return JsonResponse(session_json(request.session['ride_the_bus_session']))


@wallet_required
def lower(request, session_id):
    session = request.session.get('ride_the_bus_session', None)

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "casino.game.ride_the_bus.errors.session_expired"}, status=400)

    result = draw_card(session['deck'])
    if result is None:
        return JsonResponse({"error": "casino.game.ride_the_bus.errors.deck_empty"}, status=400)
    card, left_over_cards = result

    bet = session['initial_bet'] * 3 if compare_cards(session['cards'][0], card) == "lower" else 0

    cards = session['cards'] + [card] if session['cards'] else [card]

    request.session['ride_the_bus_session'] = create_session(deck=left_over_cards, cards=cards, bet=bet, session=session)

    if bet <= 0:
        return end(request)

    return JsonResponse(session_json(request.session['ride_the_bus_session']))


@wallet_required
def inside(request, session_id):
    session = request.session.get('ride_the_bus_session', None)

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "casino.game.ride_the_bus.errors.session_expired"}, status=400)

    result = draw_card(session['deck'])
    if result is None:
        return JsonResponse({"error": "casino.game.ride_the_bus.errors.deck_empty"}, status=400)
    card, left_over_cards = result

    bet = session['initial_bet'] * 4 if is_card_inside(card, session['cards'][0], session['cards'][1]) else 0

    cards = session['cards'] + [card] if session['cards'] else [card]

    request.session['ride_the_bus_session'] = create_session(deck=left_over_cards, cards=cards, bet=bet, session=session)

    if bet <= 0:
        return end(request)

    return JsonResponse(session_json(request.session['ride_the_bus_session']))


@wallet_required
def outside(request, session_id):
    session = request.session.get('ride_the_bus_session', None)

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "casino.game.ride_the_bus.errors.session_expired"}, status=400)

    result = draw_card(session['deck'])
    if result is None:
        return JsonResponse({"error": "casino.game.ride_the_bus.errors.deck_empty"}, status=400)
    card, left_over_cards = result

    bet = session['initial_bet'] * 4 if not is_card_inside(card, session['cards'][0], session['cards'][1]) else 0

    cards = session['cards'] + [card] if session['cards'] else [card]

    request.session['ride_the_bus_session'] = create_session(deck=left_over_cards, cards=cards, bet=bet, session=session)

    if bet <= 0:
        return end(request)

    return JsonResponse(session_json(request.session['ride_the_bus_session']))


@wallet_required
def hearts(request, session_id):
    session = request.session.get('ride_the_bus_session', None)

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "casino.game.ride_the_bus.errors.session_expired"}, status=400)

    result = draw_card(session['deck'])
    if result is None:
        return JsonResponse({"error": "casino.game.ride_the_bus.errors.deck_empty"}, status=400)
    card, left_over_cards = result

    bet = session['initial_bet'] * 20 if get_suit(card) == "hearts" else 0

    cards = session['cards'] + [card] if session['cards'] else [card]

    request.session['ride_the_bus_session'] = create_session(deck=left_over_cards, cards=cards, bet=bet, session=session)

    return end(request)


@wallet_required
def diamonds(request, session_id):
    session = request.session.get('ride_the_bus_session', None)

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "casino.game.ride_the_bus.errors.session_expired"}, status=400)

    result = draw_card(session['deck'])
    if result is None:
        return JsonResponse({"error": "casino.game.ride_the_bus.errors.deck_empty"}, status=400)
    card, left_over_cards = result

    bet = session['initial_bet'] * 20 if get_suit(card) == "diamonds" else 0

    cards = session['cards'] + [card] if session['cards'] else [card]

    request.session['ride_the_bus_session'] = create_session(deck=left_over_cards, cards=cards, bet=bet, session=session)

    return end(request)


@wallet_required
def clubs(request, session_id):
    session = request.session.get('ride_the_bus_session', None)

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "casino.game.ride_the_bus.errors.session_expired"}, status=400)

    result = draw_card(session['deck'])
    if result is None:
        return JsonResponse({"error": "casino.game.ride_the_bus.errors.deck_empty"}, status=400)
    card, left_over_cards = result

    bet = session['initial_bet'] * 20 if get_suit(card) == "clubs" else 0

    cards = session['cards'] + [card] if session['cards'] else [card]

    request.session['ride_the_bus_session'] = create_session(deck=left_over_cards, cards=cards, bet=bet, session=session)

    return end(request)


@wallet_required
def spades(request, session_id):
    session = request.session.get('ride_the_bus_session', None)

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "casino.game.ride_the_bus.errors.session_expired"}, status=400)

    result = draw_card(session['deck'])
    if result is None:
        return JsonResponse({"error": "casino.game.ride_the_bus.errors.deck_empty"}, status=400)
    card, left_over_cards = result

    bet = session['initial_bet'] * 20 if get_suit(card) == "spades" else 0

    cards = session['cards'] + [card] if session['cards'] else [card]

    request.session['ride_the_bus_session'] = create_session(deck=left_over_cards, cards=cards, bet=bet, session=session)

    return end(request)


@wallet_required
def leave(request, session_id):
    session = request.session.get('ride_the_bus_session', None)

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "casino.game.higher_lower.errors.session_expired"}, status=400)

    if session['bet'] == session['initial_bet']:
        return JsonResponse({"error": "casino.game.higher_lower.errors.invalid_round"}, status=400)

    card, left_over_cards = draw_card(session['deck'])
    if card is None:
        return JsonResponse({"error": "casino.game.ride_the_bus.errors.deck_empty"}, status=400)

    cards = session['cards'] + [card] if session['cards'] else [card]

    request.session['ride_the_bus_session'] = create_session(deck=left_over_cards, cards=cards, session=session)

    return end(request)


def end(request):
    session = request.session.get('ride_the_bus_session', None)
    wallet = get_or_none(models.Wallet, wallet_id=request.session['wallet_id'])

    if not session:
        return JsonResponse({"error": "casino.game.ride_the_bus.errors.session_expired"}, status=400)

    if session['bet'] > 0:
        update_wallet(wallet, session['bet'])

    del request.session['ride_the_bus_session']

    return JsonResponse(session_json(session))
