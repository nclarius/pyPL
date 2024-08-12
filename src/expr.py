#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Define the language and semantics of classical (standard and modal) (prepositional and first-order) logic.
"""

from structure import *

structure = __import__("structure")

from itertools import product

verbose = False


class Expr:
    """
    Well-formed expression of predicate logic.
    α, β, ...

    @method freevars: the set of free variables in the expression
    @method boundvars: the set of bound variables in the expression
    @method subst: substitution of a term for a variable in the expression
    @method denot: denotation of the expression relative to a structure s and assignment v
    """

    def __repr__(self):
        return str(self)

    def tex(self) -> str:
        """
        The expression formatted in LaTeX code.

        @return self in LaTeX code
        @rtype str
        """

    def __len__(self):
        """
        The length of the expression.

        @return the length of the expression
        @rtype int
        """
        return 1 + sum(len(subexpr) for subexpr in vars(self) if isinstance(subexpr, Expr))

    def imm_subexprs(self):
        """
        The immediate subexpressions of the expression.

        @return the immediate subexpressions of the expression
        @rtype list[Expr]
        """
        return [field for field in vars(self) if isinstance(field, Expr)]

    def subexprs(self):
        """
        The recursive subexpressions of the expression.

        @return the subexpressions of the expression
        @rtype list[Expr]
        """
        res = [self] + self.imm_subexprs()
        for subexpr in self.imm_subexprs():
            res += subexpr.subexprs()
        return res

    def propvars(self) -> set[str]:
        """
        The set of propositional variables in the expression.

        @return: the set of propositional variables in the expression
        @rtype: set[str]
        """
        return {pv for subexpr in self.subexprs() for pv in subexpr.propvars()}

    def freevars(self) -> set[str]:
        """
        The set of free variables in the expression.

        @return: the set of free variables in the expression
        @rtype: set[str]
        """
        return {fv for subexpr in self.subexprs() for fv in subexpr.freevars()}

    def boundvars(self) -> set[str]:
        """
        The set of bound variables in the expression.

        @return: the set of bound variables in the expression
        @rtype: set[str]
        """
        return {fv for subexpr in self.subexprs() for fv in subexpr.boundvars()}

    def nonlogs(self):
        """
        The set of non-logical symbols in the expression.
        
        @return the set of non-logical symbols in the expression: (constants, functions, predicates)
        @rtype: tuple[set[str]]
        """
        pass

    def redex(self):
        """
        Whether or not the expression is a redex.

        @return True iff self is a redex, and False otherwise
        @rtype: bool
        """
        return False

    def redexes(self):
        """
        The set of redexes in the subterms of the expression.

        @return the set of redexes in the subterms of self
        @rtype list[Expr]
        """
        return [r for subexpr in self.subexprs() for r in subexpr.redexes()]

    def subst(self, u, t):
        """
        Substitute all occurrences of the variable u for the term t in self.

        @param u: the variable to be substituted
        @type u: Union[IIVar, LIVar]
        @param t: the term to substitute
        @type t: Union[Term, LIVar]
        @return: the result of substituting all occurrences of the variable v for the term t in self
        @rtype Expr
        """
        return type(self)(*[subexpr.subst(u, t) for subexpr in self.subexprs()])

    def denot(self, s, v: dict[str, str] = {}, w: str = ""):
        """
        The denotation of the expression relative to a structure s and assignment v.

        @param s: the structure to evaluate the formula against
        @type s
        @param v: the assignment to evaluate the formula against
        @type v: dict[str,str]
        @param w: the possible world to evaluate the formula against
        @type w: str
        @return: the denotation of the expression relative to the structure s and assignment v
        """
        return None

    def denotV(self, s, w = ""):
        """
        The denotation of the expression relative to a structure S (abstracted over assignments).

        @param s: a structure
        @type s: Structure
        @attr w: a possible world
        @type w: str
        @return: the denotation of self in s
        @rtype: Any
        """
        return self.denot(s, {}, w)

    def denotW(self, s, v = {}):
        """
        The denotation of the expression relative to a structure S and assignment v (abstracted over possible worlds).

        @param s: a structure
        @type s: Structure
        @attr v: an assignment function
        @type v: dict[str,str]
        @return: the denotation of self in s under v
        @rtype: Any
        """
        return self.denot(s, v, "")

    def denotVW(self, s):
        """
        The denotation of a formula relative to a structure S (abstracted over assignments and possible worlds).

        @param s: a structure
        @type s: Structure
        @return: the denotation of self in s
        @rtype: bool
        """
        print("denotVW:", self.denot(s))
        return self.denot(s)

    def alpha_conv(self, convex, u):
        """
        The alpha conversion step on the expression's subexpressions w.r.t. a bound term and a new bound variable name.
        φ ≡α ψ
        """
        # todo not recursive
        converted = False
        subexprs = []
        for subexpr in self.imm_subexprs():
            if not converted and subexpr == convex:
                var_type = type(self.u)
                expr_type = type(self)
                subexpr = expr_type(var_type(u), *[subexpr.subst(self.u, u) for subexpr in self.subexprs()])
                converted = True
            subexprs.append(subexpr)
        return type(self)(*subexprs)

    def alpha_congr(self, other):
        """
        Whether the expression is beta-equivalent (beta-reduces to the same normal form) to the other.
        φ ≡α ψ

        @attr other: the other expression to check for beta equivalence
        @type other: Expr
        @return: True iff self is beta-equivalent to other
        @rytpe: bool
        """
        if self == other:
            return True
        bounaterms_self = [subexpr for subexpr in self.subexprs()
                            if any([isinstance(subexpr, LIVar) or isinstance(subexpr, Var)])]
        bounavars_other = [subexpr.u for subexpr in other.subexprs()
                            if any([isinstance(subexpr, LIVar) or isinstance(subexpr, Var)])]
        print(bounaterms_self, bounavars_other)
        if len(bounaterms_self) == len(bounavars_other):
            conversions = product(bounaterms_self, bounavars_other)
            print(conversions)
            for convex, u in conversions:
                conv = self.alpha_conv(convex, u)
                print(conv)
                if conv == other:
                    return True
        return False

    def beta_contr(self, redex=None):
        """
        The beta contraction step on the expression's subexpressions w.r.t. to a redex.
        φ ▻β ψ
        """
        # todo not recursive
        contracted = False
        subexprs = []
        for subexpr in self.subexprs():
            if not contracted and subexpr == redex:
                subexpr = subexpr.beta_contr()
                contracted = True
            subexprs.append(subexpr)
        return type(self)(*subexprs)

    def beta_reduce(self):
        """
        Beta-reduce this expression to normal form by leftmost reduction.
        φ ▻β ψ

        @return: the beta-normal form of the expression
        @rtype: Expr
        """
        # todo printout
        reduction = self
        # todo inefficient to first collect redexes, then traverse again to perform reduction
        while reduction.redxes():
            leftmost_redex = reduction.redexes()[0]
            reduction = reduction.beta_contr(leftmost_redex)
            reduction = reduction.beta_reduce()
        return reduction

    def beta_equiv(self, other):
        """
        Whether the expression is beta-equivalent (beta-reduces to the same normal form) to the other.
        φ =β ψ

        @attr other: the other expression to check for beta equivalence
        @type other: Expr
        @return: True iff self is beta-equivalent to other
        @rytpe: bool
        """
        return self.beta_reduce().alpha_congr(other.beta_reduce())


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

    def denot(self, s, v = {}, w = "") -> str:
        """
        @rtype: str
        """
        pass

    def denotVW(self, s) -> str:
        """
        @rtype: str
        """
        return self.denot(s)


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

    def denot(self, s, v = {}, w = ""):
        """
        The denotation of a variable is that individual that the assignment function v assigns it.
        """
        return v[self.u]


indiv_vars = ["x", "y", "z"]  # the individual variables of the language


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
        return "\\mathit{" + self.c + "}"

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

    def denot(self, s, v = {}, w = ""):
        """
        The denotation of a constant is that individual that the interpretation function f assigns it.
        """
        i = s.i
        if not w:
            return i[self.c]
        else:
            return i[self.c][w]


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
        return "\\mathit{" + self.f + "}"

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

    def denot(self, s, v = {}, w = "") -> dict[tuple[str], str]:
        """
        The denotation of a function symbol is the function that the interpretation function f assigns it.
        """
        i = s.i
        if not w:
            return i[self.f]
        else:
            return i[self.f][w]

    def denotVW(self, s) -> dict[tuple[str], str]:
        """
        @rtype: dict[tuple[str],str]
        """
        return self.denot(s)


class FuncTerm(Term):
    """
    Function symbol applied to an appropriate number of terms.
    f(s), h(x,t), ...

    Note that 1-place function applications have to be specified as
    Atm('f', (t1, ))
    rather than
    Atm('f', (t))
    or
    Atm('f', t1).

    @attr f: the function symbol
    @type f: Func
    @attr terms: the term tuple to apply the function symbol to
    @type terms: tuple[Term, ...]
    """

    def __init__(self, f: Func, terms: tuple[Term, ...]):
        self.f = f
        self.terms = terms

    def __str__(self):
        return str(self.f) + "(" + ",".join([str(t) for t in self.terms]) + ")"

    def tex(self):
        return self.f.tex() + "(" + ",".join([t.tex() for t in self.terms]) + ")"

    def __eq__(self, other):
        return isinstance(other, FuncTerm) and self.f == other.f and self.terms == other.terms

    def __len__(self):
        return len(self.f) + sum([len(t) for t in self.terms])

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

    def denot(self, s, v = {}, w = "") -> str:
        """
        The denotation of a function symbol applied to an appropriate number of terms is that individual that the
        interpretation function f assigns to the application.
        """
        i = s.i
        if not w:
            return i[self.f.f][tuple([t.denot(s, v, w) for t in self.terms])]
        else:
            return i[self.f.f][w][tuple([t.denot(s, v, w) for t in self.terms])]


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
        return "\\mathit{" + self.p + "}"

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

    def denot(self, s, v = {}, w = "") -> set[tuple[str]]:
        """
        The denotation of a predicate is the set of ordered tuples of individuals that the interpretation function f
        assigns it.
        """
        i = s.i
        if not w:
            return i[self.p]
        else:
            return i[self.p][w]

    def denotVW(self, s) -> set[tuple[str]]:
        """
        @rtype: set[tuple[str]]
        """
        return self.denot(s)


depth = 0  # keep track of the level of nesting


# todo depth has to be reset manually after each call of `denot`


class Formula(Expr):
    """
    Formula.
    φ, ψ, ...

    @method denotV: the truth value of a formula relative to a structure s (without reference to a particular
    assignment)
    """

    def atom(self):
        return isinstance(self, Verum) or isinstance(self, Falsum) or \
               isinstance(self, Prop) or isinstance(self, Eq) or isinstance(self, Atm)

    def literal(self):
        return self.atom() or isinstance(self, Neg) and self.phi.atom()

    def subst(self, u, t):
        """
        @rtype: Formula
        """
        pass

    def denot(self, s, v = {}, w = "") -> bool:
        """
        @rtype: bool
        """
        pass

    def denotV(self, s, w: str = "") -> bool:
        """
        A formula is true in a structure S iff it is true in S under all assignments v of variables occurring free in the formula.

        @rtype: bool
        """
        if "propositional" in s.mode():
            return self.denot(s, None, w)

        global depth

        # all variable assignment functions for the free variables of the formula
        vs = [{v: a
               for (v, a) in zip(self.freevars(), distr)}  # for each pair of variable and element from D
              for distr in list(product(list(s.d), repeat=len(self.freevars())))]  # for each possible |vars| long combination of elements from D

        for v in vs:  # check the denotation for all assignment functions
            depth += 1
            if verbose:
                print((depth * " ") + "checking v := " + str(v) + " ...")
            witness = self.denot(s, v, w)
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

    def denotW(self, s, v: dict[str, str] = {}) -> bool:
        """
        A formula is true in a structure S iff it is true in S and v in all possible worlds w.

        @rtype: bool
        """
        global depth

        for w in s.w:
            depth += 1
            if verbose:
                print((depth * "  ") + "checking w := " + str(w) + " ...")
            witness = self.denot(s, v, w)
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

    def denotVW(self, s) -> bool:
        """
        In CL:
        A formula is true in a structure S iff it is true in S and v under all assignments v and all possible worlds w.

        In IL:
        A formula is true in a structure S iff it is true in the root state k0.

        @rtype: bool
        """
        # todo doesn't work for modal structures with varying domain yet (due different structure of assignment
        #  functions)
        global depth

        if "classical" in s.mode():
            for w in s.w:
                depth += 1
                if verbose:
                    print((depth * " ") + "checking w := " + str(w) + " ...")
                witness = self.denotV(s, w)
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

        else:
            return self.denotV(s, "k0")

    def tableau_pos(self, mode):
        """
        Tableau rules for the unnegated formula.
        @return: A list of triples of
                 - the rule name
                 - the type of rule (α/β/γ/δ/μ/nu)
                 - the arguments of the rule: the formulas to extend and, if applicable, parameter/signature information
        @rtype list[tuple[str,str,Any]]
        """
        pass

    def tableau_neg(self, mode):
        """
        Tableau rules for the negated formula.
        @return: A list of triples of
                 - the rule name
                 - the type of rule (α/β/γ/δ/μ/nu)
                 - the arguments of the rule: the formulas to extend and, if applicable, parameter/signature information
        @rtype list[tuple[str,str,Any]]
        """
        pass

    def tableau_contradiction_pos(self, other, sign):
        """
        The cases where the positive formula leads to a contradiction in the branch.

        - φ
          ⋮
        + φ

        @param other: the other formula
        @type other: Formula
        @param sign: the sign of the other formula
        @type sign: bool
        @return True iff self contradicts other
        @rtype bool
        """
        return self == other and not sign

    def tableau_contradiction_neg(self, other, sign):
        """
        The cases where the negative formula leads to a contradiction in the branch.

        + φ
          ⋮
        - φ

        @param other: the other formula
        @type other: Formula
        @param sign: the sign of the other formula
        @type sign: bool
        @return True iff self contradicts other
        @rtype bool
        """
        return self == other and sign


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

    def denot(self, s, v = {}, w = ""):
        """
        The denotation of a propositional variable is the truth value the valuation function V assigns it.
        """
        if "classical" in s.mode():
            v = s.v
            if not w:
                return v[self.p]
            else:
                return v[self.p][w]
        else:
            return (s.v[self.p][w] or
                    True in [self.denot(s, v, w_) for w_ in s.past(w) - {w}])

    def tableau_pos(self, mode):
        """
        IL:
          σ + p
           |
        σ.n + p
        where σ.n is old
        """
        if mode["classical"]:
            return dict()
        else:
            return {"+p": ("ν", [(True, self)],)}

    def tableau_neg(self, mode):
        return dict()


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
    @type terms: tuple[Term, ...]
    """

    def __init__(self, pred: Pred, terms: tuple[Term, ...]):
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

    def denot(self, s, v = {}, w = ""):
        """
        The denotation of an atomic predication P(t1, ..., tn) is true iff the tuple of the denotation of the terms is
        an element of the interpretation of the predicate.
        """
        if "classical" in s.mode():
            return tuple([t.denot(s, v, w) for t in self.terms]) in self.pred.denot(s, v, w)
        else:
            return (tuple([t.denot(s, v, w) for t in self.terms]) in self.pred.denot(s, v, w) or
                    True in [self.denot(s, v, w_) for w_ in s.past(w) - {w}])

    def tableau_pos(self, mode):
        """
        IL:
          σ + P(...)
              |
        σ.n + P(...)
        where σ.n is old
        """
        if mode["classical"]:
            return dict()
        else:
            return {"+P": ("μ", [(True, self)])}

    def tableau_neg(self, mode):
        return dict()


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
        return "(" + str(self.t1) + " = " + str(self.t2) + ")"

    def tex(self):
        return "(" + self.t1.tex() + " = " + self.t2.tex() + ")"

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

    def denot(self, s, v = {}, w = ""):
        """
        The denotation of a term equality t1 = t2 is true iff t1 and t2 denote the same individual.
        """
        return self.t1.denot(s, v, w) == self.t2.denot(s, v, w)

    def tableau_pos(self, mode):
        return dict()

    def tableau_neg(self, mode):
        return dict()

    def tableau_contradiction_pos(self, other, _):
        """
        t1 = t2
        """
        # todo wrong
        return str(self.t1) != str(self.t2)  # todo IL

    def tableau_contradiction_neg(self, other, _):
        """
        t ≠ t
        """
        return str(self.t1) == str(self.t2)  # todo IL


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
        return "\\top"

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

    def denot(self, s, v = {}, w = ""):
        """
        The denotation of the verum is always true.
        """
        return True

    def tableau_pos(self, mode):
        return dict()

    def tableau_neg(self, mode):
        return dict()

    def tableau_contradiction_pos(self, other, sign):
        """
        An unnegated verum is never contradictory.
        """
        return False

    def tableau_contradiction_neg(self, other, sign):
        """
        A negated verum is always contradictory.
        """
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
        return "\\bot"

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

    def denot(self, s, v = {}, w = ""):
        """
        The denotation of the falsum is always false.
        """
        return False

    def tableau_pos(self, mode):
        return dict()

    def tableau_neg(self, mode):
        return dict()

    def tableau_contradiction_pos(self, other, sign):
        """
        An unnegated falsum is always contradictory.
        """
        return True

    def tableau_contradiction_neg(self, other, sign):
        """
        A negated falsum is never contradictory.
        """
        return False


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
            return "(" + str(self.phi.t1) + "≠" + str(self.phi.t2) + ")"
        elif isinstance(self.phi, Neg) and isinstance(self.phi,phi, Eq):
            return "¬¬" + str(self.phi.phi)
        if isinstance(self.phi, Inf): # double negated equality
            return "⊬"
        return "¬" + str(self.phi)

    def tex(self):
        if isinstance(self.phi, Eq):
            return "(" + self.phi.t1.tex() + " \\neq " + self.phi.t2.tex() + ")"
        elif isinstance(self.phi, Neg) and isinstance(self.phi,phi, Eq):
            return "\\neg \\neg" + self.phi.phi.tex()
        if isinstance(self.phi, Inf):
            return "\\nvdash"
        return "\\neg " + self.phi.tex()

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

    def denot(self, s, v = {}, w = ""):
        """
        In CL, the denotation of a negated formula Neg(phi) is true iff phi is false.

        In IL, the denotation of a negated formula Neg(phi) is true iff phi is false at all subsequent states k' >= k.

        """
        if "classical" in s.mode():  # CL
            return not self.phi.denot(s, v, w)
        else:  # IL
            return True not in [self.phi.denot(s, v, w_) for w_ in s.future(w)]

    def tableau_pos(self, mode):
        """
        CL:     IL:
        + ¬φ    σ + ¬φ
                  σ.n
         |         |
        - φ    σ.n - φ
        """
        if mode["classical"]:
            return {"+¬": ("α", [(False, self.phi)])}
        else:
            return {"+¬": ("ν", [(False, self.phi)])}

    def tableau_neg(self, mode):
        """
        CL:    IL:
        - ¬φ    σ - ¬φ
          |        |
        + φ     σ.n + φ
               where σ.n is new
        """
        if mode["classical"]:
            return {"-¬": ("α", [(True, self.phi)])}
        else:
            return {"-¬": ("μ", [(True, self.phi)])}

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

    def denot(self, s, v = {}, w = ""):
        """
        The denotation of a conjoined formula Con(phi,psi) is true iff phi is true and psi is true.
        """
        return self.phi.denot(s, v, w) and self.psi.denot(s, v, w)

    def tableau_pos(self, mode):
        """
        + (φ∧ψ)
            |
        +   φ
        +   ψ
        """
        return {"+∧": ("α", [(True, self.phi),
                             (True, self.psi)])}

    def tableau_neg(self, mode):
        """
          - (φ∧ψ)
            /  \
         - φ  - ψ
        """
        return {"-∧": ("β", [(False, self.phi), (False, self.psi)])}


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

    def denot(self, s, v = {}, w = ""):
        """
        The denotation of a conjoined formula Disj(phi,psi) is true iff phi is true or psi is true.
        """
        return self.phi.denot(s, v, w) or self.psi.denot(s, v, w)

    def tableau_pos(self, mode):
        """
         + (φ∨ψ)
           /  \
        + φ  + ψ
        """
        return {"+∨": ("β", [(True, self.phi), (True, self.psi)])}

    def tableau_neg(self, mode):
        """
        - (φ∨ψ)
            |
        -   φ
        -   ψ
        """
        return {"-∨": ("α", [(False, self.phi),
                             (False, self.psi)])}


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

    def denot(self, s, v = {}, w = ""):
        """
        In CL, the denotation of an implicational formula Imp(phi,psi) is true iff phi is false or psi is true.

        In IL, the denotation of an implicational formula Imp(phi,psi) is true at k iff
        at all subsequent states k' >= k, either phi is false or psi is true at k'.
        """
        if "classical" in s.mode():  # CL
            return not self.phi.denot(s, v, w) or self.psi.denot(s, v, w)
        else:  # IL
            return False not in [(not self.phi.denot(s, v, w_) or self.psi.denot(s, v, w_)) for w_ in s.future(w)]

    def tableau_pos(self, mode):
        """
        CL:      IL:
          + (φ→ψ)            σ + (φ→ψ)
           /  \                 σ.n
        - φ  + ψ             /      \
                      σ.n - φ  σ.n + ψ
        """
        if mode["classical"]:
            return {"+→": ("β", [(False, self.phi), (True, self.psi)])}
        else:
            return {"+→": ("χ", [(False, self.phi), (True, self.psi)])}

    def tableau_neg(self, mode):
        """
        CL:      IL:
        - (φ→ψ)   σ - (φ→ψ)
            |        |
           + φ      σ.n
           - ψ    σ.n + φ
                  σ.n - ψ
        """
        if mode["classical"]:
            return {"-→": ("α", [(True, self.phi),
                                 (False, self.psi)])}
        else:
            return {"-→": ("μ", [(True, self.phi),
                                 (False, self.psi)])}


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

    def denot(self, s, v = {}, w = ""):
        """
        In CL, the denotation of an biimplicational formula Biimp(phi,psi) is true iff
        phi and psi have the same truth value.

        In IL, the denotation of an biimplicational formula Biimp(phi,psi) is true at k iff
        at all subsequent states k' >= k, phi and psi have the same truth value.
        """
        if "classical" in s.mode():  # CL
            return self.phi.denot(s, v, w) == self.psi.denot(s, v, w)
        else:  # IL
            return False not in [(self.phi.denot(s, v, w_) == self.psi.denot(s, v, w_)) for w_ in s.future(w)]

    def tableau_pos(self, mode):
        """
        CL:        IL:
         + (φ↔ψ)         σ + (φ→ψ)
           /  \            σ.n
        + φ  - φ        /       \
        + ψ  - ψ   σ.n + φ   σ.n - φ
                   σ.n + ψ   σ.n - ψ
        """
        if mode["classical"]:
            return {"+↔": ("β", [(True, self.phi), (False, self.phi),
                                (True, self.psi), (False, self.psi)])}
        else:
            return {"+↔": ("χ", [(True, self.phi), (False, self.phi),
                                (True, self.psi), (False, self.psi)])}

    def tableau_neg(self, mode):
        """
        CL:          IL:
         - (φ↔ψ)         σ - (φ↔ψ)
           /  \           /   \
        + φ  - φ             σ.n
         |    |      σ.n + φ   σ.n - φ
        - ψ  + ψ     σ.n - ψ   σ.n ψ
        """
        if mode["classical"]:
            return {"-↔": ("β", [(True, self.phi), (False, self.phi),
                                 (False, self.psi), (True, self.psi)])}
        else:
            return {"-↔": ("ξ", [(True, self.phi), (False, self.phi),
                                 (False, self.psi), (True, self.psi)])}


