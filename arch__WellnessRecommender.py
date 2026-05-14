# -*- coding: utf-8 -*-
"""AO architecture for the wellness micro-habit recommender domain."""

import ao_arch as ar


description = "Wellness Micro-Habit Recommender System"

# focus area, time bucket, social flag, current wellness goal
arch_i = [3, 2, 1, 2]
arch_z = [10]
arch_c = []
connector_function = "full_conn"

arch = ar.Arch(arch_i, arch_z, arch_c, connector_function, description)
