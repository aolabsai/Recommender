# -*- coding: utf-8 -*-
"""
Arch file for Programming/Coding Education Resource Recommender
Suggests programming tutorials, courses, and practice resources 
based on the user's skill level, interests, and learning progress.
"""

import ao_arch as ar

description = "Programming Education Resource Recommender"

# Input encoding: topic(3) + difficulty(2) + format(1) + experience(2) = 8 bits
# topic: web/mobile/data/AI/systems/DevOps/game/crypto/embedded/other
# difficulty: beginner/intermediate/advanced
# format: video/article/interactive
# experience: none/some/experienced
arch_i = [3, 2, 1, 2]   # topic_binary + difficulty_binary + format_binary + experience_binary
arch_z = [10]            # output: resource recommendation encoding
arch_c = []              
connector_function = "full_conn"

arch = ar.Arch(arch_i, arch_z, arch_c, connector_function, description)
