import uuid
from random import shuffle
from django.http.response import JsonResponse
from core.models import get_or_none
from ..cards import card_to_string, CardDeck, is_higher, is_lower, is_inside, is_outside
from .... import models
from ....decorators import wallet_required


def create_session(session_id=None, deck=None, cards=None, bet=None, initial_bet=None, session=None):
    return {
        "session_id": session_id if session_id is not None else session["session_id"],
        "deck": deck if deck is not None else session["deck"],
        "cards": cards if cards is not None else session["cards"],
        "bet": bet if bet is not None else session["bet"],
        "initial_bet": initial_bet if initial_bet is not None else session["initial_bet"],
    }

def session_json(session):
    return {
        "session_id": session["session_id"],
        "card": card_to_string(session["cards"][-1]) if session["cards"] else None,
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

    deck = CardDeck()

    request.session['ride_the_bus_session'] = create_session(uuid.uuid4().hex, deck.remaining(), [], bet, bet)

    return JsonResponse(session_json(request.session['ride_the_bus_session']))


def process_turn(request, session_id, multiplier=1, higher_lower_function=None, inside_outside_function=None, suit=None, suits=None):
    session = request.session.get('ride_the_bus_session', None)

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "casino.game.ride_the_bus.errors.session_expired"}, status=400)

    deck = CardDeck(session['deck'])
    card = deck.draw()
    if card is None:
        return None, JsonResponse({"error": "casino.game.higher_lower.errors.deck_empty"}, status=400)

    if suit:
        bet = session['initial_bet'] * multiplier if card['suit'] == suit else 0
    elif suits:
        bet = session['initial_bet'] * multiplier if card['suit'] in suits else 0
    elif higher_lower_function:
        bet = session['initial_bet'] * multiplier if higher_lower_function(card, session['cards'][0]) else 0
    elif inside_outside_function:
        bet = session['initial_bet'] * multiplier if inside_outside_function(card, session['cards'][0], session['cards'][1]) else 0
    else:
        bet = session['initial_bet']

    cards = session['cards'] + [card] if session['cards'] else [card]

    request.session['ride_the_bus_session'] = create_session(deck=deck.remaining(), cards=cards, bet=bet, session=session)

    if bet <= 0:
        return end(request)

    return JsonResponse(session_json(request.session['ride_the_bus_session']))

@wallet_required
def red(request, session_id):
    return process_turn(request, session_id, multiplier=2, suits=["diamonds", "hearts"])


@wallet_required
def black(request, session_id):
    return process_turn(request, session_id, multiplier=2, suits=["clubs", "spades"])

@wallet_required
def higher(request, session_id):
    return process_turn(request, session_id, multiplier=3, higher_lower_function=is_higher)


@wallet_required
def lower(request, session_id):
    return process_turn(request, session_id, multiplier=3, higher_lower_function=is_lower)


@wallet_required
def inside(request, session_id):
    return process_turn(request, session_id, multiplier=4, inside_outside_function=is_inside)


@wallet_required
def outside(request, session_id):
    return process_turn(request, session_id, multiplier=4, inside_outside_function=is_outside)


@wallet_required
def hearts(request, session_id):
    return process_turn(request, session_id, multiplier=20, suit="hearts")


@wallet_required
def diamonds(request, session_id):
    return process_turn(request, session_id, multiplier=20, suit="diamonds")


@wallet_required
def clubs(request, session_id):
    return process_turn(request, session_id, multiplier=20, suit="clubs")


@wallet_required
def spades(request, session_id):
    return process_turn(request, session_id, multiplier=20, suit="spades")


@wallet_required
def leave(request, session_id):
    session = request.session.get('ride_the_bus_session', None)

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "casino.game.higher_lower.errors.session_expired"}, status=400)

    if session['bet'] == session['initial_bet']:
        return JsonResponse({"error": "casino.game.higher_lower.errors.invalid_round"}, status=400)

    deck = CardDeck(session['deck'])
    card = deck.draw()

    if card is not None:
        cards = session['cards'] + [card] if session['cards'] else [card]
    else:
        cards = session['cards']

    request.session['ride_the_bus_session'] = create_session(deck=deck.remaining(), cards=cards, session=session)

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
