
import numpy as np

from briscolaAI.utils import init_briscola_deck

from briscolaAI.card import BriscolaCard

class BriscolaDealer:

    def __init__(self, num_players, np_random):
        ''' Initialize a Briscola dealer class
        '''
        self.np_random = np_random
        self.deck = init_briscola_deck(num_players)
        self.briscola = None
        self.cards_on_table = []

    def shuffle(self):
        ''' Shuffle the deck
        '''
        shuffle_deck = np.array(self.deck)

        self.np_random.shuffle(shuffle_deck)
        self.deck = list(shuffle_deck)

    def deal_briscola(self):
        self.briscola = self.deck.pop()
        self.deck.insert(0, self.briscola)

    def communicate_briscola(self, players):
        for player in players:
            player.briscola = self.briscola

    def deal_card(self, player):
        ''' Distribute one card to the player

        Args:
            player_id (int): the target player's id
        '''
        card = self.deck.pop()
        for i in range(3):
            if player.hand[i] == None:
                player.hand[i] = card
                break
        else:
            raise Exception("ahduashdi")
