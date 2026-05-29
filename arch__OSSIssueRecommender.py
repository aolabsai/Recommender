# -*- coding: utf-8 -*-
"""
// aolabs.ai software >ao_core/Arch.py (C) 2023 Animo Omnis Corporation. All Rights Reserved.

Arch file for OSS Issue Recommender domain.
8-bit input shape matching the base Recommender architecture.
"""

import ao_arch as ar

description = "Open-Source Issue Recommender Domain"

# 8-bit input: [area(3)] [effort(2)] [beginner_friendly(1)] [goal(2)]
arch_i = [3, 2, 1, 2]   # Area encoding + Effort encoding + Beginner flag + Goal category
arch_z = [12]            # 12 catalog items to rank against
arch_c = []              # No context outputs
connector_function = "full_conn"

arch = ar.Arch(arch_i, arch_z, arch_c, connector_function, description)
