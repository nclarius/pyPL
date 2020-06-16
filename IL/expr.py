# -*- coding: utf-8 -*-

"""
Define the language and semantics of intuitionistic (prepositional and first-order) logic.
"""


from main import *
from struct import *


class Expr:
    """
    Well-formed expression of predicate logic.
    α, β, ...

    @method freevars: the set of the free variable occurrences in the expression
    @method boundvars: the set of bound variable occurrences in the expression
    @method subst: substitution of a term for a variable in the expression
    @method denot: denotation of the expression relative to a structure m and assignment g
    """

    def freevars(self):
        """
        The set of the free variable occurrences in the expression.

        @return: the set of the free variable occurrences in the expression
        @rtype: set[str]
        """
        pass

    def boundvars(self):
        """
        The set of the bound variable occurrences in the expression.

        @return: the set of the bound variable occurrences in the expression
        @rtype: set[str]
        """
        pass

    def subst(self, v, t):
        """
        Substitute all occurrences of the variable v for the term t in self.

        @param v: the variable to be substituted
        @type v: Var
        @param a: the term to substitute
        @type a: Term
        @return: the result of substituting all occurrences of the variable v for the term t in self
        @rtype Expr
        """
        pass

    def denot(self, m, k, g):
        """
        Compute the denotation of the expression relative to a structure m and assignment g.

        @param m: the structure to evaluate the formula against
        @type m: Structure
        @param g: the assignment to evaluate the formula against
        @type g: dict[str,str]
        @param k: the state to evaluate the formula against
        @type k: str
        @return: the denotation of the expression relative to the structure m and assignment g
        """
        pass


class Term(Expr):
    """
    Term (constant, variable).
    t1, t2, ...
    """

    def denot(self, m, k, g):
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

    def __init__(self, c):
        self.c = c

    def __repr__(self):
        return self.c

    def freevars(self):
        return {}

    def boundvars(self):
        return {}

    def subst(self, v, t):
        return self

    def denot(self, m, k, g):
        """
        The denotation of a constant is that individual that the interpretation function f assigns it.
        """
        i = m.i[k][k]
        return i[self.c]


class Var(Term):
    """
    Individual variable.
    x, y, z, u, v, w, x1, x2, ...

    @attr v: the variable name
    @type v: str
    """

    # NB: When dealing with variable occurrences in the further processing,
    # it will be necessary to reference the variables by their name (self.v)
    # rather than the variable objects themselves (self)
    # in order for different variable occurrences with the same name to be identified, as desired in the theory.
    def __init__(self, v):
        self.v = v

    def __repr__(self):
        return self.v

    def freevars(self):
        return {self.v}

    def boundvars(self):
        return set()

    def subst(self, v, t):
        if self.v == v:
            return Var(repr(a))
        else:
            return self

    def denot(self, m, k, g):
        """
        The denotation of a constant is that individual that the assignment function g assigns it.
        """
        return g[self.v]


class Func(Expr):
    """
    Function symbol.
    f, h, ...

    @attr f: the function name
    @type f: str
    """

    def __init__(self, f):
        self.f = f

    def __repr__(self):
        return self.f

    def freevars(self):
        return {}

    def boundvars(self):
        return {}

    def subst(self, v, t):
        return self

    def denot(self, m, k, g):
        """
        The denotation of a constant is that individual that the assignment function g assigns it.
        """
        i = m.i[k][k]
        return i[self.f]


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

    def __init__(self, f, terms):
        self.f = f
        self.terms = terms

    def __repr__(self):
        return repr(self.f) + "(" + ", ".join([repr(t) for t in self.terms]) + ")"

    def freevars(self):
        return set().union(*[t.freevars() for t in self.terms])

    def boundvars(self):
        return set().union(*[t.boundvars() for t in self.terms])

    def subst(self, v, t):
        return FuncTerm(self.f, map(lambda t: t.subst(v, t), self.terms))

    def denot(self, m, k, g):
        """
        The denotation of a function symbol applied to an appropriate number of terms is that individual that the
        interpretation function f assigns to the application.
        """
        i = m.i[k][k]
        return i[self.f.f][tuple([t.denot(m, k, g) for t in self.terms])]


class Pred(Expr):
    """
    Predicate.
    P, Q, ...

    @attr p: the predicate name
    @type p: str
    """

    def __init__(self, p):
        self.p = p

    def __repr__(self):
        return self.p

    def freevars(self):
        return {}

    def boundvars(self):
        return {}

    def subst(self, v, t):
        return self

    def denot(self, m, k, g):
        """
        The denotation of a predicate is the set of ordered tuples of individuals that the interpretation function f
        assigns it.
        """
        i = m.i[k]
        return i[self.p]


