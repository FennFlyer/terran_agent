import random
#import math
#import os.path

#import numpy as np
#import pandas as pd

from pysc2.agents import base_agent
from pysc2.lib import actions
from pysc2.lib import features
from pysc2.lib import units



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