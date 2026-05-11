# -*- coding: utf-8 -*-
"""
AO architecture for the recipe-domain recommender demo.
"""

import ao_arch as ar

description = "Recipe Recommender System"

# recipe attributes plus requested meal slot, cook-time limit, dietary preference, and mood
arch_i = [3, 2, 2, 2, 4, 2, 2, 4, 2]
arch_z = [12]
arch_c = []
connector_function = "full_conn"

arch = ar.Arch(arch_i, arch_z, arch_c, connector_function, description)
