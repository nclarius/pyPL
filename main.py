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
    parser = __import__("parser")
    parse_fml = parser.FmlParser().parse
    parse_strct = parser.StructParser().parse

    print(len(parse_fml("R(x)")))
    print(len(parse_fml("Know(x)")))