class Xor(Formula):
    """
    Exclusive or..
    (φ⊕ψ)

    @attr phi: the left formula
    @type phi: Formula
    @attr psi: the right formula
    @type psi: Formula
    """

    def __init__(self, phi: Formula, psi: Formula):
        self.phi = phi
        self.psi = psi

    def __str__(self):
        return "(" + str(self.phi) + " ⊕  " + str(self.psi) + ")"

    def tex(self):
        return "(" + self.phi.tex() + " \\oplus " + self.psi.tex() + ")"

    def __eq__(self, other):
        return isinstance(other, Xor) and self.phi == other.phi and self.psi == other.psi

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

    def denot(self, s, v = {}, w = ""):
        """
        In CL, the denotation of an biimplicational formula Biimp(phi,psi) is true iff
        phi and psi have the same truth value.

        In IL, the denotation of an biimplicational formula Biimp(phi,psi) is true at k iff
        at all subsequent states k' >= k, phi and psi have the same truth value.
        """
        if "classical" in s.mode():  # CL
            return self.phi.denot(s, v, w) != self.psi.denot(s, v, w)
        else:  # IL
            return False not in [(self.phi.denot(s, v, w_) != self.psi.denot(s, v, w_)) for w_ in s.future(w)]

    def tableau_pos(self, mode):
        """
        CL:        IL:
        + (φ⊕ψ)          σ  +(φ⊕ψ)
           /  \            /   \
        + φ  - φ            σ.n
         |    |      σ.n + φ   σ.n - φ
        - ψ  + ψ     σ.n - ψ   σ.n ψ
        """
        if mode["classical"]:
            return {"+⊕": ("β", [(True, self.phi), (False, self.phi),
                                 (False, self.psi), (True, self.psi)])}
        else:
            return {"+⊕": ("χ", [(True, self.phi), (False, self.phi),
                                 (False, self.psi), (True, self.psi)])}

    def tableau_neg(self, mode):
        """
        CL:        IL:
         - (φ⊕ψ)        σ - (φ⊕ψ)
           /  \            σ.n
        + φ  - φ        /       \
        + ψ  - ψ   σ.n + φ   σ.n - φ
                   σ.n + ψ   σ.n - ψ
        """
        if mode["classical"]:
            return {"+⊕": ("β", [(True, self.phi), (False, self.phi),
                                 (True, self.psi), (False, self.psi)])}
        else:
            return {"+⊕s": ("χ", [(True, self.phi), (False, self.phi),
                                  (True, self.psi), (False, self.psi)])}


