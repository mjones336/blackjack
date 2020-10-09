""" UNUSED SCRIPT.

    Game Rules: 
    8-deck Blackjack, Dealer stands on soft 17, no Double-after-Split, 
    no Resplit, shuffled every round, only double or split on any 2 cards, 
    no Surrender, Blackjack wins vs other 21-sum hand. 
"""

import random
import sys
import math
from optimal_strategy_auto import OptimalStrategyAuto


class GameAuto():
    def __init__(self, num_decks, num_trials, player_start_val, dealer_start_val):
        hit = {'Rounds_Played': 0, 'Total_Staked': 0, 'Balance': 0}
        stand = {'Rounds_Played': 0, 'Total_Staked': 0, 'Balance': 0}
        split = {'Rounds_Played': 0, 'Total_Staked': 0, 'Balance': 0}
        double = {'Rounds_Played': 0, 'Total_Staked': 0, 'Balance': 0}
        global move_stats
        move_stats = {'hit': hit, 'stand': stand, 'split': split, 'double': double}
        self.dealer = Dealer()
        self.player = Player('Player')
        self.d_start = dealer_start_val
        self.p_start = player_start_val
        self.total_staked = 0
        self.bets = [0, 0]
        self.balance = 0
        self.random_move = None

        # setup dicts complete with optimal moves
        self.OptMoves = OptimalStrategyAuto()
        
        for i in range(num_trials):
            # initialise deck
            # print('TURN ', i+1)
            self.deck = Cards(num_decks)
            self.place_bets()  # start process
            self.assign_result()  # end process: collect results
            # clear hands
            self.player.reset()
            self.dealer.reset()
        
        # self.print_expected_return(num_trials)
    
    def place_bets(self):
        """ Ask all players how much they want to bet. """
        self.bets = [1,0]
        self.balance = -1
        self.total_staked = 1
        self.random_move = None
        self.setup()
        
    def assign_result(self):
        # print(self.random_move)
        global move_stats
        move_stats[self.random_move]['Rounds_Played'] += 1
        move_stats[self.random_move]['Total_Staked'] += self.total_staked
        move_stats[self.random_move]['Balance'] += self.balance


    def setup(self):
        self.dealer.deal(self.d_start)
        self.player.deal(self.p_start)
        self.play()

    def possible_moves(self, hand_value):
        # stand always possible
        # legal_moves = ['Stand']
        legal_moves = [b'01']
        # hit possible if hand value < 21
        if hand_value < 21:
            # legal_moves.append('Hit')
            legal_moves.append(b'00')
        return legal_moves

    def play(self):
        dealer_num = self.dealer.hand[0][0][:-1]
        try:
            dealer_val = int(dealer_num)
        except ValueError:
            if cardVal != 'A':
                dealer_val = 10
            else:
                dealer_val = 11

        for player in [self.player]:
            play_random = True
            allowSplit = True # only allowed on first turn
            hasSplit = False # only allowed once
            allow_double = True # only allowed once, before split
            # ask player what they want to do until they 'stick', or go bust
            while not player.hasStuck:
                # determine if hard/soft/split situation
                hand = player.hand[0]
                player_val, hand_type = cardVal(hand)
                
                if play_random:
                    legal_moves = self.possible_moves(player_val)
                    if allow_double:
                        # legal_moves.append('Double')
                        legal_moves.append(b'11')
                    # split
                    if hand[0][0] == hand[1][0] and allowSplit:
                        # legal_moves.append('Split')
                        legal_moves.append(b'10')
                    answer = random.choice(legal_moves)
                    play_random = False
                    # print(f'Rand Ans: {answer}')

                    if answer == b'00':
                        self.random_move = 'hit'
                        player.hit(self.deck)
                        
                    # stick
                    elif answer == b'01':
                        self.random_move = 'stand'
                        player.stick()
                        
                    # split
                    elif answer == b'10':
                        self.random_move = 'split'
                        self.total_staked += 1
                        self.bets = [1, 1]
                        self.balance -= 1
                        player.split(self.deck)
                        hasSplit = True

                    # double
                    elif answer == b'11':
                        self.random_move = 'double'
                        player.double(self.deck)
                        self.total_staked += 1
                        self.bets = [2, 0]
                        self.balance -= 1

                else:
                    # split
                    if hand[0][0] == hand[1][0] and allowSplit:
                        if hand[0][0] != 'A':
                            answer = self.OptMoves.optimal_play_splits[(player_val, dealer_val)]
                        else:
                            answer = self.OptMoves.optimal_play_splits[(22, dealer_val)]
                    # hard - i.e. no ace, or aces count as 1
                    elif hand_type == 'hard' or (hand[0][0] == 'A' and hand[1][0] == 'A'):
                        answer = self.OptMoves.optimal_play_hard[(player_val, dealer_val)]
                    # soft - i.e. includes ace which counts as 11
                    else:
                        answer = self.OptMoves.optimal_play_soft[(player_val, dealer_val)]
                    # print(f'Opt Ans: {answer}')
                    
                    # hit
                    if answer == b'00':
                        player.hit(self.deck)
                        
                    # stick
                    elif answer == b'01':
                        player.stick()
                        
                    # split
                    elif answer == b'10':
                        # allow split if players card's values match, and they haven't split before
                        self.total_staked += 1
                        self.bets = [1, 1]
                        self.balance -= 1
                        player.split(self.deck)
                        hasSplit = True

                    # double
                    elif answer == b'11':
                        if allow_double:
                            player.double(self.deck)
                            self.total_staked += 1
                            self.bets = [2, 0]
                            self.balance -= 1
                        elif hand_type == 'hard':
                            player.hit(self.deck)
                        elif hand_type == 'soft':
                            if player_val <= 17:
                                player.hit(self.deck)
                            else:
                                player.stick()
                
                # only allow as first move
                allowSplit = False
                allow_double = False

            # play split hand
            if hasSplit:
                player.hasStuck = False
                player.handIndex += 1
                while not player.hasStuck:
                    # determine if hard/soft/split situation
                    hand = player.hand[1]
                    player_val, hand_type  = cardVal(hand)
                    dealer_num = self.dealer.hand[0][0][:-1]
                    try:
                        dealer_val = int(dealer_num)
                    except ValueError:
                        if cardVal != 'A':
                            dealer_val = 10
                        else:                
                            dealer_val = 11
                    # hard - i.e. no ace, or aces count as 1
                    if hand_type == 'hard' or (hand[0][0] == 'A' and hand[1][0] == 'A'):
                        answer = self.OptMoves.optimal_play_hard[(player_val, dealer_val)]
                    # soft - i.e. includes ace which counts as 11
                    else:
                        answer = self.OptMoves.optimal_play_soft[(player_val, dealer_val)]
                    # hit
                    if answer == b'00':
                        player.hit(self.deck)
                    # stick
                    elif answer == b'01':
                        player.stick()
                    # double
                    elif answer == b'11':
                        if hand_type == 'hard':
                            player.hit(self.deck)
                        elif hand_type == 'soft':
                            if player_val <= 17:
                                player.hit(self.deck)
                            else:
                                player.stick()
        
        self.dealer.dealerAutoPlay(self.deck)
        
        self.determineWinner()

    def determineWinner(self):
        dealerHandVal, dealer_hand_type = cardVal(self.dealer.hand[0])
        if dealerHandVal > 21:
            dealerHandVal = 0
        winners = []
        drawers = []
        
        for player in [self.player]:
            for hand_num, hand in enumerate(player.hand):
                playerVal, handType = cardVal(hand)
                # player bust means they lose, irrelevant of dealer 
                if playerVal > 21:
                    continue
                elif playerVal > dealerHandVal:
                    winners += [player.name]
                    # only blackjack (ace + picture card) pays 3/2
                    if handType != 'Natural':
                        self.balance += 2*self.bets[hand_num]
                    else:
                        self.balance += 5/2*self.bets[hand_num]
                elif playerVal == dealerHandVal:
                    if handType == 'Natural' and dealer_hand_type != 'Natural':
                        winners += [player.name]
                        self.balance += 5/2*self.bets[hand_num]
                    elif dealer_hand_type == 'Natural' and handType != 'Natural':
                        continue # player loses
                    else:
                        drawers += [player.name]
                        self.balance += self.bets[hand_num]

        
        # print(f'Winners: {winners}', end='')
        # print(f'Drawers: {drawers}')
        # total_str = ''
        # for winner in winners:
        #     if total_str != '' and total_str[-1] == '!':
        #         total_str += '\n'
        #     total_str += str(winner) + ' wins!'
        # for drawer in drawers:
        #     if total_str != '' and total_str[-1] == '!':
        #         total_str += '\n'
        #     total_str += str(drawer) + ' draws!'
        # if len(drawers) == 0 and len(winners) == 0:
        #     total_str += 'Dealer wins'
        # print(total_str)

        # print('Balances:')
        # for player in self.allPlayers[:-1]:
            # print(str(player.name) + ': ' + str(player.balance))
            # pass
        
    def print_expected_return(self, num_trials):
        print(f'Balance: {self.balance}')
        print(f"Player: {(self.balance)/self.total_staked*100:,.2f}")


