from copy import deepcopy
import numpy as np

from briscolaAI.dealer import BriscolaDealer
from briscolaAI.judger import BriscolaJudger
from briscolaAI.dqn_agent import DQNAgent

from briscolaAI.utils import str_to_card

class BriscolaGame:

    def __init__(self, players, allow_step_back=False, random_agent_id=True):
        ''' Initialize the class Briscola Game
        '''
        self.allow_step_back = allow_step_back
        self.players = players
        self.num_players = len(players)
        self.np_random = np.random.RandomState()
        self.random_agent_id = True

    def init_game(self):

        for p in self.players:
            p.reset()

        if self.random_agent_id:
            ids = [0, 1]
            self.np_random.shuffle(ids)
            for i, p in enumerate(self.players):
                p.player_id = ids[i]
            self.players = [self.players[i] for i in ids]

        self.agent_id = next(i for i,x in enumerate(self.players) if isinstance(x, DQNAgent))
        self.n_step = 0
        self.dealer = BriscolaDealer(self.num_players, self.np_random)
        self.judger = BriscolaJudger()
        self.dealer.shuffle()
        self.dealer.deal_briscola()
        self.dealer.communicate_briscola(self.players)
        self.dealer.communicate_briscola([self.judger])

        for i in range(3):
            for j in range(self.num_players):
                self.dealer.deal_card(self.players[j])

        self.history = []
        self.active_player = 0
        self.on_table = []
        self.winner = None

        return self.get_state(self.active_player), self.active_player

    def step(self, action):
        ''' Get the next state

        Args:
            action (str): a specific action

        Returns:/
            dict: next player's state
            int: next plater's id
        '''
        self.n_step += 1
        if self.allow_step_back:
            self.update_history()

        played_card = str_to_card(action)
        active_player_hand = self.players[self.active_player].hand
        idx_card = active_player_hand.index(played_card)
        active_player_hand[idx_card] = None
        self.np_random.shuffle(active_player_hand)

        self.on_table.append([self.active_player, played_card])

        if len(self.on_table) == self.num_players:
            self.winner_round_id, self.round_points = self.judger.judge_round_winner(self.on_table[0], self.on_table[1])
            self.players[self.winner_round_id].pile += [id_card[1] for id_card in self.on_table]
            self.on_table = []
            self.active_player = self.winner_round_id
            if self.dealer.deck != []:
                for j in range(self.num_players):
                    self.dealer.deal_card(self.players[j])
        else:
            self.active_player += 1
            self.active_player %= self.num_players

        if self.is_over():
            winner_ids = tuple(self.judger.judge_game_winner(self.players))
            self.winner = winner_ids
            return None, None
        else:
            next_state = {}
            next_state['current_player_actions'] = self.players[self.active_player].hand
            next_state['current_player_state'] = self.players[self.active_player].hand        
            return next_state, self.active_player

    def get_state(self, player_id):
        ''' Return player's state

        Args:
            player_id (int): player id

        Returns:
            state (dict): corresponding player's state
        '''
        hand = self.players[player_id].hand
        state = {}
        state['current_player_actions'] = hand
        state['current_player_state'] = hand
        return state

    def get_player_id(self):
        ''' Return the current player's id

        Returns:
            player_id (int): current player's id
        '''
        return self.active_player

    def get_num_actions(self):
        ''' Return the number of applicable actions
        '''
        return 3

    def get_num_players(self):
        ''' Return the number of players
        '''
        return self.num_players

    def update_history(self):
        if self.allow_step_back:
            current_game_state = (deepcopy(self.dealer), deepcopy(self.players),
                                  deepcopy(self.on_table), self.active_player, self.winner)
            self.history.append(current_game_state)
        else:
            pass

    def step_back(self):
        ''' Return to the previous state of the game

        Returns:
            Status (bool): check if the step back is success or not
        '''
        if len(self.history) > 0:
            hs = self.history.pop()
            self.dealer, self.players, self.on_table, self.active_player, self.winner = hs
            return True
        return False

    def is_over(self):
        ''' Check if the game is over

        Returns:
            status (bool): True/False
        '''
        if self.dealer.deck == [] and all(player.hand == [None, None, None] for player in self.players):
            return True
        return False