class Exists(Formula):
    """
    Existential quantification.
    ∃uφ

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
        return 1 + len(self.phi)

    def propvars(self):
        return set()

    def freevars(self):
        return self.phi.freevars() - {self.u.u}

    def boundvars(self):
        return self.phi.boundvars() | {self.u.u}

    def nonlogs(self):
        return self.phi.nonlogs()

    def subst(self, u, t):
        if u.u == self.u.u:
            return self
        elif not (self.u.u in t.freevars() and u.u in self.phi.freevars()):
            return Exists(self.u, self.phi.subst(u, t))
        else:
            varnames = ["x", "y", "z"] + ["x" + str(i) for i in range(100)]
            u_ = [var for var in varnames if var not in self.phi.freevars() | t.freevars()][0]
            return Exists(Var(u_), self.phi.subst(self.u, Var(u_)).subst(u, t))

    def denot(self, s, v = {}, w = ""):
        """
        The denotation of an existentially quantified formula Exists(u, phi) is true
        iff phi is true under at least one u-variant of v.
        """
        global verbose
        d = s.d
        if "vardomains" in s.mode() or "intuitionstic" in s.mode():
            d = s.d[w]

        # short version
        if not verbose:
            return any([self.phi.denot(s, v | {self.u.u: a}, w) for a in d])

        # long version
        global depth
        depth += 1

        # iterate through the individuals in the domain
        for a in sorted(d):

            # compute the u-variant v' of v
            v_ = v  # v' is just like v, except...
            v_[self.u.u] = a  # ... the value for the variable u is now the new individual a

            # check whether the current u-variant under consideration makes phi true
            print((depth * 2 * " ") + "checking v" + (depth * "'") + ": " + str(self.u) + " ↦ " + str(a) + " ...")
            witness = self.phi.denot(s, v_, w)

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

    def tableau_pos(self, mode):
        """
        +  ∃vφ
            |
        + φ[v/c]
        where c is new
        """
        if mode["validity"]:
            return {"+∃": ("δ", [(True, self.phi, self.u)])}
        else:
            if mode["linguistic"]:
                return {"+∃": ("ε", [(True, self.phi, self.u)])}
            else:
                return {"+∃": ("θ", [(True, self.phi, self.u)])}

    def tableau_neg(self, mode):
        """
        -  ∃vφ
            |
        - φ[v/c]
        where c is arbitrary
        """
        if mode["validity"]:
            return {"-∃": ("γ", [(False, self.phi, self.u)])}
        else:
            if mode["classical"]:
                return {"-∃": ("η", [(False, self.phi, self.u)])}
            else:
                return {"-∃": ("ω", [(False, self.phi, self.u)])}


class Forall(Formula):
    """
    Universal quantification.
    ∀uφ

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
        return 1 + len(self.phi)

    def propvars(self):
        return set()

    def freevars(self):
        return self.phi.freevars() - {self.u.u}

    def boundvars(self):
        return self.phi.boundvars() | {self.u.u}

    def nonlogs(self):
        return self.phi.nonlogs()

    def subst(self, u, t):
        if u.u == self.u.u:
            return self
        elif not (self.u.u in t.freevars() and u.u in self.phi.freevars()):
            return Forall(self.u, self.phi.subst(u, t))
        else:
            varnames = ["x", "y", "z"] + ["x" + str(i) for i in range(100)]
            u_ = [var for var in varnames if var not in self.phi.freevars() | t.freevars()][0]
            return Forall(Var(u_), self.phi.subst(self.u, Var(u_)).subst(u, t))

    def denot(self, s, v = {}, w = ""):
        """
        In CL, the denotation of universally quantified formula Forall(u, phi) is true iff
        phi is true under all u-variants of v.

        In IL, the denotation of universally quantified formula Forall(u, phi) is true at k iff
        at all subsequent states k' >= k, phi is true under all u-variants v' of v at k'.
        """
        global verbose
        global depth
        depth += 1
        d = s.d
        if "vardomains" in s.mode():
            d = s.d[w]

        if "classical" in s.mode():  # CL

            # short version
            if not verbose:
                return all([self.phi.denot(s, v | {self.u.u: a}, w) for a in d])

            # long version

            # iterate through the individuals in the domain
            for a in sorted(d):

                # compute the u-variant v' of v
                g_ = v  # v' is just like v, except...
                g_[self.u.u] = a  # ... the value for the variable u is now the new individual a

                # check whether the current u-variant under consideration makes phi true
                print((depth * 2 * " ") + "checking v" + (depth * "'") + ": " + str(self.u) + "  ↦ " + str(a) + " ...")
                witness = self.phi.denot(s, g_, w)

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
                return all([all([self.phi.denot(s, v | {self.u.u: a}, w_) for a in s.d[w_]]) for w_ in s.future(w)])

            # long version

            # quantify over the subsequent states
            for w_ in s.future(w):
                d = s.d[w_]
                depth += 1

                # iterate through the individuals in the domain of the future state
                for a in d:
                    # compute the u-variant v' of v
                    v_ = v  # v' is just like v, except...
                    v_[self.u.u] = a  # ... the value for the variable u is now the new individual d

                    # check whether the current indiv. a under consideration makes phi true at k'
                    print((depth * 2 * " ") + "checking v" + (depth * "'") + ": " + str(self.u) + " ↦ " + str(
                            a) + " ...")
                    witness = self.phi.denot(s, v, w_)

                    # if yes, everything is fine until now, we do nothing and go check the next one (continue)
                    if witness:
                        print(((depth + 1) * 2 * " ") + "✓")

                    # if not, we found a counter witness, the universal statement is false, and we can stop checking
                    else:
                        print(((depth + 1) * 2 * " ") + "✗")
                        print(((depth + 1) * 2 * " ") + "counter witness: k' = " + str(w_) + ", " +
                              "v" + (depth * "'") + ": " + str(self.u) + " ↦ " + str(a))
                        return False

                # if no counter witness has been found, the universal statement is true at k'
                depth -= 1

            # if no counter state has been found, the universal statement is true at k
            depth -= 1
            return True

    def tableau_pos(self, mode):
        """
        CL:*         IL:**
        +  ∀vφ       σ   +  ∀vφ
            |                |
        + φ[v/c]     σ.n + φ[v/c]
        * where c is arbitrary
        ** where c is arbitrary and σ.n is old
        """
        if mode["validity"]:
            if mode["classical"]:
                return {"+∀": ("γ", [(True, self.phi, self.u)])}
            else:
                return {"+∀": ("ο", [(True, self.phi, self.u)])}
        else:
            if mode["classical"]:
                return {"+∀": ("η", [(True, self.phi, self.u)])}
            else:
                return {"+∀": ("ω", [(True, self.phi, self.u)])}

    def tableau_neg(self, mode):
        """
        CL:*       IL:**
        -  ∀vφ      σ   - ∀vφ
            |              |
        - φ[x/c]    σ.n - φ[x/c]
        * where c is new
        ** where c is new and σ.n is new
        """
        if mode["validity"]:
            if mode["classical"]:
                return {"-∀": ("δ", [(False, self.phi, self.u)])}
            else:
                return {"-∀": ("υ", [(False, self.phi, self.u)])}
        else:
            if mode["linguistic"]:
                return {"-∀": ("ε", [(False, self.phi, self.u)])}
            else:
                return {"-∀": ("θ", [(False, self.phi, self.u)])}