class Player():
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.handIndex = 0
        self.hasStuck = False
        # self.dealer_card_vals = [str(v) for v in range(2,11)] + ['J', 'Q', 'K', 'A']
        # HARD only - exlcude Ace
        self.player_card_vals = [v for v in range(2,11)] + [10, 10, 10]
        self.picture_cards = ['10', 'J', 'Q', 'K']
    
    def deal(self, start_value):
        if self.name == 'Dealer':
            cards = [str(start_value)+'H']
        # player: choose cards at random
        else:
            sum_value = 0
            # keep trying until required total reached
            card_val_list = []
            while sum_value != start_value:
                card_val_list.clear()    
                card_val_list += [random.choice(self.player_card_vals)]
                card_val_list += [random.choice(self.player_card_vals)]
                sum_value = sum(card_val_list)
            # if any 10's, convert randomly to picture cards
            cards = []
            for card in card_val_list:
                if card == 10:
                    card = random.choice(self.picture_cards)+'C'
                else:
                    card = str(card)+'C'
                cards.append(card)
        
        # print(cards)
        self.hand.append(cards)
    
    def updateHand(self, hand):
        self.hand[self.handIndex] += hand
    
    def printHand(self):
        # print(self.name, ': ', self.hand)
        return self.name, self.hand
    
    def hit(self, Cards):
        # adds 1 card
        card = Cards.hit()
        self.hand[self.handIndex].append(card)
        self.printHand()
        handVal, handType = cardVal(self.hand[self.handIndex])
        if handVal > 21:
            # print(self.name, ' bust!')
            self.stick()
    
    def stick(self):
        # player declares they stick with their current hand
        self.hasStuck = True
    
    def split(self, Cards):
        """ Gives the player a second hand. """
        # move 1 card from hand into second hand
        self.hand += [[self.hand[self.handIndex].pop()]]
        # add 1 card from deck to each hand
        self.hand[self.handIndex].append(Cards.hit())
        self.hand[self.handIndex+1].append(Cards.hit())
        self.printHand()
        handVal, handType = cardVal(self.hand[self.handIndex])
        # print(self.name, ': ', handVal)

    def printDealerFirstCard(self):
        # print(self.name, ': ', [self.hand[0][0]])
        return self.name, self.hand[0][0]
    
    def double(self, Cards):
        """ Allow player to double their bet if they haven't doubled or split 
        before, and have only 2 cards in their current hand. Doubling means 
        the player automatically hits one final time.
        """
        self.hit(Cards)
        self.stick()
    
    def reset(self):
        self.hand = []
        self.handIndex = 0
        self.hasStuck = False


    
