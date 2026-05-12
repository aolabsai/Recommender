# -*- coding: utf-8 -*-
"""
AO architecture for the music-domain recommender demo.
"""

import ao_arch as ar


description = "Music Recommender System"

# genre + tempo + energy + recency + vocal/instrumental + listening context
arch_i = [3, 2, 2, 1, 1, 2]
arch_z = [10]
arch_c = []
connector_function = "full_conn"

arch = ar.Arch(arch_i, arch_z, arch_c, connector_function, description)
