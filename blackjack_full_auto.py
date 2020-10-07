""" 8-deck Blackjack, Dealer stands on soft 17, no Double-after-Split, 
    no Resplit, shuffled every round, only double or split on any 2 cards, 
    no Surrender, Blackjack wins vs other 21-sum hand. 
"""
# could extend: add card counting

import random
import sys
from optimal_strategy_auto import OptimalStrategyAuto


class GameAuto():
    def __init__(self, numPlayers, playerNames, num_decks, num_trials):
        if len(playerNames) != numPlayers:
            sys.exit("Number of names doesn't match the number of players")

        self.dealer = Dealer()
        self.allPlayers = [Player(name) for name in playerNames] + [self.dealer]

        # setup dicts complete with optimal moves
        self.OptMoves = OptimalStrategyAuto()
        
        
        for i in range(num_trials):
            # initialise deck
            # print('TURN ', i+1)
            self.deck = Cards(num_decks)
            self.place_bets()
            # clear hands
            for player in self.allPlayers:
                player.reset()
        
        for player in self.allPlayers[:-1]:
            player.print_expected_return(num_trials)
    
    def place_bets(self):
        """ Ask all players how much they want to bet. """
        for player in self.allPlayers[:-1]:
            player.bet = 1
            player.balance -= 1
        self.setup()

    def setup(self):
        for player in self.allPlayers:
            player.deal(self.deck)
        self.play()

    def play(self):
        dealer_num = self.dealer.hand[0][0][:-1]
        try:
            dealer_val = int(dealer_num)
        except ValueError:
            if cardVal != 'A':
                dealer_val = 10
            else:
                dealer_val = 11

        for player in self.allPlayers[:-1]:
            allowSplit = True # only allowed on first turn
            hasSplit = False # only allowed once
            allow_double = True # only allowed once, before split
            # ask player what they want to do until they 'stick', or go bust
            while not player.hasStuck:
                # determine if hard/soft/split situation
                hand = player.hand[0]
                player_val, hand_type  = cardVal(hand)
                
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
                
                # hit
                if answer == b'00':
                    player.hit(self.deck)
                    
                # stick
                elif answer == b'01':
                    player.stick()
                    
                # split
                elif answer == b'10':
                    # allow split if players card's values match, and they haven't split before
                    player.split(self.deck)
                    hasSplit = True

                # double
                elif answer == b'11':
                    if allow_double:
                        player.double(self.deck)
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
        
        for player in self.allPlayers[:-1]:
            for hand in player.hand:
                playerVal, handType = cardVal(hand)
                # player bust means they lose, irrelevant of dealer 
                if playerVal > 21:
                    continue
                elif playerVal > dealerHandVal:
                    winners += [player.name]
                    # only blackjack (ace + picture card) pays 3/2
                    if handType != 'Natural':
                        player.balance += 2*player.bet
                    else:
                        player.balance += 5/2*player.bet
                elif playerVal == dealerHandVal:
                    if handType == 'Natural' and dealer_hand_type != 'Natural':
                        winners += [player.name]
                        player.balance += 5/2*player.bet
                    elif dealer_hand_type == 'Natural' and handType != 'Natural':
                        continue # player loses
                    else:
                        drawers += [player.name]
                        player.balance += player.bet

        
        total_str = ''
        for winner in winners:
            if total_str != '' and total_str[-1] == '!':
                total_str += '\n'
            total_str += str(winner) + ' wins!'
        for drawer in drawers:
            if total_str != '' and total_str[-1] == '!':
                total_str += '\n'
            total_str += str(drawer) + ' draws!'
        if len(drawers) == 0 and len(winners) == 0:
            total_str += 'Dealer wins'
        # print(total_str)

        # print('Balances:')
        # for player in self.allPlayers[:-1]:
            # print(str(player.name) + ': ' + str(player.balance))
            # pass
        


class Player():
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.handIndex = 0
        self.hasStuck = False
        self.bet = 0
        self.balance = 0
    
    def deal(self, Cards):
        cards = Cards.deal()
        self.hand.append(cards)
        if self.name != 'Dealer':
            self.printHand()
        else:
            self.printDealerFirstCard()    
    
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
        self.balance -= self.bet
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
        self.balance -= self.bet
        self.bet += self.bet
        self.hit(Cards)
        self.stick()
    
    def reset(self):
        self.hand = []
        self.handIndex = 0
        self.hasStuck = False

    def print_expected_return(self, num_trials):
        print(self.name, ': ', f"{(num_trials + self.balance)/num_trials*100 - 100:,.2f}")

    
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


# random.seed(2)
# playerNames = ['Mark', 'Nat']
# num_decks = 8
# num_trials = 1000
# GameAuto(len(playerNames), playerNames, num_decks, num_trials)




# hand = ['At', '5d', '5d', 'kh']
# print(cardVal(hand))



