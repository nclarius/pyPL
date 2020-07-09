#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Define the Kripke structures of intuitionistic (propositional and first-order) logic.
"""


from main import *
from expr import *

from itertools import product


indiv_vars = ["x", "y", "z"]  # the individual variables of the language


class KripkeStructure():
    """
    A Kripke structure of intuitionistic predicate logic.

    A ConstModalStructure is a quadrupel <K,R,D,I> with
      - K = set of states
      - R = the accessibility relation, a binary relation on K
      - D = an assignment of possible worlds to domains of discourse
      - I = interpretation function assigning to each member of K and each non-logical symbol a denotation
    and a set of assignment functions gs assigning to each statek to each variable an element from the domain of k.

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

    - The interpretation function F is a dictionary with
      - states as keys and
      - and an interpretation of the non-logical symbols as values

        - The interpretation function F_k is a dictionary with
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

    @attr w: the set of states
    @type w: set[str]
    @attr r: the accessibility relation on self.k
    @type r: set[tuple[str,str]]
    @attr d: the mapping of states to domains of discourse
    @type d: dict[str,set[str]]
    @attr i: the interpretation function
    @type i: dict[str,dict[str,Any]]
    """

    def __init__(self, k, r, d, i):
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

    def __repr__(self):
        return "Structure M = (K,R,D,F) with\n" \
               "K = {" + ", ".join([repr(k) for k in self.k]) + "}\n" \
               "R = {" + ", ".join([repr(r) for r in self.r]) + "}\n" \
               "D = {\n" + \
                    (", \n".join([repr(k) + " ↦ " + \
                            ", ".join([repr(d) for d in self.d[k]]) + "}"
                    for k in self.k]) if self.d else "") +\
                    "}\n" \
               "F = {\n" + \
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
                            for (k, fk) in self.i.items()]) + \
                    "\n    }"

