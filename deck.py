""" Contains 'Deck' and 'Card' classes. """

import random


class Deck():
    def __init__(self, num_decks):
        """ Create deck. """
        card_vals = [str(val) for val in range(2,11)] + ['J', 'Q', 'K', 'A']
        card_suits = ['C', 'S', 'D', 'H']
        # deck consists of 52*num_deck Cards
        self.deck = [Card(v,s) for s in card_suits for v in card_vals] \
                    * num_decks
        self.shuffle()
    
    def shuffle(self):
        """ Shuffles deck. """
        random.shuffle(self.deck)
        self.card_pointer = 0
        
    def draw(self, num_cards):
        """ Returns the input number of random cards from the deck as a list,
            without replacement. 
        """
        pointer = self.card_pointer
        dealt_cards = self.deck[pointer : pointer + num_cards]
        self.card_pointer += num_cards
        return dealt_cards

    def draw_pair(self):
        """ Returns 2 cards with the same random number from the deck,
            as a list. 
        """
        # select value from 8/9/A as they are very likely to result 
        # in the optimal move being 'Split'.
        card1_val = random.choice(['8', '9', 'A'])
        card_suits = ['C', 'S', 'D', 'H']
        # select 2nd card with diff suit, and same value
        card1_suit = random.choice(card_suits)
        card1_suit_idx = card_suits.index(card1_suit)
        card2_suit = card_suits[(card1_suit_idx+1)%4]
        return [Card(card1_val, card1_suit), Card(card1_val, card2_suit)]


class Card():
    def __init__(self, value, suit):
        """ Creates card with given value and suit. """
        self.value = value
        self.suit = suit