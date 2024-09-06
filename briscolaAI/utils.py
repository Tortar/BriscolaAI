
from briscolaAI.card import BriscolaCard

import numpy as np

suit_list = ['Coins', 'Swords', 'Cups', 'Batons']
rank_list = ['Ace', '2', 'Three', '4', '5', '6', '7', 'Queen', 'Knight', 'King']

def init_briscola_deck(num_players):
    ''' Initialize a briscola deck

    Returns:
        (list): A list of Card object
    '''
    deck = [BriscolaCard(suit, rank) for suit in suit_list for rank in rank_list]
    if num_players == 3:
        deck = [card for card in deck if str(card) != '2Cups']
    return deck

def str_to_card(s):
    ''' Get the corresponding card representation of a string
    '''
    rank = next(rank for rank in rank_list if s.startswith(rank))
    suit = next(suit for suit in suit_list if s.endswith(suit))
    return BriscolaCard(suit, rank)
