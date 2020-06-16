#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is pyPL, a simple model checker for intuitionistic first-order logic with Kripke semantics.

Usage notes:
------------
This tool is not equipped with an interactive user interface; input has to be specified in the source code.
A number of examples are already set up.
- Models and formulas to compute denotations for are defined in the function 'compute' (near bottom of source code).
  Formulas, unforunately, have to be entered in prenex form.
  Follow the existing examples and the documentations of the classes and methods to get an idea.
- You can select which models to include in the output by editing the variable 'active' (near top of source code).
- You can select whether or not to print out intermediate steps by editing the variable 'verbose' (same place).
After specifying your input in the source code, execute this script in a terminal to view the output.

If you would like to understand what's going on under the hood:
The interesting part for you are the 'denot' methods in each of the expression classes.
Compare how the formal definitions can be translated into code almost 1:1,
and try to follow why the implementation works the way it does, especially the loop logic for the quantifiers.
A recommendation is to set breakpoints and step through an evaluation process symbol by symbol
to see how a denotation is computed recursively in line with the inductive definitions,
or trace the variables v and v_ to keep track of what the current variable assignment looks like during quantification.
The '__str__' methods are what makes the expressions formatted human-readable in the output.
Simply ignore all the print statements and anything that looks completely unfamiliar to you (such as 'w'/modal stuff).

Notes on notation:
- 'M' = model/structure (aka 'A')
- 'D' = domain of discourse (aka 'M')
- 'I' = interpretation function for non-logical symbols (aka 'F')
- 'v' = variable assignment function for individual variables (aka 'g')
- 'V' = valuation function for propositional variables

Have fun!
"""


from IPL.expr import *
from IPL.model import *


# settings
active = [1, 2, 3]  # set here which models to include in the output (see def.s in fnc. 'compute')
verbose = True  # set this to True if you'd like intermediate steps to be printed out, and False otherwise


def compute():
    """
    Define models and formulas to compute denotations for here.
    """
    global depth, active

    # Example 1: counter model of p v -p and --p -> p
    #############################
    print("\n---------------------------------\n")
    #############################

    k1 = {"k0", "k1"}
    r1 = {("k0", "k1")}
    d1 = {}
    f1 = {"k0": {"p": False},
          "k1": {"p": True}}
    m1 = KripkeModel(k1, r1, d1, f1)

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
        print("[[" + repr(e) + "]]^M1 =")
        print(e.denotK(m1))
        depth = 0
        print()
        print("[[" + repr(e) + "]]^M1,k0 =")
        print(e.denotG(m1, "k0"))
        depth = 0
        print()
        print("[[" + repr(e) + "]]^M1,k1 =")
        print(e.denotG(m1, "k1"))
        depth = 0

    # Example 2: counter model of (p -> q) v (q -> p)
    #############################
    print("\n---------------------------------\n")
    #############################

    k2 = {"k0", "k1", "k2"}
    r2 = {("k0", "k1"), ("k0", "k2")}
    d2 = {}
    f2 = {"k0": {"p": False, "q": False},
          "k1": {"p": True, "q": False},
          "k2": {"p": False, "q": True}}
    m2 = KripkeModel(k2, r2, d2, f2)

    print(m2)
    print(m2.r)
    print(m2.gs)

    e2 = {
        1: Disj(Imp(Prop("p"), Prop("q")), Imp(Prop("q"), Prop("p")))
    }

    for nr, e in e2.items():
        print()
        print("[[" + repr(e) + "]]^M2 =")
        print(e.denotK(m2))
        depth = 0
    
    # Example 3: counter model of (p -> q) -> (-p v q)
    #############################
    print("\n---------------------------------\n")
    #############################

    k3 = {"k0", "k1", "k2", "k3"}
    r3 = {("k0", "k1"), ("k0", "k2"), ("k1", "k3"), ("k2", "k3")}
    d3 = {}
    f3 = {"k0": {"p": False, "q": False},
          "k1": {"p": False, "q": True},
          "k2": {"p": True, "q": True},
          "k3": {"p": True, "q": True}
          }
    m3 = KripkeModel(k3, r3, d3, f3)

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
            print("[[" + repr(e) + "]]^M3 =")
            print(e.denotK(m3))
            depth = 0
        elif nr in [2]:
            print("[[" + repr(e) + "]]^M3,k3 =")
            print(e.denotG(m3, "k3"))
            depth = 0
            print("[[" + repr(e) + "]]^M3,k1 =")
            print(e.denotG(m3, "k1"))
            depth = 0
            print("[[" + repr(e) + "]]^M3,k0 =")
            print(e.denotG(m3, "k0"))
            depth = 0
        elif nr in [3, 4, 5]:
            print("[[" + repr(e) + "]]^M3,k0 =")
            print(e.denotG(m3, "k0"))
            depth = 0


if __name__ == "__main__":
    print(__doc__)
    compute()
    print("\nScroll up for help information.")
