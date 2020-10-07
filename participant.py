""" Contains the 'Participant' class and it's children ('Player' and 'Dealer')
    and the 'Hand' class which describes how Participants' hand(s) can be 
    interacted with.
"""

class Participant():
    def __init__(self, name):
        self.name = name
        self.hands = []
        self.hand_pointer = 0
        self.bets = [0, 0]
        self.bet_pointer = 0
        self.balance = 100
        self.roundCounter = 0
    
    def reset(self):
        self.hands = []
        self.hand_pointer = 0
        self.bets = [0, 0]
        self.bet_pointer = 0

    def place_bets(self, bet):
        self.bets[self.bet_pointer] = bet
        self.balance -= bet
    
    def restore_balance(self):
        self.balance = 100

    def deal(self, Deck):
        """ Add Hand of 2 cards to participant's hands variable. """
        # insert a random pair at start of deck as test
        self.roundCounter += 1
        if self.roundCounter == 2 and self.name == 'me':
            hand = Hand(Deck, pair=True)
            self.hands.append(hand)
        else:
            hand = Hand(Deck)
            self.hands.append(hand)
    
    def show_hand(self):
        """ Returns dict of 'cards': list of (card value, card suit),
        'value': total hand value, 'stand': bool, 'bust': bool. 
        All cards in the hand are evaluated for all Players, 
        whereas for the Dealer only the first card is evaluated.
        """
        hand_in_play = self.hands[self.hand_pointer]
        if self.name != 'Dealer':
            return hand_in_play.show_cards_and_value()
        else:
            return hand_in_play.show_cards_and_value(first_card_only=True)

    def possible_moves(self):
        legal_moves = []
        hand = self.show_hand()
        hand_value, hand_type = hand['value']
        # hit possible if hand value < 21
        if hand_value < 21:
            legal_moves.append('Hit')
            # if sufficient remaining balance
            if self.balance >= self.bets[self.bet_pointer]:
                # double possible
                if hand['allow_double']:
                    legal_moves.append('Double')
                # split possible
                if hand['allow_split']:
                    legal_moves.append('Split')
        # stand always possible
        legal_moves.append('Stand')
        return legal_moves

    def is_last_hand(self):
        """ Bool: True if hand-in-play is the Participant's final hand. """
        return True if self.hand_pointer + 1 == len(self.hands) else False

    def advance_hand_pointer(self):
        """ Increments hand_pointer by 1. """
        self.hand_pointer += 1
        self.bet_pointer += 1
    
    def hit(self):
        """ Hits the hand-in-play. """
        hand_in_play = self.hands[self.hand_pointer]
        hand_in_play.hit()

    def stand(self):
        """ Stands the hand-in-play. """
        hand_in_play = self.hands[self.hand_pointer]
        hand_in_play.stand()

    def split(self, Deck):
        """ Splits the hand-in-play, and adds 1 new card to each of 
        the 2 hands, so both hands have total 2 cards. 
        Returns a list of dicts of ALL hands, consisting of:
        'cards': list of (card value, card suit),
        'value': total hand value, 'stand': bool, 'bust': bool, 
        'allow_split': bool, 'allow_double': bool.
        """
        original_hand = self.hands[self.hand_pointer]
        # create new hand with 2 new cards
        new_hand = Hand(Deck)
        # remove last card from new hand
        new_hand_card1 = new_hand.remove_card()
        # move last card from first hand into the new second hand
        new_hand.add_card(original_hand.remove_card(), 0)
        # add back card2 from new hand into original hand
        original_hand.add_card(new_hand_card1, 1)
        self.hands.append(new_hand)
        # adjust bets
        self.balance -= self.bets[self.bet_pointer]
        self.bets[self.bet_pointer+1] = self.bets[self.bet_pointer]

        return {self.name: [original_hand.show_cards_and_value(),
                new_hand.show_cards_and_value()]}

    def double(self):
        """ Doubles the Player's bet and their hand-in-play 
        (i.e. automatic hit, then stand if not bust). 
        """
        self.balance -= self.bets[self.bet_pointer]
        self.bets[self.bet_pointer] *= 2
        hand_in_play = self.hands[self.hand_pointer]
        hand_in_play.double()


class Dealer(Participant):
    def __init__(self):
        super().__init__('Dealer')
        self.face_up_card_pointer = 0  # tells which of the 2 cards is face-up
    
    def face_up_value(self):
        dealer_hand = self.hands[self.hand_pointer]
        face_up_card = dealer_hand[self.face_up_card_pointer]
        
    def auto_play(self):
        """ Dealer hits on ≤16 and soft-17, otherwise stands. 
        Return finished Dealer hand. 
        """
        dealer_hand = self.hands[self.hand_pointer]
        while not dealer_hand.is_stand:
            hand_value, hand_type = dealer_hand.value()
            if hand_value <= 16:
                dealer_hand.hit()
            elif hand_value == 17 and hand_type == 'soft':
                dealer_hand.hit()
            else:
                dealer_hand.stand()
        return dealer_hand.show_cards_and_value()


