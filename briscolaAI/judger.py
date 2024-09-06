
class BriscolaJudger:

    rank_to_value = {'Ace': 10, '2': 1, 'Three': 9, '4': 2,
                     '5': 3, '6': 4, '7': 5, 'Queen': 6, 
                     'Knight': 7, 'King': 8}

    rank_to_points = {'Ace': 11, '2': 0, 'Three': 10, '4': 0,
                      '5': 0, '6': 0, '7': 0, 'Queen': 2, 
                      'Knight': 3, 'King': 4}

    def __init__(self):
        self.briscola = None

    def compute_points(self, pile):
        return sum(self.rank_to_points[card.rank] for card in pile)

    def judge_game_winner(self, players):
        ''' Judge the winner of the game

        Args:
            players (list): The list of players who play the game

        Returns:
            (list): The player id of the winner
        '''
        #assert sum(len(p.pile) for p in players) == (40 if len(players) != 3 else 39)
        points_piles = [self.compute_points(p.pile) for p in players]
        max_points = max(points_piles)
        return [i for i, p in enumerate(points_piles) if p == max_points]

    def judge_round_winner(self, player_card_1, player_card_2):

        briscola = self.briscola
        on_table = [player_card_1, player_card_2]
        dominant_suit = on_table[0][1].suit
        winner_player_id, winning_card = None, None
        for player_id, card in on_table:
            if winning_card == None:
                winner_player_id, winning_card = player_id, card
            else:
                if card.suit == briscola.suit and winning_card.suit != briscola.suit:
                    winner_player_id, winning_card = player_id, card
                elif card.suit == briscola.suit and winning_card.suit == briscola.suit:
                    if self.rank_to_value[card.rank] > self.rank_to_value[winning_card.rank]:
                        winner_player_id, winning_card = player_id, card
                else:
                    if card.suit == dominant_suit:
                        if self.rank_to_value[card.rank] > self.rank_to_value[winning_card.rank]:
                            winner_player_id, winning_card = player_id, card
        return winner_player_id, sum(self.rank_to_points[card[1].rank] for card in on_table)


    	