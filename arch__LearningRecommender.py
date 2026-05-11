# -*- coding: utf-8 -*-
"""
AO architecture for the learning-resource recommender demo.
"""

import ao_arch as ar


description = "Learning Resource Recommender System"

# topic + format + duration + difficulty + hands-on + free/paid + learner goal
arch_i = [3, 2, 2, 1, 1, 1, 2]
arch_z = [10]
arch_c = []
connector_function = "full_conn"

arch = ar.Arch(arch_i, arch_z, arch_c, connector_function, description)