class Most(Formula):
    """
    "most" quantification.
    most u(φ,ψ)

    @attr u: the binding variable
    @type u: Var
    @attr phi: the restriction to be compared
    @type phi: Formula
    @attr chi: the nucleus to be compared against
    @type chi: Formula
    """

    def __init__(self, u: Var, phi: Formula, chi: Formula):
        self.u = u
        self.phi = phi
        self.chi = chi

    def __str__(self):
        return "most " + str(self.u) + "(" + ",".join([str(self.phi), str(self.chi)]) + ")"

    def tex(self):
        return "\\mathrm{most}\ " + self.u.tex() + "(" + ",".join([self.phi.tex(), self.chi.tex()]) + ")"

    def __eq__(self, other):
        return isinstance(other, Most) and self.u == other.u and \
               self.phi == other.phi and self.chi == other.chi

    def __len__(self):
        return 1 + len(self.phi) + len(self.chi)

    def propvars(self):
        return set()

    def freevars(self):
        return self.phi.freevars() | self.chi.freevars() - {self.u.u}

    def boundvars(self):
        return self.phi.boundvars() | self.chi.boundvars() | {self.u.u}

    def nonlogs(self):
        return tuple([self.phi.nonlogs()[i] | self.chi.nonlogs()[i] for i in range(3)])

    def subst(self, u, t):
        if u.u == self.u.u:
            return self
        elif not (self.u.u in t.freevars() and u.u in self.phi.freevars()):
            return Most(self.u, self.phi.subst(u, t), self.chi.subst(u, t))
        else:
            varnames = ["x", "y", "z"] + ["x" + str(i) for i in range(100)]
            u_ = [var for var in varnames if var not in self.phi.freevars() | t.freevars()][0]
            return Most(Var(u_), self.phi.subst(self.u, Var(u_)).subst(u, t), self.chi.subst(u, Var(u_)).subst(u, t))

    def denot(self, s, v = {}, w = ""):
        """
        The denotation of most u(phi, chi) is true iff
        |phi ∩ chi| > |phi - chi|.
        """
        return len({d for d in s.d if self.phi.denot(s, v | {self.u.u: d}, w)} &
                   {d for d in s.d if self.chi.denot(s, v | {self.u.u: d}, w)}) \
               > \
               len({d for d in s.d if self.phi.denot(s, v | {self.u.u: d}, w)} -
                   {d for d in s.d if self.chi.denot(s, v | {self.u.u: d}, w)})


