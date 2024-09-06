
from briscolaAI.player import BriscolaPlayer

class BriscolaRuleAgent(BriscolaPlayer):

    def __init__(self, player_id, np_random):
        ''' Initialize a Blackjack player class

        Args:
            player_id (int): id for the player
        '''
        super().__init__(player_id, np_random)

    def rule_card(self, game, epsilon = 0.0):
        card = None
        if self.np_random.random() > epsilon:
            card = self.action_if_win(game)
            if card == None:
                if len(game.on_table) == 0:
                    card = card if card != None else self.rule_first_1(game)
                else:
                    card = card if card != None else self.rule_second_1(game)
                    card = card if card != None else self.weakest_card(game)
        return card if card != None else self.random_card()

    def briscolas_in_hand(self):
        return [card for card in self.get_hand_cards() if card.suit == self.briscola.suit]

    def min_briscola_in_hand(self, min_points = None):
        briscolas_in_hand = self.briscolas_in_hand()
        if min_points != None:
            briscolas_in_hand = [card for card in briscolas_in_hand 
                                 if self.rank_to_points[card.rank] > min_points]
        if briscolas_in_hand != []:
            return min(briscolas_in_hand, key=lambda card: self.rank_to_value[card.rank])
        else:
            return None

    def dominant_suit_in_hand(self, dominant_suit):
        return [card for card in self.get_hand_cards() if card.suit == dominant_suit]

    def min_dominant_in_hand(self, dominant_card, min_points = None):
        dominant_in_hand = self.dominant_suit_in_hand(dominant_card.suit)
        if min_points != None:
            dominant_in_hand = [card for card in dominant_in_hand 
                                if self.rank_to_points[card.rank] > min_points]

        if dominant_in_hand != []:
            return min(dominant_in_hand, key=lambda card: self.rank_to_value[card.rank])
        else:
            return None

    def rule_second_1(self, game):
        min_points = 2
        card_on_table = game.on_table[0][1]
        card_points = self.rank_to_points[card_on_table.rank]
        if self.card_is_valuable(card_on_table, min_points):
            if not self.card_is_briscola(card_on_table):
                player_min_dominant = self.min_dominant_in_hand(card_on_table, min_points)
                if player_min_dominant != None:
                    return player_min_dominant
                player_min_briscola = self.min_briscola_in_hand()
                if player_min_briscola != None:
                    return player_min_briscola
        return None

    def card_is_valuable(self, card, min_points):
        return self.rank_to_points[card.rank] >= min_points

    def card_is_briscola(self, card):
        return card.suit == self.briscola.suit

    def weakest_card(self, game):
        rem_suit_points = self.remaining_suit_points([p.pile for p in game.players])
        score_suit_points = sorted(rem_suit_points, key = lambda suit: rem_suit_points[suit], 
                                   reverse=True)
        score_suit_points = {score_suit_points[i]: i / 1000 for i in range(4)}
        def compute_weakest(self, card):
            if card.suit == self.briscola.suit:
                return self.rank_to_points[card.rank] + 1.1 + self.rank_to_value[card.rank] * score_suit_points[card.suit]
            else:
                return self.rank_to_points[card.rank] + self.rank_to_value[card.rank] * score_suit_points[card.suit]
        return min(self.get_hand_cards(), key = lambda card: compute_weakest(self, card))

    def rule_first_1(self, game):
        rem_suit_points = self.remaining_suit_points([p.pile for p in game.players])
        def order_cards(card):
            return rem_suit_points[card.suit] + 1/1000 * self.rank_to_value[card.rank]
        rem_points_sorted_hand = sorted(self.get_hand_cards(), key = lambda card: order_cards(card))
        for card in rem_points_sorted_hand:
            if not self.card_is_briscola(card):
                return card
        return None

    def remaining_suit_points(self, piles):
        suit_points = {'Coins': 30, 'Swords': 30, 'Cups': 30, 'Batons': 30}
        for card in self.get_hand_cards():
            suit_points[card.suit] -= self.rank_to_points[card.rank]
        for pile in piles:
            for card in pile:
                suit_points[card.suit] -= self.rank_to_points[card.rank]
        return suit_points

    def action_if_win(self, game):
        agent_pile = self.pile
        gathered_points = game.judger.compute_points(agent_pile)
        if gathered_points > 60:
            return None
        if len(game.on_table) == 1:
            other_card = game.on_table[0]
            for i, agent_card in enumerate(self.get_hand_cards()):
                agent_card_p = (self.player_id, agent_card)
                winner_id, new_points = game.judger.judge_round_winner(other_card, agent_card_p)
            if winner_id == self.player_id and gathered_points + new_points > 60:
                return agent_card
        elif len(game.on_table) == 0:
            for i, ag_card in enumerate(self.get_hand_cards()):
                card_points = self.rank_to_points[ag_card.rank]
                if gathered_points + card_points > 60:
                    b_suit = game.dealer.briscola.suit
                    all_b_seen = self.seen_suit_cards(game)[b_suit] == 10
                    if (all_b_seen and ag_card.suit != b_suit) or ag_card.suit == b_suit:
                        suit_left = self.highest_suit_cards_left(game)[ag_card.suit]
                        if suit_left == set() or card_points > max(suit_left):
                            return ag_card
        return None

    def seen_suit_cards(self, game):
        piles = [p.pile for p in game.players]
        suit_cards = {'Coins': 0, 'Swords': 0, 'Cups': 0, 'Batons': 0}
        player_id = game.agent_id
        for card in game.players[player_id].get_hand_cards():
            suit_cards[card.suit] += 1
        for pile in piles:
            for card in pile:
                suit_cards[card.suit] += 1
        return suit_cards

    def highest_suit_cards_left(self, game):
        piles = [p.pile for p in game.players]
        suit_cards = {'Coins': {11, 10, 4, 3, 2}, 'Swords': {11, 10, 4, 3, 2}, 
                      'Cups': {11, 10, 4, 3, 2}, 'Batons': {11, 10, 4, 3, 2}}

        player_id = game.agent_id
        for card in game.players[player_id].get_hand_cards():
            rank_p = self.rank_to_points[card.rank]
            if rank_p > 0: suit_cards[card.suit].discard(rank_p)
        for pile in piles:
            for card in pile:
                rank = self.rank_to_points[card.rank]
                if rank_p > 0: suit_cards[card.suit].discard(rank)
        return suit_cards