depth = 0  # keep track of the level of nesting


class Formula(Expr):
    """
    Formula.
    φ, ψ, ...

    @method denot: the truth value of a formula relative to a structure m (without reference to a particular state)
    """

    def denot(self, m, k, g):
        """
        @rtype: bool
        """
        pass

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
        return self.denotG(m, "k0")

    def denotG(self, m, k):
        """
        The truth value of a formula relative to a structure M and state k (w/o reference to a particular var. ass.).
        A formula is true in a structure M and state k iff it is true in M and k under all assignments g.

        @param m: a structure
        @type m: KripkeStructure
        @attr g: an assignment function
        @type g: dict[str,str]
        @return: the truth value of self in m at k
        @rtype: bool
        """
        global depth
        # for efficiency, restrict the domain of the assignment functions to the vars that actually occur in the formula
        if m.d:
            var_occs = self.freevars().union(self.boundvars())
            gs_ = [{v: g[v] for v in g if v in var_occs} for g in m.gs[k]]
            gs = [dict(tpl) for tpl in {tuple(g.items()) for g in gs_}]  # filter out now duplicate assignment functions
        else:  # propositional structure, compute empty assignment functions
            gs = [dict()]

            if not self.freevars():  # if the formula is closed,
                # spare yourself the quantification over all assignment functions and pick an arbitrary assignment
                # (here: the first)
                return self.denot(m, k, gs[0])

        for g in m.gs:  # otherwise, check the denotation for all assignment functions
            depth += 1
            if verbose:
                print((depth * " ") + "checking g := " + repr(g) + " ...")
            witness = self.denot(m, k, g)
            if witness:
                if verbose:
                    print((depth * 2 * " ") + "✓")
                depth -= 1
            else:
                if verbose:
                    print((depth * 2 * " ") + "✗")
                    print((depth * " ") + "counter assignment: g := " + repr(g))
                depth -= 1
                return False
        return True


class Verum(Formula):
    """
    Verum.
    ⊤
    """

    def __init__(self):
        pass

    def __repr__(self):
        return "⊤"

    def freevars(self):
        return set()

    def boundvars(self):
        return set()

    def subst(self, v, t):
        return self

    def denot(self, m, k, g):
        """
        The denotation of the verum is always true.
        """
        return True


class Falsum(Formula):
    """
    Falsum.
    ⊥
    """

    def __init__(self):
        pass

    def __repr__(self):
        return "⊥"

    def freevars(self):
        return set()

    def boundvars(self):
        return set()

    def subst(self, v, t):
        return self

    def denot(self, m, k, g):
        """
        The denotation of the falsum is always false.
        """
        return False


class Prop(Formula):
    """
    Propositional variable.
    p, q, ...

    @attr p: the propositional variable
    @type p: str
    """

    def __init__(self, p):
        self.p = p

    def __repr__(self):
        return self.p

    def freevars(self):
        return set()

    def boundvars(self):
        return set()

    def subst(self, v, t):
        return self

    def denot(self, m, k, g):
        """
        The denotation of a propositional variable is the truth value the interpretation function f assigns it,
        or its downwards monotonicity closure.
        """
        return (m.i[k][self.p] or
                True in [self.denot(m, k_, g) for k_ in m.past(k) - {k}])


class Eq(Formula):
    """
    Equality between terms.
    t1 = t2

    @attr t1: the left equality term
    @type t1: Term
    @attr t2: the right equality term
    @type t2: Term
    """

    def __init__(self, t1, t2):
        self.t1 = t1
        self.t2 = t2

    def __repr__(self):
        return repr(self.t1) + " = " + repr(self.t2)

    def freevars(self):
        return self.t1.freevars() | self.t2.freevars()

    def boundvars(self):
        return self.t1.boundvars() | self.t2.boundvars()

    def subst(self, v, t):
        return Eq(self.t1.subst(v, t), self.t2.subst(v, t))

    def denot(self, m, k, g):
        """
        The denotation of a term equality t1 = t2 is true iff t1 and t2 denote the same individual.
        """
        return self.t1.denot(m, k, g) == self.t2.denot(m, k, g)


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

    def __init__(self, pred, terms):
        self.pred = pred
        self.terms = terms

    def __repr__(self):
        return repr(self.pred) + "(" + ",".join([repr(t) for t in self.terms]) + ")"

    def freevars(self):
        return set().union(*[t.freevars() for t in self.terms])

    def boundvars(self):
        return set().union(*[t.boundvars() for t in self.terms])

    def subst(self, v, t):
        return Atm(self.pred, map(lambda t: t.subst(v, t), self.terms))

    def denot(self, m, k, g):
        """
        The denotation of an atomic predication P(t1, ..., tn) is true iff the tuple of the denotation of the terms is
        an element of the interpretation of the predicate at k, or
        there is a preceding state k' <= k at which P(t1, ..., tn) is true.
        """
        return (tuple([t.denot(m, k, g) for t in self.terms]) in self.pred.denot(m, k, g) or
                True in [self.denot(m, k_, g) for k_ in m.past(k) - {k}])


