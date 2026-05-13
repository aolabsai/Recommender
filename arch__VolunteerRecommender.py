# -*- coding: utf-8 -*-
"""AO architecture for the community volunteering recommender domain."""

import ao_arch as ar

description = "Community Volunteering Recommender"

# opportunity category + time commitment + skill level + user goal
arch_i = [3, 2, 1, 2]
arch_z = [10]
arch_c = []
connector_function = "full_conn"

arch = ar.Arch(arch_i, arch_z, arch_c, connector_function, description)

