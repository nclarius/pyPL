#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Main module.
"""

from expr import *
from parser import *
from structure import *
from denotation import *
from tableau import *

if __name__ == "__main__":
    parser = Parser()
    fml = r"\exi x \all y R(x,y) -> \all y \exi x R(x,y)"
    tab = Tableau(parser.parse_fml(fml))
