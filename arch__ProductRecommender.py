# -*- coding: utf-8 -*-
"""
AO architecture for the product catalog recommender example.
"""

import ao_arch as ar


description = "Product Catalog Recommender"

# category + price tier + sustainability preference match + shopper use case
arch_i = [3, 2, 1, 2]
arch_z = [10]
arch_c = []
connector_function = "full_conn"

arch = ar.Arch(arch_i, arch_z, arch_c, connector_function, description)
