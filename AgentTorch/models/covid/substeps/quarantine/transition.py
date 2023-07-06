import torch
import torch.nn as nn
import re

from AgentTorch.substep import SubstepTransition
from AgentTorch.helpers import *

class Quarantine(SubstepTransition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.device = self.config['simulation_metadata']['device']
        self.num_agents = self.config['simulation_metatdata']['num_citizens']
        self.quarantine_days = self.config['simulation_metadata']['quarantine_days']
        self.num_steps = self.config['simulation_metadata']['num_steps']

    def end_quarantine(self, t, is_quarantined, quarantine_start_date):
        agents_quarantine_end_date = quarantine_start_date + self.quarantine_days
        agent_quarantine_ends =  (t>= agents_quarantine_end_date)

        if agent_quarantine_ends.sum() >= 0:
            is_quarantined[t, agent_quarantine_ends.bool()] = 0
            quarantine_start_date[agent_quarantine_ends.bool()] = self.num_steps + 1
        
        return is_quarantined, quarantine_start_date

    def start_quarantine(self, t, is_quarantined, quarantine_start_date, quarantine_start_prob):
        agents_quarantine_start = diff_sample(quarantine_start_prob,size=self.num_agents).to(self.device)
         agents_quarantine_start = torch.logical_and(
            torch.logical_not(is_quarantined[t]), agents_quarantine_start)
        if agents_quarantine_start.sum() >= 0:
            is_quarantined[t, agents_quarantine_start.bool()] = 1
            quarantine_start_date[agents_quarantine_start.bool()] = t

        return is_quarantined, quarantine_start_date

    def break_quarantine(self, t, is_quarantined, quarantine_start_date, quarantine_break_prob):
        agents_quarantine_break = diff_sample(quarantine_start_prob, size=self.num_agents).to(self.device)
        agents_quarantine_break = torch.logical_and(is_quarantined[t], agents_quarantine_break)
        
        if agents_quarantine_break.sum() >= 0:
            is_quarantined[t, agents_quarantine_break.bool()] = 0
            quarantine_start_date[agents_quarantine_break.bool()] = self.params['num_steps'] + 1

        return is_quarantined, quarantine_start_date

    def update_quarantine_status(self, t, is_quarantined, quarantine_start_date, quarantine_start_prob, quarantine_break_prob):
        is_quarantined, quarantine_start_date = self.end_quarantine(t, is_quarantined, quarantine_start_date)
        is_quarantined, quarantine_start_date = self.start_quarantine(t, is_quarantined, quarantine_start_date, quarantine_start_prob)
        is_quarantined, quarantine_start_date = self.break_quarantine(t, is_quarantined, quarantine_start_date, quarantine_break_prob)

        return is_quarantined, quarantine_start_date

    def forward(self, state, action=None):
        input_variables = self.input_variables
        t = state['current_step']

        is_quarantined = get_by_path(state, re.split("/", input_variables['is_quarantined']))
        quarantine_start_date = get_by_path(state, re.split("/", input_variables['quarantine_start_date']))

        quarantine_start_prob = get_by_path(state, re.split("/", input_variables['quarantine_start_prob']))
        quarantine_break_prob = get_by_path(state, re.split("/", input_variables['quarantine_break_prob']))

        new_is_quarantined, new_quarantine_start_date = update_quarantine_status(self, t, is_quarantined, quarantine_start_date, quarantine_start_prob, quarantine_break_prob)

        return {self.output_variables[0]: new_is_quarantined, self.output_variablesp[1]: new_quarantine_start_date}