# -*- coding: utf-8 -*-
"""AO architecture for the plant care recommender domain."""

import ao_arch as ar


description = "Plant Care Recommender System"

# plant_type, light level, high effort flag, care goal
arch_i = [3, 2, 1, 2]
arch_z = [10]
arch_c = []
connector_function = "full_conn"

arch = ar.Arch(arch_i, arch_z, arch_c, connector_function, description)
