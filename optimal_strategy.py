
class OptimalStrategy():
    def __init__(self):
        """ Setup Optimal Strategy dictionaries for splits, hard, and soft 
        hands. 
        """
        self.optimal_play_hard = dict()
        self.optimal_play_soft = dict()
        self.optimal_play_splits = dict()

        def h(n):
            return ['Hit'] * n

        def st(n):
            return ['Stand'] * n

        def sp(n):
            return ['Split'] * n

        def d(n):
            return ['Double'] * n

        # optimal play hard: 10 columns, 11 rows
        r1 = h(10)
        r2 = h(1) + d(4) + h(5)
        r3 = d(8) + h(2)
        r4 = d(10)
        r5 = h(2) + st(3) + h(5)
        r6 = st(5) + h(5)
        r7 = st(5) + h(5)
        r8 = st(5) + h(5)
        r9 = st(5) + h(5)
        r10 = st(10)
        r11 = st(10)

        matrix = [r1, r1, r1, r1, r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, 
                  r11, r11, r11, r11]

        for row_num, row in enumerate(matrix):
            player_hand = row_num + 4
            for col_num, move in enumerate(row):
                dealer_card = col_num+2
                self.optimal_play_hard[(player_hand, dealer_card)] = move


        # self.optimal_play_soft: 8 rows, 10 cols
        r1 = h(3) + d(2) + h(5)
        r2 = h(3) + d(2) + h(5)
        r3 = h(2) + d(3) + h(5)
        r4 = h(2) + d(3) + h(5)
        r5 = h(1) + d(4) + h(5)
        r6 = d(5) + st(2) + h(3)
        r7 = st(4) + d(1) + st(5)
        r8 = st(10)

        matrix = [r1, r2, r3, r4, r5, r6, r7, r8, r8]

        for row_num, row in enumerate(matrix):
            player_hand = row_num + 13
            for col_num, move in enumerate(row):
                dealer_card = col_num+2
                self.optimal_play_soft[(player_hand, dealer_card)] = move
                    

        # self.optimal_play_splits: 8 rows, 10 cols
        r1 = h(2) + sp(4) + h(4)
        r2 = h(2) + sp(4) + h(4)
        r3 = h(10)
        r4 = d(8) + h(2)
        r5 = h(1) + sp(4) + h(5)
        r6 = sp(6) + h(4)
        r7 = sp(10)
        r8 = sp(5) + st(1) + sp(2) + st(2)
        r9 = st(10)
        r10 = sp(10)

        matrix = [r1, r2, r3, r4, r5, r6, r7, r8, r9, r10]

        for row_num, row in enumerate(matrix):
            player_hand = (row_num+2) * 2
            for col_num, move in enumerate(row):
                dealer_card = col_num+2
                self.optimal_play_splits[(player_hand, dealer_card)] = move
    
    def load_move(self, player_hand_type, player_hand_value, 
                  dealer_faceup_value, player_splittable
                  ):
        # split
        if player_splittable:
            if player_hand_type != 'soft':  # Soft means player has two Aces
                return self.optimal_play_splits[(player_hand_value, 
                                                 dealer_faceup_value
                                                 )]
            else:
                return self.optimal_play_splits[(22, dealer_faceup_value)]
        # soft - i.e. includes ace which counts as 11
        elif player_hand_type == 'soft':
            try:
                return self.optimal_play_soft[(player_hand_value, 
                                               dealer_faceup_value
                                               )]
            # e.g. edge case where hand equals two Aces and cannot be resplit
            except KeyError: 
                return self.optimal_play_hard[(player_hand_value, 
                                               dealer_faceup_value
                                               )]    
        # hard: any aces count as 1
        else:
            return self.optimal_play_hard[(player_hand_value, 
                                           dealer_faceup_value
                                           )]

