
import numpy as np
from collections import OrderedDict

from rlcard.envs.env import Env

from briscolaAI.utils import init_briscola_deck
from briscolaAI.agent import BriscolaRuleAgent
from briscolaAI.game import BriscolaGame
from briscolaAI.card import BriscolaCard
from briscolaAI.utils import init_briscola_deck

DEFAULT_GAME_CONFIG = {
    'game_num_players': 2,
}

class BriscolaEnv(Env):
    ''' Briscola Environment
    '''

    rank_to_points = {'Ace': 11, '2': 0, 'Three': 10, '4': 0,
                      '5': 0, '6': 0, '7': 0, 'Queen': 2, 
                      'Knight': 3, 'King': 4}

    rank_to_pos = {
        'Ace':0, '2':1, 'Three':2, '4':3, '5':4, '6':5, '7':6, 'Queen':7, 'Knight':8, 'King':9
    }

    suit_to_pos = {
        'Coins':10, 'Swords':11, 'Cups':12, 'Batons':13
    }

    def __init__(self, config = {}):
        ''' Initialize the Briscola environment
        '''
        self.name = 'briscola'
        self.game = BriscolaGame(players=config["players"], 
                                 allow_step_back=config.get("allow_step_back", False))
        self.default_game_config = DEFAULT_GAME_CONFIG

        briscola_cards = init_briscola_deck(num_players = config.get("num_players", 2))
        self.actions = [str(card) for card in briscola_cards]

        self.card_to_id = {x:i for i,x in enumerate(briscola_cards)}
        self.id_to_card = {i:x for i,x in enumerate(briscola_cards)}
        super().__init__(config)

        self.state_shape = [[len(self.actions)] for _ in range(self.num_players)]
        self.action_shape = [None for _ in range(self.num_players)]

    def _get_legal_actions(self):
        ''' Get all legal actions

        Returns:
            encoded_action_list (list): return encoded legal action list (from str to int)
        '''
        active_player = self.game.players[self.game.active_player]
        encoded_action_list = []
        for i in range(len(active_player.hand)):
            if active_player.hand[i] != None:
                encoded_action_list.append(i)
        return encoded_action_list

    def _extract_state(self, state):
        ''' Extract the state representation from state dictionary for agent

        Args:
            state (dict): Original state from the game

        Returns:
            observation (list): combine the player's score and dealer's observable score for observation
        '''
        state = self.get_perfect_information()

        # simple components -> 72 bits
        obs = self.one_hot_card(state['briscola_card'])

        for card in state["hand_cards"][self.game.agent_id]:
            if card != None:
                one_hot = self.one_hot_card(card)
                obs = np.concatenate((obs, one_hot), axis=None)
            else:
                one_hot = np.zeros((14,), dtype=int)
                obs = np.concatenate((obs, one_hot), axis=None)

        for card in state["table_cards"]:
            one_hot = self.one_hot_card(card[1])
            obs = np.concatenate((obs, one_hot), axis=None)
        
        for _ in range(1 - len(state["table_cards"])):
            one_hot = np.zeros((14,), dtype=int)
            obs = np.concatenate((obs, one_hot), axis=None)

        ids = [self.game.agent_id, (self.game.agent_id + 1) % 2]
        for i in ids:
            pile = state["pile_cards"][i]
            norm_points = self.game.judger.compute_points(pile)/120
            obs = np.concatenate((obs, norm_points), axis=None)

        # more info 1 -> 81 bits

        #suit_cards_seen_norm = [x/30 for x in self.seen_suit_points().values()]
        #obs = np.concatenate((obs, suit_cards_seen_norm), axis=None)

        #suit_cards_seen_norm = [x/10 for x in self.seen_suit_cards().values()]
        #obs = np.concatenate((obs, suit_cards_seen_norm), axis=None)

        #n_step_norm = self.game.n_step/40
        #obs = np.concatenate((obs, n_step_norm), axis=None)

        # more info 2 -> 112 bits 

        #bools_cards = self.cards_in_piles_or_hand()
        #obs = np.concatenate((obs, bools_cards), axis=None)

        extracted_state = {'obs': obs}
        active_player = self.game.players[self.game.active_player]
        legal_actions = OrderedDict({i: None for i in self._get_legal_actions()})
        extracted_state["legal_actions"] = legal_actions
        extracted_state["raw_legal_actions"] = [str(c) for c in active_player.get_hand_cards()]
        return extracted_state

    def _extract_state_old(self, state):
        ''' Extract the state representation from state dictionary for agent

        Args:
            state (dict): Original state from the game

        Returns:
            observation (list): combine the player's score and dealer's observable score for observation
        '''
        obs = np.zeros((len(self.actions),), dtype=int)
        state = self.get_perfect_information()
        enc_briscola_card = self.encode_briscola_card(state)
        enc_hand_cards = self.encode_hand_cards(state)
        enc_table_cards = self.encode_table_cards(state)
        enc_pile_cards_curr, enc_pile_cards_next = self.encode_piles_cards(state)
        for i, enc_pos in enumerate(enc_hand_cards):
            obs[enc_hand_cards[i]] = i+1
        obs[enc_table_cards] = 4
        obs[enc_pile_cards_curr] = 5
        obs[enc_pile_cards_next] = 6
        obs[enc_briscola_card] = 7
        extracted_state = {'obs': obs}
        active_player = self.game.players[self.game.active_player]
        legal_actions = OrderedDict({i: None for i in range(len(active_player.get_hand_cards()))})
        extracted_state["legal_actions"] = legal_actions
        extracted_state["raw_legal_actions"] = [str(c) for c in active_player.get_hand_cards()]

        #print(extracted_state)
        return extracted_state

    def get_payoffs(self):
        ''' Get the payoff of a game

        Returns:
           payoffs (list): list of payoffs
        '''
        if len(self.game.winner) == 2:
        	payoffs = [0, 0]
        elif self.game.winner[0] == 0:
        	payoffs = [1, -1]
        else:
        	payoffs = [-1, 1]
        return np.array(payoffs)

    def _decode_action(self, action_id):
        ''' Decode the action for applying to the game

        Args:
            action id (int): action id

        Returns:
            action (str): action for the game
        '''
        active_player = self.game.players[self.game.active_player]
        return str(active_player.hand[action_id])

    def get_reward(self):
        agent_id = self.game.agent_id
        winner_id = self.game.winner_round_id
        round_points = self.game.round_points
        if agent_id == winner_id:
            return round_points/22
        else:
            return -round_points/22

    def game_is_terminated(self):
        return False if self.game.winner == None else True

    def get_perfect_information(self):
        ''' Get the perfect information of the current state

        Returns:
            (dict): A dictionary of all the perfect information of the current state
        '''
        state = {}
        state['num_players'] = self.num_players
        state['briscola_card'] = self.game.dealer.briscola
        state['hand_cards'] = [player.hand for player in self.game.players]
        state['pile_cards'] = [player.pile for player in self.game.players]
        state['table_cards'] = self.game.on_table
        state['current_player'] = self.game.agent_id
        state['legal_actions'] = state['hand_cards'][self.game.agent_id]
        return state

    def encode_hand_cards(self, state):
        player_id = self.game.agent_id
        #print(player_id)
        enc_hand_cards = [self.card_to_id[card] for card in state['hand_cards'][player_id]]
        return enc_hand_cards
        
    def encode_piles_cards(self, state):
        players_id = [0, 1]
        enc_hand_cards = [[self.card_to_id[card] for card in state['pile_cards'][p_id]] 
                          for p_id in players_id]
        return enc_hand_cards

    def encode_table_cards(self, state):
        enc_table_cards = [self.card_to_id[card[1]] for card in state['table_cards']]
        return enc_table_cards

    def encode_briscola_card(self, state):
        return self.card_to_id[state["briscola_card"]]

    def one_hot_card(self, card):
        one_hot = np.zeros((14,), dtype=int)
        suitp = self.suit_to_pos[card.suit]
        rankp = self.rank_to_pos[card.rank]
        one_hot[suitp] = 1
        one_hot[rankp] = 1
        return one_hot

    def compute_points_left(self):
        return 120 - sum(sum(self.rank_to_points[card.rank] for card in p.pile) 
                         for p in self.game.players)

    def cards_in_piles_or_hand(self):
        bools = [0]*40
        for p in self.game.players:
            for pile_card in p.pile:
                p = self.rank_to_pos[pile_card.rank]
                p += (self.suit_to_pos[pile_card.suit]-10)*10
                bools[p] = 1
        for hand_card in self.game.players[self.game.agent_id].hand:
            if hand_card == None: continue
            p = self.rank_to_pos[hand_card.rank]
            p += (self.suit_to_pos[hand_card.suit]-10)*10
            bools[p] = 1
        return bools

    def seen_suit_points(self):
        piles = [p.pile for p in self.game.players]
        suit_points = {'Coins': 0, 'Swords': 0, 'Cups': 0, 'Batons': 0}
        player_id = self.game.agent_id
        for card in self.game.players[player_id].get_hand_cards():
            suit_points[card.suit] += self.rank_to_points[card.rank]
        for pile in piles:
            for card in pile:
                suit_points[card.suit] += self.rank_to_points[card.rank]
        return suit_points
        
    def seen_suit_cards(self):
        piles = [p.pile for p in self.game.players]
        suit_cards = {'Coins': 0, 'Swords': 0, 'Cups': 0, 'Batons': 0}
        player_id = self.game.agent_id
        for card in self.game.players[player_id].get_hand_cards():
            suit_cards[card.suit] += 1
        for pile in piles:
            for card in pile:
                suit_cards[card.suit] += 1
        return suit_cards

    def highest_suit_cards_left(self):
        piles = [p.pile for p in self.game.players]
        suit_cards = {'Coins': {11, 10, 4, 3, 2}, 'Swords': {11, 10, 4, 3, 2}, 
                      'Cups': {11, 10, 4, 3, 2}, 'Batons': {11, 10, 4, 3, 2}}

        player_id = self.game.agent_id
        for card in self.game.players[player_id].get_hand_cards():
            rank_p = self.rank_to_points[card.rank]
            if rank_p > 0: suit_cards[card.suit].discard(rank_p)
        for pile in piles:
            for card in pile:
                rank = self.rank_to_points[card.rank]
                if rank_p > 0: suit_cards[card.suit].discard(rank)
        return suit_cards
