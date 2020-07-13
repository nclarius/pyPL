#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Define the language and semantics of classical (standard and modal) (prepositional and first-order) logic.
"""


from main import *
from structure import *
# from tableau import *

from typing import List, Dict, Set, Tuple

frame = ""


class Expr:
    """
    Well-formed expression of predicate logic.
    α, β, ...

    @method freevars: the set of free variables in the expression
    @method boundvars: the set of bound variables in the expression
    @method subst: substitution of a term for a variable in the expression
    @method denot: denotation of the expression relative to a structure m and assignment g
    """

    def tex(self) -> str:
        """
        The expression formatted in LaTeX code.

        @return self in LaTeX code
        @rtype str
        """

    def propvars(self) -> Set[str]:
        """
        The set of propositional variables in the expression.

        @return: the set of propositional varibles in the expression
        @rtype: set[str]
        """
        return self.phi.propvars()

    def freevars(self) -> Set[str]:
        """
        The set of free variables in the expression.

        @return: the set of free variables in the expression
        @rtype: set[str]
        """
        pass

    def boundvars(self) -> Set[str]:
        """
        The set of bound variables in the expression.

        @return: the set of bound variables in the expression
        @rtype: set[str]
        """
        pass
    
    def nonlogs(self):
        """
        The set of non-logical symbols in the expression.
        
        @return the set of non-logical symbols in the expression: (constants, functions, predicates)
        @rtype: tuple[set[str]]
        """

    def subst(self, u, t):
        """
        Substitute all occurrences of the variable u for the term t in self.

        @param u: the variable to be substituted
        @type u: Var
        @param t: the term to substitute
        @type t: Term
        @return: the result of substituting all occurrences of the variable v for the term t in self
        @rtype Expr
        """
        # todo doesnt work
        pass

    def denot(self, m: Structure, v: Dict[str,str] = None, w: str = None):
        """
        Compute the denotation of the expression relative to a structure m and assignment g.

        @param m: the structure to evaluate the formula against
        @type m: Structure
        @param v: the assignment to evaluate the formula against
        @type v: dict[str,str]
        @param w: the possible world to evaluate the formula against
        @type w: str
        @return: the denotation of the expression relative to the structure m and assignment g
        """
        pass


class Term(Expr):
    """
    Term (constant, variable).
    t1, t2, ...
    """

    def subst(self, u, t):
        """
        @rtype: Term
        """
        pass

    def denot(self, m, v=None, w=None) -> str:
        """
        @rtype: str
        """
        pass


class Const(Term):
    """
    Individual constant.
    a, b, c, c1, c2, ...

    @attr c: the constant name
    @type c: str
    """

    def __init__(self, c: str):
        self.c = c

    def __str__(self):
        return self.c

    def tex(self):
        return self.c

    def __eq__(self, other):
        return isinstance(other, Const) and self.c == other.c

    def __len__(self):
        return 1

    def propvars(self):
        return set()

    def freevars(self):
        return set()

    def boundvars(self):
        return set()

    def nonlogs(self):
        return {self.c}, set(), set()

    def subst(self, u, t):
        return self

    def denot(self, m, v=None, w=None):
        """
        The denotation of a constant is that individual that the interpretation function f assigns it.
        """
        i = m.i
        if isinstance(m, ModalStructure) or isinstance(m, KripkeStructure):
            i = m.i[w]
        return i[self.c]

class Var(Term):
    """
    Individual variable.
    x, y, z, u, v, w, x1, x2, ...

    @attr u: the variable name
    @type u: str
    """
    # NB: When dealing with variable occurrences in the further processing,
    # it will be necessary to reference the variables by their name (self.v)
    # rather than the variable objects themselves (self)
    # in order for different variable occurrences with the same name to be identified, as desired in the theory.

    def __init__(self, u: str):
        self.u = u

    def __str__(self):
        return self.u

    def tex(self):
        return self.u

    def __eq__(self, other):
        return isinstance(other, Var) and self.u == other.u

    def __len__(self):
        return 1

    def propvars(self):
        return set()

    def freevars(self):
        return {self.u}

    def boundvars(self):
        return set()

    def nonlogs(self):
        return set(), set(), set()

    def subst(self, u, t):
        if u.u == self.u:
            return t
        else:
            return self

    def denot(self, m, v=None, w=None):
        """
        The denotation of a constant is that individual that the assignment function g assigns it.
        """
        return v[self.u]


class Func(Expr):
    """
    Function symbol.
    f, h, ...

    @attr f: the function name
    @type f: str
    """

    def __init__(self, f: str):
        self.f = f

    def __str__(self):
        return self.f

    def tex(self):
        return self.f

    def __eq__(self, other):
        return isinstance(other, Func) and self.f == other.f

    def __len__(self):
        return 1

    def propvars(self):
        return set()

    def freevars(self):
        return set()

    def boundvars(self):
        return set()

    def nonlogs(self):
        return set(), {self.f}, set()

    def subst(self, u, t):
        return self

    def denot(self, m, v=None, w=None) -> str:
        """
        The denotation of a constant is that individual that the assignment function g assigns it.
        """
        i = m.i
        if isinstance(m, ModalStructure) or isinstance(m, KripkeStructure):
            i = m.i[w]
        return i[self.i]


class FuncTerm(Term):
    """
    Function symbol applied to an appropriate number of terms.
    f(m), h(x,t), ...

    Note that 1-place function applications have to be specified as
    Atm('f', (t1, ))
    rather than
    Atm('f', (t))
    or
    Atm('f', t1).

    @attr f: the function symbol
    @type f: Func
    @attr terms: the term tuple to apply the function symbol to
    @type terms: tuple[Term]
    """

    def __init__(self, f: Func, terms: Tuple[Term]):
        self.f = f
        self.terms = terms

    def __str__(self):
        return str(self.f) + "(" + ", ".join([str(t) for t in self.terms]) + ")"

    def tex(self):
        return self.f.tex() + "(" + ", ".join([t.tex() for t in self.terms]) + ")"

    def __eq__(self, other):
        return isinstance(other, FuncTerm) and self.f == other.f and self.terms == other.terms

    def __len__(self):
        return len(self.func) + sum([len(t) for t in self.terms])

    def propvars(self):
        return set()

    def freevars(self):
        return set().union(*[t.freevars() for t in self.terms])

    def boundvars(self):
        return set().union(*[t.boundvars() for t in self.terms])

    def nonlogs(self):
        return set().union(*[t.nonlogs()[0] for t in self.terms]), \
               set().union(*[t.nonlogs()[1] for t in self.terms]) | {self.f}, \
               set()

    def subst(self, u, t):
        return FuncTerm(self.f, tuple([term.subst(u, t) for term in self.terms]))

    def denot(self, m, v=None, w=None) -> str:
        """
        The denotation of a function symbol applied to an appropriate number of terms is that individual that the
        interpretation function f assigns to the application.
        """
        i = m.i
        if isinstance(m, ModalStructure) or isinstance(m, KripkeStructure):
            i = m.i[w]
        return i[self.f.f][tuple([t.denot(m, v, w) for t in self.terms])]


class Pred(Expr):
    """
    Predicate.
    P, Q, ...

    @attr p: the predicate name
    @type p: str
    """
    def __init__(self, p: str):
        self.p = p

    def __str__(self):
        return self.p

    def tex(self):
        return self.p

    def __eq__(self, other):
        return isinstance(other, Pred) and self.p == other.p

    def __len__(self):
        return 1

    def propvars(self):
        return set()

    def freevars(self):
        return set()

    def boundvars(self):
        return set()

    def nonlogs(self):
        return set(), set(), {self.p}

    def subst(self, u, t):
        return self

    def denot(self, m, v=None, w=None) -> Set[Tuple[str]]:
        """
        The denotation of a predicate is the set of ordered tuples of individuals that the interpretation function f
        assigns it.
        """
        i = m.i
        if isinstance(m, ModalStructure) or isinstance(m, KripkeStructure):
            i = m.i[w]
        return i[self.p]


depth = 0  # keep track of the level of nesting


class Formula(Expr):
    """
    Formula.
    φ, ψ, ...

    @method denotV: the truth value of a formula relative to a structure m (without reference to a particular assignment)
    """
    def subst(self, u, t):
        """
        @rtype: Formula
        """
        pass

    def denot(self, m: Structure, v=None, w=None) -> bool:
        """
        @rtype: bool
        """
        pass

    def denotV(self, m: Structure, w: str = None) -> bool:
        """
        The truth value of a formula relative to a structure M (without reference to a particular assignment).
        A formula is true in a structure M iff it is true in M under all assignment functions g.

        @param m: a structure
        @type m: Structure
        @attr w: a possible world
        @type w: str
        @return: the truth value of self in m
        @rtype: bool
        """
        if isinstance(m, PropStructure) or isinstance(m, KripkePropStructure):
            return self.denot(m, w)

        global depth
        # for efficiency, restrict the domain of the assignment functions o the vars that actually occur in the formula
        var_occs = self.freevars() | self.boundvars()
        vs__ = m.vs
        if isinstance(m, VarModalStructure):
            vs__ = m.vs[w]
        vs_ = [{u: v[u] for u in v if u in var_occs} for v in vs__]
        vs = [dict(tpl) for tpl in {tuple(v.items()) for v in vs_}]  # filter out now duplicate assignment functions

        if not self.freevars():  # if the formula is closed,
            # spare yourself the quantification over all assignment functions and pick an arbitrary assignment
            # (here: the first)
            return self.denot(m, vs[0], w)

        for v in vs:  # otherwise, check the denotation for all assignment functions
            depth += 1
            if verbose:
                print((depth * " ") + "checking v := " + str(v) + " ...")
            witness = self.denot(m, v, w)
            if witness:
                if verbose:
                    print((depth * 2 * " ") + "✓")
                depth -= 1
            else:
                if verbose:
                    print((depth * 2 * " ") + "✗")
                    print((depth * " ") + "counter assignment: v := " + str(v))
                depth -= 1
                return False
        return True

    def denotW(self, m: Structure, v: Dict[str,str]) -> bool:
        """
        The truth value of a formula relative to a structure M and assmnt. g (without reference to a particular world).
        A formula is true in a structure M iff it is true in M and g in all possible worlds w.

        @param m: a structure
        @type m: ModalStructure
        @attr g: an assignment function
        @type v: dict[str,str]
        @return: the truth value of self in m under g
        @rtype: bool
        """
        global depth
        # for efficiency, restrict the domain of the assignment functions to the vars that actually occur in the formula
        var_occs = self.freevars() | self.boundvars()
        vs_ = [{u: v[u] for u in v if u in var_occs} for v in m.vs]
        m.vs_ = [dict(tpl) for tpl in {tuple(v.items()) for v in vs_}]  # filter out duplicate assignment functions

        for w in m.w:
            depth += 1
            if verbose:
                print((depth * "  ") + "checking w := " + str(w) + " ...")
            witness = self.denot(m, v, w)
            if witness:
                if verbose:
                    print((depth * 2 * " ") + "✓")
                depth -= 1
            else:
                if verbose:
                    print((depth * 2 * " ") + "✗")
                    print((depth * " ") + "counter world: w := " + str(w))
                depth -= 1
                return False
        return True

    def denotVW(self, m: Structure) -> bool:
        """
        The truth value of a formula relative to a structure M (without reference to a particular assignment and world).
        A formula is true in a structure M iff it is true in M and g under all assignments g and all possible worlds w.

        @param m: a structure
        @type m: ModalStructure
        @attr g: an assignment function
        @type v: dict[str,str]
        @return: the truth value of self in m under g
        @rtype: bool
        """
        # todo doesn't work for modal structures with varying domain yet (due different structure of assignment functions)
        global depth

        for w in m.w:
            depth += 1
            if verbose:
                print((depth * " ") + "checking w := " + str(w) + " ...")
            witness = self.denotV(m, w)
            if witness:
                if verbose:
                    print((depth * 2 * " ") + "✓")
                depth -= 1
            else:
                if verbose:
                    print((depth * 2 * " ") + "✗")
                    print((depth * " ") + "counter world: w := " + str(w))
                depth -= 1
                return False
        return True

    def denotK(self, m):
        """
        The truth value of a formula relative to a structure M (without reference to a particular state).
        A formula is true in a structure M iff it is true in M in the root state.

        @param m: a structure
        @type m: KripkeStructure
        @return: the truth value of self in m
        @rtype: bool
        """
        global depth

        # a formula is true in a structure M iff it is true in the root state k0
        return self.denotV(m, "k0")

    def tableau_pos(self):
        """
        Tableau rules for the unnegated formula.

        @return: A list of triples of
                 - the rule name
                 - the type of rule (alpha/beta/gamma/delta/mu/nu)
                 - the arguments of the rule: the formulas to extend and, if applicable, parameter/signature information
        @rtype List[Tuple[str,str,Any]]
        """
        pass

    def tableau_neg(self):
        """
        Tableau rules for the negated formula.

        @return: A list of triples of
                 - the rule name
                 - the type of rule (alpha/beta/gamma/delta/mu/nu)
                 - the arguments of the rule: the formulas to extend and, if applicable, parameter/signature information
        @rtype List[Tuple[str,str,Any]]
        """
        pass

    def tableau_contradiction_pos(self, node):
        """
        The cases where the unnegated formula leads to a contradiction in the branch.
        """
        for other in node.branch[:-1]:  # contradiction to another formula in the same branch
            #  φ        ¬φ
            #  ⋮    or    ⋮
            # ¬φ         φ
            if Neg(self) == other.fml or self == Neg(other.fml):
                node.add_closed([other.line, node.line])
                return True
        return False

    def tableau_contradiction_neg(self, node):
        """
        The cases where the unnegated formula leads to a contradiction in the branch.
        """
        for other in node.branch[:-1]:  # contradiction to another formula in the same branch
            #  φ        ¬φ
            #  ⋮    or    ⋮
            # ¬φ         φ
            if self == other.fml:
                node.add_closed([other.line, node.line])
                return True
        return False

# define short names for tableau rule names
alpha, beta, gamma, delta, mu, nu = "alpha", "beta", "gamma", "delta", "mu", "nu"

class Verum(Formula):
    """
    Verum.
    ⊤
    """
    def __init__(self):
        pass

    def __str__(self):
        return "⊤"

    def tex(self):
        return "⊤"

    def __eq__(self, other):
        return isinstance(other, Verum)

    def __len__(self):
        return 1

    def propvars(self):
        return set()

    def freevars(self):
        return set()

    def boundvars(self):
        return set()

    def nonlogs(self):
        return set(), set(), set()

    def subst(self, u, t):
        return self

    def denot(self, m, v=None, w=None):
        """
        The denotation of the verum is always true.
        """
        return True

    def tableau_pos(self):
        return []

    def tableau_neg(self):
        return []

    def tableau_contradiction_pos(self, node):
        return False

    def tableau_contradiction_neg(self, node):
        node.add_closed(node.line)
        return True


class Falsum(Formula):
    """
    Falsum.
    ⊥
    """

    def __init__(self):
        pass

    def __str__(self):
        return "⊥"

    def tex(self):
        return "⊥"

    def __eq__(self, other):
        return isinstance(other, Falsum)

    def __len__(self):
        return 1

    def propvars(self):
        return set()

    def freevars(self):
        return set()

    def boundvars(self):
        return set()

    def nonlogs(self):
        return set(), set(), set()

    def subst(self, u, t):
        return self

    def denot(self, m, v=None, w=None):
        """
        The denotation of the falsum is always false.
        """
        return False

    def tableau_pos(self):
        return []

    def tableau_neg(self):
        return []

    def tableau_contradiction_pos(self, node):
        node.add_closed(node.line)
        return True

    def tableau_contradiction_neg(self, node):
        return False


class Prop(Formula):
    """
    Propositional variable.
    p, q, ...

    @attr p: the propositional variable
    @type p: str
    """

    def __init__(self, p: str):
        self.p = p

    def __str__(self):
        return self.p

    def tex(self):
        return self.p

    def __eq__(self, other):
        return isinstance(other, Prop) and self.p == other.p

    def __len__(self):
        return 1

    def propvars(self):
        return {self.p}

    def freevars(self):
        return set()

    def boundvars(self):
        return set()

    def nonlogs(self):
        return set(), set(), set()

    def subst(self, u, t):
        return self

    def denot(self, m, v=None, w=None):
        """
        The denotation of a propositional variable is the truth value the valuation function V assigns it.
        """
        if not isinstance(m, KripkeStructure):
            v = m.v
            return v[self.p]
        else:
            return (m.v[w][self.p] or
                    True in [self.denot(m, w_, v) for w_ in m.past(w) - {w}])

    def tableau_pos(self):
        return []

    def tableau_neg(self):
        return []


class Eq(Formula):
    """
    Equality between terms.
    t1 = t2

    @attr t1: the left equality term
    @type t1: Term
    @attr t2: the right equality term
    @type t2: Term
    """

    def __init__(self, t1: Term, t2: Term):
        self.t1 = t1
        self.t2 = t2

    def __str__(self):
        return str(self.t1) + " = " + str(self.t2)

    def tex(self):
        return self.t1.tex() + " = " + self.t2.tex()

    def __eq__(self, other):
        return isinstance(other, Eq) and self.t1 == other.t1 and self.t2 == other.t2

    def __len__(self):
        return 1 + len(self.t1) + len(self.t2)

    def propvars(self):
        return set()

    def freevars(self):
        return self.t1.freevars() | self.t2.freevars()

    def boundvars(self):
        return self.t1.boundvars() | self.t2.boundvars()

    def nonlogs(self):
        return self.t1.nonlogs()[0] | self.t2.nonlogs()[0], \
               self.t1.nonlogs()[1] | self.t2.nonlogs()[1], \
               set()

    def subst(self, u, t):
        return Eq(self.t1.subst(u, t), self.t2.subst(u, t))

    def denot(self, m, v=None, w=None):
        """
        The denotation of a term equality t1 = t2 is true iff t1 and t2 denote the same individual.
        """
        return self.t1.denot(m, v, w) == self.t2.denot(m, v, w)

    def tableau_pos(self):
        return []

    def tableau_neg(self):
        return []

    def tableau_contradiction_pos(self, node):
        if str(self.t1) != str(self.t2):
            node.add_closed([node.line])
            return True
        return False

    def tableau_contradiction_neg(self, node):
        if str(self.t1) == str(self.t2):
            node.add_closed([node.line])
            return True
        return False


class Atm(Formula):
    """
    Atomic formula (predicate symbol applied to a number of terms).
    P(t1, ..., tn)

    Note that 1-place predications have to be specified as
    Atm('P', (t1, ))
    rather than
    Atm('P', (t))
    or
    Atm('P', t1).

    @attr pred: the predicate symbol
    @type pred: Pred
    @attr terms: the terms to apply the predicate symbol to
    @type terms: tuple[Term]
    """
    def __init__(self, pred: Pred, terms: Tuple[Term]):
        self.pred = pred
        self.terms = terms

    def __str__(self):
        return str(self.pred) + "(" + ",".join([str(t) for t in self.terms]) + ")"

    def tex(self):
        return self.pred.tex() + "(" + ",".join([t.tex() for t in self.terms]) + ")"

    def __eq__(self, other):
        return isinstance(other, Atm) and self.pred == other.pred and self.terms == other.terms

    def __len__(self):
        return len(self.pred) + sum([len(t) for t in self.terms])

    def propvars(self):
        return set()

    def freevars(self):
        return set().union(*[t.freevars() for t in self.terms])

    def boundvars(self):
        return set().union(*[t.boundvars() for t in self.terms])

    def nonlogs(self):
        return set().union(*[t.nonlogs()[0] for t in self.terms]), \
               set().union(*[t.nonlogs()[1] for t in self.terms]), \
               {self.pred.p}

    def subst(self, u, t):
        return Atm(self.pred, tuple([term.subst(u, t) for term in self.terms]))

    def denot(self, m, v=None, w=None):
        """
        The denotation of an atomic predication P(t1, ..., tn) is true iff the tuple of the denotation of the terms is
        an element of the interpretation of the predicate.
        """
        if not isinstance(m, KripkeStructure):
            return tuple([t.denot(m, v, w) for t in self.terms]) in self.pred.denot(m, v, w)
        else:
            return (tuple([t.denot(m, w, v) for t in self.terms]) in self.pred.denot(m, w, v) or
                    True in [self.denot(m, w_, v) for k_ in m.past(w) - {w}])

    def tableau_pos(self):
        """
        IL:
         σ p
          |
        σ.n p
        where σ.n is old
        """
        return []

    def tableau_neg(self):
        return []


class Neg(Formula):
    """
    Negation.
    ¬φ

    @attr phi: the negated formula
    @type phi: Formula
    """
    def __init__(self, phi: Formula):
        self.phi = phi

    def __str__(self):
        if isinstance(self.phi, Eq):
            return str(self.phi.t1) + "≠" + str(self.phi.t2)
        return "¬" + str(self.phi)

    def tex(self):
        if isinstance(self.phi, Eq):
            return self.phi.t1.tex() + " \\neq " + self.phi.t2.tex()
        return "\\neg" + self.phi.tex()

    def __eq__(self, other):
        return isinstance(other, Neg) and self.phi == other.phi

    def __len__(self):
        return 1 + len(self.phi)

    def propvars(self):
        return self.phi.propvars()

    def freevars(self):
        return self.phi.freevars()

    def boundvars(self):
        return self.phi.boundvars()

    def nonlogs(self):
        return self.phi.nonlogs()[0], \
               self.phi.nonlogs()[1], \
               self.phi.nonlogs()[2]

    def subst(self, u, t):
        return Neg(self.phi.subst(u, t))

    def denot(self, m, v=None, w=None):
        """
        In CL, the denotation of a negated formula Neg(phi) is true iff phi is false.

        In IL, the denotation of a negated formula Neg(phi) is true iff phi is false at all subsequent states k' >= k.

        """
        if not isinstance(m, KripkeStructure):  # CL
            return not self.phi.denot(m, v, w)
        else:  # IL
            return True not in [self.phi.denot(m, w_, v) for w_ in m.future(w)]

    def tableau_pos(self):
        """
        CL + IL:    IL:
        ¬φ           σ ¬φ
         ⋮             |
                    σ.n ¬φ
                    where σ.n is old
        """
        # If the negation does not occur under another neg., apply the negative tableau rule on the negative formula.
        return self.phi.tableau_neg()

    def tableau_neg(self):
        """
        CL:    IL:
        ¬¬φ    σ ¬¬φ
         |       |
         φ     σ.n φ
               where σ.n is new
        """
        # If the negation is itself negated, apply the double negation elimination rule on the double negated formula.
        return [("¬¬", alpha, [self.phi])]

    def tableau_contradiction_pos(self, node):
        return self.phi.tableau_contradiction_neg(node)


class Conj(Formula):
    """
    Conjunction.
    (φ∧ψ)

    @attr phi: the left conjunct
    @type phi: Formula
    @attr psi: the right conjunct
    @type psi: Formula
    """
    def __init__(self, phi: Formula, psi: Formula):
        self.phi = phi
        self.psi = psi

    def __str__(self):
        return "(" + str(self.phi) + " ∧ " + str(self.psi) + ")"

    def tex(self):
        return "(" + self.phi.tex() + " \\wedge " + self.psi.tex() + ")"

    def __eq__(self, other):
        return isinstance(other, Conj) and self.phi == other.phi and self.psi == other.psi

    def __len__(self):
        return 1 + len(self.phi) + len(self.psi)

    def propvars(self):
        return self.phi.propvars() | self.psi.propvars()

    def freevars(self):
        return self.phi.freevars() | self.psi.freevars()

    def boundvars(self):
        return self.phi.boundvars() | self.psi.boundvars()

    def nonlogs(self):
        return self.phi.nonlogs()[0] | self.psi.nonlogs()[0], \
               self.phi.nonlogs()[1] | self.psi.nonlogs()[1], \
               self.phi.nonlogs()[2] | self.psi.nonlogs()[2]

    def subst(self, u, t):
        return Conj(self.phi.subst(u, t), self.psi.subst(u, t))

    def denot(self, m, v=None, w=None):
        """
        The denotation of a conjoined formula Con(phi,psi) is true iff phi is true and psi is true.
        """
        return self.phi.denot(m, v, w) and self.psi.denot(m, v, w)

    def tableau_pos(self):
        """
        (φ∧ψ)
          φ
          |
          ψ
        """
        return [("∧", alpha, ([self.phi, self.psi]))]

    def tableau_neg(self):
        """
         ¬(φ∧ψ)
          /  \
        ¬φ   ¬ψ
        """
        return [("¬∧", beta, ([Neg(self.phi)], [Neg(self.psi)]))]


class Disj(Formula):
    """
    Disjunction.
    (φ∨ψ)

    @attr phi: the left disjunct
    @type phi: Formula
    @attr psi: the right disjunct
    @type psi: Formula
    """
    def __init__(self, phi: Formula, psi: Formula):
        self.phi = phi
        self.psi = psi

    def __str__(self):
        return "(" + str(self.phi) + " ∨ " + str(self.psi) + ")"

    def tex(self):
        return "(" + self.phi.tex() + " \\vee " + self.psi.tex() + ")"

    def __eq__(self, other):
        return isinstance(other, Disj) and self.phi == other.phi and self.psi == other.psi

    def __len__(self):
        return 1 + len(self.phi) + len(self.psi)

    def propvars(self):
        return self.phi.propvars() | self.psi.propvars()

    def freevars(self):
        return self.phi.freevars() | self.psi.freevars()

    def boundvars(self):
        return self.phi.boundvars() | self.psi.boundvars()

    def nonlogs(self):
        return self.phi.nonlogs()[0] | self.psi.nonlogs()[0], \
               self.phi.nonlogs()[1] | self.psi.nonlogs()[1], \
               self.phi.nonlogs()[2] | self.psi.nonlogs()[2]

    def subst(self, u, t):
        return Disj(self.phi.subst(u, t), self.psi.subst(u, t))

    def denot(self, m, v=None, w=None):
        """
        The denotation of a conjoined formula Disj(phi,psi) is true iff phi is true or psi is true.
        """
        return self.phi.denot(m, v, w) or self.psi.denot(m, v, w)

    def tableau_pos(self):
        """
        (φ∨ψ)
         /  \
        φ   ψ
        """
        return [("∨", beta, ([self.phi], [self.psi]))]

    def tableau_neg(self):
        """
        ¬(φ∨ψ)
           |
          ¬φ
           |
          ¬ψ
        """
        return [("¬∨", alpha, ([Neg(self.phi), Neg(self.psi)]))]


class Imp(Formula):
    """
    Implication.
    (φ→ψ)

    @attr phi: the antecedent
    @type phi: Formula
    @attr psi: the consequent
    @type psi: Formula
    """
    def __init__(self, phi: Formula, psi: Formula):
        self.phi = phi
        self.psi = psi

    def __str__(self):
        return "(" + str(self.phi) + " → " + str(self.psi) + ")"

    def tex(self):
        return "(" + self.phi.tex() + " \\rightarrow " + self.psi.tex() + ")"

    def __eq__(self, other):
        return isinstance(other, Imp) and self.phi == other.phi and self.psi == other.psi

    def __len__(self):
        return 1 + len(self.phi) + len(self.psi)

    def propvars(self):
        return self.phi.propvars() | self.psi.propvars()

    def freevars(self):
        return self.phi.freevars() | self.psi.freevars()

    def boundvars(self):
        return self.phi.boundvars() | self.psi.boundvars()

    def nonlogs(self):
        return self.phi.nonlogs()[0] | self.psi.nonlogs()[0], \
               self.phi.nonlogs()[1] | self.psi.nonlogs()[1], \
               self.phi.nonlogs()[2] | self.psi.nonlogs()[2]

    def subst(self, u, t):
        return Imp(self.phi.subst(u, t), self.psi.subst(u, t))

    def denot(self, m, v=None, w=None):
        """
        In CL, the denotation of an implicational formula Imp(phi,psi) is true iff phi is false or psi is true.

        In IL, the denotation of an implicational formula Imp(phi,psi) is true at k iff
        at all subsequent states k' >= k, either phi is false or psi is true at k'.
        """
        if not isinstance(self, KripkeStructure):  # CL
            return not self.phi.denot(m, v, w) or self.psi.denot(m, v, w)
        else:  # IL
            return False not in [(not self.phi.denot(m, w_, v) or self.psi.denot(m, w_, v)) for w_ in m.future(w)]

    def tableau_pos(self):
        """
        CL:      IL:
        (φ→ψ)        σ (φ→ψ)
         /  \         /   \
        ¬φ  ψ    σ.n ¬φ  σ.n ψ
                 where σ.n is old
        """
        # todo IL
        return [("→", beta, ([Neg(self.phi)], [self.psi]))]

    def tableau_neg(self):
        """
        CL:      IL:
        ¬(φ→ψ)   σ ¬(φ→ψ)
           |        |
           φ     σ.n φ
           |        |
          ¬ψ     σ.n ¬ψ
                 where σ.n is new
        """
        # todo IL
        return [("¬→", alpha, ([self.phi, Neg(self.psi)]))]


class Biimp(Formula):
    """
    Biimplication.
    (φ↔ψ)

    @attr phi: the left formula
    @type phi: Formula
    @attr psi: the right formula
    @type psi: Formula
    """
    def __init__(self, phi: Formula, psi: Formula):
        self.phi = phi
        self.psi = psi

    def __str__(self):
        return "(" + str(self.phi) + " ↔ " + str(self.psi) + ")"

    def tex(self):
        return "(" + self.phi.tex() + " \\leftrightarrow " + self.psi.tex() + ")"

    def __eq__(self, other):
        return isinstance(other, Biimp) and self.phi == other.phi and self.psi == other.psi

    def __len__(self):
        return 1 + len(self.phi) + len(self.psi)

    def propvars(self):
        return self.phi.propvars() | self.psi.propvars()

    def freevars(self):
        return self.phi.freevars() | self.psi.freevars()

    def boundvars(self):
        return self.phi.boundvars() | self.psi.boundvars()

    def nonlogs(self):
        return self.phi.nonlogs()[0] | self.psi.nonlogs()[0], \
               self.phi.nonlogs()[1] | self.psi.nonlogs()[1], \
               self.phi.nonlogs()[2] | self.psi.nonlogs()[2]

    def subst(self, u, t):
        return Biimp(self.phi.subst(u, t), self.psi.subst(u, t))

    def denot(self, m, v=None, w=None):
        """
        In CL, the denotation of an biimplicational formula Biimp(phi,psi) is true iff
        phi and psi have the same truth value.

        In IL, the denotation of an biimplicational formula Biimp(phi,psi) is true at k iff
        at all subsequent states k' >= k, phi and psi have the same truth value.
        """
        if not isinstance(m, KripkeStructure):  # CL
            return self.phi.denot(m, v, w) == self.psi.denot(m, v, w)
        else:  # IL
            return False not in [(self.phi.denot(m, w_, v) == self.psi.denot(m, w_, v)) for w_ in m.future(w)]

    def tableau_pos(self):
        """
        CL:        IL:
         (φ↔ψ)         σ (φ→ψ)
         /  \          /     \
        φ   ¬φ     σ.n φ   σ.n ¬φ
        |    |       |        |
        ψ   ¬ψ     σ.n ψ   σ.n ¬ψ
                   where σ.n is old
        """
        return [("↔", beta, ([self.phi, self.psi], [Neg(self.phi), Neg(self.psi)]))]

    def tableau_neg(self):
        """
        CL:         IL:
         ¬(φ↔ψ)         σ ¬(φ↔ψ)
          /  \            /   \
         φ   ¬φ      σ.n φ    σ.n ¬φ
         |    |         |        |
        ¬ψ    ψ      σ.n ¬ψ   σ.n ψ
                    where σ.n is new
        """
        return [("¬↔", beta, ([self.phi, Neg(self.psi)], [Neg(self.phi), self.psi]))]


class Exists(Formula):
    """
    Existential quantification.
    ∃xφ

    @attr u: the binding variable
    @type u: Var
    @attr phi: the formula to be quantified
    @type phi: Formula
    """
    def __init__(self, u: Var, phi: Formula):
        self.u = u
        self.phi = phi

    def __str__(self):
        return "∃" + str(self.u) + str(self.phi)

    def tex(self):
        return "\\exists " + self.u.tex() + " " + self.phi.tex()

    def __eq__(self, other):
        return isinstance(other, Exists) and self.u == other.u and self.phi == other.phi

    def __len__(self):
        return 2 + len(self.phi)

    def propvars(self):
        return set()

    def freevars(self):
        return self.phi.freevars() - {self.u.u}

    def boundvars(self):
        return self.phi.boundvars() | {self.u.u}

    def nonlogs(self):
        return self.phi.nonlogs()

    def subst(self, u, t):
        if u.u == self.u:
            return self
        else:
            return Exists(self.u, self.phi.subst(u, t))

    def denot(self, m, v=None, w=None):
        """
        The denotation of an existentially quantified formula Exists(x, phi) is true
        iff phi is true under at least one x-variant of v.
        """
        global verbose
        d = m.d
        if isinstance(m, VarModalStructure) or isinstance(m, KripkeStructure):
            d = m.d[w]

        # short version
        if not verbose:
            return any([self.phi.denot(m, {**v, self.u.u: d_}) for d_ in d])

        # long version
        global depth
        depth += 1

        # iterate through the individuals in the domain
        for d_ in sorted(d):

            # compute the x-variant v' of v
            v_ = v  # v' is just like v, except...
            v_[self.u.u] = d_  # ... the value for the variable u is now the new individual d

            # check whether the current x-variant under consideration makes phi true
            print((depth * 2 * " ") + "checking v" + (depth * "'") + "(" + str(self.u) + ") := " + str(d_) + " ...")
            witness = self.phi.denot(m, v_, w)

            # if yes, we found a witness, the existential statement is true and we can stop checking (return)
            if witness:
                print((depth * 2 * " ") + "✓")
                depth -= 1
                return True

            # if not, we do nothing and try with the next one (continue)
            else:
                print((depth * 2 * " ") + "✗")
                continue

        # if we reach the end, then no witness has been found, and the existential statement is false
        depth -= 1
        return False

    def tableau_pos(self):
        """
         ∃vφ
          |
        φ[v/c]
        where c is new
        """
        return [("∃", delta, (self.phi, self.u))]

    def tableau_neg(self):
        """
         ¬∃vφ
           |
        ¬φ[v/c]
        where c is arbitrary
        """
        return [("¬∃", gamma, (Neg(self.phi), self.u))]


class Forall(Formula):
    """
    Universal quantification.
    ∀xφ

    @attr u: the binding variable
    @type u: Var
    @attr phi: the formula to be quantified
    @type phi: Formula
    """
    def __init__(self, u: Var, phi: Formula):
        self.u = u
        self.phi = phi

    def __str__(self):
        return "∀" + str(self.u) + str(self.phi)

    def tex(self):
        return "\\forall " + self.u.tex() + " " + self.phi.tex()

    def __eq__(self, other):
        return isinstance(other, Forall) and self.u == other.u and self.phi == other.phi

    def __len__(self):
        return 2 + len(self.phi)

    def propvars(self):
        return set()

    def freevars(self):
        return self.phi.freevars() - {self.u.u}

    def boundvars(self):
        return self.phi.boundvars() | {self.u.u}

    def nonlogs(self):
        return self.phi.nonlogs()

    def subst(self, u, t):
        if u.u == self.u:
            return self
        else:
            return Forall(self.u, self.phi.subst(u, t))

    def denot(self, m, v=None, w=None):
        """
        In CL, the denotation of universally quantified formula Forall(x, phi) is true iff
        phi is true under all x-variants of v.

        In IL, the denotation of universally quantified formula Forall(x, phi) is true at k iff
        at all subsequent states k' >= k, phi is true under all x-alternatives v' of v at k'.
        """
        global verbose
        global depth
        depth += 1
        d = m.d
        if isinstance(w, VarModalStructure):
            d = m.d[w]

        if not isinstance(m, KripkeStructure):  # CL

            # short version
            if not verbose:
                return all([self.phi.denot(m, {**v, self.u.u: d_}) for d_ in d])

            # long version

            # iterate through the individuals in the domain
            for d_ in sorted(d):

                # compute the x-variant v' of v
                v_ = v  # v' is just like v, except...
                v_[self.u.u] = d_  # ... the value for the variable u is now the new individual d

                # check whether the current x-variant under consideration makes phi true
                print((depth * 2 * " ") + "checking v" + (depth * "'") + "(" + str(self.u) + ") := " + str(d_) + " ...")
                witness = self.phi.denot(m, v_, w)

                # if yes, everything is fine until now, we do nothing and go check the next one (continue)
                if witness:
                    print((depth * 2 * " ") + "✓")
                    continue

                # if not, we found a counter witness, the universal statement is false and we can stop checking (return)
                else:
                    print((depth * 2 * " ") + "✗")
                    depth -= 1
                    return False

            # if we reach the end, then no counter witness has been found, and the universal statement is true
            depth -= 1
            return True

        else:  # IL

            # short version
            if not verbose:
                return all([all([self.phi.denot(m, w_, {**v, self.u.u: d_}) for d_ in m.d[w_]]) for w_ in m.future(w)])

            # long version

            # quantify over the subsequent states
            for w_ in m.future(w):
                d = m.d[w_]
                depth += 1

                # iterate through the individuals in the domain of the future state
                for d_ in d:

                    # compute the x-variant v' of v
                    v_ = v  # v' is just like v, except...
                    v_[self.u.u] = d_  # ... the value for the variable u is now the new individual d

                    # check whether the current indiv. d under consideration makes phi true at k'
                    print((depth * 2 * " ") + "checking v" + (depth * "'") + "(" + str(self.u) + ") := " + str(
                        d_) + " ...")
                    witness = self.phi.denot(m, w_, v_)

                    # if yes, everything is fine until now, we do nothing and go check the next one (continue)
                    if witness:
                        print(((depth + 1) * 2 * " ") + "✓")

                    # if not, we found a counter witness, the universal statement is false, and we can stop checking
                    else:
                        print(((depth + 1) * 2 * " ") + "✗")
                        print(((depth + 1) * 2 * " ") + "counter witness: k' = " + str(w_) + ", " +
                              "v" + (depth * "'") + "(" + str(self.u) + ") := " + str(d_))
                        return False

                # if no counter witness has been found, the universal statement is true at k'
                depth -= 1

            # if no counter state has been found, the universal statement is true at k
            depth -= 1
            return True

    def tableau_pos(self):
        """
        CL:       IL:
         ∀vφ         σ ∀vφ
          |            |
        φ[v/c]    σ.n φ[v/c]
                  where σ.n is old
        where c is arbitrary
        """
        return [("∀", gamma, (self.phi, self.u))]

    def tableau_neg(self):
        """
        CL:        IL:
        ¬∀vφ          σ ¬∀vφ
          |             |
        ¬φ[x/c]    σ.n ¬φ[x/c]
                   where σ.n is new
        where c is new
        """
        return [("¬∀", delta, (Neg(self.phi), self.u))]


class Poss(Formula):
    """
    Possibility.
    ◇φ

    @attr phi: the formula to apply the modal operator to
    @type phi: Formula
    """
    def __init__(self, phi: Formula):
        self.phi = phi

    def __str__(self):
        return "◇" + str(self.phi)

    def tex(self):
        return "\\Diamond " + " " + self.phi.tex()

    def __eq__(self, other):
        return isinstance(other, Poss) and self.phi == other.phi

    def __len__(self):
        return 1 + len(self.phi)

    def propvars(self):
        return self.phi.propvars()

    def freevars(self):
        return self.phi.freevars()

    def boundvars(self):
        return self.phi.boundvars()

    def nonlogs(self):
        return self.phi.nonlogs()

    def subst(self, u, t):
        return Poss(self.phi.subst(u, t))

    def denot(self, m, v, w):
        """
        In CL, the denotation of a possiblity formula is true iff
        phi is true at at least one world accessible from w.

        @param m: the structure to evaluate the formula in
        @type m: ModalStructure
        @param v: the assignment function to evaluate the formula in
        @type v: dict[str,str]
        @param w: the world to evaluate the formula in
        @type w: str
        @return: the denotation of Poss(phi)
        """
        if isinstance(m, KripkeStructure):
            return  # not implemented

        # all possible worlds w' which are accessible from w
        neighbors = [w_ for w_ in m.w if (w, w_) in m.r]

        # short version
        if not verbose:
            return any([self.phi.denot(m, v, w_) for w_ in neighbors])

        # long version
        global depth
        depth += 1

        # iterate through ws neighbors w'
        for w_ in neighbors:

            # check whether phi is true in w
            print((depth * "  ") + "checking w" + (depth * "'") + " := " + str(w_) + " ...")
            witness = self.phi.denot(m, v, w_)

            # if yes, we found a witnessing neighbor, the poss. statement is true, and we can stop checking (return)
            if witness:
                print((depth * 2 * " ") + "✓")
                print((depth * 2 * " ") + "neighbor: w" + (depth * "'") + " := " + str(w_))
                depth -= 1
                return True

            # if not, we do nothing and try with the next one (continue)
            else:
                print((depth * 2 * " ") + "✗")
                continue

        # if no witness has been found, the possibility statement is false
        depth -= 1
        return False

    def tableau_pos(self):
        """
        Rule K:
         σ ◇φ
          |
        σ.n φ
        where σ.n is new
        """
        rules = [("◇", mu, self.phi)]
        return rules

    def tableau_neg(self):
        """
        Rule K:   Rule D:   Rule T:   Rule B:   Rule 4:   Rule 4r:
         σ ¬◇φ    σ ¬◇φ     σ ¬◇φ     σ.n ¬◇φ    σ ¬◇φ    σ.n ¬◇φ
           |         |         |         |         |          |
        σ.n ¬φ    σ ¬◻φ     σ  ¬φ      σ ¬φ     σ.n ¬◇φ    σ ¬◇φ
        where σ and σ.n are old
        """
        rules = [("¬", nu, Neg(self.phi))]
        if frame in ["D"]:
            rules.append(("¬D", "epsilon", ([Neg(Nec(self.phi))])))
        if frame in ["T", "B", "S4", "S5"]:
            rules.append(("¬T", "epsilon", ([Neg(self.phi)])))
        if frame in ["B"]:
            rules.append(("¬B", "zeta", ([Neg(self.phi)])))
        if frame in ["K4", "S4", "S5"]:
            rules.append(("¬4", "nu", ([Neg(Poss(self.phi))])))
        if frame in ["S5"]:
            rules.append(("¬4r", "zeta", ([Neg(Poss(self.phi))])))
        return rules


class Nec(Formula):
    """
    Necessity.
    ◻φ

    @attr phi: the formula to apply the modal operator to
    @type phi: Formula
    """

    def __init__(self, phi: Formula):
        self.phi = phi

    def __str__(self):
        return "◻" + str(self.phi)

    def tex(self):
        return "\\Box " + " " + self.phi.tex()

    def __eq__(self, other):
        return isinstance(other, Nec) and self.phi == other.phi

    def __len__(self):
        return 1 + len(self.phi)

    def propvars(self):
        return self.phi.propvars()

    def freevars(self):
        return self.phi.freevars()

    def boundvars(self):
        return self.phi.boundvars()

    def nonlogs(self):
        return self.phi.nonlogs()

    def subst(self, u, t):
        return Poss(self.phi.subst(u, t))

    def denot(self, m, v, w):
        """
        In CL, the denotation of a necessity formula is true iff
        phi is true at all worlds accessible from w.

        @param m: the structure to evaluate the formula in
        @type m: ModalStructure
        @param w: the world to evaluate the formula in
        @type w: str
        @param v: the assignment function to evaluate the formula in
        @type v: dict[str,str]
        """
        if isinstance(m, KripkeStructure):
            return  # not implemented

        # all possible worlds w' which are accessible from w
        neighbors = [w_ for w_ in m.w if (w, w_) in m.r]

        # short version
        if not verbose:
            return all([self.phi.denot(m, v, w_) for w_ in neighbors])

        # long version
        global depth
        depth += 1

        # iterate through ws neighbors w'
        for w_ in neighbors:

            # check whether phi is true in w
            print((depth * "  ") + "checking w" + (depth * "'") + " := " + str(w_) + " ...")
            witness = self.phi.denot(m, v, w_)

            # if yes, everything is fine until now, we do nothing and go check the next one (continue)
            if witness:
                print((depth * 2 * " ") + "✓")
                continue

            # if not, we found a counter neighbor, the necessity statement is false, and we can stop checking
            else:
                print((depth * 2 * " ") + "✗")
                print((depth * 2 * " ") + "counter neighbor: w" + (depth * "'") + " := " + str(w_))
                depth -= 1
                return False

        # if no counter neighbor has been found, the necessity statement is true
        depth -= 1
        return True

    def tableau_pos(self):
        """
        Rule K:   Rule D:   Rule T:   Rule B:   Rule 4:   Rule 4r:
        σ ◻φ      σ ◻φ      σ ◻φ      σ.n ◻φ     σ ◻φ     σ.n ◻φ
          |         |         |          |         |        |
        σ.n φ     σ ◇φ       σ φ       σ ¬φ     σ.n ◻φ     σ ◻φ
        where σ.n is old
        """
        rules = [("◻", nu, self.phi)]
        if frame in ["D"]:
            rules.append(("D", "epsilon", ([Poss(self.phi)])))
        if frame in ["T", "B", "S4", "S5"]:
            rules.append(("T", "epsilon", ([self.phi])))
        if frame in ["B"]:
            rules.append(("B", "zeta", ([self.phi])))
        if frame in ["K4", "S4", "S5"]:
            rules.append(("4", "nu", ([Nec(self.phi)])))
        if frame in ["S5"]:
            rules.append(("4r", "zeta", ([Nec(self.phi)])))
        return rules

    def tableau_neg(self):
        """
        Rule K:
         σ ¬◻φ
           |
        σ.n ¬φ
        where σ.n is new
        """
        rules = [("¬◻", mu, Neg(self.phi))]
        return rules


class Closed(Formula):
    """
    Special pseudo-formula indicating a branch is closed.
    ×
    """

    def __init__(self):
        pass

    def __str__(self):
        return "×"


class Open(Formula):
    """
    Special pseudo-formula indicating a branch is open.
    ○
    """

    def __init__(self):
        pass

    def __str__(self):
        return "○"


class Infinite(Formula):
    """
    Special pseudo-formula indicating a branch is (probably) infinite.
    ...
    """

    def __init__(self):
        pass

    def __str__(self):
        return "⋮"
