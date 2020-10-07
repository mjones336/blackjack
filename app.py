import os
from flask import Flask, jsonify, request, render_template, session, send_from_directory
from flask_session import Session
from game import Game
from optimal_strategy import OptimalStrategy
from optimal_strategy_auto import OptimalStrategyAuto
from blackjack_full_auto_sub_opt_simulation import *


app = Flask(__name__, static_folder='build')  # enables python to use built react app

app.secret_key = os.environ['FLASK_SECRET_KEY']
# Configure session to use filesystem (instead of signed cookies)
# app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 3600
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Serve React App once built
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


# receive data from JS
@app.route('/action', methods=['POST'])
def action():
    # POST request
    if request.method == 'POST':
        print('Incoming from JS..')
        json_data = request.get_json(force=True)
        print(json_data)
        act, value = json_data['action']
        session['state'] = act
        session[act] = None  # store the current game action/state
        if act == 'setup':
            session['game'] = Game([value], 8)
            session['playerName'] = value
            session['optimal_strategy'] = OptimalStrategy()
            session[act] = 'Setup Complete'
            session.modified = True
        elif act == 'bet':
            session['game'].place_bets({session['playerName']: int(value)})
            session[act] = 'Betting Complete'
            session.modified = True
        elif act == 'deal':
            session['starting_hands'] = session['game'].deal()
            session['dealer_hand'] = session['starting_hands']['Dealer']
            session['dealer_faceup_value'] = session['starting_hands']['Dealer'][0]['value']
            session['split'] = False
            session[act] = session['starting_hands']
            session.modified = True
        elif act == 'whoseTurn':
            name, hand, hand_num = session['game'].next_to_play()
            possible_moves = session['game'].possible_moves()
            optimal_move = show_optimal_move(name, hand)
            session[act] = {'turn': name, 'hand': hand, 'possible_moves': possible_moves, 'optimal_move': optimal_move, 'hand_num': hand_num}
            session.modified = True
        elif act == 'play':
            round_finished = False  # tells JS that round is finished so it can change state/prompt player move
            result = None  # only has value when round has a result
            bets = None
            balance = None  # only computed upon round finishing
            # update player and dealer hand
            move = value
            print(f'Move: {move}')
            name, hand, hand_num = session['game'].next_to_play()
            new_hand = session['game'].play_move(move)
            player_hand = new_hand
            dealer_hand = session['dealer_hand']
            # if played move was legal
            if new_hand:
                # store hands if player has split 
                if session['split']:
                    player_hand = dict()
                    if hand_num == 0:
                        player_hand['me'] = [new_hand['me'][0], session['split_hand']]
                        session['first_hand'] = new_hand['me'][0]
                    else:
                        player_hand['me'] = [session['first_hand'], new_hand['me'][0]]
                        session['split_hand'] = new_hand['me'][0]

                if move == 'Split':
                    session['split'] = True
                    session['first_hand'] = player_hand['me'][0]
                    session['split_hand'] = player_hand['me'][1]
                
                session['game'].advance_turn()
                new_name, new_hand, new_hand_num = session['game'].next_to_play()
                # if Dealer's turn, let Dealer play
                if new_name == 'Dealer':
                    dealer_hand = session['game'].dealer_auto_play()['Dealer']
                    round_finished = True
                    result = session['game'].determine_winner()
            bets, balance = session['game'].get_player_balance('me')
            session[act] = {'hand_num': hand_num,
                            'player_hand': player_hand, 
                            'dealer_hand': dealer_hand, 
                            'round_finished': round_finished, 
                            'result': result,
                            'bets': bets,
                            'balance': balance
                            }
            session.modified = True
        elif act == 'playAgain':
            session['game'].reset()
            session[act] = 'Play Again'
            session.modified = True
        elif act=='restartGame':
            session['game'].restart_game()
            session[act] = 'Restart Game'
            session.modified = True
        else:
            session.modified = True

        print(act, ': ',session[act])
        return 'OK', 200


# send data to JS
@app.route('/update', methods=['GET'])
def update():
    act = session['state']
    # return whole game each time, letting App.js choose vars it needs
    print(f'UPDATE ROUTE ACTIVATED: ', session[act])
    return jsonify(session[act])  # serialize and use JSON headers


def show_optimal_move(name, player_hand):
    """Returns the optimal move"""
    hand_value, hand_type = player_hand['value']
    optimal_move = session['optimal_strategy'].load_move(hand_type, 
                                    hand_value, 
                                    session['dealer_faceup_value'], 
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



# receive data from JS
@app.route('/simulate', methods=['POST'])
def simulate():
    # POST request
    if request.method == 'POST':
        print('Incoming from JS..')
        json_data = request.get_json(force=True)
        print(json_data)
        fraction_optimal = float(json_data['params'][0])/100
        num_hands  = int(json_data['params'][1])
        session['sim_result'] = None  # Initialise to avoid Key Error
        sim = GameAuto(8, num_hands, fraction_optimal)
        temp_var = sim.house_edge()  # stops race condition on session var
        session['sim_result'] = temp_var
        print('Simulation Result', ': ',session['sim_result'])
        return 'OK', 200


# send data to JS
@app.route('/simulationOutput', methods=['GET'])
def simulation_output():
    print(f'SIM OUTPUT ROUTE ACTIVATED: ', session['sim_result'])
    return jsonify(session['sim_result'])  # serialize and use JSON headers
