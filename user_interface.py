

""" Script uses Tkinter GUI rendering module to display Blackjack game 
    instead of JavaScript.

    Game rules:
    8-deck Blackjack, Dealer hits on soft 17, no Double-after-Split, 
    no Resplit, shuffled every round, only double or split on any 2 cards, 
    no Surrender, Blackjack wins vs other 21-sum hand. 
"""

import tkinter as tk
import sys

sys.path.append('/Library/Frameworks/Python.framework/Versions/3.7/lib/python3.7/site-packages')
from PIL import Image, ImageTk
from game import Game
from optimal_strategy import OptimalStrategy

class UserInterface():
    def __init__(self, root):
        WIDTH, HEIGHT = 1280, 620
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        
        # launch app
        self.root = root
        self.root.title('Blackjack')
        self.root.geometry('{}x{}'.format(WIDTH, HEIGHT))

        # load background blackjack board image onto canvas
        img = Image.open("/Users/markjones/Documents/CompSci/Live_Projects/"
                         + "Blackjack/bjtable.png").crop((0,0,WIDTH,HEIGHT))
        photo = ImageTk.PhotoImage(img, Image.ANTIALIAS)
        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT)
        self.canvas.pack()
        self.canvas.background = photo
        self.canvas.create_image(0,0, 
                                 anchor=tk.NW, 
                                 image=photo)

        self.total_frame = tk.Frame(self.root)

        self.load_buttons()

    def load_buttons(self):
        exit_button = tk.Button(self.root, text='Exit', 
                               font=("Courier", 40),
                               command=self.exit, 
                               anchor=tk.SE, 
                               relief=tk.RIDGE,
                               )
        exit_button.pack(side=tk.RIGHT)

        play_again_button = tk.Button(self.root, 
                                    text='Play Again',
                                    font=("Courier", 40),
                                    command=self.playAgain, 
                                    anchor=tk.CENTER, 
                                    relief=tk.RIDGE,
                                    )
        play_again_button.pack()
        
        hit_button = tk.Button(self.root, 
                              text='Hit',
                              font=("Courier", 40),
                              command = lambda 
                                        move='Hit': 
                                        self.play_move(move),
                              anchor=tk.CENTER, 
                              relief=tk.RIDGE,
                              )
        hit_button.pack()

        stand_button = tk.Button(self.root, 
                              text='Stand',
                              font=("Courier", 40),
                              command = lambda 
                                        move='Stand': 
                                        self.play_move(move),
                              anchor=tk.CENTER, 
                              relief=tk.RIDGE,
                              )
        stand_button.pack()

        split_button = tk.Button(self.root, 
                              text='Split',
                              font=("Courier", 40),
                              command = lambda 
                                        move='Split': 
                                        self.play_move(move),
                              anchor=tk.CENTER, 
                              relief=tk.RIDGE,
                              )
        split_button.pack()

        double_button = tk.Button(self.root, 
                              text='Double',
                              font=("Courier", 40),
                              command = lambda 
                                        move='Double': 
                                        self.play_move(move),
                              anchor=tk.CENTER, 
                              relief=tk.RIDGE
                              )
        double_button.pack()

        # place buttons on canvas
        self.canvas.create_window((0,0),window=exit_button, anchor=tk.NW)
        self.canvas.create_window((self.WIDTH,0),window=play_again_button, anchor=tk.NE)
        self.canvas.create_window((self.WIDTH*0.3555,self.HEIGHT),window=hit_button, anchor=tk.S)
        self.canvas.create_window((self.WIDTH*0.445,self.HEIGHT),window=stand_button, anchor=tk.S)
        self.canvas.create_window((self.WIDTH*0.555,self.HEIGHT),window=split_button, anchor=tk.S)
        self.canvas.create_window((self.WIDTH*0.673,self.HEIGHT),window=double_button, anchor=tk.S)

        self.game_setup()

    def card_positioning(self):
        # face-up dimensions: 691 × 1056
        # back dimensions: 686 × 976
        self.CARD_WIDTH = int(69*0.9)
        self.CARD_HEIGHT = int(100*0.9)
        self.CARD_SEP_X = 15
        self.CARD_SEP_Y = 15
        self.HAND_SEP_X = 120

        self.setupCardBasePosn(self.player_names)
        self.linkCardsToImages()

        # used to delete canvas windows for the playAgain function
        self.canvasWindowNum = 5
        self.deal()
    
    def setupCardBasePosn(self, playerNames):
        self.card_posn = dict()
        if len(playerNames) == 2:
            # store tuple in dict: (num cards in hand0, hand1, x_coord, y)
            self.card_posn[playerNames[0]] = [0, 0, self.WIDTH*0.635, 350]
            self.card_posn[playerNames[1]] = [0, 0, self.WIDTH*0.3, 350]
            self.card_posn['Dealer'] = [0, 0, self.WIDTH*0.473, 225]

    def add_card_image(self, player_name, card_value, card_suit, hand_num):
        hand0_cards, hand1_cards, x, y = self.card_posn[player_name]
        card = tk.Label(self.root, image=self.card_image[str(card_value)
                                                         +str(card_suit)
                                                         ]
                        )
        card.pack(side=tk.LEFT)
        
        # adjust x axis coordinate if multiple hands exist 
        # and increment the num_cards the player has in their hand by 1
        if hand_num == 0:
            x = x + hand0_cards*self.CARD_SEP_X
            y = y + hand0_cards*self.CARD_SEP_Y
            self.card_posn[player_name][0] += 1
        elif hand_num == 1:
            x = x + hand1_cards*self.CARD_SEP_X + self.HAND_SEP_X
            y = y + hand1_cards*self.CARD_SEP_Y
            self.card_posn[player_name][1] += 1
            
        return self.canvas.create_window((x, y),
                                          window=card, 
                                          anchor=tk.CENTER, 
                                          tags=('cards', str(player_name))
                                          )
    
    def linkCardsToImages(self):
        self.card_image = dict()
        card_vals = [str(v) for v in range(2,11)] + ['J', 'Q', 'K', 'A']
        card_suits = ['C', 'S', 'D', 'H']
        for val in card_vals:
            for suit in card_suits:
                image_open = Image.open('/Users/markjones/Documents/CompSci/Live_Projects/Blackjack/playing_cards/'+val+suit+'.png').resize((self.CARD_WIDTH, self.CARD_HEIGHT))
                tk_img = ImageTk.PhotoImage(image_open, Image.ANTIALIAS)
                self.card_image[val+suit] = tk_img
        # add card back to image dict
        image_open = Image.open("/Users/markjones/Documents/CompSci/Live_Projects/Blackjack/playing_cards/card_back.png").resize((self.CARD_WIDTH,self.CARD_HEIGHT))
        self.card_image['back'] = ImageTk.PhotoImage(image_open, Image.ANTIALIAS)

    def exit(self):
        self.root.destroy()

    def game_setup(self):
        # GUI user input: distinct player names, num decks, num rounds, 
        # bool on simulations or manual play
        self.player_names = ['Mark', 'Nat']
        num_decks = 8
        self.total_rounds = 5
        self.completed_rounds = 0
        self.manual_play = True
        
        self.game = Game(self.player_names, num_decks)
        self.optimal_strategy = OptimalStrategy()

        self.bets = {"Mark": 1, "Nat": 1}
        self.place_bets(self.bets)
        # GUI user input: bets

    def place_bets(self, bets):
        self.game.place_bets(bets)
        # show bets in GUI next to player names
        self.card_positioning()
    
    def deal(self):
        starting_hands = self.game.deal()

        # store dealer's face-up card value
        self.dealer_faceup_value = starting_hands['Dealer'][0]['value']
        print(starting_hands)
        # dealt cards show up in GUI
        for name, hand in starting_hands.items():
            for card in hand[0]['cards']:
                value, suit = card
                hand_num = 0  # dealt cards, so must be 1st hand
                self.add_card_image(name, value, suit, hand_num)
                
        self.prompt_move()

    def prompt_move(self):
        """Prompt correct player to make possible move with visual effects"""
        next_to_play_name, hand = self.game.next_to_play()
        print((next_to_play_name, hand))
        # GUI: show clearly who is next to play and the hand 
        # they are deciding on (cards + soft & hard value)

        possible_moves = self.game.possible_moves()
        print(possible_moves)
        # GUI: highlight which moves are possible

        # GUI: show what optimal move is if player asked for it
        optimal_move = self.show_optimal_move()
        print(optimal_move)

        # either let computer always play optimal move, or play manually
        if not self.manual_play:
            self.play_move(optimal_move)

    def show_optimal_move(self):
        """Returns the optimal move"""
        name, player_hand = self.game.next_to_play()
        hand_value, hand_type = player_hand['value']
        optimal_move = self.optimal_strategy.load_move(hand_type, 
                                        hand_value, 
                                        self.dealer_faceup_value, 
                                        player_hand['allow_split']
                                        )
        # double only allowed on first 2 cards
        if optimal_move == 'Double' and not player_hand['allow_double']:
            hand_value, hand_type = player_hand['value']
            if hand_type == 'hard':
                optimal_move = 'Hit'
            elif hand_type == 'soft':
                if hand_value <= 17:
                    optimal_move = 'Hit'
                else:
                    optimal_move = 'Stand'
        return optimal_move

    def display_new_cards(self, cards, name):
        """Adds given card(s) into participant's in the GUI"""
        pass

    def play_move(self, move):
        name, old_hand = self.game.next_to_play()
        new_hand = self.game.play_move(move)

        # if move is legal, proceed
        if new_hand:
            print(new_hand)
            # GUI: print any new card(s) to screen
            new_cards = self.new_cards(old_hand, new_hand)
            for hand_num, hand in enumerate(new_cards):
                for card in hand:
                    value, suit = card
                    self.add_card_image(name, value, suit, hand_num)

            self.game.advance_turn()
        
            # if Dealer's turn, let Dealer play
            name, hand = self.game.next_to_play()
            if name == 'Dealer':
                self.dealer_auto_play()
            # else, prompt next Playermove
            else:
                self.prompt_move()
        else: 
            print("Illegal Move")

    def new_cards(self, old_hand, new_hand):
        """Returns new player cards, in a list where the index represents the hand number. 
        Or returns None if none exist.
        """
        # new hand ≥ old hand, so iterate through new hand looking for matches
        added_cards = []
        for hand_num, hand in enumerate(new_hand):
            for card in hand['cards']:
                if old_hand[hand_num]['cards'].count(card) == 0:
                    added_cards.append([card])
        return added_cards


                


    def dealer_auto_play(self):
        """ First reveal the hole-card, then play out rest of Dealer's turn 
        until they bust/stand, reporting each card to the GUI in turn. 
        """
        d = self.game.dealer_auto_play()
        print(d)
        # GUI: reveal Dealer's hand

        self.determine_winner()  # once dealer has played, determine winner
        
    def determine_winner(self):
        """ Determine who has won and/or drawn vs the Dealer, 
        print results to GUI, and update Player balances. 
        """
        winners, drawers = self.game.determine_winner()
        print(winners, drawers)
        # GUI: display player's round win/loss/draw and overall balances
        
        self.reset_game()  # reset player's hands
        
    def reset_game(self):
        """ Clear all participants' hands ready for new round, and increment 
        the round counter by 1. 
        If completed all rounds, display realised returns.
        """
        self.game.reset()
        self.completed_rounds += 1
        if self.completed_rounds == self.total_rounds:
            exp_return = self.game.players_percent_returns(self.total_rounds)
            print(exp_return)
            # GUI: state 'Game Over', and show overall realised returns
            # restrict possible move to 'Play Again' and 'Exit'
        
        # else, restart playing sequence of events
        else:
            # delete all cards in GUI
            self.canvas.delete('cards')
            self.place_bets(self.bets)

    def playAgain(self):
        """Restarts game with same parameters as before"""
        self.game_setup()

root = tk.Tk()
app = UserInterface(root)
root.mainloop()