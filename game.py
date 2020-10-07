""" Contains the 'Game' class which invokes all operations in the game 
    e.g. 'deal', 'advance turn', etc
"""

from participant import Participant, Player, Dealer, Hand
from deck import Deck


class Game():
    def __init__(self, player_names, num_decks):
        """ Takes a list of player_names as input, along with number of decks 
            and number of rounds of the game to play, and initialises the game.
        """
        self.dealer = Dealer()
        self.all_players = [Player(name) for name in player_names]
        self.all_participants = self.all_players + [self.dealer]
        self.turn_pointer = 0
        self.deck = Deck(num_decks)  # setup deck
        self.legal_moves = []

    def whose_turn(self):
        """ Returns Player/Dealer object of whoever's turn it currently is. 
            If game is finished, returns 'Game Over'.
        """
        if self.turn_pointer + 1 <= len(self.all_participants):
            return self.all_participants[self.turn_pointer]
        else:
            return 'Game Over'

    def advance_turn(self):
        """ Advances onto the next hand if a player stands or busts, 
            else does nothing.
        """
        # if now stood or bust, hand dead, so move onto next 
        player = self.whose_turn()
        hand = player.show_hand()
        if hand['stand'] or hand['bust']:
            # if player has no more hands to play, move pointer 
            # onto next player. else, move onto next hand
            if player.is_last_hand():
                self.turn_pointer += 1
            else:
                player.advance_hand_pointer()

    def next_to_play(self):
        """ Returns player name and hand of player whose turn it is. """
        active_player = self.whose_turn()
        return active_player.name, active_player.show_hand(), active_player.hand_pointer
    
    def find_player_obj(self, name):
        """ Return the Player object, given the name. 
            Maintains abstraction of UserInterface class.
        """
        for Participant in self.all_participants:
            if Participant.name == name:
                return Participant

    def place_bets(self, bets):
        """ Takes dict of player_name: bet_value as input.
            Places those bets for the players.
        """
        for player_name, bet_value in bets.items():
            player = self.find_player_obj(player_name)
            player.place_bets(bet_value)

    def deal(self):
        """ Deal new 2-card hand to all participants. 
            Returns dict of Participant name: their hand. 
        """
        starting_hands = dict()
        for participant in self.all_participants:
            participant.deal(self.deck)
            starting_hands[participant.name] = [participant.show_hand()]
        return starting_hands
    
    def possible_moves(self):
        """ Returns list of which moves are possible.""" 
        player = self.whose_turn()
        # return None if game is finished
        if player == 'Game Over':
            return None
        self.legal_moves = player.possible_moves()
        return self.legal_moves

    def play_move(self, move):
        """ If the given move is possible for the given player, this function 
            returns the new card, else it returns False.
        """
        # Check if move possible, and return False if not
        print(f'legal moves: {self.legal_moves}')
        print(f'play_move: {move}')
        if move not in self.legal_moves:
            return False

        player = self.whose_turn()
        if move == 'Hit':
            player.hit()
        elif move == 'Stand':
            player.stand()
        elif move == 'Split':
            # Return split event early as it comprises mulitple hands
            return player.split(self.deck)
        elif move == 'Double':
            player.double()
        
        updated_hand = player.show_hand()
        return {player.name: [updated_hand]}

    def determine_winner(self):
        """ Compare dealer's hand to players' hands, 
            and return a tuple of lists of winners, drawers. 
        """
        dealer_hand_value, dealer_hand_type = self.dealer.hands[0].value()
        if dealer_hand_value > 21:
            dealer_hand_value = 0
        
        results_string = ''
        
        # iterate through all players' hands to see if they win/draw/lose
        for player in self.all_players:
            for hand_num, hand in enumerate(player.hands):
                player_value, hand_type = hand.value()
                # player bust means they lose, irrelevant of dealer 
                if player_value > 21:
                    results_string += self.result_text(player.hands, hand_num, "lose", -player.bets[hand_num])
                # player wins
                elif player_value > dealer_hand_value:
                    # only blackjack (ace + picture card) pays 3/2
                    if hand_type != 'Natural':
                        results_string += self.result_text(player.hands, hand_num, 'win', player.bets[hand_num])
                        player.balance += 2*player.bets[hand_num]
                    else:
                        results_string += self.result_text(player.hands, hand_num, 'win', 3/2*player.bets[hand_num])
                        player.balance += 5/2*player.bets[hand_num]
                # player hand value = dealer hand value
                elif player_value == dealer_hand_value:
                    # player has BJ, dealer doesn't. player wins 3/2
                    if hand_type == 'Natural'  \
                       and dealer_hand_type != 'Natural':
                        results_string += self.result_text(player.hands, hand_num, 'win with Blackjack', 3/2*player.bets[hand_num])
                        player.balance += 5/2 * player.bets[hand_num]
                    # dealer has BJ, player doesn't. player loses
                    elif dealer_hand_type == 'Natural' \
                         and hand_type != 'Natural':
                            results_string += self.result_text(player.hands, hand_num, "lose (vs Dealer's Blackjack)", -player.bets[hand_num])
                    # draw: player hand == dealer hand, including BJ: push. money returned
                    else:
                        results_string += self.result_text(player.hands, hand_num, "draw", 0)
                        player.balance += player.bets[hand_num]
                else:
                    # lost
                    results_string += self.result_text(player.hands, hand_num, "lose", -player.bets[hand_num])
        return results_string
    
    def get_player_balance(self, name):
        """ Returns player's current bet(s) and balance. """
        for player in self.all_players:
            if player.name == name:
                return player.bets, player.balance

    def result_text(self, hands, hand_num, single_string, balance_change):
        """ Returns a string describing the round's outcome. """
        s = ''
        if len(hands) == 1:                        
                s += f'You '+single_string+(" $"+str(abs(round(balance_change,2))) if single_string != 'draw' else '')+'!'
        else:
            if hand_num == 0:
                s += f"Your hands "+single_string+(" $"+str(abs(round(balance_change,2))) if single_string != 'draw' else '')
            else:
                s += f", and "+single_string+(" $"+str(abs(round(balance_change,2))) if single_string != 'draw' else '')+"!"
        return s

    def reset(self):
        """ Reset all participants to be ready to play the next round. """
        self.turn_pointer = 0  # reset game class
        # reset Players/Dealer classes
        for participant in self.all_participants:
            participant.reset()

    def restart_game(self):
        """ Restarts the whole game for every player by resetting the round,
            and restoring the initial balance.
        """
        self.turn_pointer = 0  # reset game class
        # reset Players/Dealer classes
        for participant in self.all_participants:
            participant.reset()
            participant.restore_balance()

    def players_percent_returns(self, num_rounds):
        """ Return actual % returns each player has made. """
        player_returns = dict()
        for player in self.all_players:
            player_returns[player.name] = player.actual_percent_return(num_rounds)
        return player_returns
    
    def dealer_auto_play(self):
        """Returns dict of Participant name: their hand."""
        # use list here to keep format consistent for .js
        return {'Dealer': [self.dealer.auto_play()]}