class Neg(Formula):
    """
    Negation.
    ¬φ

    @attr phi: the negated formula
    @type phi: Formula
    """

    def __init__(self, phi):
        self.phi = phi

    def __repr__(self):
        if isinstance(self.phi, Eq):
            return repr(self.phi.t1) + "≠" + repr(self.phi.t2)
        return "¬" + repr(self.phi)

    def freevars(self):
        return self.phi.freevars()

    def boundvars(self):
        return self.phi.boundvars()

    def subst(self, v, t):
        return Neg(self.phi.subst(v, t))

    def denot(self, m, k, g):
        """
        The denotation of a negated formula Neg(phi) is true iff phi is false at all subsequent states k' >= k.
        """
        return True not in [self.phi.denot(m, k_, g) for k_ in m.future(k)]


class Conj(Formula):
    """
    Conjunction.
    (φ∧ψ)

    @attr phi: the left conjunct
    @type phi: Formula
    @attr psi: the right conjunct
    @type psi: Formula
    """

    def __init__(self, phi, psi):
        self.phi = phi
        self.psi = psi

    def __repr__(self):
        return "(" + repr(self.phi) + " ∧ " + repr(self.psi) + ")"

    def freevars(self):
        return self.phi.freevars() | self.psi.freevars()

    def boundvars(self):
        return self.phi.boundvars() | self.psi.boundvars()

    def subst(self, v, t):
        return Conj(self.phi.subst(v, t), self.psi.subst(v, t))

    def denot(self, m, k, g):
        """
        The denotation of a conjoined formula Con(phi,psi) is true iff phi is true and psi is true at k.
        """
        return self.phi.denot(m, k, g) and self.psi.denot(m, k, g)


class Disj(Formula):
    """
    Disjunction.
    (φ∨ψ)

    @attr phi: the left disjunct
    @type phi: Formula
    @attr psi: the right disjunct
    @type psi: Formula
    """

    def __init__(self, phi, psi):
        self.phi = phi
        self.psi = psi

    def __repr__(self):
        return "(" + repr(self.phi) + " ∨ " + repr(self.psi) + ")"

    def freevars(self):
        return self.phi.freevars() | self.psi.freevars()

    def boundvars(self):
        return self.phi.boundvars() | self.psi.boundvars()

    def subst(self, v, t):
        return Disj(self.phi.subst(v, t), self.psi.subst(v, t))

    def denot(self, m, k, g):
        """
        The denotation of a conjoined formula Disj(phi,psi) is true iff phi is true or psi is true at k.
        """
        return self.phi.denot(m, k, g) or self.psi.denot(m, k, g)


class Imp(Formula):
    """
    Implication.
    (φ→ψ)

    @attr phi: the antecedent
    @type phi: Formula
    @attr psi: the consequent
    @type psi: Formula
    """

    def __init__(self, phi, psi):
        self.phi = phi
        self.psi = psi

    def __repr__(self):
        return "(" + repr(self.phi) + " → " + repr(self.psi) + ")"

    def freevars(self):
        return self.phi.freevars() | self.psi.freevars()

    def boundvars(self):
        return self.phi.boundvars() | self.psi.boundvars()

    def subst(self, v, t):
        return Imp(self.phi.subst(v, t), self.psi.subst(v, t))

    def denot(self, m, k, g):
        """
        The denotation of an implicational formula Imp(phi,psi) is true at k iff
        at all subsequent states k' >= k, either phi is false or psi is true at k'.
        """
        return False not in [(not self.phi.denot(m, k_, g) or self.psi.denot(m, k_, g)) for k_ in m.future(k)]


