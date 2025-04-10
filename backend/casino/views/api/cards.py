import random

ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
suits = ['clubs', 'diamonds', 'hearts', 'spades']

def create_deck():
    return [ { 'rank': rank, 'suit': suit } for rank in ranks for suit in suits ]

def is_higher(card1, card2):
    return ranks.index(card1['rank']) > ranks.index(card2['rank'])

def is_lower(card1, card2):
    return ranks.index(card1['rank']) < ranks.index(card2['rank'])

def is_equal(card1, card2):
    return ranks.index(card1['rank']) == ranks.index(card2['rank'])

def is_inside(card, card1, card2):
    card_index = ranks.index(card['rank'])
    card1_index = ranks.index(card1['rank'])
    card2_index = ranks.index(card2['rank'])
    return card1_index < card_index < card2_index or card2_index < card_index < card1_index

def is_outside(card, card1, card2):
    card_index = ranks.index(card['rank'])
    card1_index = ranks.index(card1['rank'])
    card2_index = ranks.index(card2['rank'])
    return card_index < card1_index and card_index < card2_index or card_index > card1_index and card_index > card2_index

def card_to_string(card):
    return f"{card['rank']}_of_{card['suit']}"

class CardDeck:
    def __init__(self, remaining_cards=None):
        self.cards = remaining_cards if remaining_cards is not None else create_deck()

        if remaining_cards is None:
            self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        if self.cards:
            return self.cards.pop()
        else:
            return None

    def remaining(self):
        return self.cards
