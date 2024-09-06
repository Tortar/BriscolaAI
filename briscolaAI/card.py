
class BriscolaCard:
    '''
    BriscolaCard stores the suit and rank of a single card
    '''
    valid_suit = ['Coins', 'Swords', 'Cups', 'Batons']
    valid_rank = ['Ace', '2', 'Three', '4', '5', '6', '7', 'Queen', 'Knight', 'King']

    def __init__(self, suit, rank):
        ''' Initialize the suit and rank of a card

        Args:
            suit: string, suit of the card, should be one of valid_suit
            rank: string, rank of the card, should be one of valid_rank
        '''
        assert suit in self.valid_suit
        assert rank in self.valid_rank
        self.suit = suit
        self.rank = rank

    def __eq__(self, other):
        if isinstance(other, BriscolaCard):
            return self.rank == other.rank and self.suit == other.suit
        else:
            # don't attempt to compare against unrelated types
            return NotImplemented

    def __hash__(self):
        suit_index = BriscolaCard.valid_suit.index(self.suit)
        rank_index = BriscolaCard.valid_rank.index(self.rank)
        return rank_index + 100 * suit_index

    def __str__(self):
        ''' Get string representation of a card.

        Returns:
            string: the combination of rank and suit of a card. Eg: AS, 5H, JD, 3C, ...
        '''
        return self.rank + self.suit

    def get_index(self):
        ''' Get index of a card.

        Returns:
            string: the combination of suit and rank of a card. Eg: 1S, 2H, AD, BJ, RJ...
        '''
        return self.suit+self.rank
