import math
from decimal import Decimal
from datetime import timedelta
import numpy as np
from typing import Dict, List

from cadCAD.configuration import Experiment
from cadCAD.configuration.utils import bound_norm_random, ep_time_step, config_sim, access_block

from .genesis_states import genesis_states
from .partial_state_update_block import partial_state_update_block


sim_config = config_sim({
    'N': 5,
    'T': range(100),  # day
})


env_processes = {}

exp = Experiment()

exp.append_configs(
    sim_configs=sim_config,
    initial_state=genesis_states,
    env_processes=env_processes,
    partial_state_update_blocks=partial_state_update_block
)

