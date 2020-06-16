# -*- coding: utf-8 -*-

"""
Define the structures of classical (standard and modal) (prepositional and first-order) logic.
"""


from main import *
from expr import *


# helper functions
def cart_prod(a, n):
    """
    Compute the n-fold cartesian product of a list A.
    A x ... x A (n times)

    @param a: the list to form the cartesian product of
    @type a: list
    @param n: the arity of the cartesian product
    @type n: int
    @return: A^n
    @rtype: list[list[Any]]
    """
    if n == 0:
        return []
    res = [[x] for x in a]
    for i in range(n-1):
        res = [t+[x] for t in res for x in a]
    res = [tuple(el) for el in res]
    return res

indiv_vars = ["x", "y", "z"]  # the individual variables of the language


class Structure:
    """
    A structure of (modal) predicate logic.

    @attr d: the domain of discourse
    @attr i: an interpretation function
    """
    pass


class PropStructure(Structure):
    """
    A structure of propositional logic with valuation function.

    A structure M is a function V: VAR -> {True, False}.
    V = {"p": True, "q": False, "r": True}

    @attr v: the valuation function
    @type v: dict[str,bool]
    """
    def __init__(self, v):
        self.v = v

    def __str__(self):
        return "Structure M = V with V: " + ", ".join([str(key) + " ↦ " + str(val) for key, val in self.v.items()])


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

    @attr d: the domain of discourse
    @type d: set[str]
    @attr i: the interpretation function assigning denotations to the non-logical symbols
    @type i: dict[str,Any]
    @type vs: the assignment functions associated with the structure
    @type vs: list[dict[str,str]]]
    """

    def __init__(self, d, i):
        self.d = d
        self.i =i
        # all ways of forming sets of |vars| long combinations of elements from D
        dprod = cart_prod(list(d), len(indiv_vars))
        # all variable assignment functions
        self.vs = [{v: a for (v, a) in zip(indiv_vars, distr)} for distr in dprod]

    def __str__(self):
        return "Structure M = ⟨D,I⟩ with\n" \
               "D = {" + ", ".join([str(d) for d in self.d]) + "}\n" \
               "I = {\n" + ", \n".join(["     " + str(key) + " ↦ " +
                                        (str(val) if isinstance(val, str) else
                                         (", ".join(["(" + str(key2) + " ↦ " + str(val2) + "⟩"
                                                     for key2, val2 in val.items()])
                                          if isinstance(val, dict) else
                                          ("{" +
                                           ", ".join(["⟨" + ", ".join([str(t) for t in s]) + "⟩" for s in val]) +
                                           "}")))
                                        for (key, val) in self.i.items()]) +\
               "\n    }"


class ModalStructure(Structure):
    """
    A modal of (modal) predicate logic.

    @attr w: a set of possible worlds
    @type w: set[str]
    @attr r: an accessibility relation on r
    @type r: set[tuple[str,str]]
    """
    pass


class ConstModalStructure(ModalStructure):
    """
    A structure of modal predicate logic with constant domain.

    A ConstModalStructure M is a quadrupel <W,R,D,F> with
      - W = set of possible worlds
      - R = the accessibility relation, a binary relation on W
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

    @attr w: the set of possible worlds
    @type w: set[str]
    @attr r: the accessibility relation on self.w
    @type r: set[tuple[str,str]]
    @attr d: the domain of discourse
    @type d: set[str]
    @attr i: the interpretation function
    @type i: dict[str,dict[str,Any]]
    """
    # todo doesnt work yet (assignment function)
    def __init__(self, w, r, d, f):
        self.w = w
        self.r = r
        self.d = d
        self.i = f
        # all ways of forming sets of |vars| long combinations of elements from D
        dprod = cart_prod(list(d), len(indiv_vars))
        # all variable assignment functions
        self.vs = [{v: a for (v, a) in zip(indiv_vars, distr)} for distr in dprod]

    def __str__(self):
        return "Structure M = ⟨W,R,D,I⟩ with\n" \
               "W = {" + ", ".join([str(w) for w in self.w]) + "}\n"\
               "R = {" + ", ".join([str(r) for r in self.r]) + "}\n"\
               "D = {" + ", ".join([str(d) for d in self.d]) + "}\n" \
               "I = {\n" +\
                    " \n".join(["    " + str(w) + " ↦ \n" + \
                        ", \n".join(
                        ["           " + str(keyI) + " ↦ " +
                         (str(valI) if isinstance(valI, str) else
                          (", ".join(["(" + str(keyI2) + " ↦ " + str(valI2) + ")"
                                      for keyI2, valI2 in valI.items()])
                           if isinstance(valI, dict) else
                           ("{" +
                            ", ".join(["⟨" + ", ".join([str(t) for t in s]) + "⟩" for s in valI]) +
                            "}")))
                        for (keyI, valI) in self.i[w].items()]) + \
                        "\n    "
                    for (w, fw) in self.i.items()]) +\
                    "}"


class VarModalStructure(ModalStructure):
    """
    A structure of modal predicate logic with varying domains.

    A VarModalStructure M is a quadrupel <W,R,D,I> with
      - W = set of possible worlds
      - R = the accessibility relation, a binary relation on W
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

    @attr w: the set of possible worlds
    @type w: set[str]
    @attr r: the accessibility relation on self.w
    @type r: set[tuple[str,str]]
    @attr d: the mapping of worlds to domains of discourse
    @type d: dict[str,set[str]]
    @attr i: the interpretation function
    @type i: dict[str,dict[str,Any]]
    """

    def __init__(self, w, r, d, i):
        self.w = w
        self.r = r
        self.d = d
        self.i = i
        # all ways of forming sets of |vars| long combinations of elements from D per world
        dprods = {w: cart_prod(list(self.d[w]), len(indiv_vars)) for w in self.w}
        # all variable assignment functions per world
        self.vs = {w: [{v: a for (v, a) in zip(indiv_vars, distr)} for distr in dprods[w]] for w in self.w}

    def __str__(self):
        return "Structure M = ⟨W,R,D,F⟩ with\n" \
               "W = {" + ", ".join([str(w) for w in self.w]) + "}\n" \
               "R = {" + ", ".join([str(r) for r in self.r]) + "}\n" \
               "D = {\n" + \
                    ", \n".join([str(w) + " ↦ " + \
                            ", ".join([str(d) for d in self.d[w]]) + "}"
                    for w in self.w]) +\
                    "}\n" \
               "I = {\n" + \
                    ", \n".join(["    " + str(w) + " ↦ " +\
                            ", \n".join(
                                ["         " + str(keyI) + " ↦ " +
                                 (str(valI) if isinstance(valI, str) else
                                  (", ".join(["(" + str(keyI2) + " ↦ " + str(valI2) + ")"
                                              for keyI2, valI2 in valI.items()])
                                   if isinstance(valI, dict) else
                                   ("{" +
                                    ", ".join(["⟨" + ", ".join([str(t) for t in s]) + "⟩" for s in valI]) +
                                    "}")))
                                 for (keyI, valI) in self.i[w].items()]) + \
                            "\n    }"
                            for (w, fw) in self.i.items()]) + \
                    "}"
