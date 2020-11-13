#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Main module.
"""


if __name__ == "__main__":
    parser = __import__("parser")
    parse_fml = parser.FmlParser().parse
    parse_strct = parser.StructParser().parse
