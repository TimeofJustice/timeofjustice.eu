import uuid

from django.http.response import JsonResponse
from django.views.decorators.http import require_http_methods

from core.helpers import BodyContent, get_or_none
from games import models
from games.decorators import wallet_required
from games.views.cards import CardDeck, card_to_string, is_higher, is_inside, is_lower, is_outside
from games.views.core.api import get_vault


def create_session(session_id=None, round_index=None, deck=None, cards=None, bet=None, initial_bet=None, session=None):
    return {
        "session_id": session_id if session_id is not None else session["session_id"],
        "round": round_index if round_index is not None else session["round"],
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

    vault, _ = get_vault()
    vault.balance += bet * -1
    vault.save()

@wallet_required
@require_http_methods(["POST"])
def start(request):
    wallet = get_or_none(models.Wallet, wallet_id=request.session['wallet_id'])
    post_data = BodyContent(request)

    if not wallet:
        return JsonResponse({"error": "games.game.ride_the_bus.errors.session_expired"}, status=400)

    if not post_data or not post_data.get('bet'):
        return JsonResponse({"error": "games.game.ride_the_bus.errors.invalid_request"}, status=400)

    bet = post_data.get('bet')

    if bet <= 0 or bet > wallet.balance or bet > 500:
        return JsonResponse({"error": "games.game.ride_the_bus.errors.invalid_bet"}, status=400)

    update_wallet(wallet, -bet)

    deck = CardDeck()

    request.session['ride_the_bus_session'] = create_session(uuid.uuid4().hex, 0, deck.remaining(), [], bet, bet)

    return JsonResponse(session_json(request.session['ride_the_bus_session']))


def process_turn(request, round_index, multiplier=1, higher_lower_function=None, inside_outside_function=None, suit=None, suits=None):
    session = request.session.get('ride_the_bus_session', None)
    post_data = BodyContent(request)

    if not post_data or not post_data.get('session'):
        return JsonResponse({"error": "games.game.ride_the_bus.errors.invalid_request"}, status=400)

    session_id = post_data.get('session')

    if not session or session['session_id'] != session_id or session['round'] != round_index:
        return JsonResponse({"error": "games.game.ride_the_bus.errors.session_expired"}, status=400)

    deck = CardDeck(session['deck'])
    card = deck.draw()
    if card is None:
        return None, JsonResponse({"error": "games.game.higher_lower.errors.deck_empty"}, status=400)

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

    request.session['ride_the_bus_session'] = create_session(round_index=round_index + 1,deck=deck.remaining(), cards=cards, bet=bet, session=session)

    if bet <= 0 or round_index == 3:
        return end(request)

    return JsonResponse(session_json(request.session['ride_the_bus_session']))

@wallet_required
@require_http_methods(["POST"])
def red(request):
    return process_turn(request, round_index=0, multiplier=2, suits=["diamonds", "hearts"])


@wallet_required
@require_http_methods(["POST"])
def black(request):
    return process_turn(request, round_index=0, multiplier=2, suits=["clubs", "spades"])

@wallet_required
@require_http_methods(["POST"])
def higher(request):
    return process_turn(request, round_index=1, multiplier=3, higher_lower_function=is_higher)


@wallet_required
@require_http_methods(["POST"])
def lower(request):
    return process_turn(request, round_index=1, multiplier=3, higher_lower_function=is_lower)


@wallet_required
@require_http_methods(["POST"])
def inside(request):
    return process_turn(request, round_index=2, multiplier=4, inside_outside_function=is_inside)


@wallet_required
@require_http_methods(["POST"])
def outside(request):
    return process_turn(request, round_index=2, multiplier=4, inside_outside_function=is_outside)


@wallet_required
@require_http_methods(["POST"])
def hearts(request):
    return process_turn(request, round_index=3, multiplier=8, suit="hearts")


@wallet_required
@require_http_methods(["POST"])
def diamonds(request):
    return process_turn(request, round_index=3, multiplier=8, suit="diamonds")


@wallet_required
@require_http_methods(["POST"])
def clubs(request):
    return process_turn(request, round_index=3, multiplier=8, suit="clubs")


@wallet_required
@require_http_methods(["POST"])
def spades(request):
    return process_turn(request, round_index=3, multiplier=8, suit="spades")


@wallet_required
@require_http_methods(["POST"])
def leave(request):
    session = request.session.get('ride_the_bus_session', None)
    post_data = BodyContent(request)

    if not post_data or not post_data.get('session'):
        return JsonResponse({"error": "games.game.ride_the_bus.errors.invalid_request"}, status=400)

    session_id = post_data.get('session')

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "games.game.higher_lower.errors.session_expired"}, status=400)

    if session['bet'] == session['initial_bet']:
        return JsonResponse({"error": "games.game.higher_lower.errors.invalid_round"}, status=400)

    deck = CardDeck(session['deck'])
    card = deck.draw()

    cards = (session['cards'] + [card] if session['cards'] else [card]) if card is not None else session['cards']

    request.session['ride_the_bus_session'] = create_session(deck=deck.remaining(), cards=cards, session=session)

    return end(request)


def end(request):
    session = request.session.get('ride_the_bus_session', None)
    wallet = get_or_none(models.Wallet, wallet_id=request.session['wallet_id'])

    if not session:
        return JsonResponse({"error": "games.game.ride_the_bus.errors.session_expired"}, status=400)

    if session['bet'] > 0:
        update_wallet(wallet, session['bet'])

    del request.session['ride_the_bus_session']

    return JsonResponse(session_json(session))
