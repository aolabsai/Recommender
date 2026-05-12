# -*- coding: utf-8 -*-
"""AO architecture for the fitness recommender demo."""

import ao_arch as ar

from fitness_domain import INPUT_SCHEMA


description = "Fitness and workout recommender"

arch_i = [width for _, width in INPUT_SCHEMA]
arch_z = [12]
arch_c = []
connector_function = "full_conn"

arch = ar.Arch(arch_i, arch_z, arch_c, connector_function, description)