class Biimp(Formula):
    """
    Biimplication.
    (φ↔ψ)

    @attr phi: the left formula
    @type phi: Formula
    @attr psi: the right formula
    @type psi: Formula
    """

    def __init__(self, phi, psi):
        self.phi = phi
        self.psi = psi

    def __repr__(self):
        return "(" + repr(self.phi) + " ↔ " + repr(self.psi) + ")"

    def freevars(self):
        return self.phi.freevars() | self.psi.freevars()

    def boundvars(self):
        return self.phi.boundvars() | self.psi.boundvars()

    def subst(self, v, t):
        return Biimp(self.phi.subst(v, t), self.psi.subst(v, t))

    def denot(self, m, k, g):
        """
        The denotation of an biimplicational formula Biimp(phi,psi) is true at k iff
        at all subsequent states k' >= k, phi and psi have the same truth value.
        """
        return False not in [(self.phi.denot(m, k_, g) == self.psi.denot(m, k_, g)) for k_ in m.future(k)]


class Exists(Formula):
    """
    Existential quantification.
    ∃xφ

    @attr v: the binding variable
    @type v: Var
    @attr phi: the formula to be quantified
    @type phi: Formula
    """

    def __init__(self, v, phi):
        self.v = v
        self.phi = phi

    def __repr__(self):
        return "∃" + repr(self.v) + (" " if isinstance(self.phi, Atm) else "") + repr(self.phi)

    def freevars(self):
        return self.phi.freevars() - {self.v.v}

    def boundvars(self):
        return self.phi.boundvars() | {self.v.v}

    def subst(self, v, t):
        if v == self.v:
            return self
        else:
            return self.phi.subst(v, t)

    def denot(self, m, k, g):
        """
        The denotation of an existentially quantified formula Exists(x, phi) is true at k iff
        phi is true under at least one x-alternative of g at k.
        """
        global depth
        depth += 1
        d_ = m.d[k]
        # quantify over the individuals in the domain
        for d in d_:
            # compute the x-alternative g'
            g_ = {**g, self.v.v: d}  # unpack g and overwrite the dictionary value for v with d
            # check whether the current indiv. d under consideration makes phi true
            if verbose:
                print(
                    (depth * 2 * " ") + "checking g" + (depth * "'") + "(" + repr(self.v) + ") := " + repr(d) + " ...")
            witness = self.phi.denot(m, k, g_)
            # if yes, we found a witness, the existential statement is true, and we can stop checking
            if witness:
                if verbose:
                    print(((depth + 1) * 2 * " ") + "✓")
                    print(
                        ((depth + 1) * 2 * " ") + "witness: g" + (depth * "'") + "(" + repr(self.v) + ") := " + repr(d))
                depth -= 1
                return True
            if not witness:
                if verbose:
                    print(((depth + 1) * 2 * " ") + "✗")
        # if no witness has been found, the existential statement is false
        depth -= 1
        return False


class Forall(Formula):
    """
    Universal quantification.
    ∀xφ

    @attr v: the binding variable
    @type v: Var
    @attr phi: the formula to be quantified
    @type phi: Formula
    """

    def __init__(self, v, phi):
        self.v = v
        self.phi = phi

    def __repr__(self):
        return "∀" + repr(self.v) + (" " if isinstance(self.phi, Atm) else "") + repr(self.phi)

    def freevars(self):
        return self.phi.freevars() - {self.v.v}

    def boundvars(self):
        return self.phi.boundvars() | {self.v.v}

    def subst(self, v, t):
        if v == self.v:
            return self
        else:
            return self.phi.subst(v, t)

    def denot(self, m, k, g):
        """
        The denotation of universally quantified formula Forall(x, phi) is true at k iff
        at all subsequent states k' >= k, phi is true under all x-alternatives of g at k.
        """
        global depth
        depth += 1

        # quantify over the subsequent states
        for k_ in m.future(k):
            d_ = m.d[k_]
            depth += 1
            # quantify over the individuals in the domain
            for d in d_:
                # compute the x-alternative g'
                g_ = {**g, self.v.v: d}  # unpack_ g and overwrite the dictionary value for v with d
                # check whether the current indiv. d under consideration makes phi true at k'
                if verbose:
                    print((depth * 2 * " ") + "checking g" + (depth * "'") + "(" + repr(self.v) + ") := " + repr(
                        d) + " ...")
                witness = self.phi.denot(m, k_, g_)
                if witness:
                    if verbose:
                        print(((depth + 1) * 2 * " ") + "✓")
                # if not, we found a counter witness, the universal statement is false, and we can stop checking
                else:
                    # if verbose:
                    #     # print(((depth+1) * 2 * " ") + "✗")
                    #     # print(((depth+1) * 2 * " ") + "counter witness: g" + (depth * "'") +
                    return False
            # if no counter witness has been found, the universal statement is true at k'
            depth -= 1

        # if no counter state has been found, the universal statement is true at k
        depth -= 1
        return True
