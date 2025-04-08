import json
import uuid
from random import shuffle

from django.conf import settings
from django.http.response import HttpResponseRedirect, JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from inertia import render

from core.models import get_or_none
from .. import models
from ..decorators import wallet_required


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


def props(props):
    return {
        "production": settings.DEBUG is False,
        **props
    }


def error(request, status_code):
    page_props = {
        "status_code": status_code
    }

    return render(request, "Error", props=props(page_props))


def index(request):
    wallet = request.session.get('wallet_id', None)

    if not wallet:
        return render(request, "Casino/Entry")

    return wallet_test(request)


@ensure_csrf_cookie
def login(request):
    post_data = BodyContent(request)
    error = None

    if post_data:
        wallet_id = post_data.get('wallet_id')
        if wallet_id:
            wallet = get_or_none(models.Wallet, wallet_id=wallet_id.lower())

            if wallet:
                request.session['wallet_id'] = wallet.wallet_id
                return HttpResponseRedirect('/casino/')
            else:
                error = "casino.login.error.invalid_wallet"

    page_props = {
        "error": error,
    }

    return render(request, "Casino/Login", props=props(page_props))


def register(request):
    response = HttpResponseRedirect('/casino/')

    wallet_id = uuid.uuid4().hex
    wallet = get_or_none(models.Wallet, wallet_id=wallet_id)

    while wallet:
        wallet_id = uuid.uuid4().hex
        wallet = get_or_none(models.Wallet, wallet_id=wallet_id)

    wallet = models.Wallet.objects.create(wallet_id=wallet_id)

    request.session['wallet_id'] = wallet.wallet_id

    return response


def logout(request):
    response = HttpResponseRedirect('/casino/login/')

    if 'wallet_id' in request.session:
        del request.session['wallet_id']

    return response


@wallet_required
def wallet_test(request):
    wallet = get_or_none(models.Wallet, wallet_id=request.session['wallet_id'])

    page_props = {
        "wallet": wallet.json(),
    }

    return render(request, "Casino/Main", props=props(page_props))


card_set = [
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
    # Example input: 'queen_of_clubs'
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

@wallet_required
def higher_lower_start(request, bet):
    wallet = get_or_none(models.Wallet, wallet_id=request.session['wallet_id'])

    if not wallet:
        return JsonResponse({"error": "Session expired"}, status=400)

    if bet <= 0 or bet > wallet.balance or 100 < bet:
        return JsonResponse({"error": "Invalid bet"}, status=400)

    left_over_cards = card_set.copy()
    shuffle(left_over_cards)

    session = {
        "session_id": uuid.uuid4().hex,
        "deck": left_over_cards,
        "card": left_over_cards.pop(0),
        "bet": bet,
        "initial_bet": bet,
    }

    wallet = get_or_none(models.Wallet, wallet_id=request.session['wallet_id'])
    wallet.balance -= bet
    wallet.save()

    request.session['higher_lower_session'] = session

    return JsonResponse({"card": session["card"], "bet": bet, "initial_bet": bet, "cards_left": len(left_over_cards), "session_id": session["session_id"]})


@wallet_required
def higher_lower_higher(request, session_id):
    session = request.session.get('higher_lower_session', None)

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "Session expired"}, status=400)

    left_over_cards = session['deck']
    card = left_over_cards.pop(0)
    bet = session['bet'] * 2 if compare_cards(session['card'], card) == "higher" else 0

    request.session['higher_lower_session'] = {
        "session_id": session['session_id'],
        "deck": left_over_cards,
        "card": card,
        "bet": bet,
        "initial_bet": session['initial_bet'],
    }

    if bet <= 0:
        return end_higher_lower(request, card, left_over_cards)

    return JsonResponse({"card": card, "bet": bet, "initial_bet": session['initial_bet'], "cards_left": len(left_over_cards), "session_id": session["session_id"]})


@wallet_required
def higher_lower_lower(request, session_id):
    session = request.session.get('higher_lower_session', None)

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "Session expired"}, status=400)

    left_over_cards = session['deck']
    card = left_over_cards.pop(0)
    bet = session['bet'] * 2 if compare_cards(session['card'], card) == "lower" else 0

    request.session['higher_lower_session'] = {
        "session_id": session['session_id'],
        "deck": left_over_cards,
        "card": card,
        "bet": bet,
        "initial_bet": session['initial_bet'],
    }

    if bet <= 0:
        return end_higher_lower(request, card, left_over_cards)

    return JsonResponse({"card": card, "bet": bet, "initial_bet": session['initial_bet'], "cards_left": len(left_over_cards), "session_id": session["session_id"]})


@wallet_required
def higher_lower_draw(request, session_id):
    session = request.session.get('higher_lower_session', None)

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "Session expired"}, status=400)

    left_over_cards = session['deck']
    card = left_over_cards.pop(0)
    bet = session['bet'] * 2 if compare_cards(session['card'], card) == "draw" else 0

    request.session['higher_lower_session'] = {
        "session_id": session['session_id'],
        "deck": left_over_cards,
        "card": card,
        "bet": bet,
        "initial_bet": session['initial_bet'],
    }

    if bet <= 0:
        return end_higher_lower(request, card, left_over_cards)

    return JsonResponse({"card": card, "bet": bet, "initial_bet": session['initial_bet'], "cards_left": len(left_over_cards), "session_id": session["session_id"]})


@wallet_required
def higher_lower_leave(request, session_id):
    session = request.session.get('higher_lower_session', None)

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "Session expired"}, status=400)

    return end_higher_lower(request)


def end_higher_lower(request, card=None, left_over_cards=None):
    session = request.session.get('higher_lower_session', None)
    wallet = get_or_none(models.Wallet, wallet_id=request.session['wallet_id'])

    if not session:
        return JsonResponse({"error": "Session expired"}, status=400)

    bet = session['bet']
    initial_bet = session['initial_bet']

    if bet > 0:
        wallet.balance += bet
        wallet.save()

    del request.session['higher_lower_session']

    return JsonResponse({"card": card, "bet": bet, "initial_bet": initial_bet, "cards_left": len(left_over_cards) if left_over_cards else 0})