class More(Formula):
    """
    "more than" quantification.
    more u(φ,ψ,χ)

    @attr u: the binding variable
    @type u: Var
    @attr phi: the first restriction to be compared
    @type phi: Formula
    @attr psi: the second restriction to be compared
    @type psi: Formula
    @attr chi: the nucleus to be compared against
    @type chi: Formula
    """

    def __init__(self, u: Var, phi: Formula, psi: Formula, chi: Formula):
        self.u = u
        self.phi = phi
        self.psi = psi
        self.chi = chi

    def __str__(self):
        return "more " + str(self.u) + "(" + ",".join([str(self.phi), str(self.psi), str(self.chi)]) + ")"

    def tex(self):
        return "\\mathrm{more}\ " + self.u.tex() + "(" + ",".join(
                [self.phi.tex(), self.psi.tex(), self.chi.tex()]) + ")"

    def __eq__(self, other):
        return isinstance(other, More) and self.u == other.u and \
               self.phi == other.phi and self.psi == other.psi and self.chi == other.chi

    def __len__(self):
        return 1 + len(self.phi) + len(self.psi) + len(self.chi)

    def propvars(self):
        return set()

    def freevars(self):
        return self.phi.freevars() | self.psi.freevars() | self.chi.freevars() - {self.u.u}

    def boundvars(self):
        return self.phi.boundvars() | self.psi.boundvars() | self.chi.boundvars() | {self.u.u}

    def nonlogs(self):
        return tuple([self.phi.nonlogs()[i] | self.psi.nonlogs()[i] | self.chi.nonlogs()[i] for i in range(3)])

    def subst(self, u, t):
        if u.u == self.u.u:
            return self
        elif not (self.u.u in t.freevars() and u.u in self.phi.freevars()):
            return More(self.u, self.phi.subst(u, t), self.psi.subst(u, t), self.chi.subst(u, t))
        else:
            varnames = ["x", "y", "z"] + ["x" + str(i) for i in range(100)]
            u_ = [var for var in varnames if var not in self.phi.freevars() | t.freevars()][0]
            return More(Var(u_), self.phi.subst(self.u, Var(u_)).subst(u, t), self.psi.subst(u, Var(u_)).subst(u, t),
                        self.chi.subst(u, Var(u_)).subst(u, t))

    def denot(self, s, v = {}, w = ""):
        """
        The denotation of morethan u(phi, psi, chi) is true iff
        |phi ∩ chi| > |psi ∩ chi|
        """
        return len({d for d in s.d if self.phi.denot(s, v | {self.u.u: d}, w)} &
                   {d for d in s.d if self.chi.denot(s, v | {self.u.u: d}, w)}) \
               > \
               len({d for d in s.d if self.psi.denot(s, v | {self.u.u: d}, w)} &
                   {d for d in s.d if self.chi.denot(s, v | {self.u.u: d}, w)})


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

    def denot(self, s, v, w):
        """
        In CL, the denotation of a possiblity formula is true iff
        phi is true at at least one world accessible from w.

        @param s: the structure to evaluate the formula in
        @type s
        @param v: the assignment function to evaluate the formula in
        @type v: dict[str,str]
        @param w: the world to evaluate the formula in
        @type w: str
        @return: the denotation of Poss(phi)
        """
        if "intuitionistic" in s.mode():
            return  # not implemented

        # all possible worlds w' which are accessible from w
        neighbors = [w_ for w_ in s.w if (w, w_) in s.r]

        # short version
        if not verbose:
            return any([self.phi.denot(s, v, w_) for w_ in neighbors])

        # long version
        global depth
        depth += 1

        # iterate through ws neighbors w'
        for w_ in neighbors:

            # check whether phi is true in w
            print((depth * "  ") + "checking w" + (depth * "'") + " := " + str(w_) + " ...")
            witness = self.phi.denot(s, v, w_)

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

    def tableau_pos(self, mode):
        """
        Rule K:
        σ   + ◇φ
              |
        σ.n + φ
        where σ.n is new
        """
        if mode["validity"]:
            rules = {"+◇": ("μ", [(True, self.phi)])}
        else:
            rules = {"+◇": ("κ", [(True, self.phi)])}
        return rules

    def tableau_neg(self, mode):
        """
        Rule K:   Rule D:   Rule T:   Rule B:   Rule 4:   Rule 4r:
         σ + ◇φ    σ + ◇φ     σ + ◇φ     σ.n + ◇φ    σ + ◇φ    σ.n + ◇φ
           |         |         |         |         |          |
        σ.n + φ    σ + ◻φ     σ  + φ      σ + φ     σ.n + ◇φ    σ + ◇φ
        where σ and σ.n are old
        """
        if mode["validity"]:
            rules = {"-◇": ("ν", [(False, self.phi)])}
        else:
            rules = {"-◇": ("λ", [(False, self.phi)])}
        if mode["frame"] in ["D"]:
            rules["-D"] = ("α", [(False, Nec(self.phi))])
        if mode["frame"] in ["T", "B", "S4", "S5"]:
            rules["-T"] = ("α", [(False, self.phi)])
        if mode["frame"] in ["B"]:
            rules["-B"] = ("π", [(False, self.phi)])
        if mode["frame"] in ["K4", "S4", "S5"]:
            rules["-4"] = ("ν", [(False, Poss(self.phi))])
        if mode["frame"] in ["S5"]:
            rules["-4r"] = ("π", [(False, Poss(self.phi))])
        return rules