class Dealer(Player):
    def __init__(self):
        super().__init__('Dealer')
    
    def dealerAutoPlay(self, Cards):
        while self.hasStuck == False:
            sumCards, handType = cardVal(self.hand[0])
            if sumCards <= 16:
                self.hit(Cards)
            # if code below active, dealer hits on soft 17
            # elif sumCards == 17 and handType == 'soft':
            #     self.hit(Cards)
            else:
                self.stick()
    
            

class Cards():
    def __init__(self, num_decks):
        # create deck
        cardVals = [str(v) for v in range(2,11)] + ['J', 'Q', 'K', 'A']
        cardSuits = ['C', 'S', 'D', 'H']
        self.deck = [v+s for s in cardSuits for v in cardVals] * num_decks
        random.shuffle(self.deck)

    def deal(self):
        """ Return list of 2 random cards. """
        return [self.deck.pop(), self.deck.pop()]
        
    def hit(self):
        return self.deck.pop()

        
def cardVal(hand):
    """ returns sum of value of cards given a list of cards """
    # setup mapping
    numAces = 0
    sumVals = 0
    # by default aces are hard - changed by function if ace used as 11
    softHard = 'hard'

    for card in hand:
        cardVal = card[:-1]
        try:
            sumVals += int(cardVal)
        except ValueError:
            if cardVal != 'A':
                sumVals += 10
            else:                
                numAces += 1
    # add aces back into sum, counting them as 11 if possible, else 1
    for i in range(numAces):
        # test for blackjack
        if sumVals == 10 and len(hand) == 2 and (hand[0][0] == 'A' or hand[1][0] == 'A'):
            return 21, 'Natural'
        # ace fits as an 11 (allowing space for any other aces too)
        if sumVals + 11 + (numAces-1-i) <= 21:
            sumVals += 11
            softHard = 'soft'
        # ace doesn't fit: add all aces as 1's immediately and break
        else:
            sumVals += (numAces-i) 
            break
    
    return sumVals, softHard


