#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Main module. Input specification and program execution are defined here."""


from expr import *
from struct import *


# settings
active = [1, 2, 3]  # set here which structures to include in the output (see def.s in fnc. 'compute')
verbose = True  # set this to True if you'd like intermediate steps to be printed out, and False otherwise


def compute():
    """
    Define structures and formulas to compute denotations for here.
    """
    global depth, active

    # Example 1: counter structure of p v -p and --p -> p
    #############################
    print("\n---------------------------------\n")
    #############################

    k1 = {"k0", "k1"}
    r1 = {("k0", "k1")}
    d1 = {}
    i1 = {"k0": {"p": False},
          "k1": {"p": True}}
    m1 = KripkeStructure(k1, r1, d1, i1)

    print(m1)
    print(m1.r)
    print(m1.gs)

    e1 = {
        1: Disj(Prop("p"), Neg(Prop("p"))),
        2: Imp(Neg(Neg(Prop("p"))), Prop("p")),
        3: Neg(Neg(Disj(Prop("p"), Neg(Prop("p"))))),
        4: Prop("p"),
        5: Neg(Prop("p")),
        6: Neg(Neg(Prop("p")))
    }

    for nr, e in e1.items():
        print()
        print("[[" + str(e) + "]]^M1 =")
        print(e.denotK(m1))
        depth = 0
        print()
        print("[[" + str(e) + "]]^M1,k0 =")
        print(e.denotV(m1, "k0"))
        depth = 0
        print()
        print("[[" + str(e) + "]]^M1,k1 =")
        print(e.denotV(m1, "k1"))
        depth = 0

    # Example 2: counter structure of (p -> q) v (q -> p)
    #############################
    print("\n---------------------------------\n")
    #############################

    k2 = {"k0", "k1", "k2"}
    r2 = {("k0", "k1"), ("k0", "k2")}
    d2 = {}
    i2 = {"k0": {"p": False, "q": False},
          "k1": {"p": True, "q": False},
          "k2": {"p": False, "q": True}}
    m2 = KripkeStructure(k2, r2, d2, i2)

    print(m2)
    print(m2.r)
    print(m2.gs)

    e2 = {
        1: Disj(Imp(Prop("p"), Prop("q")), Imp(Prop("q"), Prop("p")))
    }

    for nr, e in e2.items():
        print()
        print("[[" + str(e) + "]]^M2 =")
        print(e.denotK(m2))
        depth = 0
    
    # Example 3: counter structure of (p -> q) -> (-p v q)
    #############################
    print("\n---------------------------------\n")
    #############################

    k3 = {"k0", "k1", "k2", "k3"}
    r3 = {("k0", "k1"), ("k0", "k2"), ("k1", "k3"), ("k2", "k3")}
    d3 = {}
    i3 = {"k0": {"p": False, "q": False},
          "k1": {"p": False, "q": True},
          "k2": {"p": True, "q": True},
          "k3": {"p": True, "q": True}
          }
    m3 = KripkeStructure(k3, r3, d3, i3)

    print(m3)
    print(m3.r)
    print(m3.gs)

    e3 = {
        1: Imp(Imp(Prop("p"), Prop("q")), Disj(Neg(Prop("p")), Prop("q"))),
        2: Imp(Prop("p"), Prop("q")),
        3: Disj(Neg(Prop("p")), Prop("q")),
        4: Neg(Prop("p")),
        5: Prop("q")
    }

    for nr, e in e3.items():
        print()
        if nr in [1]:
            print("[[" + str(e) + "]]^M3 =")
            print(e.denotK(m3))
            depth = 0
        elif nr in [2]:
            print("[[" + str(e) + "]]^M3,k3 =")
            print(e.denotV(m3, "k3"))
            depth = 0
            print("[[" + str(e) + "]]^M3,k1 =")
            print(e.denotV(m3, "k1"))
            depth = 0
            print("[[" + str(e) + "]]^M3,k0 =")
            print(e.denotV(m3, "k0"))
            depth = 0
        elif nr in [3, 4, 5]:
            print("[[" + str(e) + "]]^M3,k0 =")
            print(e.denotV(m3, "k0"))
            depth = 0

    #############################
    print("\n---------------------------------\n")
    #############################

if __name__ == "__main__":
    compute()