class Nec(Formula):
    """
    Necessity.
    □φ

    @attr phi: the formula to apply the modal operator to
    @type phi: Formula
    """

    def __init__(self, phi: Formula):
        self.phi = phi

    def __str__(self):
        return "□" + str(self.phi)

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
        return Nec(self.phi.subst(u, t))

    def denot(self, s, v, w):
        """
        In CL, the denotation of a necessity formula is true iff
        phi is true at all worlds accessible from w.

        @param s: the structure to evaluate the formula in
        @type s
        @param w: the world to evaluate the formula in
        @type w: str
        @param v: the assignment function to evaluate the formula in
        @type v: dict[str,str]
        """
        if "intuitionistic" in s.mode():
            return  # not implemented

        # all possible worlds w' which are accessible from w
        neighbors = [w_ for w_ in s.w if (w, w_) in s.r]

        # short version
        if not verbose:
            return all([self.phi.denot(s, v, w_) for w_ in neighbors])

        # long version
        global depth
        depth += 1

        # iterate through ws neighbors w'
        for w_ in neighbors:

            # check whether phi is true in w
            print((depth * "  ") + "checking w" + (depth * "'") + " := " + str(w_) + " ...")
            witness = self.phi.denot(s, v, w_)

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

    def tableau_pos(self, mode):
        """
        Rule K:   Rule D:   Rule T:   Rule B:   Rule 4:   Rule 4r:
        σ + ◻φ      σ + ◻φ      σ + ◻φ      σ.n + ◻φ     σ + ◻φ     σ.n + ◻φ
          |         |         |          |         |        |
        σ.n + φ     σ + ◇φ       σ + φ       σ - φ     σ.n + ◻φ     σ + ◻φ
        where σ.n is old
        """
        if mode["validity"]:
            rules = {"+◻": ("ν", [(True, self.phi)])}
        else:
            rules = {"+◻": ("λ", [(True, self.phi)])}
        if mode["frame"] in ["D"]:
            rules["+D"] = ("α", [(True, Poss(self.phi))])
        if mode["frame"] in ["T", "B", "S4", "S5"]:
            rules["+T"] = ("α", [(True, self.phi)])
        if mode["frame"] in ["B"]:
            rules["+B"] = ("π", [(True, self.phi)])
        if mode["frame"] in ["K4", "S4", "S5"]:
            rules["+4"] = ("ν", [(True, self)])
        if mode["frame"] in ["S5"]:
            rules["+4r"] = ("π", [(True, Nec(self.phi))])
        return rules

    def tableau_neg(self, mode):
        """
        Rule K:
         σ - ◻φ
           |
        σ.n - φ
        where σ.n is new
        """
        if mode["validity"]:
            rules = {"-◻": ("μ", [(False, self.phi)])}
        else:
            rules = {"-◻": ("κ", [(False, self.phi)])}
        return rules


