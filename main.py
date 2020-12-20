#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Main module.
"""

import gui


if __name__ == "__main__":
    # # ########################
    # # # command-line interface
    # # ########################
    # truthtable = __import__("truthtable")
    # denotation = __import__("denotation")
    # tableau = __import__("tableau")
    # parser = __import__("parser")
    # parse_fml = parser.FmlParser().parse
    # parse_struct = parser.StructParser().parse
    # s1 = parse_struct(r"[p: True, q: False, r: True]")
    # fml1 = parse_fml("(p -> q) v (q -> r)")
    # fml2 = parse_fml(r"\all x (P(x) -> \exi y (Q(y) ^ R(x,y)))")
    # fml3 = parse_fml(r"\exi y (Q(y) ^ \all x (P(x) -> R(x,y)))")
    # fml4 = parse_fml(r"- \exi x * U(x)")
    # fml5 = parse_fml(r"* \exi x U(x)")
    # # compute truth table for ((p → q) ∨ (q → r))
    # truthtable.TruthTable(fml1, latex=False).show()
    # # check denotation of ((p → q) ∨ (q → r)) in <[p: True, q: False, r: True]>
    # denotation.Denotation([(fml1, s1, None, None)]).show(latex=False)
    # # find tableau proof for ∃y(Q(y) ∧ ∀x(P(x) → R(x,y))) ⊨ ∀x(P(x) → ∃y(Q(y) ∧ R(x,y)))
    # print(tableau.Tableau(fml2, premises=[fml3]))
    # # find counter model for ∀x(P(x) → ∃y(Q(y) ∧ R(x,y))) ⊭ ∃y(Q(y) ∧ ∀x(P(x) → R(x,y)))
    # print(tableau.Tableau(fml3, premises=[fml2], validity=False))
    # # find model for ¬∃x◇U(x), # ◇∃xU(x)
    # print(tableau.Tableau(None, premises=[fml4, fml5], validity=False, satisfiablility=True))

    # #############################
    # start the graphical interface
    # #############################
    gui.main()
