# -*- coding: utf-8 -*-
"""AO architecture for the home maintenance recommender domain."""

import ao_arch as ar


description = "Home Maintenance Recommender"

# category + urgency + high effort + household goal
arch_i = [3, 2, 1, 2]
arch_z = [10]
arch_c = []
connector_function = "full_conn"

arch = ar.Arch(arch_i, arch_z, arch_c, connector_function, description)
