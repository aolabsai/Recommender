# -*- coding: utf-8 -*-
"""AO architecture for the board-game-night recommender demo."""

import ao_arch as ar

description = "Board Game Night Recommender"

# game_type, duration_bucket, interaction, table_mood
arch_i = [3, 2, 1, 2]
arch_z = [10]
arch_c = []
connector_function = "full_conn"

# Keep the exported name compatible with AO examples in this repository.
arch = ar.Arch(arch_i, arch_z, arch_c, connector_function, description)