def nice_print_spec_vals(player_start_val, dealer_start_val, move_stats):
    moves_returns = []
    for move in move_stats:
        moves_returns.append([move, move_stats[move]['Return']])
    sorted_moves = sorted(moves_returns, key=lambda x: 0 if isinstance(x[1],str) else x[1], reverse=True)
    print(f'({player_start_val}, {dealer_start_val}): {sorted_moves}')


# random.seed(2)
playerNames = 'Mark'
num_decks = 8
num_trials = 0

move_dict = dict()

dealer_vals = [str(v) for v in range(2,11)] + ['A']

# for player_start_val in range(4, 12):
for player_start_val in range(4, 22):
    for dealer_start_val in dealer_vals:
        move_stats = []
        GameAuto(num_decks, num_trials, player_start_val, dealer_start_val)
        for move in ['hit', 'stand', 'split', 'double']:
            if move_stats[move]['Total_Staked'] > 0:
                move_stats[move]['Return'] = round(move_stats[move]['Balance']/move_stats[move]['Total_Staked'] * 100, 2)
            else:
                move_stats[move]['Return'] = 'Error: no rounds played'
        move_dict[(player_start_val, dealer_start_val)] = move_stats
        nice_print_spec_vals(player_start_val, dealer_start_val, move_stats)




def nice_print_dict(move_dict):
    for start_vals in move_dict:
        moves_returns = []
        for move in move_dict[start_vals]:
            moves_returns.append( (move, move_dict[start_vals][move]['Return']))
        sorted_moves = sorted(moves_returns, key=lambda x: 0 if isinstance(x[1],str) else x[1], reverse=True)
        print(f'{start_vals}: {sorted_moves}')

# nice_print_dict(move_dict)