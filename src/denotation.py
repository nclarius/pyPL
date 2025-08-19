#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Helper file for denotations.
"""

from expr import *

import os
from time import time
import re

from functools import reduce


class Denotation:

    def __init__(self, exprs):
        self.exprs = exprs

    def show(self, latex):
        res = ""

        # print preamble
        if latex:
            path_preamble = os.path.join(os.path.dirname(__file__), "preamble.tex")
            with open(path_preamble) as f:
                preamble = f.read()
                preamble += "\n\n\\setlength\\tabcolsep{3pt}\n"
            res += preamble + "\n\n\\begin{document}\n\n"

        # print structure
        if not latex:
            res += str(self.exprs[0][1]) + "\n\n"
        else:
            res += self.exprs[0][1].tex() + "\\\\ \\ \\\\ \n"

        for fml, s, v, w in self.exprs:
            # print expression
            if not latex:
                res += "[[" + str(fml) + "]]" + s.s + ("," + v if v else "") + ("," + w if w else "") + "\n= "
            else:
                res += "$[\\![" + fml.tex() + "]\\!]^" + "{" + \
                       "\\mathcal{" + s.s[0] + ("_{" + s.s[1:] + "}" if len(s.s) > 1 else "") + "}" + \
                       ("," + v if v else "") + \
                       ("," + w if w else "") + \
                       "}\\\\\n= "
                res = re.sub("v(\d+)", "v_{\\1}", res)
                res = re.sub("w(\d+)", "w_{\\1}", res)

            # print denotation
            print(fml, v, w)
            with SleepInhibitor("computing a denotation"):
                self.start = time()
                if "modal" not in s.mode() and "classical" in s.mode():  # classical non-modal logic
                    if not v:
                        res += self.format(fml.denotV(s), latex)
                    else:
                        res += self.format(fml.denot(s, s.v[v]), latex)
                else:  # classical modal logic or intuitionistic logic
                    if not v:
                        if not w:
                            print("computing denotVW", fml)
                            print(str(self.format(fml.denotVW(s), latex)))
                            res += str(self.format(fml.denotVW(s), latex))
                            print("done computing denotVW", fml)
                        else:
                            res += self.format(fml.denotV(s, w), latex)
                    else:
                        if not w:
                            res += self.format(fml.denotW(s, s.v[v]), latex)
                        else:
                            res += self.format(fml.denot(s, s.v[v], w), latex)
                self.end = time()
            if not latex:
                res += "\n\n"
            else:
                res += "$\\\\ \n\n" if latex else ""

        # print postamble
        if latex:
            res += "\n\n\\end{document}"

        # write and open output
        write_output = __import__("gui").write_output
        print("writing output")
        write_output(res, latex)

    def format(self, obj, latex):
        if isinstance(obj, str):
            if obj[0] == "w" and obj[-1].isdigit():
                if latex:
                    return "w" + "_{" + obj[1:] + "}"
                else:
                    return obj
            else:
                if latex:
                    return "\\textrm{" + obj + "}"
                else:
                    return obj
        elif isinstance(obj, bool):
            if latex:
                return "\\textrm{" + str(obj) + "}"
            else:
                return str(obj)
        elif isinstance(obj, tuple):
            if latex:
                return "\\langle" + ", ".join([self.format(el, latex) for el in obj]) + "\\rangle"
            else:
                return "⟨" + ", ".join([self.format(el, latex) for el in obj]) + "⟩"
        elif isinstance(obj, set):
            if latex:
                return "\\{" + ", ".join([self.format(el, latex) for el in obj]) + "\\}"
            else:
                return "{" + ", ".join([self.format(el, latex) for el in obj]) + "}"
        elif isinstance(obj, dict):
            if latex:
                return "\\begin{matrix*}[l]\n" + "\\\\\n".join([self.format(key, latex) + " & \\mapsto & " +
                                                                self.format(value, latex) for key, value in obj.items()]
                ) + "\n\\end{matrix*}\n"
            else:
                return "[" + ", ".join(
                        [self.format(key, latex) + ": " + self.format(value, latex) for key, value in obj.items()]
                ) + "]"
        elif isinstance(obj, frozenset):
            if latex:
                return "\\begin{matrix*}[l]\n" + "\\\\\n".join(
                        [self.format(key, latex) + " & \\mapsto & " + self.format(value, latex) for key, value in obj]
                ) + "\n\\end{matrix*}\n"
            else:
                return "[" + ", ".join(
                        [self.format(key, latex) + ": " + self.format(value, latex) for key, value in obj]
                ) + "]"
        else:
            return str(obj)


def compute_active():
    """
    Define structures and formulas to compute denotations for here.
    """
    # todo update to use class

    global depth, active
    active = []  # set here which denotations to include in the output (see def.s in fnc. 'compute_active')
    verbose = True  # set this to True if you'd like intermediate steps to be printed out, and False otherwise

    if 1 in active:
        ############################
        print("\n---------------------------------\n")
        ############################

        print("Example #1: tupperware boxes, lids and a bunny (logic for linguists lecture 010)")
        print()

        d1 = {"roundbox", "roundlid", "rectbox", "rectlid", "bunny"}
        i1 = {"b1": "roundbox", "b2": "rectbox", "f": "bunny",
              "box": {("roundbox", ), ("rectbox", )},
              "lid": {("roundlid", ), ("rectlid", )},
              "fit": {("roundlid", "roundbox"), ("rectlid", "rectbox")}
        }
        s1 = PredStructure("S1", d1, i1)
        v1 = {"x": "roundbox", "y": "bunny"}
        vv1 = {"x": "bunny", "y": "rectbox"}

        print(s1)
        print("v1 = " + str(v1))
        print("v'1 = " + str(vv1))

        e1 = {
            1: Var("x"),
            2: Const("f"),
            3: Atm(Pred("box"), (Var("x"),)),
            4: Forall(Var("x"), Imp(Atm(Pred("box"), (Var("x"),)),
                                    Exists(Var("y"), Conj(Atm(Pred("lid"), (Var("y"),)),
                                                          Atm(Pred("fit"), (Var("y"), Var("x"))))))),
            5: Exists(Var("y"), Conj(Atm(Pred("lid"), (Var("y"),)),
                                     Forall(Var("x"), Imp(Atm(Pred("box"), (Var("x"),)),
                                                          Atm(Pred("fit"), (Var("y"), Var("x")))))))
        }

        for nr, e in e1.items():
            if nr <= 3:
                print()
                print("⟦" + str(e) + "⟧^S1,v1 =")
                print(e.denot(s1, v1))
                depth = 0
                print()
                print("⟦" + str(e) + "⟧^S1,v'1 =")
                print(e.denot(s1, vv1))
                depth = 0
            if nr > 3:
                print()
                print("⟦" + str(e) + "⟧^S1 =")
                print(e.denotV(s1))
                depth = 0



    if 2 in active:
        #############################
        print("\n---------------------------------\n")
        ############################

        print("Example #2: MMiL (logic for linguists Example #from the book)")
        print()

        d2 = {"Mary", "Jane", "MMiL"}
        i2 = {"m": "Mary",
              "student": {("Mary", ), ("Jane", )},
              "book": {("MMiL", )},
              "read": {("Mary", "MMiL")}
        }
        s1 = PredStructure("D2", d2, i2)
        v2 = {"x": "Jane", "y": "Mary", "z": "MMiL"}

        print(s1)
        print("v = " + str(v2))

        e2 = {
            1: Var("x"),  # Jane
            2: Const("m"),  # Mary
            3: Pred("read"),  # {(Mary, MMiL)}
            4: Atm(Pred("book"), (Var("x"),)),  # false, since Jane is not a book
            5: Exists(Var("x"), Conj(Atm(Pred("book"), (Var("x"),)), Atm(Pred("read"), (Const("m"), Var("x"))))), # true
            6: Forall(Var("y"), Imp(Atm(Pred("student"), (Var("y"),)),
                                    Exists(Var("x"),
                                           Conj(Atm(Pred("book"), (Var("x"),)),
                                                Atm(Pred("read"), (Var("y"), Var("z"))))))),
               # false, since Jane doesn't read a book
            7: Neg(Exists(Var("y"), Conj(Atm(Pred("student"), (Var("y"),)),
                                         Exists(Var("x"),
                                                Conj(Atm(Pred("book"), (Var("x"),)),
                                                     Atm(Pred("read"), (Var("y"), (Var("z")))))))))
               # false, since Mary reads a book
        }

        for nr, e in e2.items():
            print()
            print("⟦" + str(e) + "⟧^S2,v2 =")
            print(e.denot(s1, v2))
            depth = 0


    if 3 in active:
        #############################
        print("\n---------------------------------\n")
        #############################

        print("Example #3: love #1 (logic for linguists ExSh 10 Ex. 1)")
        print()

        d3 = {"Mary", "John", "Peter"}
        i3 = {"j": "Peter", "p": "John",
              "woman": {("Mary",)},
              "man": {("John", ), ("Peter", )},
              "love": {("Mary", "John"), ("John", "Mary"), ("John", "John"), ("Peter", "Mary"), ("Peter", "John")},
              "jealous": {("Peter", "John", "Mary"), ("Peter", "Mary", "John")}}
        s1 = PredStructure("S3", d3, i3)
        v3 = {"x": "Mary", "y": "Mary", "z": "Peter"}
        vv3 = {"x": "John", "y": "Peter", "z": "John"}

        print(s1)
        print("v = " + str(v3))
        print("v' = " + str(vv3))

        e3 = {
            1:  Const("p"),
            2:  Var("y"),
            3:  Var("y"),
            4:  Atm(Pred("love"), (Const("p"), Const("j"))),
            5:  Atm(Pred("love"), (Var("y"), Var("z"))),
            6:  Atm(Pred("love"), (Var("y"), Var("z"))),
            7:  Exists(Var("x"), Neg(Atm(Pred("love"), (Const("j"), Var("x"))))),
            8:  Forall(Var("x"), Exists(Var("y"), Atm(Pred("love"), (Var("x"), Var("y"))))),
            9:  Neg(Forall(Var("x"), Imp(Atm(Pred("woman"), (Var("x"),)),
                                         Exists(Var("y"), Conj(Atm(Pred("man"), (Var("y"),)),
                                                               Atm(Pred("love"), (Var("x"), Var("y"))))
                                                )))),
            10: Neg(Exists(Var("y"), Exists(Var("z"), Atm(Pred("jealous"), (Const("j"), Var("y"), Var("z"))))))

        }

        for nr, e in e3.items():
            # print(e)
            if nr in [1, 2, 4, 5, 7, 8, 9, 11, 12, 13]:
                print()
                print("⟦" + str(e) + "⟧^S3,v3 =")
                print(e.denot(s1, v3))
                depth = 0
            elif nr in [3, 6, 10]:
                print()
                print("⟦" + str(e) + "⟧^S3,v'3 =")
                print(e.denot(s1, vv3))
                depth = 0


    if 4 in active:
        #############################
        print("\n---------------------------------\n")
        #############################

        print("(Example #4: love #2 (modification of Example #3)")
        print()

        d4 = {"Mary", "John", "Susan"}
        i4 = {"m": "Mary", "j": "John", "s": "Susan",
              "rain": {},
              "sun": {()},
              "woman": {("Mary",), ("Susan",)}, "man": {("John",)},
              "love": {("John", "Mary"), ("Mary", "Susan"), ("Susan", "Mary"), ("Susan", "Susan")},
              "jealous": {("John", "Susan", "Mary")}}
        s1 = PredStructure("S4", d4, i4)
        v4 = s1.vs[5]

        print(s1)
        print("v = " + str(v4))

        e4 = {
            1:  Var("x"),  # Susan
            2:  Const("j"),  # John
            3:  Pred("love"),  # {(J,M), (M,S), (S,M), (S,S)}
            4:  Atm(Pred("love"), (Var("x"), Const("m"))),  # true under g, false in m
            5:  Atm(Pred("love"), (Const("j"), Const("m"))),  # true
            6:  Exists(Var("x"), Atm(Pred("love"), (Const("j"), Var("x")))),  # true
            7:  Forall(Var("x"), Atm(Pred("love"), (Const("j"), Var("x")))),  # false
            8:  Conj(Atm(Pred("love"), (Const("m"), Const("s"))), Atm(Pred("love"), (Const("s"), Const("m")))),  # true
            9:  Forall(Var("x"), Imp(Atm(Pred("love"), (Const("s"), Var("x"))), Atm(Pred("woman"), (Var("x"),)))),# true
            10: Neg(Exists(Var("x"), Atm(Pred("love"), (Var("x"), Var("x"))))),  # false
            11: Neg(Forall(Var("x"), Atm(Pred("love"), (Var("x"), Var("x"))))),  # true
            12: Forall(Var("x"), Imp(Atm(Pred("woman"), (Var("x"),)),
                                     Exists(Var("y"), Conj(Atm(Pred("man"), (Var("y"),)),
                                                           Atm(Pred("love"), (Var("x"), Var("y"))))))),  # false
            13: Imp(
                Conj(Conj(Atm(Pred("love"), (Var("x"), Var("y"))),
                          Atm(Pred("love"), (Var("y"), Var("z")))),
                     Neg(Atm(Pred("love"), (Var("y"), Var("x"))))),
                Atm(Pred("jealous"), (Var("x"), Var("z"), Var("y")))),  # true
            14: Conj(Exists(Var("x"), Atm(Pred("love"), (Var("x"), Var("x")))), Atm(Pred("woman"), (Var("x"),))),
            15: Atm(Pred("rain"), ()),
            16: Atm(Pred("sun"), ())
        }

        for nr, e in e4.items():
            if 1 <= nr <= 4:
                print()
                print("⟦" + str(e) + "⟧^S4,v4 =")
                print(e.denot(s1, v4))
                depth = 0
            if 4 <= nr <= 16:
                print()
                print("⟦" + str(e) + "⟧^S4 =")
                print(e.denotV(s1))
                depth = 0
            # if nr == 14:
            #     print(e.freevars())
            #     print(e.boundvars())


    if 5 in active:
        #############################
        print("\n---------------------------------\n")
        #############################

        print("Example #5: term equality and function symbols")
        print()

        d5 = {"Mary", "Peter", "Susan", "Jane"}
        i5 = {"m": "Mary", "s": "Susan", "j": "Jane",
              "mother": {("Mary",): "Susan", ("Peter",): "Susan", ("Susan",): "Jane"}}
        s1 = PredStructure("S5", d5, i5)
        v5 = {"x": "Susan", "y": "Mary", "z": "Peter"}

        print(s1)
        print("v = " + str(v5))

        e5 = {
            1: FuncTerm(Func("mother"), (Const("m"),)),  # Susan
            2: FuncTerm(Func("mother"), (FuncTerm(Func("mother"), (Const("m"),)),)),  # Jane
            3: Eq(FuncTerm(Func("mother"), (Const("m"),)), Const("s")),  # true
            4: Neg(Eq(Var("x"), Const("m")))  # true
        }

        for nr, e in e5.items():
            print()
            print("⟦" + str(e) + "⟧^S5,v5 =")
            print(e.denot(s1, v5))
            depth = 0


    if 6 in active:
        #############################
        print("\n---------------------------------\n")
        #############################

        print("Example #6: modal logic with constant domain")
        print()

        w6 = {"w1", "w2"}
        r6 = {("w1", "w1"), ("w1", "w2"), ("w2", "w2"), ("w2", "w2")}
        d6 = {"a"}
        i6 = {"P": {"w1": {()}, "w2": set()}}
        s1 = ConstModalStructure("S6", w6, r6, d6, i6)
        v6 = s1.vs[0]

        print(s1)
        print(v6)

        e6 = {
            1: Poss(Nec(Eq(Var("x"), Var("x")))),
            2: Nec(Disj(Atm(Pred("P"), tuple()), Neg(Atm(Pred("P"), tuple())))),
            3: Disj(Nec(Atm(Pred("P"), tuple())), Nec(Neg(Atm(Pred("P"), tuple()))))
        }

        for nr, e in e6.items():
            # print()
            # print("⟦" + str(e) + "⟧^S6,v6,w1 =")
            # print(e.denot(s1, v6, "w1"))
            # depth = 0
            # print()
            # print("⟦" + str(e) + "⟧^S6,v6,w2 =")
            # print(e.denot(s1, v6, "w2"))
            # depth = 0
            print("⟦" + str(e) + "⟧^S6,v6 =")
            print(e.denotW(s1, v6))
            depth = 0


    if 7 in active:
        #############################
        print("\n---------------------------------\n")
        #############################

        print("Example #7: modal logic with varying domain")
        print()

        w7 = {"w1", "w2"}
        r7 = {("w1", "w1"), ("w1", "w2"), ("w2", "w2"), ("w2", "w2")}
        d7 = {"w1": {"a"},
              "w2": {"a", "b"}}
        i7 = {"P": {"w1": {("a",)}, "w2": {("b",)}}}
        s1 = VarModalStructure("S7", w7, r7, d7, i7)

        print(s1)
        print(s1.vs)

        e7 = {
            1: Exists(Var("x"), Exists(Var("y"), Neg(Eq(Var("x"), Var("y"))))),
            2: Exists(Var("x"), Eq(Var("x"), Var("x")))
        }

        for nr, e in e7.items():
            print()
            print("⟦" + str(e) + "⟧^S7,w1 =")
            print(e.denotV(s1, "w1"))
            depth = 0
            print()
            print("⟦" + str(e) + "⟧^S7,w2 =")
            print(e.denotV(s1, "w2"))
            depth = 0
            print()
            print("⟦" + str(e) + "⟧^S7 =")
            print(e.denotVW(s1))
            depth = 0
            # print(e.denotV(s1))
            # print(e.denotW(s1, v7))
            # print(e.denotVW(s1))
            # depth = 0

    if 8 in active:
        #############################
        print("\n---------------------------------\n")
        #############################

        print("Example #8: propositional logic")
        print()

        v8a = {"p": True, "q": False, "r": True}
        s1a = PropStructure("S8", v8a)

        print(s1a)

        e8 = {
            1: Disj(Imp(Prop("p"), Prop("r")), Imp(Prop("q"), Prop("r")))
        }

        for nr, e in e8.items():
            print()
            print("⟦" + str(e) + "⟧^S9 =")
            print(e.denot(s1a))
            depth = 0

        v8b = {"p": True, "q": True, "r": False}
        s1b = PropStructure("S8'", v8b)

        print()

        print(s1b)

        for nr, e in e8.items():
            print()
            print("⟦" + str(e) + "⟧^S8' =")
            print(e.denot(s1b))
            depth = 0

    if 9 in active:
        #############################
        print("\n---------------------------------\n")
        #############################

        print("Example #9: predicate logic (logic for computer scientists lecture 07)")
        print()

        d9a = {"m1", "m2"}
        i9a = {"S": {("m1", )},
               "R": {("m1", "m1"), ("m2", "m1")}}
        s1a = PredStructure("S9a", d9a, i9a)

        print(s1a)

        e9 = {
            1: Forall(Var("x"), Exists(Var("y"),
                                       Conj(Atm(Pred("S"), (Var("y"),)), Atm(Pred("R"), (Var("x"), Var("y"))))))
        }

        for nr, e in e9.items():
            print()
            print("⟦" + str(e) + "⟧^S9 =")
            print(e.denotV(s1a))
            depth = 0

        print()

        d9b = {"s1", "s1"}
        i9b = {"S": {("s1", )},
               "R": {("s1", "s1"), ("s1", "s1")}
              }
        s1b = PredStructure("S9'", d9b, i9b)

        print(s1b)

        for nr, e in e9.items():
            print()
            print("⟦" + str(e) + "⟧^S9' =")
            print(e.denotV(s1b))
            depth = 0

    if 10 in active:
        #############################
        print("\n---------------------------------\n")
        #############################

        print("Example #10: predicate logic (logic for computer scientists exercise sheet 07)")
        print()

        d10 = {"a", "b", "c"}
        i10 = {"P": {("a",)},
               "R": {("a", "a"), ("a", "b"), ("a", "c"), ("b", "c")},
               "k": "b",
               "l": "a"}
        s1 = PredStructure("S10", d10, i10)

        print(s1)

        e10 = {
            1: Neg(Atm(Pred("R"), (Const("l"), Var("x")))),
            2: Exists(Var("x"), Exists(Var("y"), Atm(Pred("R"), (Var("x"), Var("y"))))),
            3: Forall(Var("x"), Exists(Var("y"),
                                       Conj(Atm(Pred("P"), (Var("x"),)), Atm(Pred("R"), (Var("x"), Var("y"))))))
        }

        for nr, e in e10.items():
            print()
            print("⟦" + str(e) + "⟧^S10 =")
            print(e.denotV(s1))
            depth = 0

        print()

    # todo IL doesn't work yet

    if 11 in active:
        #############################
        print("\n---------------------------------\n")
        #############################
        print("Example 11: IL -- counter model of p v -p and --p -> p")

        k11 = {"k0", "k1"}
        r11 = {("k0", "k1")}
        v11 = {"p": {"k0": False, "k1": True}}
        s1 = KripkePropStructure("S11", k11, r11, v11)

        print(s1)
        print(s1.r)

        e11 = {
            11: Disj(Prop("p"), Neg(Prop("p"))),
            2: Imp(Neg(Neg(Prop("p"))), Prop("p")),
            3: Neg(Neg(Disj(Prop("p"), Neg(Prop("p"))))),
            4: Prop("p"),
            5: Neg(Prop("p")),
            6: Neg(Neg(Prop("p")))
        }

        for nr, e in e11.items():
            print()
            print("[[" + str(e) + "]]^S11 =")
            print(e.denotVW(s1))
            depth = 0
            print()
            print("[[" + str(e) + "]]^S11,k0 =")
            print(e.denotV(s1, "k0"))
            depth = 0
            print()
            print("[[" + str(e) + "]]^S11,k1 =")
            print(e.denotV(s1, "k1"))
            depth = 0

    if 12 in active:
        #############################
        print("\n---------------------------------\n")
        #############################
        print("Example 12: IL -- counter model of (p -> q) v (q -> p)")

        k12 = {"k0", "k1", "k2"}
        r12 = {("k0", "k1"), ("k0", "k2")}
        v12 = {"p": {"k0": False, "k1": True, "k2": False},
               "q": {"k0": False, "k1": False, "k2": True}}
        s1 = KripkePropStructure("S12", k12, r12, v12)

        print(s1)
        print(s1.r)

        e12 = {
            1: Disj(Imp(Prop("p"), Prop("q")), Imp(Prop("q"), Prop("p")))
        }

        for nr, e in e12.items():
            print()
            print("[[" + str(e) + "]]^S12 =")
            print(e.denotVW(s1))
            depth = 0

    if 13 in active:
        #############################
        print("\n---------------------------------\n")
        #############################
        print("Example 13: IL -- counter model of (p -> q) -> (-p v q)")

        k13 = {"k0", "k1", "k2", "k3"}
        r13 = {("k0", "k1"), ("k0", "k2"), ("k1", "k13"), ("k2", "k3")}
        v13 = {"p": {"k0": False, "k1": False, "k2": True, "k3": True},
               "q": {"k0": False, "k1": True, "k2": True, "k3": True}}
        s1 = KripkePropStructure("S113", k13, r13, v13)

        print(s1)
        print(s1.r)

        e13 = {
            1: Imp(Imp(Prop("p"), Prop("q")), Disj(Neg(Prop("p")), Prop("q"))),
            2: Imp(Prop("p"), Prop("q")),
            13: Disj(Neg(Prop("p")), Prop("q")),
            4: Neg(Prop("p")),
            5: Prop("q")
        }

        for nr, e in e13.items():
            print()
            if nr in [1]:
                print("[[" + str(e) + "]]^S13 =")
                print(e.denotVW(s1))
                depth = 0
            elif nr in [2]:
                print("[[" + str(e) + "]]^S13,k3 =")
                print(e.denotV(s1, "k3"))
                depth = 0
                print("[[" + str(e) + "]]^S13,k1 =")
                print(e.denotV(s1, "k1"))
                depth = 0
                print("[[" + str(e) + "]]^S13,k0 =")
                print(e.denotV(s1, "k0"))
                depth = 0
            elif nr in [13, 4, 5]:
                print("[[" + str(e) + "]]^S13,k0 =")
                print(e.denotV(s1, "k0"))
                depth = 0

    if 14 in active:
        #############################
        print("\n---------------------------------\n")
        #############################
        print("Example 14: ML - believe-contexts")

        w14 = {"w0", "w1", "w2"}
        r14 = set()
        d14 = {"John", "JoeBiden", "DonaldTrump"}
        i14 = {"e": {"w0": "JoeBiden", "w1": "DonaldTrump", "w2": "DonaldTrump"},
               "j": {"w0": "John", "w1": "John", "w3": "John"},
               "b": {"w0": "JoeBiden", "w1": "JoeBiden", "w3": "JoeBiden"},
               "t": {"w0": "DonaldTrump", "w1": "DonaldTrump", "w3": "DonaldTrump"}}

        s14 = ConstModalStructure("S14", w14, r14, d14, i14)
        print(s14)

        e14 = {
                1: Const("e"),
                2: Int(Const("e")),
                3: Ext(Int(Const("e"))),
                4: Eq(Ext(Int(Const("e"))), Const("e"))
        }

        for nr, e in e14.items():
            print()
            if nr in [1, 2, 3, 4, 5]:
                print("[[" + str(e) + "]]^S14,w0 =")
                print(e.denotV(s14, "w0"))
                depth = 0

        #############################
        print("\n---------------------------------\n")
        #############################

    if 15 in active:
        #############################
        print("\n---------------------------------\n")
        #############################
        print("Example 15: PL - love")

        d15 = {"Mary", "Susan", "John", "Peter"}
        i15 = {"Woman": {("Mary", ), ("Susan",)},
               "Man": {("John",), ("Peter", )},
               "Love": {("Mary", "John"), ("Susan", "Peter"), ("John", "Mary"), ("John", "Peter")}}

        s14 = PredStructure("S15", d15, i15)
        print(s14)

        e14 = {
                1: Forall(Var("x"), Imp(Atm(Pred("Woman"), (Var("x"),)),
                                        Exists(Var("y"), Conj(Atm(Pred("Man"), (Var("y"),)),
                                                              Atm(Pred("Love"), (Var("x"), Var("y"))))))),
                2: Forall(Var("x"), Imp(Atm(Pred("Man"), (Var("x"),)),
                                        Exists(Var("y"), Conj(Atm(Pred("Woman"), (Var("y"),)),
                                                              Atm(Pred("Love"), (Var("x"), Var("y"))))))),
                3: More(Var("x"), Atm(Pred("Woman"), (Var("x"),)), Atm(Pred("Man"), (Var("x"),)),
                        Exists(Var("y"), Atm(Pred("Love"), (Var("x"), Var("y"))))),
                4: Most(Var("x"), Atm(Pred("Man"), (Var("x"),)),
                        Exists(Var("y"), Atm(Pred("Love"), (Var("x"), Var("y")))))
        }

        for nr, e in e14.items():
            if nr in [1, 2]:
                print()
                print("[[" + str(e) + "]]S15 =")
                print(e.denotV(s14))
                depth = 0

        #############################
        print("\n---------------------------------\n")
        #############################


if __name__ == "__main__":
    compute_active()
