
import numpy as np
import numpy.random
import time

import torch
import rlcard
from rlcard.envs.registration import register, make

from briscolaAI.briscola import BriscolaEnv
from briscolaAI.game import BriscolaGame
from briscolaAI.agent import BriscolaRuleAgent
from briscolaAI.dqn_agent import DQNAgent

def rl_based_action(player, env, state):
    action = player.action_if_win(env.game)
    if action != None:
        action = player.hand.index(action)
    else: 
        action = player.eval_step(state)[0]
    return action

def random_action(player, env):
    return player.hand.index(player.random_card())
    
def rule_based_action(player, env, epsilon = 0.0):
    return player.hand.index(player.rule_card(env.game, epsilon))

def run_eval_games(env, action_func, n):
    game_results = {"win": 0, "odds": 0, "loss": 0}
    for _ in range(n):
        state, player_id = env.reset()
        agent_id = env.game.agent_id
        while True:
            player = env.game.players[player_id]
            if player_id == agent_id:
            	action = rl_based_action(player, env, state) 
            else:
                action = action_func(player, env)
            next_state, player_id = env.step(action)
            if player_id is None: break
            state = next_state 
        winner = env.game.winner
        result_k = "win" if winner == (agent_id,) else ("odds" if len(winner) == 2 else "loss")
        game_results[result_k] += 1
    return game_results

def eval_agent(env, n_episode):
    random_results = run_eval_games(env, random_action, 1000)
    rule_based_results = run_eval_games(env, rule_based_action, 1000)
    print_results(random_results, n_episode, "random")
    print_results(rule_based_results, n_episode, "rule")
    return random_results, rule_based_results

def print_results(results, n_episode, player_type):
	str_results = " ".join(f"{k}: {results[k]}" for k in results)
	print(f"after {n_episode} episodes vs. {player_type} -> {str_results}")

def train_agent(env, n_total):
	random_all_results = []
	rule_all_results = []
	for n_episode in range(n_total):
		#a = time.time()
		if n_episode % 1000 == 0: 
			random_results, rule_based_results = eval_agent(env, n_episode)
			env.game.players[env.game.agent_id].save_checkpoint(path="./models/", 
				                                                filename = f'checkpoint_dqn_episode_{n_episode}.pt')
			random_all_results.append(random_results)
			rule_all_results.append(rule_based_results)
		state, curr_player_id = env.reset()
		curr_player = env.game.players[curr_player_id]
		agent_id = env.game.agent_id
		agent_player = env.game.players[agent_id]
		if curr_player_id != agent_id:
			action = rule_based_action(curr_player, env, max(0.0, min(1.0, n_episode/(n_total-30000))))
			state, curr_player_id = env.step(action)
		total_reward = 0
		while True:
			assert curr_player_id == agent_id
			curr_player = env.game.players[curr_player_id]
			agent_action = agent_player.step(state)
			next_state, curr_player_id = env.step(agent_action)
			while curr_player_id != agent_id and curr_player_id != None:
				curr_player = env.game.players[curr_player_id]
				action = rule_based_action(curr_player, env, max(0.0, n_episode/n_total - 0.1))
				next_state, curr_player_id = env.step(action)
			reward = env.get_reward()
			total_reward += reward
			sarst = [state, agent_action, reward, next_state, env.game_is_terminated()]
			agent_player.feed(sarst)
			state = next_state
			if curr_player_id == None: 
				break
		#b = time.time()
		#print(f"time: {b - a}")
		#print(env.game.agent_id == env.game.winner[0], total_reward)
	return random_all_results, rule_all_results

def print_state(env, agent_action):
	print()
	print(f"agent id {env.game.agent_id} with action: {agent_action}")
	for p in env.game.players:
		print(f"player {p.player_id} hand {[str(c) for c in p.hand]}")
	print(f"on table: {[str([c[0], str(c[1])]) for c in env.game.on_table]}")

try:
	register(
    	env_id='briscola',
    	entry_point='briscolaAI.briscola:BriscolaEnv',
	)
except ValueError:
	pass

config = {
	"players": [
		DQNAgent(0, numpy.random, state_shape=[72], device="cpu"), 
		BriscolaRuleAgent(1, numpy.random)
	]
}

env = make('briscola', config = config)

#torch.set_num_threads(6)
random_results, rule_results = train_agent(env, 100001)

import pandas as pd
import matplotlib.pyplot as plt

df_random = pd.DataFrame(random_results)
df_random.index *= 1000
df_random /= 1000

df_rule = pd.DataFrame(rule_results)
df_rule.index *= 1000
df_rule /= 1000

df_rule_win_odds = df_rule["win"] + df_rule["odds"]
df_random_win_odds = df_random["win"] + df_random["odds"]
best_epoch = (df_rule_win_odds / df_rule_win_odds.max() + df_random_win_odds / df_random_win_odds.max()).idxmax()

df_random.plot(title="Training Evaluation: DQN Agent vs. Random Agent", xlabel="episode", ylabel="estimated probability")
plt.axvline(best_epoch, color="red", linestyle="--")
plt.savefig('./results/Agent_vs_Random.png', dpi=300)
plt.show()

df_rule.plot(title="Training Evaluation: DQN Agent vs. Rule Agent", xlabel="episode", ylabel="estimated probability")
plt.axvline(best_epoch, color="red", linestyle="--")
plt.savefig('./results/Agent_vs_Rule.png', dpi=300)
plt.show()

plt.plot(config["players"][0].losses[1:])
plt.title("MSE Loss (average of each episode)")
plt.xlabel("episode")
plt.ylabel("loss")
plt.savefig('./results/Loss.png', dpi=300)
plt.show()

print(df_random.loc[best_epoch])
print(df_rule.loc[best_epoch])