class Int(Expr):
    """
    The intension of an expression.
    ^φ

    @attr phi: the formula to compute the intension for
    @type phi: Formula
    """

    def __init__(self, phi: Expr):
        self.phi = phi

    def __str__(self):
        return "^" + str(self.phi)

    def tex(self):
        return "{}^{\\wedge} " + " " + self.phi.tex()

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
        return Int(self.phi.subst(u, t))

    def denot(self, s, v = {}, w = ""):
        """
        The denotation of the intension of an expression is
        the function from possible worlds to the extension of the expression in that world.

        @param s: the structure to evaluate the formula in
        @type s
        @param w: the world to evaluate the formula in
        @type w: str
        @param v: the assignment function to evaluate the formula in
        @type v: dict[str,str]
        """
        return frozenset({w_: self.phi.denot(s, v, w_) for w_ in s.w}.items())


class Ext(Expr):
    """
    The extension of an intensional expression.
    ⱽφ

    @attr phi: the formula to compute the extension for
    @type phi: Formula
    """

    def __init__(self, phi: Expr):
        self.phi = phi

    def __str__(self):
        return "ⱽ" + str(self.phi)

    def tex(self):
        return "{}^{\\vee} " + " " + self.phi.tex()

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
        return Int(self.phi.subst(u, t))

    def denot(self, s, v = {}, w = ""):
        """
        The denotation of the extension of an intensional expression is
        the intension function applied to the possible world.

        @param s: the structure to evaluate the formula in
        @type s
        @param w: the world to evaluate the formula in
        @type w: str
        @param v: the assignment function to evaluate the formula in
        @type v: dict[str,str]
        """
        return dict(self.phi.denot(s, v, w))[w]


class Lexpr(Expr):
    """
    Lambda terms.
    """
    pass


class LIVar(Lexpr):
    """
    Lambda variable.
    x, y, z, x1, x2, ...

    @attr u: the variable name
    @type u: str
    """

    def __init__(self, u: str):
        self.u = u

    def __str__(self):
        return self.u

    def tex(self):
        return self.u

    def __eq__(self, other):
        return isinstance(other, LIVar) and self.u == other.u

    def subst(self, u, t):
        if u.u == self.u:
            return t
        else:
            return self

    def denot(self, s, v = {}, w = ""):
        """
        The denotation of a variable is that individual that the assignment function v assigns it.
        """
        return v[self.u]


