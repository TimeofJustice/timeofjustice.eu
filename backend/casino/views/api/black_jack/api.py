import uuid
from django.http.response import JsonResponse

from core.helpers import BodyContent
from core.models import get_or_none
from ..cards import CardDeck, is_higher, is_lower, is_equal, card_to_string, cards_score
from .... import models
from ....decorators import wallet_required


def create_session(session_id=None, deck=None, cards=None, dealer_cards=None, bet=None, initial_bet=None, status=None, session=None):
    return {
        "session_id": session_id if session_id is not None else session["session_id"],
        "deck": deck if deck is not None else session["deck"],
        "cards": cards if cards is not None else session["cards"],
        "dealer_cards": dealer_cards if dealer_cards is not None else session["dealer_cards"],
        "bet": bet if bet is not None else session["bet"],
        "initial_bet": initial_bet if initial_bet is not None else session["initial_bet"],
        "status": status if status is not None else session["status"],
    }


def session_json(session, reveal_hole_card=True):
    return {
        "session_id": session["session_id"],
        "cards_left": len(session["deck"]) if session["deck"] else 0,
        "cards": [card_to_string(card) for card in session["cards"]],
        "cards_score": cards_score(session["cards"]),
        "dealer_cards": [card_to_string(card) for card in session["dealer_cards"]] if reveal_hole_card else [card_to_string(session["dealer_cards"][0])],
        "dealer_score": cards_score(session["dealer_cards"]) if reveal_hole_card else cards_score([session["dealer_cards"][0]]),
        "bet": session["bet"],
        "initial_bet": session["initial_bet"],
        "status": session["status"],
    }


def update_wallet(wallet, bet):
    wallet.balance += bet
    wallet.save()


@wallet_required
def start(request):
    wallet = get_or_none(models.Wallet, wallet_id=request.session['wallet_id'])
    post_data = BodyContent(request)

    if not wallet:
        return JsonResponse({"error": "casino.game.black_jack.errors.session_expired"}, status=400)

    if not post_data or not post_data.get('bet'):
        return JsonResponse({"error": "casino.game.black_jack.errors.invalid_request"}, status=400)

    bet = post_data.get('bet')

    if bet <= 0 or bet > wallet.balance or 1000 < bet:
        return JsonResponse({"error": "casino.game.black_jack.errors.invalid_bet"}, status=400)

    update_wallet(wallet, -bet)

    deck = CardDeck()
    player_card1 = deck.draw()
    dealer_card1 = deck.draw()
    player_card2 = deck.draw()
    dealer_card2 = deck.draw()

    if player_card1 is None or dealer_card1 is None or player_card2 is None or dealer_card2 is None:
        return JsonResponse({"error": "casino.game.black_jack.errors.deck_empty"}, status=400)

    dealer_cards = [dealer_card1, dealer_card2]
    player_cards = [player_card1, player_card2]

    if cards_score(dealer_cards) == 21 and cards_score(player_cards) == 21:
        status = "push"
        request.session['black_jack_session'] = create_session(uuid.uuid4().hex, deck.remaining(),
                                                               [player_card1, player_card2], [dealer_card1, dealer_card2], bet, bet, status)

        return end(request)
    elif cards_score(dealer_cards) == 21 and cards_score(player_cards) < 21:
        status = "lost"
        new_bet = 0
        request.session['black_jack_session'] = create_session(uuid.uuid4().hex, deck.remaining(),
                                                               [player_card1, player_card2], [dealer_card1, dealer_card2], new_bet, bet, status)

        return end(request)
    elif cards_score(dealer_cards) < 21 and cards_score(player_cards) == 21:
        status = "won"
        new_bet = bet * 2.5
        request.session['black_jack_session'] = create_session(uuid.uuid4().hex, deck.remaining(),
                                                               [player_card1, player_card2], [dealer_card1, dealer_card2], new_bet, bet, status)

        return end(request)
    else:
        status = "playing"
        request.session['black_jack_session'] = create_session(uuid.uuid4().hex, deck.remaining(),
                                                               [player_card1, player_card2], [dealer_card1, dealer_card2], bet, bet, status)

        return JsonResponse(session_json(request.session['black_jack_session'], reveal_hole_card=False))


@wallet_required
def hit(request):
    session = request.session.get('black_jack_session', None)
    post_data = BodyContent(request)

    if not post_data or not post_data.get('session'):
        return JsonResponse({"error": "casino.game.black_jack.errors.invalid_request"}, status=400)

    session_id = post_data.get('session')

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "casino.game.black_jack.errors.session_expired"}, status=400)

    deck = CardDeck(session['deck'])
    card = deck.draw()

    if card is None:
        return JsonResponse({"error": "casino.game.black_jack.errors.deck_empty"}, status=400)

    cards = session['cards'] + [card]
    status = session['status']

    if cards_score(cards) > 21:
        status = "lost"
        bet = 0
        request.session['black_jack_session'] = create_session(deck=deck.remaining(), cards=cards, bet=bet, status=status, session=session)

        return end(request)

    request.session['black_jack_session'] = create_session(deck=deck.remaining(), cards=cards, status=status, session=session)

    return JsonResponse(session_json(request.session['black_jack_session'], reveal_hole_card=False))


@wallet_required
def stand(request):
    session = request.session.get('black_jack_session', None)
    post_data = BodyContent(request)

    if not post_data or not post_data.get('session'):
        return JsonResponse({"error": "casino.game.black_jack.errors.invalid_request"}, status=400)

    session_id = post_data.get('session')

    if not session or session['session_id'] != session_id:
        return JsonResponse({"error": "casino.game.black_jack.errors.session_expired"}, status=400)

    deck = CardDeck(session['deck'])

    dealer_cards = session['dealer_cards']

    while cards_score(dealer_cards) < 17:
        dealer_card = deck.draw()
        if dealer_card is None:
            return JsonResponse({"error": "casino.game.black_jack.errors.deck_empty"}, status=400)
        dealer_cards.append(dealer_card)

    if cards_score(dealer_cards) > 21 and cards_score(session['cards']) > 21:
        status = "push"
        request.session['black_jack_session'] = create_session(deck=deck.remaining(), dealer_cards=dealer_cards, status=status, session=session)

        return end(request)
    if cards_score(dealer_cards) > 21:
        status = "won"
        bet = session['bet'] * 2
        request.session['black_jack_session'] = create_session(deck=deck.remaining(), dealer_cards=dealer_cards, bet=bet, status=status, session=session)

        return end(request)
    elif cards_score(dealer_cards) == cards_score(session['cards']):
        status = "push"
        request.session['black_jack_session'] = create_session(deck=deck.remaining(), dealer_cards=dealer_cards, status=status, session=session)

        return end(request)
    elif cards_score(session['cards']) > cards_score(dealer_cards):
        status = "won"
        bet = session['bet'] * 2
        request.session['black_jack_session'] = create_session(deck=deck.remaining(), dealer_cards=dealer_cards, bet=bet, status=status, session=session)

        return end(request)
    else:
        status = "lost"
        bet = 0
        request.session['black_jack_session'] = create_session(deck=deck.remaining(), dealer_cards=dealer_cards, bet=bet, status=status, session=session)

        return end(request)


def end(request):
    session = request.session.get('black_jack_session', None)
    wallet = get_or_none(models.Wallet, wallet_id=request.session['wallet_id'])

    if not session:
        return JsonResponse({"error": "casino.game.black_jack.errors.session_expired"}, status=400)

    if session['bet'] > 0:
        update_wallet(wallet, session['bet'])

    del request.session['black_jack_session']

    return JsonResponse(session_json(session))
