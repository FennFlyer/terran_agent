import pandas as pd
import numpy as np

class QLearningTable:

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
			self.q_table = self.q_table.append(pd.Series([0] * len(self.actions), index=self.q_table.columns, name=state))