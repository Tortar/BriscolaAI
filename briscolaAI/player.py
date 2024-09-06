
class BriscolaPlayer:

    rank_to_value = {'Ace': 10, '2': 1, 'Three': 9, '4': 2,
                     '5': 3, '6': 4, '7': 5, 'Queen': 6, 
                     'Knight': 7, 'King': 8}

    rank_to_points = {'Ace': 11, '2': 0, 'Three': 10, '4': 0,
                      '5': 0, '6': 0, '7': 0, 'Queen': 2, 
                      'Knight': 3, 'King': 4}

    def __init__(self, player_id, np_random):
        ''' Initialize a Blackjack player class

        Args:
            player_id (int): id for the player
        '''
        self.np_random = np_random
        self.player_id = player_id
        self.hand = [None, None, None]
        self.pile = []
        self.briscola = None

    def get_player_id(self):
        ''' Return player's id
        '''
        return self.player_id

    def random_card(self):
        return self.np_random.choice(self.get_hand_cards())

    def get_hand_cards(self):
        return [c for c in self.hand if c != None]

    def reset(self):
        self.hand = [None, None, None]
        self.pile = []
        self.briscola = None

