#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Define the structures (aka models) of standard logic.
"""

from denotation import *

import re
from itertools import product

sort_i = lambda kv: (  # sort interpretation functions by ...
        sort_type(kv[1]),  # type (1. constants, 2. functions, 3. predicates)
        sort_val(kv[1]),  # valency (shorter tuples first)
        kv[0])  # name of the symbol (alphabetical)
sort_i_w = lambda kv: (  # sort interpretation functions by ...
        sort_type(kv[1][list(kv[1])[0]]),  # type (1. constants, 2. functions, 3. predicates)
        sort_val(kv[1][list(kv[1])[0]]),  # valency (shorter tuples first)
        kv[0])  # name of the symbol (alphabetical)
sort_type = lambda v: {str: 1, dict: 2, set: 3}[type(v)]
sort_val = lambda v: len(list(v)[0]) if v and type(v) in [set, dict] else 0


class Structure:
    """
    A structure of logic.

    @attr d: the domain of discourse
    @attr i: an interpretation function
    """

    def mode(self):
        mode = []
        mode.append("intuitionistic" if isinstance(self, KripkeStructure) else "classical")
        mode.append("modal" if isinstance(self, ModalStructure) else "nonmodal")
        mode.append("vardomains" if isinstance(self, VarModalStructure) else
                    "constdomains" if (isinstance(self, ConstModalStructure)) else "")
        mode.append("propositional" if isinstance(self, PropStructure) or \
                                       isinstance(self, PropModalStructure) or isinstance(self, KripkePropStructure) else
                    "predicational")
        return [m for m in mode if m]

    def text(self, s):
        return "\\text{" + str(s) + "}"


class PropStructure(Structure):
    """
    A structure of propositional logic with valuation function.

    A structure M is a function V: VAR -> {True, False}.
    V = {"p": True, "q": False, "r": True}

    @attr s: the name of the structure (such as "M1")
    @type s: str
    @attr v: the valuation function
    @type v: dict[str,bool]
    """

    def __init__(self, s, v):
        self.s = s
        self.v = v

    def __str__(self):
        suffix = self.s.removeprefix("S") if self.s[-1].isdigit() else ""
        s, v = self.s, "V" + suffix
        return "Structure " + s + " = ⟨" + ",".join([v]) + "⟩ with \n" + \
               v + ": " + ", ".join([str(key) + " ↦ " + str(val) for key, val in sorted(self.v.items())])

    def tex(self):
        suffix = "_" + "{" + self.s.removeprefix("S") + "}" if self.s[-1].isdigit() else ""
        s, v = re.sub("S(\d*)", r"\\mathcal{S}_{\1}", self.s), "\\mathcal{V}" + suffix
        return "Structure $" + s + " = \\tpl{" + ", ".join([v]) + "}$ with \\\\\n" + \
               "\\begin{tabular}{AA}\n" + \
               v + " : & " + \
                   ", ".join([str(p) + " \\mapsto " + str(tv).replace("True", "1").replace("False", "0")
                              for p, tv in sorted(self.v.items())]) + "\\\\\n" + \
               "\\end{tabular}" \
                   .replace("\\set{}", "\\emptyset{}")

indiv_vars = ["x", "y", "z"]

class PredStructure(Structure):
    """
    A structure of predicate logic with domain and interpretation function.

    A Structure M is a pair <D, I> with
      - D = domain of discourse
      - I = interpretation function assigning a denotation to each non-logical symbol

    - The domain D is a set of individuals, specified as strings:
       D = {'a', 'b', 'c', ...}

    - The interpretation function F is a dictionary with
      - non-logical symbols (specified as strings) as keys and
      - members/subsets/functions of D as values

       {'c': 'a', 'P': {('a', ), ('b', )}, 'f': {('c1',): 'a', ('c2',): 'b'}}

        - The denotation of individual constants is a member (string) of D:
           'c': 'a'

        - The denotation of predicates is a set of tuples of members (strings) of D:
           'P': {('a', ), ('b', )}
           'R': {('a', 'b'), ('b', 'c')}

          - Note that the denotation of 1-place predicates (set of individuals) has to be specified as
             'P': {('a', ), ('b', ), ('c', )}
            rather than
             'P': {('a'), ('b'), ('c')}
             or
             'P': {'a','b','c'}

          - The denotation of 0-place predicates has to be specified as a set of 0-tuples:
             'Q': {()}      iff the proposition expressed by 'Q' is true
             'Q': {}        iff the proposition expressed by 'Q' false

        - The denotation of function symbols is a dictionary with
          - tuples of members of D as keys and
          - members of D as values
           'f': {('c1',): 'a', ('c2',): 'b'}
           'h': {('c1', 'c2'): 'a'}

    - An assignment function v is a dictionary with
      - variables (specified as strings) as keys and
      - members of D (specified as strings) as values
       {'x': 'a', 'y': 'b', 'z': 'c'}

    ---------

    @attr s: the name of the structure (such as "M1")
    @type s: str
    @attr d: the domain of discourse
    @type d: set[str]
    @attr i: the interpretation function assigning denotations to the non-logical symbols
    @type i: dict[str,Any]
    """

    def __init__(self, s, d, i):
        self.s = s
        self.d = d
        self.i = i

    def __str__(self):  # todo sort interpretation by type and arity of symbol
        suffix = self.s.removeprefix("S") if self.s[-1].isdigit() else ""
        s, d, i = self.s, "D" + suffix, "I" + suffix
        return "Structure " + s + " = ⟨" + ",".join([d, i]) + "⟩ with \n" + \
        d + " = " + "{" + ", ".join(self.d) + "}" + "\n" + \
        i + " : " + ", \n    ".join(
                [str(key) + " ↦ " +
                 (str(val) if isinstance(val, str) else
                  (", ".join(["⟨" + str(key2) + " ↦ " + str(val2) + "⟩"
                              for key2, val2 in val.items()])
                   if isinstance(val, dict) else
                   ("{" +
                    ", ".join(["⟨" + ", ".join([str(t) for t in e]) + "⟩" for e in sorted(val)]) +
                    "}")))
                 for (key, val) in sorted(self.i.items(), key=sort_i)])

    def tex(self):
        suffix = "_" + "{" + self.s.removeprefix("S") + "}" if self.s[-1].isdigit() else ""
        s, d, i = re.sub("S(\d*)", r"\\mathcal{S}_{\1}", self.s), "\\mathcal{D}" + suffix, "\\mathcal{I}" + suffix
        return "Structure $" + s + " = \\tpl{" + ", ".join([d, i]) + "}$ with \\\\\n" + \
               "\\begin{tabular}{AAA}\n" + \
               d + " = & " \
                   "\\multicolumn{2}{A}{\\set{" + ", ".join([self.text(d) for d in sorted(self.d)]) + "}}\\\\\n" +\
               i + " : &" + \
                   "\\\\\n    & ".join(
                       ["\\mathit{" + str(key) + "} & \\mapsto " +
                        (self.text(val) if isinstance(val, str) else
                         (", ".join(["\\tpl{" + ", ".join([self.text(t) for t in key2]) + "}" +
                                     " \\mapsto " + self.text(val2)
                                     for key2, val2 in val.items()])
                          if isinstance(val, dict) else
                          ("\\set{" +
                           ", ".join(["\\tpl{" + ", ".join([self.text(t) for t in e]) + "}" for e in sorted(val)]) +
                           "}")))
                        for (key, val) in sorted(self.i.items(), key=sort_i)]) + "\\\\\n" + \
               "\\end{tabular}" \
                .replace("\\set{}", "\\emptyset{}")


class ModalStructure(Structure):
    """
    A modal of (modal) predicate logic.

    @attr s: the name of the structure (such as "M1")
    @type s: str
    @attr w: a set of possible worlds
    @type w: set[str]
    @attr r: an accessibility relation on r
    @type r: set[tuple[str,str]]
    """
    pass


class PropModalStructure(ModalStructure):
    """
    A structure of modal propositional logic.

    A PropModalStructure M is a triple <W,R,V> with
      - W = set of possible worlds
      - R = accessibility relation, a binary relation on W
      - V = valuation function

    - The set of possible worlds W is a set of possible worlds, specified as strings:
       W = {'w1', 'w2', ...}

    - The accessibility relation W is a set of tuples of possible worlds:
      R = {('w1', 'w2'), ('w2', 'w2'), ...}

    - The valuation function V is a dictionary with
      - propositional variablse as keys and
      - a dictionary with
        - possible worlds as keys and
        - truth values as values
      as values.
      V = {'p': {'w1': True, 'w2': False}, 'q': {'w1': False, 'w2': False}, ...}

    @attr s: the name of the structure (such as "M1")
    @type s: str
    @attr w: the set of possible worlds
    @type w: set[str]
    @attr r: the accessibility relation on self.w
    @type r: set[tuple[str,str]]
    @attr v: the valuation function
    @type v: dict[str,dict[str,bool]]
    """

    def __init__(self, s, w, r, v):
        self.s = s
        self.w = w
        self.r = r
        self.v = v

    def __str__(self):
        suffix = self.s.removeprefix("S") if self.s[-1].isdigit() else ""
        s, w, r, v = self.s, "W" + suffix, "R" + suffix, "V" + suffix
        return "Structure " + s + " = ⟨" + ",".join([w, r, v]) + "⟩ with \n" + \
                w + " = {" + ", ".join([str(w) for w in sorted(self.w)]) + "}\n" +\
                r + " = {" + ", ".join(
                    ["⟨" + str(r[0]) + "," + str(r[1]) + "⟩" for r in sorted(self.r)]) + "}\n" +\
                v + " : " + ", \n    ".join(
                    [str(p) + " ↦ \n" +
                        ", \n".join(["           " + str(w) + " ↦ " + str(tv)
                        for (w, tv) in sorted(self.v[p].items())])
                    for (p, vp) in sorted(self.v.items())])

    def tex(self):
        suffix = "_" + "{" + self.s.removeprefix("S") + "}" if self.s[-1].isdigit() else ""
        s, w, r, v = re.sub("S(\d*)", r"\\mathcal{S}_{\1}", self.s), "\\mathcal{W}" + suffix, "\\mathcal{R}" + suffix, \
                     "\\mathcal{V}" + suffix
        return "Structure $" + s + " = \\tpl{" + ", ".join([w, r, v]) + "}$ with \\\\\n" + \
               "\\begin{tabular}{AAAAAA}\n" +\
               w + " = & " + \
                   "\\multicolumn{5}{A}{\\set{" + ", ".join([re.sub("w(\d+)", "w_\\1", str(w)) for w in sorted(self.w)]) + "}}\\\\\n" +\
               r + " = &" + \
                   "\\multicolumn{5}{A}{\\set{" + ", ".join(
                        ["\\tpl{" + str(r[0]) + ", " + str(r[1]) + "}" for r in sorted(self.r)]) + "}}\\\\\n" + \
               v + " : & " + \
                   "\\\\\n    & ".join([str(p) + " & \\mapsto &" +
                        ", \\\\\n &&& ".join([re.sub("w(\d+)", "w_\\1", str(w))+ " & \\mapsto &" + self.text(tv)
                        for (w, tv) in sorted(self.v[p].items())])
                    for (p, vp) in sorted(self.v.items())]) + "\\\\\n" + \
               "\\end{tabular}" \
                .replace("\\set{}", "\\emptyset{}")


class ConstModalStructure(ModalStructure):
    """
    A structure of modal predicate logic with constant domain.

    A ConstModalStructure M is a quadrupel <W,R,D,F> with
      - W = set of possible worlds
      - R = accessibility relation, a binary relation on W
      - D = domain of discourse
      - I = interpretation function assigning to each member of w and each non-logical symbol a denotation

    - The set of possible worlds W is a set of possible worlds, specified as strings:
       W = {'w1', 'w2', ...}

    - The accessibility relation W is a set of tuples of possible worlds:
      R = {('w1', 'w2'), ('w2', 'w2'), ...}

    - The domain D is a set of individuals, specified as strings:
      D = {'a', 'b', 'c', ...}

    - The interpretation function F is a dictionary with
      - the non-logical symbols as keys and
      - a dictionary with
        - possible worlds as keys and
        - and interpretation (see f) as values.
      I = {'c': {'w1': 'a', 'w2':  'a'}, 'P': {'w1: {('a',)}, 'w2': {('a', ), ('b', )}}}

    - An assignment function v is a dictionary with
      - variables (specified as strings) as keys and
      - members of D (specified as strings) as values
       {'x': 'a', 'y': 'b', 'z': 'c'}

    @attr s: the name of the structure (such as "M1")
    @type s: str @attr w: the set of possible worlds
    @type w: set[str]
    @attr r: the accessibility relation on self.w
    @type r: set[tuple[str,str]]
    @attr d: the domain of discourse
    @type d: set[str]
    @attr i: the interpretation function
    @type i: dict[str,dict[str,Any]]
    """

    # todo doesnt work yet (assignment function)
    def __init__(self, s, w, r, d, i):
        self.s = s
        self.w = w
        self.r = r
        self.d = d
        self.i = i

    def __str__(self):
        suffix = self.s.removeprefix("S") if self.s[-1].isdigit() else ""
        s, w, r, d, i = self.s, "W" + suffix, "R" + suffix, "D" + suffix, "I" + suffix
        return "Structure " + s + " = ⟨" + ",".join([w, r, d, i]) + "⟩ with \n" + \
                w + " = {" + ", ".join([str(w) for w in sorted(self.w)]) + "}\n" +\
                r + " = {" + ", ".join(["⟨" + str(r[0]) + "," + str(r[1]) + "⟩" for r in sorted(self.r)]) + "}\n" +\
                d + " = {" + ", ".join([str(d) for d in sorted(self.d)]) + "}\n" +\
                i +" : " + \
                    "\n    ".join([str(p) + " ↦ \n" + \
                        ", \n".join(["           " + str(w) + " ↦ " +
                            (str(ipw)
                                if isinstance(ipw, str) else
                            (", ".join(["(" + str(ipwKey) + " ↦ " + str(ipwVal) + ")"
                                        for ipwKey, ipwVal in sorted(ipw.items())]) if isinstance(ipw, dict) else
                            ("{" + ", ".join(["⟨" + ", ".join([str(t).replace("frozenset", "")
                                for t in e]) + "⟩" for e in sorted(ipw)]) + "}")))
                        for (w, ipw) in sorted(self.i[p].items())]) + \
                    "\n    " for (p, ip) in sorted(self.i.items(), key=sort_i_w)]).replace("\n    \n", "\n")

    def tex(self):
        suffix = "_" + "{" + self.s.removeprefix("S") + "}" if self.s[-1].isdigit() else ""
        s, w, r, d, i = re.sub("S(\d*)", r"\\mathcal{S}_{\1}", self.s), "\\mathcal{W}" + suffix, "\\mathcal{R}" + suffix, \
                        "\\mathcal{D}" + suffix, "\\mathcal{I}" + suffix
        return "Structure $" + s + " = \\tpl{" + ", ".join([w, r, d, i]) + "}$ with \\\\\n" + \
               "\\begin{tabular}{AAAAAA}\n" +\
               w + " = & " \
                   "\\multicolumn{5}{A}{\\set{" + ", ".join([re.sub("w(\d+)", "w_\\1", str(w))
                                                             for w in sorted(self.w)]) + "}}\\\\\n" + \
               r + " = &" \
                   "\\multicolumn{5}{A}{\\set{" + ", ".join(
                    ["\\tpl{" + re.sub("w(\d+)", "w_\\1", str(r[0])) + ", " + re.sub("w(\d+)", "w_\\1", str(r[1])) + "}"
                     for r in sorted(self.r)]) + "}}\\\\\n" + \
               d + " = & " + \
                   "\\multicolumn{5}{A}{\\set{" + ", ".join([self.text(d) for d in sorted(self.d)]) + "}}\\\\\n" + \
               i + " : & " + \
                   "\\\\\n    & ".join(["\\mathit{" + str(p) + "} & \\mapsto &" + \
                        "\\\\\n &&& ".join(
                            [re.sub("w(\d+)", "w_\\1", str(w)) + "& \\mapsto &" +
                                 (self.text(ipw) if isinstance(ipw, str) else
                                 (", \\\\\n && ".join(
                                          ["\\tpl{" + ", ".join([self.text(t) for t in ipwKey]) + "}"
                                           " \\mapsto " + self.text(ipwVal)
                                           for ipwKey, ipwVal in ipw.items()])
                                   if isinstance(ipw, dict) else
                                 ("\\set{" + ", ".join(["\\tpl{" + ", ".join(
                                            [self.text(t) if "frozenset" not in str(t) else
                                             str(t).replace("frozenset", "").replace("'", "")
                                             for t in e]) + "}"
                                                        for e in sorted(ipw)]) +
                                 "}")))
                            for (w, ipw) in sorted(self.i[p].items())])
                        for (p, ip) in sorted(self.i.items(), key=sort_i_w)]) + "\\\\\n" + \
               "\\end{tabular}" \
               .replace("\\set{}", "\\emptyset{}")


class VarModalStructure(ModalStructure):
    """
    A structure of modal predicate logic with varying domains.

    A VarModalStructure M is a quadrupel <W,R,D,I> with
      - W = set of possible worlds
      - R = accessibility relation, a binary relation on W
      - D = an assignment of possible worlds to domains of discourse
      - I = interpretation function assigning to each member of W and each non-logical symbol a denotation
    and a set of assignment functions vs.

    - The set of possible worlds W is a set of possible worlds, specified as strings:
       W = {'w1', 'w2', ...}

    - The accessibility relation W is a set of tuples of possible worlds:
      R = {('w1', 'w2'), ('w2', 'w2'), ...}

    - The domain D is a a dictionary with
      - possible worlds (specified as strings) as keys and
      - domains (see D) as values
      D = {'w1': {'a', 'b', 'c'}, 'w2': {'b'}, ...}

    - The interpretation function F is a dictionary with
      - possible worlds as keys and
      - and interpretation of the non-logical symbols (see f) as values.
      I = {'c': {'w1': 'a', 'w2':  'a'}, 'P': {'w1: {('a',)}, 'w2': {('a', ), ('b', )}}}

    - An assignment function v is a dictionary with
      - possible worlds (specified as strings) as keys and
      - a dictionary with
        - variables (specified as strings) as keys and
        - members of D at the world (specified as strings) as values
        as values.
       {'w1': {'x': 'a', 'y': 'b', 'z': 'c'}, 'w2': {'x': 'b', 'y': 'c', 'z': 'a'}, ...}

    @attr s: the name of the structure (such as "M1")
    @type s: str
    @attr w: the set of possible worlds
    @type w: set[str]
    @attr r: the accessibility relation on self.w
    @type r: set[tuple[str,str]]
    @attr d: the mapping of worlds to domains of discourse
    @type d: dict[str,set[str]]
    @attr i: the interpretation function
    @type i: dict[str,dict[str,Any]]
    """

    def __init__(self, s, w, r, d, i):
        self.s = s
        self.w = w
        self.r = r
        self.d = d
        self.i = i

    def __str__(self):
        suffix = self.s.removeprefix("S") if self.s[-1].isdigit() else ""
        s, w, r, d, i = self.s, "W" + suffix, "R" + suffix, "D" + suffix, "I" + suffix
        return "Structure " + s + " = ⟨" + ",".join([w, r, d, i]) + "⟩ with \n" + \
                w + " = {" + ", ".join([str(w) for w in sorted(self.w)]) + "}\n" +\
                r + " = {" + ", ".join(
                    ["⟨" + str(r[0]) + "," + str(r[1]) + "⟩" for r in sorted(self.r)]) + "}\n" +\
                d + " : " + "\n    ".join(
                    [str(w) + " ↦ " + \
                    "{" + ", ".join([str(d) for d in sorted(self.d[w])]) + "}"
                    for w in sorted(self.w)]) + "\n" + \
                i + " : " + \
                    "\n    ".join([str(p) + " ↦ \n" + \
                        ", \n".join(
                       ["           " + str(w) + " ↦ " +
                            (str(ipw) if isinstance(ipw, str) else
                            (", ".join(["(" + str(ipwKey) + " ↦ " + str(ipwVal) + ")"
                                        for ipwKey, ipwVal in sorted(ipw.items())])
                                if isinstance(ipw, dict) else
                            ("{" +
                                ", ".join(["⟨" + ", ".join(
                                   [str(t) for t in e]) + "⟩" for e in sorted(ipw)]) +
                            "}")))
                        for (w, ipw) in sorted(self.i[p].items())]) + "\n    " \
                    for (p, ip) in sorted(self.i.items(), key=sort_i_w)]).replace("\n    \n",  "\n") + "\n"

    def tex(self):
        suffix = "_" + "{" + self.s.removeprefix("S") + "}" if self.s[-1].isdigit() else ""
        s, w, r, d, i = re.sub("S(\d*)", r"\\mathcal{S}_{\1}", self.s), "\\mathcal{W}" + suffix, "\\mathcal{R}" + suffix, \
                        "\\mathcal{D}" + suffix, "\\mathcal{I}" + suffix
        return "Structure $" + s + " = \\tpl{" + ", ".join([w, r, d, i]) + "}$ with \\\\\n" + \
               "\\begin{tabular}{AAAAAA}\n" +\
               w + " = & " \
                   "\\multicolumn{5}{A}{\\set{" + ", ".join([re.sub("w(\d+)", "w_\\1", str(w))
                                                             for w in sorted(self.w)]) + "}}\\\\\n" + \
               r + " = &" + \
                   "\\multicolumn{5}{A}{\\set{" + ", ".join(
                        ["\\tpl{" + re.sub("w(\d+)", "w_\\1", str(r[0])) + ", " + re.sub("w(\d+)", "w_\\1", str(r[1])) + "}"
                         for r in sorted(self.r)]) + "}}\\\\\n" + \
               d + " : & " + \
                   "\\\\\n    & ".join([re.sub("w(\d+)", "w_\\1", str(w)) + " & \\multicolumn{4}{A}{\\mapsto " + \
                        "\\set{" + ", ".join([self.text(d) for d in sorted(self.d[w])]) + "}}" for w in sorted(self.w)]) + \
                   "\\\\\n" + \
               i + " : & " + \
                   "\\\\\n    & ".join(["\\mathit{" + str(p) + "} & \\mapsto &" + \
                        "\\\\\n &&& ".join(
                            [re.sub("w(\d+)", "w_\\1", str(w)) + "& \\mapsto &" +
                             (self.text(ipw) if isinstance(ipw, str) else
                              (", \\\\\n && ".join(
                                      ["\\tpl{" + ", ".join([self.text(t) for t in (ipwKey)]) + "}" +
                                                            " \\mapsto " + self.text(ipwVal)
                                       for ipwKey, ipwVal in ipw.items()])
                               if isinstance(ipw, dict) else
                               ("\\set{" + ", ".join(["\\tpl{" + ", ".join(
                                       [self.text(t) if "frozenset" not in str(t) else
                                        str(t).replace("frozenset", "").replace("'", "")
                                        for t in e]) + "}"
                                                      for e in sorted(ipw)]) +
                                "}")))
                             for (w, ipw) in sorted(self.i[p].items())])
                        for (p, ip) in sorted(self.i.items(), key=sort_i_w)]) + "\\\\\n" + \
               "\\end{tabular}" \
                .replace("\\set{}", "\\emptyset{}")


class KripkeStructure(Structure):
    # todo rewrite with p -> w -> I notation
    """
    A Kripke structure of intuitionistic logic.

    @attr s: the name of the structure (such as "M1")
    @type s: str
    @attr k: a set of possible states
    @type k: set[str]
    @attr r: an accessibility relation on r
    @type r: set[tuple[str,str]]
    """

    def future(self, k):
        """
        Compute subsequent states k' >= k of k.
        @param k: the state to compute the future of
        @type k: str
        @return: the set of states k' s.t. k' >= k
        @rtrype: set[str]
        """
        return {k_ for k_ in self.k if (k, k_) in self.r}

    def past(self, k):
        """
        Compute preceding states k' <= k of k.
        @param k: the state to compute the future of
        @type k: str
        @return: the set of states k' s.t. k' <= k
        @rtrype: set[str]
        """
        return {k_ for k_ in self.k if (k_, k) in self.r}


class KripkePropStructure(KripkeStructure):
    """
    A Kripke structure of intuitionistic predicate logic.

    A KripkePredStructure is a triple <K,R,V> with
      - K = set of states
      - R = the accessibility relation, a binary relation on K
      - V = valuation function assigning to each member of K and each propositional variable a truth value

    - The set of states K is a set of states, specified as strings, where the root state has to be specified as 'k0':
       K = {'k0', 'k1', 'k2' ...}

    - The accessibility relation R is a partial order on K,
      where only the primitive acessiblity pairs have to be specified and the reflexive and transitive closure
      is computed automatically:
       R = {('k0', 'k1'), ('k0', 'k2'), ...}

    - The valuation function V is a dictionary with
      - states worlds as keys and
      - a dictionary with
        - propositional variables as keys and
        - truth values as values
      as values.
      V = {'k1': {'p': True, 'q': False}, {'k2': {'p': False, 'q': False}}, ...}

    @attr s: the name of the structure
    @type s: str
    @attr k: the set of states
    @type k: set[str]
    @attr r: the accessibility relation on self.k
    @type r: set[tuple[str,str]]
    @attr v: the valuation function
    @type v: dict[str,dict[str,bool]]
    """

    def __init__(self, s, k, r, v):
        self.s = s
        self.k = k
        self.r = r
        self.v = v

        # compute the relfexive and transitive closure of R
        closure = set(self.r)
        closure = closure | set((k, k) for k in self.k)  # add reflexive closure
        # add transitive closure
        while True:
            new_relations = set((x, z) for x, y1 in closure for y2, z in closure if y1 == y2)
            closure_until_now = closure | new_relations
            if closure_until_now == closure:
                break
            closure = closure_until_now
        self.r = closure

    # def future(self, k):
    #     """
    #     Compute subsequent states k' >= k of k.
    #     @param k: the state to compute the future of
    #     @type k: str
    #     @return: the set of states k' s.t. k' >= k
    #     @rtrype: set[str]
    #     """
    #     return {k_ for k_ in self.k if (k, k_) in self.r}
    #
    # def past(self, k):
    #     """
    #     Compute preceding states k' <= k of k.
    #     @param k: the state to compute the future of
    #     @type k: str
    #     @return: the set of states k' s.t. k' <= k
    #     @rtrype: set[str]
    #     """
    #     return {k_ for k_ in self.k if (k_, k) in self.r}

    def __str__(self):
        suffix = self.s.removeprefix("S") if self.s[-1].isdigit() else ""
        s, k, r, v = self.s, "K" + suffix, "R" + suffix, "V" + suffix
        return "Structure " + s + " = ⟨" + ",".join([k, r, v]) + "⟩ with \n" + \
                k + " = {" + ", ".join([str(k) for k in sorted(self.k)]) + "}\n" +\
                r + " = {" + ", ".join(
                    ["⟨" + str(r[0]) + "," + str(r[1]) + "⟩" for r in sorted(self.r) if r[0] != r[1]]) + "}\n" +\
                v + " : " + "\n    ".join(
                    [str(p) + " ↦ \n" + ", \n".join(["        " + str(k) + " ↦ " + str(tv)
                        for (k, tv) in sorted(self.v[p].items())])
                    for (p, vp) in sorted(self.v.items())]).replace("\n    \n", "\n")

    def tex(self):
        suffix = "_" + "{" + self.s.removeprefix("S") + "}" if self.s[-1].isdigit() else ""
        s, k, r, v = re.sub("S(\d*)", r"\\mathcal{S}_{\1}", self.s), "\\mathcal{K}" + suffix, "\\mathcal{R}" + suffix, \
                        "\\mathcal{V}" + suffix
        return "Structure $" + s + " = \\tpl{" + ", ".join([k, r, v]) + "}$ with \\\\\n" + \
               "\\begin{tabular}{AAAAAA}\n" + \
               k + " = & " \
                   "\\multicolumn{5}{A}{\\set{" + ", ".join([re.sub("k(\d+)", "k_\\1", str(k)) for k in sorted(self.k)]) + "}}\\\\\n" + \
               r + " = &" \
                   "\\multicolumn{5}{A}{" \
                   "\\set{" + ", ".join(
                        ["\\tpl{" + re.sub("k(\d+)", "k_\\1", str(r[0]) )+ ", " + re.sub("k(\d+)", "k_\\1", str(r[1])) + "}" for r in sorted(self.r) if r[0] != r[1]]) + "}}\\\\\n" + \
               v + " : & " + \
                   "\\\\\n    & ".join(
                       [str(p) + " & \\mapsto &" +
                        ", \\\\\n &&& ".join([re.sub("k(\d+)", "k_\\1", str(k)) + " & \\mapsto &" + " " + self.text(tv)
                            for (k, tv) in sorted(self.v[p].items())])
                        for (p, vp) in sorted(self.v.items())]) + "\\\\\n" + \
               "\\end{tabular}" \
               .replace("\\set{}", "\\emptyset{}")


class KripkePredStructure(KripkeStructure):
    """
    A Kripke structure of intuitionistic predicate logic.

    A KripkePredStructure is a quadruple <K,R,D,I> with
      - K = set of states
      - R = the accessibility relation, a binary relation on K
      - D = an assignment of states to domains of discourse
      - I = interpretation function assigning to each member of K and each non-logical symbol a denotation
    and a set of assignment functions vs assigning to each state k to each variable an element from the domain of k.

    - The set of states K is a set of states, specified as strings, where the root state has to be specified as 'k0':
       K = {'k0', 'k1', 'k2' ...}

    - The accessibility relation R is a partial order on K,
      where only the primitive acessiblity pairs have to be specified and the reflexive and transitive closure
      is computed automatically:
       R = {('k0', 'k1'), ('k0', 'k2'), ...}

    - The domain D is a a dictionary with
      - states (specified as strings) as keys and
      - domains as values
        - The domain D_k is a set of individuals, specified as strings:
           {'a', 'b', 'c', ...}
       D = {'k0': {'a'}, 'k1': {'a', 'b'}, 'k2': {'a', 'c'}, ...}

    - The interpretation function I is a dictionary with
      - states as keys and
      - and an interpretation of the non-logical symbols as values

        - The interpretation function I_k is a dictionary with
          - non-logical symbols (specified as strings) as keys and
          - members/subsets/functions of D as values

           {'c': 'a', 'P': {('a', ), ('b', )}, 'f': {('c1',): 'a', ('c2',): 'b'}}

            - The denotation of individual constants is a member (string) of D:
               'c': 'a'

            - The denotation of predicates is a set of tuples of members (strings) of D:
               'P': {('a', ), ('b', )}
               'R': {('a', 'b'), ('b', 'c')}

              - Note that the denotation of 1-place predicates (set of individuals) has to be specified as
                 'P': {('a', ), ('b', ), ('c', )}
                rather than
                 'P': {('a'), ('b'), ('c')}
                 or
                 'P': {'a','b','c'}

              - The denotation of 0-place predicates has to be specified as a set of 0-tuples:
                 'Q': {()}      iff the proposition expressed by 'Q' is true
                 'Q': {}        iff the proposition expressed by 'Q' false

            - The denotation of function symbols is a dictionary with
              - tuples of members of D as keys and
              - members of D as values
               'f': {('c1',): 'a', ('c2',): 'b'}
               'h': {('c1', 'c2'): 'a'}

         I = {'c': {'k0': 'a', 'k1':  'a'}, 'P': {'k0: {('a',)}, 'k1': {('a', ), ('b', )}}}

    - An assignment function v is a dictionary with
      - states (specified as strings) as keys and
      - a dictionary with
        - variables (specified as strings) as keys and
        - members of the domain at the state (specified as strings) as values
        as values.
       {'k0': {'x': 'a', 'y': 'b', 'z': 'c'}, 'k1': {'x': 'b', 'y': 'c', 'z': 'a'}, ...}

    @attr s: the name of the structure
    @type s: str
    @attr k: the set of states
    @type k: set[str]
    @attr r: the accessibility relation on self.k
    @type r: set[tuple[str,str]]
    @attr d: the mapping of states to domains of discourse
    @type d: dict[str,set[str]]
    @attr i: the interpretation function
    @type i: dict[str,dict[str,Any]]
    """

    def __init__(self, s, k, r, d, i):
        self.s = s
        self.k = k
        self.r = r
        self.d = d
        self.i = i

        # compute the relfexive and transitive closure of R
        closure = set(self.r)
        closure = closure | set((k, k) for k in self.k)  # add reflexive closure
        # add transitive closure
        while True:
            new_relations = set((x, z) for x, y1 in closure for y2, z in closure if y1 == y2)
            closure_until_now = closure | new_relations
            if closure_until_now == closure:
                break
            closure = closure_until_now
        self.r = closure

    # def future(self, k):
    #     """
    #     Compute subsequent states k' >= k of k.
    #     @param k: the state to compute the future of
    #     @type k: str
    #     @return: the set of states k' s.t. k' >= k
    #     @rtrype: set[str]
    #     """
    #     return {k_ for k_ in self.k if (k, k_) in self.r}
    #
    # def past(self, k):
    #     """
    #     Compute preceding states k' <= k of k.
    #     @param k: the state to compute the future of
    #     @type k: str
    #     @return: the set of states k' s.t. k' <= k
    #     @rtrype: set[str]
    #     """
    #     return {k_ for k_ in self.k if (k_, k) in self.r}

    def __str__(self):
        suffix = self.s.removeprefix("S") if self.s[-1].isdigit() else ""
        s, k, r, d, i = self.s, "K" + suffix, "R" + suffix, "D" + suffix, "I" + suffix
        return "Structure " + s + " = ⟨" + ",".join([k, r, d, i]) + "⟩ with \n" + \
                k + " = {" + ", ".join([str(k) for k in sorted(self.k)]) + "}\n" +\
                r + " = {" + ", ".join(
                    ["⟨" + str(r[0]) + "," + str(r[1]) + "⟩" for r in sorted(self.r) if r[0] != r[1]]) + "}\n" +\
                d + " : " + ("\n    ".join(
                    [str(k) + " ↦ " + \
                        "{" + ", ".join([str(d) for d in sorted(self.d[k])]) + "}"
                     for k in sorted(self.k)]) if self.d else "") + "\n" + \
                i + " : " + \
                    "\n    ".join([str(p) + " ↦ \n" + \
                        ", \n".join(["           " + str(k) + " ↦ " +
                            (str(ipk) if isinstance(ipk, str) else
                            (", ".join(["(" + str(ipkKey) + " ↦ " + str(ipkVal) + ")"
                                        for ipkKey, ipkVal in sorted(ipk.items())])
                                 if isinstance(ipk, dict) else
                            ("{" + ", ".join(["⟨" + ", ".join([str(t) for t in e]) + "⟩" for e in sorted(ipk)]) + "}")))
                                              for (k, ipk) in sorted(self.i[p].items())]) +  "\n    "
                    for (p, ip) in sorted(self.i.items(), key=sort_i_w)]).replace("\n    \n", "\n")

    def tex(self):
        suffix = "_" + "{" + self.s.removeprefix("S") + "}" if self.s[-1].isdigit() else ""
        s, k, r, d, i = re.sub("S(\d*)", r"\\mathcal{S}_{\1}", self.s), "\\mathcal{K}" + suffix, "\\mathcal{R}" + suffix, \
                        "\\mathcal{D}" + suffix, "\\mathcal{I}" + suffix
        return "Structure $" + s + " = \\tpl{" + ", ".join([k, r, d, i]) + "}$ with \\\\\n" + \
               "\\begin{tabular}{AAAAAA}\n" +\
               k + " = & " \
                   "\\multicolumn{5}{A}{\\set{" + ", ".join([re.sub("k(\d+)", "k_\\1", str(k)) for k in sorted(self.k)]) + "}}\\\\\n" + \
               r + " = &" + \
                   "\\multicolumn{5}{A}{\\set{" + ", ".join(
                        ["\\tpl{" + str(r[0]) + ", " + str(r[1]) + "}" for r in sorted(self.r) if r[0] != r[1]]) + "}}\\\\\n" + \
               d + " : & " + \
                   "\\\\\n    & ".join([re.sub("k(\d+)", "k_\\1", str(k)) + " & \\multicolumn{4}{A}{\\mapsto " + \
                        "\\set{" + ", ".join([self.text(d) for d in sorted(self.d[k])]) + "}}" for k in sorted(self.k)]) + \
                   "\\\\\n" + \
               i + " : & " + \
                   "\\\\\n    & ".join(["\\mathit{" + str(p) + "} & \\mapsto &" + \
                        "\\\\\n &&& ".join(
                            [re.sub("k(\d+)", "k_\\1", str(k)) + "& \\mapsto &" +
                             (self.text(ipk) if isinstance(ipk, str) else
                              (", \\\\\n && ".join(
                                      ["\\tpl{" + ", ".join([self.text(t) for t in (ipkKey)]) + "}" +
                                                            " \\mapsto " + self.text(ipkVal)
                                       for ipkKey, ipkVal in ipk.items()])
                               if isinstance(ipk, dict) else
                               ("\\set{" + ", ".join(["\\tpl{" + ", ".join(
                                       [self.text(t) if "frozenset" not in str(t) else
                                        str(t).replace("frozenset", "").replace("'", "")
                                        for t in e]) + "}"
                                                      for e in sorted(ipk)]) +
                                "}")))
                             for (k, ipk) in sorted(self.i[p].items())])
                        for (p, ip) in sorted(self.i.items(), key=sort_i_w)]) + "\\\\\n" + \
               "\\end{tabular}" \
                .replace("\\set{}", "\\emptyset{}")
