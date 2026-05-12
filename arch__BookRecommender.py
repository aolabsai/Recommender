# -*- coding: utf-8 -*-
"""
Architecture definition for the book-domain recommender demo.

The input vector is built in book_domain.encode_book:
genre + pace + length + tone + format + current reader mood.
"""

import ao_arch as ar
from book_domain import binary_input_size

description = "Book recommender for local catalog and reader context"

arch_i = [binary_input_size()]
arch_z = [10]
arch_c = []
connector_function = "full_conn"

arch = ar.Arch(arch_i, arch_z, arch_c, connector_function, description)
