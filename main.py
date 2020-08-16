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

    # fml = r"\exi x \all y R(x,y) -> \all y \exi x R(x,y)"
    # tab = Tableau(parser.parse_fml(fml))

    impallout = parser.parse_fml(r"\all x (P(x) -> Q(x))")
    impallin = parser.parse_fml(r"\all x P(x) -> \all x Q(x)")
    biimpallout = parser.parse_fml(r"\all x (P(x) <-> Q(x))")
    biimpallin = parser.parse_fml(r"\all x P(x) <-> \all x Q(x)")
    tab1 = Tableau(impallin, premises=[impallout])
    tab2 = Tableau(impallout, premises=[impallin])
    tab3 = Tableau(biimpallin, premises=[biimpallout])
    tab4 = Tableau(biimpallout, premises=[biimpallin])