class LConst(Lexpr):
    """
    Lambda constant.
    a, b, c, c1, c2, ...

    @attr c: the constant name
    @type c: str
    """

    def __init__(self, c: str):
        self.c = c

    def __str__(self):
        return self.c

    def tex(self):
        return "\\mathit{" + self.c + "}"

    def __eq__(self, other):
        return isinstance(other, Const) and self.c == other.c

    def subst(self, u, t):
        return self

    def denot(self, s, v = {}, w = ""):
        """
        The denotation of a constant is that individual that the interpretation function f assigns it.
        """
        i = s.i
        if not w:
            return i[self.c]
        else:
            return i[self.c][w]


class Appl(Lexpr):
    """
    Lambda application.
    (φψ)

    @attr phi: the functor
    @type phi: Expr
    @attr psi: the argument
    @type psi: Expr
    """

    def __init__(self, phi: Expr, psi: Expr):
        self.phi = phi
        self.psi = psi

    def __str__(self):
        return "(" + str(self.phi) + str(self.psi) + ")"

    def tex(self):
        return "(" + self.phi.tex() + self.psi.tex() + ")"

    def __eq__(self, other):
        return isinstance(other, Appl) and self.phi == other.phi and self.psi == other.psi

    def redex(self):
        """
        An expression is a redex iff it is an application whose functor is an abstraction.
        """
        return isinstance(self.phi, Abstr)

    def redexes(self):
        return ([self] if self.redex() else []) + self.phi.redexes() + self.psi.redexes()

    def beta_contr(self, redex=None):
        return self.phi.m.subst(self.phi.u, self.psi)

    def subst(self, u, t):
        return Appl(self.phi.subst(u, t), self.psi.subst(u, t))

    def denot(self, s, v = {}, w = ""):
        """
        The denotation of a lambda application the value of its functor applied to the value of its argument.
        """
        return self.phi.denot(s, v, w)[self.psi.denot(s, v, w)]


class Abstr(Lexpr):
    """
    Lambda abstraction.
    λu.φ

    @attr u: the binding variable
    @type u: LIVar
    @attr phi: the body
    @type phi: Expr
    """

    def __init__(self, u: LIVar, phi: Expr):
        self.u = u
        self.phi = phi

    def __str__(self):
        return "(" + "λ" + str(self.u) + "." + str(self.phi) + ")"

    def tex(self):
        return "(" + "\\lambda " + self.u.tex() + "." + self.phi.tex() + ")"

    def __eq__(self, other):
        return isinstance(other, Abstr) and self.u == other.u and self.phi == other.phi

    def freevars(self):
        return self.phi.freevars() - {self.u}

    def boundvars(self):
        return self.phi.boundvars() | {self.u}

    def subst(self, u, t):
        if u == self.u:
            return self
        elif not (self.u.u in t.freevars() and u.u in self.phi.freevars()):
            return Abstr(self.u, self.phi.subst(u, t))
        else:
            varnames = ["x", "y", "z"] + ["x" + str(i) for i in range(100)]
            u_ = [var for var in varnames if var not in self.phi.freevars() | t.freevars()][0]
            return Abstr(LIVar(u_), self.phi.subst(self.u, LIVar(u_)).subst(u, t))

    def denot(self, s, v = {}, w = ""):
        """
        The denotation of a lambda application is a function form its variable to the body.
        """
        # todo only works for individual variables
        return {d: self.phi.denot(s, v | {self.u: d}, w) for d in s.d}


class AllWorlds(Formula):
    """
    Special pseudo-connective indicating that a formula is true in all worlds of the model.
     ⊩φ

     @attr phi: the invalid formula
     @type phi: Formula
     """

    def __init__(self, phi: Formula):
        self.phi = phi

    def __str__(self):
        return str(self.phi)

    def tex(self):
        return self.phi.tex()

    def __eq__(self, other):
        return isinstance(other, AllWorlds) and self.phi == other.phi

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

    def denot(self, s, v = {}, w = ""):
        """
        A formula is true in the model if it is true in all worlds of the model.
        """
        return self.phi.denotV(s, v)

    def tableau_pos(self, mode):
        """
        CL:       ML, IL:
        ⊩φ         ⊩φ
         |          |
         φ        σ φ
                  where σ is old
        """
        if mode["classical"] and not mode["modal"]:
            rules = self.phi.tableau_pos(mode)
        else:
            rules = {"+A": ("ι", [(True, self.phi)])}
        return rules

    def tableau_neg(self, mode):
        return dict()


class NotAllWorlds(Formula):
    """
    Special pseudo-connective indicating that a formula is not true in all worlds of the model.
     ⊮φ

     @attr phi: the invalid formula
     @type phi: Formula
     """

    def __init__(self, phi: Formula):
        self.phi = phi

    def __str__(self):
        return "¬" + str(self.phi)

    def tex(self):
        return "\\neg " + self.phi.tex()

    def __eq__(self, other):
        return isinstance(other, NotAllWorlds) and self.phi == other.phi

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

    def denot(self, s, v = {}, w = ""):
        """
        A formula is not true in the model if it is not true in all worlds of the model.
        """
        return not self.phi.denotV(s, v)

    def tableau_pos(self, mode):
        """
        CL:       ML, IL:
        ⊮φ         ⊮φ
         |          |
        ¬φ        σ ¬φ
                  where σ is new
        """
        if mode["classical"] and not mode["modal"]:
            rules = self.phi.tableau_neg(mode)
        else:
            rules = {"+A": ("κ", [(False, self.phi)])}
        return rules

    def tableau_neg(self, mode):
        return dict()


class Pseudo(Formula):
    """
    Special pseudo-formulas for tableau annotation.
    """


class Empty(Pseudo):
    """
    Special empty pseudo-formula to secretly introduce branching.
    """

    def __init__(self):
        pass

    def __str__(self):
        return "ε"

    def tex(self):
        return "\\varepsilon"


class Inf(Pseudo):
    """
    Special pseudo-formula indicating inference.
    """
    def __init__(self):
        pass

    def __str__(self):
        return "⊢"
    
    def tex(self):
        return "\\vdash"
    
    def denot(self, s, v={}, w="", conclusion=None, premises=[]):
        if conclusion:  # validity
            return conclusion.denot(s, v, w) or not all([p.denot(s, v, w) for p in premises])
        else:  # satisfiability
            return all([p.denot(s, v, w) for p in premises])

class Closed(Pseudo):
    """
    Special pseudo-formula indicating a branch is closed.
    ×
    """

    def __init__(self):
        pass

    def __str__(self):
        return "×"

    def tex(self):
        return "\\times"


class Open(Pseudo):
    """
    Special pseudo-formula indicating a branch is open.
    ○
    """

    def __init__(self):
        pass

    def __str__(self):
        return "○"

    def tex(self):
        return "\\ocircle"


class Infinite(Pseudo):
    """
    Special pseudo-formula indicating a branch is (probably) infinite.
    ...
    """

    def __init__(self):
        pass

    def __str__(self):
        return "⋮"

    def tex(self):
        return "\\vdots"
