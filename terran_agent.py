import random
#import math
#import os.path

#import numpy as np
#import pandas as pd

from pysc2.agents import base_agent
from pysc2.lib import actions
from pysc2.lib import features
from pysc2.lib import units
from pysc2.env import sc2_env
from absl import app

class TerranAgent(base_agent.BaseAgent):
	
	def unit_type_is_selected(self, obs, unit_type):
		if (len(obs.observation.single_select) > 0 and obs.observation.single_select[0].unit_type == unit_type):
			return True

		if (len(obs.observation.multi_select) > 0 and obs.observation.multi_select[0].unit_type == unit_type):
			return True

		return False

	def get_units_by_type(self, obs, unit_type):
		return [unit for unit in obs.observation.feature_units if unit.unit_type == unit_type]
	
	def step(self, obs):
		super(TerranAgent, self).step(obs)

		depots = self.get_units_by_type(obs, units.Terran.SupplyDepot)
		barracks = self.get_units_by_type(obs, units.Terran.Barracks)
		if len(barracks) == 0:
			#can't build a barracks without a supply depot
			if len(depots) >= 1:
				if self.unit_type_is_selected(obs, units.Terran.SCV):
					if (actions.FUNCTIONS.Build_Barracks_screen.id in obs.observation.available_actions):
						x = random.randint(0, 63)
						y = random.randint(0, 63)

						return actions.FUNCTIONS.Build_Barracks_screen("now", (x, y))
			#builds one depot, need to do smart checks for more
			elif len(depots) == 0:
				if self.unit_type_is_selected(obs, units.Terran.SCV):
					if (actions.FUNCTIONS.Build_SupplyDepot_screen.id in obs.observation.available_actions):
						x = random.randint(0, 63)
						y = random.randint(0, 63)

						return actions.FUNCTIONS.Build_SupplyDepot_screen("now", (x, y))
		
			scvs = self.get_units_by_type(obs, units.Terran.SCV)
			if len(scvs)  > 0:
				scv = random.choice(scvs)
				return actions.FUNCTIONS.select_point("select_all_type", (scv.x, scv.y))

		return actions.FUNCTIONS.no_op()


def main(unused_argv):
	agent = TerranAgent()
	try:
		while True:
			#command line parameters for game session

			with sc2_env.SC2Env(map_name="AbyssalReef", 
				players=[sc2_env.Agent(sc2_env.Race.terran), 
				sc2_env.Bot(sc2_env.Race.terran,
				sc2_env.Difficulty.very_easy)],
				agent_interface_format=features.AgentInterfaceFormat(
					feature_dimensions=features.Dimensions(screen=84, minimap=64),
					use_feature_units=True),
					step_mul=16,
					game_steps_per_episode=0,
					visualize=True) as env:

				agent.setup(env.observation_spec(), env.action_spec())
				timesteps = env.reset()
				agent.reset()

				while True:
					step_actions = [agent.step(timesteps[0])]
					if timesteps[0].last():
						break
					timesteps = env.step(step_actions)

	except KeyboardInterrupt:
		pass

if __name__ == "__main__":
	app.run(main)

"""class QLearningTable:

	def __init__(self, actions, learning_rate=0.01, reward_decay=0.9, e_greedy=0.9):
		self.actions = actions
		self.lr = learning_rate
		self.gamma = reward_decay
		self.epsilon = e_greedy
		self.q_table = pd.DataFrame(columns=self.actions, dtype=np.float64)
		self.disallowed_actions = {}

	def choose_action(self, observation, excluded_actions=[]):
		self.check_state_exist(observation)

		self.disallowed_actions[observation] = excluded_actions

		state_action = self.q_table.ix[observation]

		for excluded_action in excluded_actions:
			del state_action[excluded_action]
		
		if np.random.uniform() < self.epsilon:
			state_action = state_action.reindex(np.random.permutation(state_action.index))
			action = state_action.idxmax()
		#introduce randomness
		else: 
			action = np.random.choice(state_action.index)
		return action
	
	def learn(self, s, a, r, s_):
		#prevent updates to table if new state is same as old
		#--keeps less valuable actions from getting pushed to the top
		if s == s_:
			return
		self.check_state_exist(s_)
		self.check_state_exist(s)
		q_predict = self.q_table.ix[s, a]
		s_rewards = self.q_table.ix[s_, :]

		if s_ in self.disallowed_actions:
			for excluded_action in self.disallowed_actions[s_]:
				del s_rewards[excluded_action]
		if s_ != 'terminal':
			q_target = r + self.gamma *  self.q_table.ix[s_, :].max()
		else:
			q_target = r

		self.q_table.ix[s, a] += self.lr * (q_target - q_predict)

	def check_state_exist(self, state):
		if state not in self.q_table.index:
			self.q_table = self.q_table.append(pd.Series([0] * len(self.actions), index=self.q_table.columns, name=state))"""