#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Define the structures of classical (standard and modal) (prepositional and first-order) logic.
"""

# todo latex


from main import *
from expr import *

from itertools import product


indiv_vars = ["x", "y", "z"]  # the individual variables of the language


class Structure:
    """
    A structure of logic.

    @attr d: the domain of discourse
    @attr i: an interpretation function
    """
    pass


class PropStructure(Structure):
    """
    A structure of propositional logic with valuation function.

    A structure M is a function V: VAR -> {True, False}.
    V = {"p": True, "q": False, "r": True}

    @attr m: the name of the structure (such as "M1")
    @type m: str
    @attr v: the valuation function
    @type v: dict[str,bool]
    """
    def __init__(self, m, v):
        self.m = m
        self.v = v

    def __str__(self):
        return "Structure " + self.m + " = V with V: " + \
               ", ".join([str(key) + " ↦ " + str(val) for key, val in sorted(self.v.items())])


class PredStructure(Structure):
    """
    A structure of predicate logic with domain, interpretation function and a set of assignment functions.

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

    - An assignment function g is a dictionary with
      - variables (specified as strings) as keys and
      - members of D (specified as strings) as values
       {'x': 'a', 'y': 'b', 'z': 'c'}

    ---------

    @attr m: the name of the structure (such as "M1")
    @type m: str
    @attr d: the domain of discourse
    @type d: set[str]
    @attr i: the interpretation function assigning denotations to the non-logical symbols
    @type i: dict[str,Any]
    @type vs: the assignment functions associated with the structure
    @type vs: list[dict[str,str]]]
    """

    def __init__(self, m, d, i):
        self.m = m
        self.d = d
        self.i = i
        # card. product D^|vars| (= all ways of forming sets of |vars| long combinations of elements from D)
        dprod = list(product(list(d), repeat=len(indiv_vars)))
        # all variable assignment functions
        self.gs = [{v: a for (v, a) in zip(indiv_vars, distr)} for distr in dprod]

    def __str__(self):
        return "Structure " + self.m + "  = ⟨D,I⟩ with\n" \
               "D = {" + ", ".join([str(d) for d in sorted(self.d)]) + "}\n" \
               "I : " + ", \n    ".join([str(key) + " ↦ " +
                                        (str(val) if isinstance(val, str) else
                                         (", ".join(["(" + str(key2) + " ↦ " + str(val2) + "⟩"
                                                     for key2, val2 in val.items()])
                                          if isinstance(val, dict) else
                                          ("{" +
                                           ", ".join(["⟨" + ", ".join([str(t) for t in s]) + "⟩" for s in val]) +
                                           "}")))
                                        for (key, val) in sorted(self.i.items())])


class ModalStructure(Structure):
    """
    A modal of (modal) predicate logic.

    @attr m: the name of the structure (such as "M1")
    @type m: str
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
      - possible worlds as keys and
      - a dictionary with
        - propositional variables as keys and
        - truth values as values
      as values.
      V = {'w1': {'p': True, 'q': False}, {'w2': {'p': False, 'q': False}}, ...}

    @attr m: the name of the structure (such as "M1")
    @type m: str
    @attr w: the set of possible worlds
    @type w: set[str]
    @attr r: the accessibility relation on self.w
    @type r: set[tuple[str,str]]
    @attr v: the valuation function
    @type v: dict[dict[str,bool]]
    """
    def __init__(self, m, w, r, v):
        self.m = m
        self.w = w
        self.r = r
        self.v = v

    def __str__(self):
        return "Structure " + self.m + " = (W, V) with\n"\
               "W = {" + ", ".join([str(w) for w in sorted(self.w)]) + "}\n"\
               "R = {" + ", ".join([str(r) for r in sorted(self.r)]) + "}\n"\
               "V : " + ", \n    ".join([str(w) + " ↦ \n" +
                            ", \n".join(["           " + str(p) + " ↦ " + str(tv)
                            for (p, tv) in sorted(self.v[w].items())])
                        for (w, vw) in sorted(self.v.items())])


class ConstModalStructure(ModalStructure):
    """
    A structure of modal predicate logic with constant domain.

    A ConstModalStructure M is a quadrupel <W,R,D,F> with
      - W = set of possible worlds
      - R = accessibility relation, a binary relation on W
      - D = domain of discourse
      - I = interpretation function assigning to each member of w and each non-logical symbol a denotation
    and a set of assignment functions vs.

    - The set of possible worlds W is a set of possible worlds, specified as strings:
       W = {'w1', 'w2', ...}

    - The accessibility relation W is a set of tuples of possible worlds:
      R = {('w1', 'w2'), ('w2', 'w2'), ...}

    - The domain D is a set of individuals, specified as strings:
      D = {'a', 'b', 'c', ...}

    - The interpretation function F is a dictionary with
      - possible worlds as keys and
      - and interpretation of the non-logical symbols as values (see Structure.f).


    @attr m: the name of the structure (such as "M1")
    @type m: str @attr w: the set of possible worlds
    @type w: set[str]
    @attr r: the accessibility relation on self.w
    @type r: set[tuple[str,str]]
    @attr d: the domain of discourse
    @type d: set[str]
    @attr i: the interpretation function
    @type i: dict[str,dict[str,Any]]
    """
    # todo doesnt work yet (assignment function)
    def __init__(self, m, w, r, d, i):
        self.m = m
        self.w = w
        self.r = r
        self.d = d
        self.i = i
        # card. product D^|vars| (= all ways of forming sets of |vars| long combinations of elements from D)
        dprod = list(product(list(d), repeat=len(indiv_vars)))
        # all variable assignment functions
        self.gs = [{v: a for (v, a) in zip(indiv_vars, distr)} for distr in dprod]

    def __str__(self):
        return "Structure " + self.m + " = ⟨W,R,D,I⟩ with\n" \
               "W = {" + ", ".join([str(w) for w in sorted(self.w)]) + "}\n"\
               "R = {" + ", ".join([str(r) for r in sorted(self.r)]) + "}\n"\
               "D = {" + ", ".join([str(d) for d in sorted(self.d)]) + "}\n" \
               "I : " + ", \n    ".join([str(w) + " ↦ \n" + \
                        ", \n".join(
                        ["           " + str(keyI) + " ↦ " +
                         (str(valI) if isinstance(valI, str) else
                          (", ".join(["(" + str(keyI2) + " ↦ " + str(valI2) + ")"
                                      for keyI2, valI2 in valI.items()])
                           if isinstance(valI, dict) else
                           ("{" +
                            ", ".join(["⟨" + ", ".join([str(t) for t in s]) + "⟩" for s in valI]) +
                            "}")))
                        for (keyI, valI) in self.i[w].items() if w in self.i]) + \
                        "\n    "
                    for (w, iw) in sorted(self.i.items())])


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
      - domains (see Structure.D) as values
      D = {'w1': {'a', 'b', 'c'}, 'w2': {'b'}, ...}

    - The interpretation function F is a dictionary with
      - possible worlds as keys and
      - and interpretation of the non-logical symbols (see Structure.f) as values.


    @attr m: the name of the structure (such as "M1")
    @type m: str
    @attr w: the set of possible worlds
    @type w: set[str]
    @attr r: the accessibility relation on self.w
    @type r: set[tuple[str,str]]
    @attr d: the mapping of worlds to domains of discourse
    @type d: dict[str,set[str]]
    @attr i: the interpretation function
    @type i: dict[str,dict[str,Any]]
    """

    def __init__(self, m, w, r, d, i):
        self.m = m
        self.w = w
        self.r = r
        self.d = d
        self.i = i
        # card. product D^|vars| (= all ways of forming sets of |vars| long combinations of elements from D) per world
        dprods = {w: list(product(list(self.d[w]), repeat=len(indiv_vars))) for w in self.w}
        # all variable assignment functions per world
        self.gs = {w: [{v: a for (v, a) in zip(indiv_vars, distr)} for distr in dprods[w]] for w in self.w}

    def __str__(self):
        return "Structure " + self.m + " = ⟨W,R,D,F⟩ with\n" \
               "W = {" + ", ".join([str(w) for w in sorted(self.w)]) + "}\n" \
               "R = {" + ", ".join([str(r) for r in sorted(self.r)]) + "}\n" \
               "D : " + ", \n".join([str(w) + " ↦ " + \
                            ", ".join([str(d) for d in sorted(self.d[w])]) + "}"
                    for w in self.w]) +\
                    \
               "I : " + ", \n    ".join([str(w) + " ↦ " +\
                            ", \n".join(
                                ["         " + str(keyI) + " ↦ " +
                                 (str(valI) if isinstance(valI, str) else
                                  (", ".join(["(" + str(keyI2) + " ↦ " + str(valI2) + ")"
                                              for keyI2, valI2 in valI.items()])
                                   if isinstance(valI, dict) else
                                   ("{" +
                                    ", ".join(["⟨" + ", ".join([str(t) for t in s]) + "⟩" for s in valI]) +
                                    "}")))
                                 for (keyI, valI) in sorted(self.i[w].items())]) + \
                            "\n    }"
                            for (w, iw) in sorted(self.i.items())])