class Player(Participant):
    def __init__(self, name):
        super().__init__(name)

    def actual_percent_return(self, num_rounds_played):
        """ Returns % return the player has made after the 
        given number of rounds. 
        """
        return (num_rounds_played + self.balance) / num_rounds_played * 100


class Hand():
    def __init__(self, Deck, pair=False):
        """ Creates Hand by initially drawing 2 cards. """
        self.deck = Deck
        if not pair:
            self.cards = self.deck.draw(2)
        else:
            self.cards = self.deck.draw_pair()
        self.is_stand = False
        self.is_bust = False
        self.allow_split = True
        self.allow_double = True
    
    def show_cards_and_value(self, first_card_only=False):
        """ Returns dict of 'cards': list of (card value, card suit), and 
            'value': total hand value, 'stand': bool, 'bust': bool, 
            'allow_split': bool, 'allow_double': bool. 
            Optional keyword argument can return the hand's first card only 
            if set to True, else all cards are evaluated.
        """
        # update allow_split if viable move
        self.check_split()
        if not first_card_only:
            cards = [(card.value, card.suit) for card in self.cards]
            return {'cards': cards, 
                    'value': self.value(), 
                    'stand': self.is_stand, 
                    'bust': self.is_bust,
                    'allow_split': self.allow_split,
                    'allow_double': self.allow_double,
                    # 'new_card': 
                    # here^
                    }
        else:
            first_card = self.cards[0]
            cards = [(first_card.value, first_card.suit)]
            try:
                first_card_value = int(first_card.value)
            except ValueError:
                if first_card.value != 'A':
                    first_card_value = 10
                else:
                    first_card_value = 11
            return {'cards': cards, 
                    'value': first_card_value, 
                    'stand': self.is_stand, 
                    'bust': self.is_bust,
                    'allow_split': self.allow_split,
                    'allow_double': self.allow_double
                    }

    def hit(self):
        """ Draw 1 card from the deck and add it to the hand."""
        self.cards += self.deck.draw(1)
        self.allow_split = False
        self.allow_double = False
        self.check_if_bust()

    def stand(self):
        """ Updates is_stand variable to True."""
        self.is_stand = True
        self.allow_split = False
        self.allow_double = False

    def remove_card(self):
        """ Return the removed Card from the current hand. Only time this 
        event occurs is when splitting - restrict future splits & doubles. 
        """
        self.allow_split = False
        self.allow_double = False
        return self.cards.pop()
    
    def add_card(self, Card, position):
        """ Adds specified Card to the current hand."""
        self.cards.insert(position, Card)

    def check_split(self):
        """Checks if both card values are equal. 
        Only changes allow_split to False - 
        cannot override previous decisions and change it to True.
        """
        if not self.allow_split:
            return
        card0_val = self.cards[0].value
        card1_val = self.cards[1].value
        if card0_val != card1_val:
            self.allow_split = False

    def double(self):
        """Hit once, the Stand. Also restrict future splits & doubles."""
        self.hit()
        self.stand()
        self.allow_split = False
        self.allow_double = False

    def check_if_bust(self):
        """ Updates is_bust to True if hand value over 21. """
        hand_value, hand_type = self.value()
        if hand_value > 21:
            self.is_bust = True
            return True

    def value(self):
        """ Returns (value, soft/hard type) of the hand. 
        Aces are counted as 11 if they don't 'Bust' the hand, 
        otherwise they count as 1.
        """
        # setup trackers
        num_aces = 0
        total_value = 0
        # Aces 'hard' by default: i.e. all Aces assumed to be value 1
        hand_type = 'hard'

        # iterate over all cards in the hand and sum the values of non-Aces
        for card in self.cards:
            card_value = card.value
            try:
                total_value += int(card_value)
            except ValueError:
                if card_value != 'A':
                    total_value += 10
                else:                
                    num_aces += 1
        
        # add Aces back into total, counting them as 11 if possible without 
        # busting, else 1
        for i in range(num_aces):
            # test for blackjack
            if total_value == 10 and len(self.cards) == 2:
                return 21, 'Natural'
            # Ace fits as an 11 (allowing space for any other Aces too)
            if total_value + 11 + (num_aces-1-i) <= 21:
                total_value += 11
                hand_type = 'soft'
            # Ace doesn't fit: add ALL Aces as 1's and immediately return
            else:
                total_value += (num_aces-i) 
                break
        
        return total_value, hand_type
    
    