class KripkeStructure(Structure):
    """
    A Kripke structure of intuitionistic logic.

    @attr m: the name of the structure (such as "M1")
    @type m: str
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

    def __str__(self):
        return "Structure " + self.m + " = (W, V) with\n"\
               "W = {" + ", ".join([str(k) for k in sorted(self.k)]) + "}\n"\
               "R = {" + ", ".join([str(r) for r in sorted(self.r)]) + "}\n"\
               "V : " + ", \n    ".join([str(k) + " ↦ \n" +
                            ", \n".join(["           " + str(p) + " ↦ " + str(tv)
                            for (p, tv) in sorted(self.v[k].items())])
                        for (k, vk) in sorted(self.v.items())])


class KripkePropStructure(KripkeStructure):
    """
    A Kripke structure of intuitionistic predicate logic.

    A KripkePredStructure is a triple <K,R,V> with
      - K = set of states
      - R = the accessibility relation, a binary relation on K
      - I = valuation function assigning to each member of K and each propositional variabl a truth value
    and a set of assignment functions gs assigning to each state k to each variable an element from the domain of k.

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

    @attr m: the name of the structure
    @type m: str
    @attr k: the set of states
    @type k: set[str]
    @attr r: the accessibility relation on self.k
    @type r: set[tuple[str,str]]
    @attr v: the valuation function
    @type v: dict[str,dict[str,bool]]
    """

    def __init__(self, m, k, r, v):
        self.m = m
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
        return "Structure " + self.m + " = (W, V) with\n"\
               "W = {" + ", ".join([str(k) for k in sorted(self.k)]) + "}\n"\
               "R = {" + ", ".join([str(r) for r in sorted(self.r)]) + "}\n"\
               "V : " + ", \n    ".join([str(k) + " ↦ \n" +
                            ", \n".join(["           " + str(p) + " ↦ " + str(tv)
                            for (p, tv) in sorted(self.v[k].items())])
                        for (k, vk) in sorted(self.v.items())])


class KripkePredStructure(KripkeStructure):
    """
    A Kripke structure of intuitionistic predicate logic.

    A KripkePredStructure is a quadruple <K,R,D,I> with
      - K = set of states
      - R = the accessibility relation, a binary relation on K
      - D = an assignment of states to domains of discourse
      - I = interpretation function assigning to each member of K and each non-logical symbol a denotation
    and a set of assignment functions gs assigning to each state k to each variable an element from the domain of k.

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

         I = {'k0':  {'c': 'a', 'P': {('a', )}}, 'k0': {'c': 'a',  'P': {('a', ), ('b', )}}}

    @attr m: the name of the structure
    @type m: str
    @attr k: the set of states
    @type k: set[str]
    @attr r: the accessibility relation on self.k
    @type r: set[tuple[str,str]]
    @attr d: the mapping of states to domains of discourse
    @type d: dict[str,set[str]]
    @attr i: the interpretation function
    @type i: dict[str,dict[str,Any]]
    """

    def __init__(self, m, k, r, d, i):
        self.m = m
        self.k = k
        self.r = r
        self.d = d
        self.i = i
        # card. product D^|vars| (= all ways of forming sets of |vars| long combinations of elements from D) per state
        dprods = {k: list(product(list(self.d[k]), repeat=len(indiv_vars))) for k in self.k} if d else {}
        # all variable assignment functions
        self.gs = {k: [{v: a for (v, a) in zip(indiv_vars, distr)} for distr in dprods[k]] for k in self.k} if d else {}

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
        return "Structure " + self.m + " = (K,R,D,F) with\n" \
               "K = {" + ", ".join([repr(k) for k in self.k]) + "}\n" \
               "R = {" + ", ".join([repr(r) for r in self.r]) + "}\n" \
               "D = {\n" + \
                    (", \n".join([repr(k) + " ↦ " + \
                            ", ".join([repr(d) for d in self.d[k]]) + "}"
                    for k in self.k]) if self.d else "") +\
                    "}\n" \
               "I = {\n" + \
                    ", \n".join(["    " + repr(k) + " ↦ {\n" +\
                            ", \n".join(
                                ["            " + repr(keyF) + " ↦ " +
                                 (repr(valF) if isinstance(valF, str) else
                                  (", ".join(["(" + repr(keyF2) + " ↦ " + repr(valF2) + ")"
                                              for keyF2, valF2 in valF.items()])
                                   if isinstance(valF, dict) else
                                   (repr(valF) if isinstance(valF, bool) else
                                       ("{" +
                                        ", ".join(["(" + ", ".join([repr(t) for t in s]) + ")" for s in valF]) +
                                        "}")))
                                  )
                                 for (keyF, valF) in self.i[k].items()]) + \
                            "\n           }"
                            for (k, ik) in self.i.items()]) + \
                    "\n    }"

