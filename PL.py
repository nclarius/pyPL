#!/usr/bin/env python
# -*- coding: utf-8 -*-

# A naive model checker for classical first-order logic with an extension to modal first-order logic.
# © Natalie Clarius <natalie.clarius@student.uni-tuebingen.de>
# Licensed under CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/).
#
# Disclaimer:
# -----------
# This implementation is intended for didactical purposes. It is not efficient or designed for real-life applications.
# I am happy to learn about any bugs or improvement suggestions.
#
# Features:
# ---------
#  - specification of expressions in a language of FOL
#    - accepts languages with with zero-place predicates, function symbols, term equality and modal operators ◻, ◇
#    - propositional logic may be imitated by means of zero-place predicates in place of propositional variables
#  - specification of models of FOL with domain, interpretation function and variable assignments
#    - accepts models without possible worlds, modal models with constant domains and modal models with varying domains
#  - evaluation of expressions (non-log. symbols, terms, open formulas, closed formulas)
#    relative to models, variable assignments and possible worlds
#
# Restrictions:
# -------------
#  - works only on models with finite domains
#  - works only on languages with a finite set of individual variables
#  - can't infer universal validity, logical inference etc., only truth in a given model
#
# Known issues:
# -------------
#  - name of model, domain, interpr. func., variable assignment and world is not systematically recognized,
#    instead always 'M', 'D', 'I', 'v', 'w' used in printout
#  - efficiency: assignment functions have to be specified on all variables of the language;
#    the domain is not restricted expression-wise to those variables that actually occur in the expression
#  - depth has to be reset manually after each call of denot
#  - global variables are bad
#
# Wish list:
# ----------
#  - print out detailed derivation rather than just final result of evaluation, possibly with LaTeX mode
#  - more user-friendly input:
#    - expression parser instead of the cumbersome PNF specification
#    - a better way of dealing with singleton tuples
#    - interactive mode/API instead of need to edit source code in order to set up input
#  - model generation?

"""
This is pyPL, a simple model checker for classical first-order logic.

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
to see how a denotation is computed recursively in line with the inductive definitions.
The '__repr__' methods are what makes the expressions formatted human-readable in the output.
Simply ignore all the print statements and anything that looks completely unfamiliar to you (such as 'w'/modal stuff).

Notes on notation:
- 'M' = model/structure (aka 'A')
- 'D' = domain of discourse (aka 'M')
- 'I' = interpretation function (aka 'F')
- 'v' = variable assignment function (aka 'g')

Have fun!
"""


# settings
active = [1, 2, 3, 4, 5, 6, 7, 8]  # set here which models to include in the output (see def.s in function 'compute')
verbose = True  # set this to True if you'd like intermediate steps to be printed out, and False otherwise


from typing import List, Dict, Set, Tuple


class Expr:
    """
    Well-formed expression of predicate logic.
    α, β, ...

    @method freevars: the set of the free variable occurrences in the expression
    @method boundvars: the set of bound variable occurrences in the expression
    @method subst: substitution of a term for a variable in the expression
    @method denot: denotation of the expression relative to a model m and assignment g
    """

    def freevars(self) -> Set[str]:
        """
        The set of the free variable occurrences in the expression.

        @return: the set of the free variable occurrences in the expression
        @rtype: set[str]
        """
        pass

    def boundvars(self) -> Set[str]:
        """
        The set of the bound variable occurrences in the expression.

        @return: the set of the bound variable occurrences in the expression
        @rtype: set[str]
        """
        pass

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
        pass

    def denot(self, m, v, w=None):
        """
        Compute the denotation of the expression relative to a model m and assignment g.

        @param m: the model to evaluate the formula against
        @type m: Model
        @param v: the assignment to evaluate the formula against
        @type v: dict[str,str]
        @param w: the possible world to evaluate the formula against
        @type w: str
        @return: the denotation of the expression relative to the model m and assignment g
        """
        pass


class Term(Expr):
    """
    Term (constant, variable).
    t1, t2, ...
    """

    def denot(self, m, v, w=None) -> str:
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

    def freevars(self) -> Set[str]:
        return set()

    def boundvars(self) -> Set[str]:
        return set()

    def subst(self, u, t) -> Term:
        return self

    def denot(self, m, v, w=None) -> str:
        """
        The denotation of a constant is that individual that the interpretation function f assigns it.
        """
        i = m.i
        if isinstance(m, ModalModel):
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
    def __init__(self, u):
        self.u = u

    def __repr__(self):
        return self.u

    def freevars(self) -> Set[str]:
        return {self.u}

    def boundvars(self) -> Set[str]:
        return set()

    def subst(self, u, t) -> Term:
        if self.u == u:
            return Var(repr(t))
        else:
            return self

    def denot(self, m, v, w=None) -> str:
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

    def __init__(self, f):
        self.f = f

    def __repr__(self):
        return self.f

    def freevars(self) -> Set[str]:
        return set()

    def boundvars(self) -> Set[str]:
        return set()

    def subst(self, u, t) -> Term:
        return self

    def denot(self, m, v, w=None) -> str:
        """
        The denotation of a constant is that individual that the assignment function g assigns it.
        """
        i = m.i
        if isinstance(m, ModalModel):
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

    def __init__(self, f, terms):
        self.f = f
        self.terms = terms

    def __repr__(self):
        return repr(self.f) + "(" + ", ".join([repr(t) for t in self.terms]) + ")"

    def freevars(self) -> Set[str]:
        return set().union(*[t.freevars() for t in self.terms])

    def boundvars(self) -> Set[str]:
        return set().union(*[t.boundvars() for t in self.terms])

    def subst(self, u, t) -> Term:
        return FuncTerm(self.f, map(lambda t: t.subst(u, t), self.terms))

    def denot(self, m, v, w=None) -> str:
        """
        The denotation of a function symbol applied to an appropriate number of terms is that individual that the
        interpretation function f assigns to the application.
        """
        i = m.i
        if isinstance(m, ModalModel):
            i = m.i[w]
        return i[self.f.f][tuple([t.denot(m, v, w) for t in self.terms])]


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

    def freevars(self) -> Set[str]:
        return set()

    def boundvars(self) -> Set[str]:
        return set()

    def subst(self, u, t) -> Expr:
        return self

    def denot(self, m, v, w=None) -> Set[Tuple[str]]:
        """
        The denotation of a predicate is the set of ordered tuples of individuals that the interpretation function f
        assigns it.
        """
        i = m.i
        if isinstance(m, ModalModel):
            i = m.i[w]
        return i[self.p]


depth = 0  # keep track of the level of nesting


class Formula(Expr):
    """
    Formula.
    φ, ψ, ...

    @method denotV: the truth value of a formula relative to a model m (without reference to a particular assignment)
    """

    def denot(self, m, v, w=None) -> bool:
        """
        @rtype: bool
        """
        pass

    def denotV(self, m, w=None) -> bool:
        """
        The truth value of a formula relative to a model M (without reference to a particular assignment).
        A formula is true in a model M iff it is true in M under all assignment functions g.

        @param m: a model
        @type m: Model
        @attr w: a possible world
        @type w: str
        @return: the truth value of self in m
        @rtype: bool
        """
        global depth
        # for efficiency, restrict the domain of the assignment functions o the vars that actually occur in the formula
        var_occs = self.freevars() | self.boundvars()
        vs__ = m.vs
        if isinstance(m, VarModalModel):
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
                print((depth * " ") + "checking v := " + repr(v) + " ...")
            witness = self.denot(m, v, w)
            if witness:
                if verbose:
                    print((depth * 2 * " ") + "✓")
                depth -= 1
            else:
                if verbose:
                    print((depth * 2 * " ") + "✗")
                    print((depth * " ") + "counter assignment: v := " + repr(v))
                depth -= 1
                return False
        return True

    def denotW(self, m, v) -> bool:
        """
        The truth value of a formula relative to a model M and assmnt. g (without reference to a particular world).
        A formula is true in a model M iff it is true in M and g in all possible worlds w.

        @param m: a model
        @type m: ModalModel
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
                print((depth * "  ") + "checking w := " + repr(w) + " ...")
            witness = self.denot(m, v, w)
            if witness:
                if verbose:
                    print((depth * 2 * " ") + "✓")
                depth -= 1
            else:
                if verbose:
                    print((depth * 2 * " ") + "✗")
                    print((depth * " ") + "counter world: w := " + repr(w))
                depth -= 1
                return False
        return True

    def denotVW(self, m) -> bool:
        """
        The truth value of a formula relative to a model M (without reference to a particular assignment and world).
        A formula is true in a model M iff it is true in M and g under all assignments g and all possible worlds w.

        @param m: a model
        @type m: ModalModel
        @attr g: an assignment function
        @type v: dict[str,str]
        @return: the truth value of self in m under g
        @rtype: bool
        """
        # todo doesn't work for modal models with varying domain yet (due different structure of assignment functions)
        global depth

        for w in m.w:
            depth += 1
            if verbose:
                print((depth * " ") + "checking w := " + repr(w) + " ...")
            witness = self.denotV(m, w)
            if witness:
                if verbose:
                    print((depth * 2 * " ") + "✓")
                depth -= 1
            else:
                if verbose:
                    print((depth * 2 * " ") + "✗")
                    print((depth * " ") + "counter world: w := " + repr(w))
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

    def freevars(self) -> Set[str]:
        return set()

    def boundvars(self) -> Set[str]:
        return set()

    def subst(self, u, t) -> Formula:
        return self

    def denot(self, m, v, w=None) -> bool:
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

    def freevars(self) -> Set[str]:
        return set()

    def boundvars(self) -> Set[str]:
        return set()

    def subst(self, u, t) -> Formula:
        return self

    def denot(self, m, v, w=None) -> bool:
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

    def freevars(self) -> Set[str]:
        return set()

    def boundvars(self) -> Set[str]:
        return set()

    def subst(self, u, t) -> Formula:
        return self

    def denot(self, m, v, w=None) -> bool:
        """
        The denotation of a propositional variable is the truth value the interpretation function f assigns it.
        """
        i = m.i
        if isinstance(m, VarModalModel):
            i = m.i[w]
        return i[self.p]


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

    def freevars(self) -> Set[str]:
        return self.t1.freevars() | self.t2.freevars()

    def boundvars(self) -> Set[str]:
        return self.t1.boundvars() | self.t2.boundvars()

    def subst(self, u, t) -> Formula:
        return Eq(self.t1.subst(u, t), self.t2.subst(u, t))

    def denot(self, m, v, w=None) -> bool:
        """
        The denotation of a term equality t1 = t2 is true iff t1 and t2 denote the same individual.
        """
        return self.t1.denot(m, v, w) == self.t2.denot(m, v, w)


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

    def freevars(self) -> Set[str]:
        return set().union(*[t.freevars() for t in self.terms])

    def boundvars(self) -> Set[str]:
        return set().union(*[t.boundvars() for t in self.terms])

    def subst(self, u, t) -> Formula:
        return Atm(self.pred, map(lambda t: t.subst(u, t), self.terms))

    def denot(self, m, v, w=None) -> bool:
        """
        The denotation of an atomic predication P(t1, ..., tn) is true iff the tuple of the denotation of the terms is
        an element of the interpretation of the predicate.
        """
        return tuple([t.denot(m, v, w) for t in self.terms]) in self.pred.denot(m, v, w)


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

    def freevars(self) -> Set[str]:
        return self.phi.freevars()

    def boundvars(self) -> Set[str]:
        return self.phi.boundvars()

    def subst(self, u, t) -> Formula:
        return Neg(self.phi.subst(u, t))

    def denot(self, m, v, w=None) -> bool:
        """
        The denotation of a negated formula Neg(phi) is true iff phi is false.
        """
        return not self.phi.denot(m, v, w)


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

    def freevars(self) -> Set[str]:
        return self.phi.freevars() | self.psi.freevars()

    def boundvars(self) -> Set[str]:
        return self.phi.boundvars() | self.psi.boundvars()

    def subst(self, u, t) -> Formula:
        return Conj(self.phi.subst(u, t), self.psi.subst(u, t))

    def denot(self, m, v, w=None) -> bool:
        """
        The denotation of a conjoined formula Con(phi,psi) is true iff phi is true and psi is true.
        """
        return self.phi.denot(m, v, w) and self.psi.denot(m, v, w)


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

    def freevars(self) -> Set[str]:
        return self.phi.freevars() | self.psi.freevars()

    def boundvars(self) -> Set[str]:
        return self.phi.boundvars() | self.psi.boundvars()

    def subst(self, u, t) -> Formula:
        return Disj(self.phi.subst(u, t), self.psi.subst(u, t))

    def denot(self, m, v, w=None) -> bool:
        """
        The denotation of a conjoined formula Disj(phi,psi) is true iff phi is true or psi is true.
        """
        return self.phi.denot(m, v, w) or self.psi.denot(m, v, w)


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

    def freevars(self) -> Set[str]:
        return self.phi.freevars() | self.psi.freevars()

    def boundvars(self) -> Set[str]:
        return self.phi.boundvars() | self.psi.boundvars()

    def subst(self, u, t) -> Formula:
        return Imp(self.phi.subst(u, t), self.psi.subst(u, t))

    def denot(self, m, v, w=None) -> bool:
        """
        The denotation of an implicational formula Imp(phi,psi) is true iff phi is false or psi is true.
        """
        return not self.phi.denot(m, v, w) or self.psi.denot(m, v, w)


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

    def freevars(self) -> Set[str]:
        return self.phi.freevars() | self.psi.freevars()

    def boundvars(self) -> Set[str]:
        return self.phi.boundvars() | self.psi.boundvars()

    def subst(self, u, t) -> Formula:
        return Biimp(self.phi.subst(u, t), self.psi.subst(u, t))

    def denot(self, m, v, w=None) -> bool:
        """
        The denotation of an biimplicational formula Biimp(phi,psi) is true iff phi and psi have the same truth value.
        """
        return self.phi.denot(m, v, w) == self.psi.denot(m, v, w)


class Exists(Formula):
    """
    Existential quantification.
    ∃xφ

    @attr u: the binding variable
    @type u: Var
    @attr phi: the formula to be quantified
    @type phi: Formula
    """
    def __init__(self, u, phi):
        self.u = u
        self.phi = phi

    def __repr__(self):
        return "∃" + repr(self.u) + (" " if isinstance(self.phi, Atm) else "") + repr(self.phi)

    def freevars(self) -> Set[str]:
        return self.phi.freevars() - {self.u.u}

    def boundvars(self) -> Set[str]:
        return self.phi.boundvars() | {self.u.u}

    def subst(self, u, t) -> Formula:
        if u == self.u:
            return self
        else:
            return self.phi.subst(u, t)

    def denot(self, m, v, w=None) -> bool:
        """
        The denotation of an existentially quantified formula Exists(x, phi) is true
        iff phi is true under at least one x-alternative of g.
        """
        global depth
        depth += 1
        d_ = m.d
        if isinstance(m, VarModalModel):
            d_ = m.d[w]

        # quantify over the individuals in the domain
        for d in sorted(d_):

            # compute the x-alternative v'
            v_ = {**v, self.u.u: d}  # unpack v and overwrite the value for u with d

            # check whether the current indiv. d under consideration makes phi true
            if verbose:
                print((depth * 2 * " ") + "checking v" + (depth * "'") + "(" + repr(self.u) + ") := " + repr(d) + " ...")
            witness = self.phi.denot(m, v_, w)

            # if yes, we found a witness, the existential statement is true, and we can stop checking (return)
            if witness:
                if verbose:
                    print((depth * 2 * " ") + "✓")
                depth -= 1
                return True

            # if not, we do nothing and try with the next one (continue)
            else:
                if verbose:
                    # print(((depth+1) * 2 * " ") + "0")
                    print((depth * 2 * " ") + "✗")

        # if we reach the end, then no witness has been found, and the existential statement is false
        depth -= 1
        return False


class Forall(Formula):
    """
    Universal quantification.
    ∀xφ

    @attr u: the binding variable
    @type u: Var
    @attr phi: the formula to be quantified
    @type phi: Formula
    """
    def __init__(self, u, phi):
        self.u = u
        self.phi = phi

    def __repr__(self):
        return "∀" + repr(self.u) + (" " if isinstance(self.phi, Atm) else "") + repr(self.phi)

    def freevars(self) -> Set[str]:
        return self.phi.freevars() - {self.u.u}

    def boundvars(self) -> Set[str]:
        return self.phi.boundvars() | {self.u.u}

    def subst(self, u, t) -> Formula:
        if u == self.u:
            return self
        else:
            return self.phi.subst(u, t)

    def denot(self, m, v, w=None) -> bool:
        """
        The denotation of universally quantified formula Forall(x, phi) is true iff
        phi is true under all x-alternatives of g.
        """
        global depth
        depth += 1
        d_ = m.d
        if isinstance(w, VarModalModel):
            d_ = m.d[w]

        # quantify over the individuals in the domain
        for d in sorted(d_):

            # compute the x-alternative v'
            v_ = {**v, self.u.u: d}  # unpack v and overwrite the value for u with d

            # check whether the current indiv. d under consideration makes phi true
            if verbose:
                print((depth * 2 * " ") + "checking v" + (depth * "'") + "(" + repr(self.u) + ") := " + repr(d) + " ...")
            witness = self.phi.denot(m, v_, w)

            # if yes, everything is fine until now, we do nothing and go check the next one (continue)
            if witness:
                if verbose:
                    print((depth * 2 * " ") + "✓")

            # if not, we found a counter witness, the universal statement is false, and we can stop checking (return)
            else:
                if verbose:
                    print((depth * 2 * " ") + "✗")
                depth -= 1
                return False

        # if we reach the end, then no counter witness has been found, and the universal statement is true
        depth -= 1
        return True


class Poss(Formula):
    """
    Possibility.
    ◇φ

    @attr phi: the formula to apply the modal operator to
    @type phi: Expr
    """
    def __init__(self, phi):
        self.phi = phi

    def __repr__(self):
        return "◇" + repr(self.phi)

    def subst(self, u, t) -> Formula:
        return Poss(self.phi.subst(u, t))

    def freevars(self) -> Set[str]:
        return self.phi.freevars()

    def boundvars(self) -> Set[str]:
        return self.phi.boundvars()

    def denot(self, m, v, w) -> bool:
        """
        The denotation of a possiblity formula is true iff
        phi is true at at least one world accessible from w.

        @param m: the model to evaluate the formula in
        @type m: ModalModel
        @param v: the assignment function to evaluate the formula in
        @type v: dict[str,str]
        @param w: the world to evaluate the formula in
        @type w: str
        @return: the denotation of Poss(phi)
        """
        global depth
        # iterate over all possible worlds w' which are accessible from w
        neighbors = [w_ for w_ in m.w if (w, w_) in m.r]
        for w_ in neighbors:
            depth += 1
            # check whether phi is true in w
            if verbose:
                print((depth * "  ") + "checking w" + (depth * "'") + " := " + repr(w_) + " ...")
            witness = self.phi.denot(m, v, w_)
            # if yes, we found a witnessing neighbor, the possibility statement is true, and we can stop checking
            if witness:
                if verbose:
                    print((depth * 2 * " ") + "✓")
                    print((depth * 2 * " ") + "neighbor: w" + (depth * "'") + " := " + repr(w_))
                depth -= 1
                return True
            if not witness:
                if verbose:
                    print((depth * 2 * " ") + "✗")
                depth -= 1
        # if no witness has been found, the possibility statement is false
        depth -= 1
        return False


class Nec(Formula):
    """
    Necessity.
    ◻φ

    @attr phi: the formula to apply the modal operator to
    @type phi: Expr
    """

    def __init__(self, phi):
        self.phi = phi

    def __repr__(self):
        return "◻" + repr(self.phi)

    def subst(self, u, t) -> Formula:
        return Poss(self.phi.subst(u, t))

    def freevars(self) -> Set[str]:
        return self.phi.freevars()

    def boundvars(self) -> Set[str]:
        return self.phi.boundvars()

    def denot(self, m, v, w) -> bool:
        """
        The denotation of a necessity formula is true iff
        phi is true at all worlds accessible from w.

        @param m: the model to evaluate the formula in
        @type m: ModalModel
        @param w: the world to evaluate the formula in
        @type w: str
        @param v: the assignment function to evaluate the formula in
        @type v: dict[str,str]
        """
        global depth
        # iterate over all possible worlds w' which are accessible from w
        neighbors = [w_ for w_ in m.w if (w, w_) in m.r]
        for w_ in neighbors:
            depth += 1
            # check whether phi is true in w
            if verbose:
                print((depth * "  ") + "checking w" + (depth * "'") + " := " + repr(w_) + " ...")
            witness = self.phi.denot(m, v, w_)
            if witness:
                if verbose:
                    print((depth * 2 * " ") + "✓")
                depth -= 1
            # if not, we found a counter neighbor, the necessity statement is false, and we can stop checking
            else:
                if verbose:
                    print((depth * 2 * " ") + "✗")
                    print((depth * 2 * " ") + "counter neighbor: w" + (depth * "'") + " := " + repr(w_))
                depth -= 1
                return False
        # if no counter neighbor has been found, the necessity statement is true
        depth -= 1
        return True


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


vars = [Var("x"), Var("y"), Var("z")]  # the individual variables of the language


class Model:
    """
    A modal of (modal) predicate logic.

    @attr d: the domain of discourse
    @attr i: an interpretation function
    """
    pass


class PredModel(Model):
    """
    A model of predicate logic with domain, interpretation function and a set of assignment functions.

    A Model M is a pair <D, I> with
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
    @type vs: the assignment functions associated with the model
    @type vs: list[dict[str,str]]]
    """

    def __init__(self, d, i):
        self.d = d
        self.i =i
        dprod = cart_prod(list(d), len(vars))  # all ways of forming sets of |vars| long combinations of elements from D
        self.vs = [{str(v): a for (v, a) in zip(vars, distr)} for distr in dprod]

    def __repr__(self):
        return "Model M = (D,I) with\n" \
               "D = {" + ", ".join([repr(d) for d in self.d]) + "}\n" \
               "I = {\n" + ", \n".join(["     " + repr(key) + " ↦ " +
                                        (repr(val) if isinstance(val, str) else
                                         (", ".join(["(" + repr(key2) + " ↦ " + repr(val2) + ")"
                                                     for key2, val2 in val.items()])
                                          if isinstance(val, dict) else
                                          ("{" +
                                           ", ".join(["(" + ", ".join([repr(t) for t in s]) + ")" for s in val]) +
                                           "}")))
                                        for (key, val) in self.i.items()]) +\
               "\n    }"


class ModalModel(Model):
    """
    A modal of (modal) predicate logic.

    @attr w: a set of possible worlds
    @type w: set[str]
    @attr r: an accessibility relation on r
    @type r: set[tuple[str,str]]
    """
    pass


class ConstModalModel(ModalModel):
    """
    A model of modal predicate logic with constant domain.

    A ConstModalModel M is a quadrupel <W,R,D,F> with
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
      - and interpretation of the non-logical symbols as values (see Model.f).

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
        dprod = cart_prod(list(d), len(vars))  # all ways of forming sets of |vars| long combinations of elements from D
        self.vs = [{str(v): a for (v, a) in zip(vars, distr)} for distr in dprod]

    def __repr__(self):
        return "Model M = (W,R,D,I) with\n" \
               "W = {" + ", ".join([repr(w) for w in self.w]) + "}\n"\
               "R = {" + ", ".join([repr(r) for r in self.r]) + "}\n"\
               "D = {" + ", ".join([repr(d) for d in self.d]) + "}\n" \
               "I = {\n" +\
                    " \n".join(["    " + repr(w) + " ↦ \n" + \
                        ", \n".join(
                        ["           " + repr(keyI) + " ↦ " +
                         (repr(valI) if isinstance(valI, str) else
                          (", ".join(["(" + repr(keyI2) + " ↦ " + repr(valI2) + ")"
                                      for keyI2, valI2 in valI.items()])
                           if isinstance(valI, dict) else
                           ("{" +
                            ", ".join(["(" + ", ".join([repr(t) for t in s]) + ")" for s in valI]) +
                            "}")))
                        for (keyI, valI) in self.i[w].items()]) + \
                        "\n    "
                    for (w, fw) in self.i.items()]) +\
                    "}"


class VarModalModel(ModalModel):
    """
    A model of modal predicate logic with varying domains.

    A VarModalModel M is a quadrupel <W,R,D,I> with
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
      - domains (see Model.D) as values
      D = {'w1': {'a', 'b', 'c'}, 'w2': {'b'}, ...}

    - The interpretation function F is a dictionary with
      - possible worlds as keys and
      - and interpretation of the non-logical symbols (see Model.f) as values.

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
        dprods = {w: cart_prod(list(self.d[w]), len(vars)) for w in self.w}  # all ways of forming sets of |vars| long combinations of elements from D
        self.vs = {w: [{str(v): a for (v, a) in zip(vars, distr)} for distr in dprods[w]] for w in self.w}

    def __repr__(self):
        return "Model M = (W,R,D,F) with\n" \
               "W = {" + ", ".join([repr(w) for w in self.w]) + "}\n" \
               "R = {" + ", ".join([repr(r) for r in self.r]) + "}\n" \
               "D = {\n" + \
                    ", \n".join([repr(w) + " ↦ " + \
                            ", ".join([repr(d) for d in self.d[w]]) + "}"
                    for w in self.w]) +\
                    "}\n" \
               "I = {\n" + \
                    ", \n".join(["    " + repr(w) + " ↦ " +\
                            ", \n".join(
                                ["         " + repr(keyI) + " ↦ " +
                                 (repr(valI) if isinstance(valI, str) else
                                  (", ".join(["(" + repr(keyI2) + " ↦ " + repr(valI2) + ")"
                                              for keyI2, valI2 in valI.items()])
                                   if isinstance(valI, dict) else
                                   ("{" +
                                    ", ".join(["(" + ", ".join([repr(t) for t in s]) + ")" for s in valI]) +
                                    "}")))
                                 for (keyI, valI) in self.i[w].items()]) + \
                            "\n    }"
                            for (w, fw) in self.i.items()]) + \
                    "}"


def compute():
    """
    Define models and formulas to compute denotations for here.
    """
    global depth, active


    if 1 in active:
        ############################
        print("\n---------------------------------\n")
        ############################

        print("Example #1: tupperware boxes, lids and a bunny (logic for linguists lecture 09)")
        print()

        d1 = {"roundbox", "roundlid", "rectbox", "rectlid", "bunny"}
        i1 = {"b1": "roundbox", "b2": "rectbox", "f": "bunny",
              "box": {("roundbox", ), ("rectbox", )},
              "lid": {("roundlid", ), ("rectlid", )},
              "fit": {("roundlid", "roundbox"), ("rectlid", "rectbox")}
        }
        m1 = PredModel(d1, i1)
        v1 = {"x": "roundbox", "y": "bunny"}
        vv1 = {"x": "bunny", "y": "rectbox"}

        print(m1)
        print("v1 = " + repr(v1))
        print("v'1 = " + repr(vv1))

        e1 = {
            1: Var("x"),
            2: Const("f"),
            3: Atm(Pred("box"), (Var("x"), )),
            4: Forall(Var("x"), Imp(Atm(Pred("box"), (Var("x"), )),
                                    Exists(Var("y"), Conj(Atm(Pred("lid"), (Var("y"), )),
                                                          Atm(Pred("fit"), (Var("y"), Var("x"))))))),
            5: Exists(Var("y"), Conj(Atm(Pred("lid"), (Var("y"), )),
                                     Forall(Var("x"), Imp(Atm(Pred("box"), (Var("x"), )),
                                                          Atm(Pred("fit"), (Var("y"), Var("x")))))))
        }

        for nr, e in e1.items():
            if nr <= 3:
                print()
                print("[[" + repr(e) + "]]^M1,v1 =")
                print(e.denot(m1, v1))
                depth = 0
                print()
                print("[[" + repr(e) + "]]^M1,v'1 =")
                print(e.denot(m1, vv1))
                depth = 0
            if nr > 3:
                print()
                print("[[" + repr(e) + "]]^M1 =")
                print(e.denotV(m1))
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
        m2 = PredModel(d2, i2)
        v2 = {"x": "Jane", "y": "Mary", "z": "MMiL"}

        print(m2)
        print("v = " + repr(v2))

        e2 = {
            1: Var("x"),  # Jane
            2: Const("m"),  # Mary
            3: Pred("read"),  # {(Mary, MMiL)}
            4: Atm(Pred("book"), (Var("x"), )),  # false, since Jane is not a book
            5: Exists(Var("x"), Conj(Atm(Pred("book"), (Var("x"),)), Atm(Pred("read"), (Const("m"), Var("x"))))),  # true
            6: Forall(Var("y"), Imp(Atm(Pred("student"), (Var("y"), )),
                                    Exists(Var("x"),
                                           Conj(Atm(Pred("book"), (Var("x"), )),
                                                Atm(Pred("read"), (Var("y"), Var("z"))))))),
               # false, since Jane doesn't read a book
            7: Neg(Exists(Var("y"), Conj(Atm(Pred("student"), (Var("y"), )),
                                         Exists(Var("x"),
                                                Conj(Atm(Pred("book"), (Var("x"), )),
                                                     Atm(Pred("read"), (Var("y"), (Var("z")))))))))
               # false, since Mary reads a book
        }

        for nr, e in e2.items():
            print()
            print("[[" + repr(e) + "]]^M2,v2 =")
            print(e.denot(m2, v2))
            depth = 0


    if 3 in active:
        #############################
        print("\n---------------------------------\n")
        #############################

        print("Example #3: love #1 (logic for linguists ExSh 9 Ex. 1)")
        print()

        d3 = {"Mary", "John", "Peter"}
        i3 = {"j": "Peter", "p": "John",
              "woman": {("Mary",)},
              "man": {("John", ), ("Peter", )},
              "love": {("Mary", "John"), ("John", "Mary"), ("John", "John"), ("Peter", "Mary"), ("Peter", "John")},
              "jealous": {("Peter", "John", "Mary"), ("Peter", "Mary", "John")}}
        m3 = PredModel(d3, i3)
        v3 = {"x": "Mary", "y": "Mary", "z": "Peter"}
        vv3 = {"x": "John", "y": "Peter", "z": "John"}

        print(m3)
        print("v = " + repr(v3))
        print("v' = " + repr(vv3))

        e3 = {
            1: Const("p"),
            2: Var("y"),
            3: Var("y"),
            4: Atm(Pred("love"), (Const("p"), Const("j"))),
            5: Atm(Pred("love"), (Var("y"), Var("z"))),
            6: Atm(Pred("love"), (Var("y"), Var("z"))),
            7: Exists(Var("x"), Neg(Atm(Pred("love"), (Const("j"), Var("x"))))),
            8: Forall(Var("x"), Exists(Var("y"), Atm(Pred("love"), (Var("x"), Var("y"))))),
            9: Neg(Forall(Var("x"), Imp(Atm(Pred("woman"), (Var("x"),)),
                                         Exists(Var("y"), Conj(Atm(Pred("man"), (Var("y"),)),
                                                               Atm(Pred("love"), (Var("x"), Var("y"))))
                                                )))),
            10: Neg(Exists(Var("y"), Exists(Var("z"), Atm(Pred("jealous"), (Const("j"), Var("y"), Var("z"))))))
        }

        for nr, e in e3.items():
            # print(e)
            if nr in [1, 2, 4, 5, 7, 8, 9]:
                print()
                print("[[" + repr(e) + "]]^M3,v3 =")
                print(e.denot(m3, v3))
                depth = 0
            elif nr in [3, 6, 10]:
                print()
                print("[[" + repr(e) + "]]^M3,v'3 =")
                print(e.denot(m3, vv3))
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
        m4 = PredModel(d4, i4)
        v4 = m4.vs[5]

        print(m4)
        print("v = " + repr(v4))

        e4 = {
            1: Var("x"),  # Susan
            2: Const("j"),  # John
            3: Pred("love"),  # {(J,M), (M,S), (S,M), (S,S)}
            4: Atm(Pred("love"), (Var("x"), Const("m"))),  # true under g, false in m
            5: Atm(Pred("love"), (Const("j"), Const("m"))),  # true
            6: Exists(Var("x"), Atm(Pred("love"), (Const("j"), Var("x")))),  # true
            7: Forall(Var("x"), Atm(Pred("love"), (Const("j"), Var("x")))),  # false
            8: Conj(Atm(Pred("love"), (Const("m"), Const("s"))), Atm(Pred("love"), (Const("s"), Const("m")))),  # true
            9: Forall(Var("x"), Imp(Atm(Pred("love"), (Const("s"), Var("x"))), Atm(Pred("woman"), (Var("x"),)))),  # true
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
                print("[[" + repr(e) + "]]^M4,v4 =")
                print(e.denot(m4, v4))
                depth = 0
            if 4 <= nr <= 16:
                print()
                print("[[" + repr(e) + "]]^M4 =")
                print(e.denotV(m4))
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
        m5 = PredModel(d5, i5)
        v5 = {"x": "Susan", "y": "Mary", "z": "Peter"}

        print(m5)
        print("v = " + repr(v5))

        e5 = {
            1: FuncTerm(Func("mother"), (Const("m"),)),  # Susan
            2: FuncTerm(Func("mother"), (FuncTerm(Func("mother"), (Const("m"),)),)),  # Jane
            3: Eq(FuncTerm(Func("mother"), (Const("m"),)), Const("s")),  # true
            4: Neg(Eq(Var("x"), Const("m")))  # true
        }

        for nr, e in e5.items():
            print()
            print("[[" + repr(e) + "]]^M5,v5 =")
            print(e.denot(m5, v5))
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
        i6 = {"w1": {"P": {()}},
              "w2": {"P": set()}}
        m6 = ConstModalModel(w6, r6, d6, i6)
        v6 = m6.vs[0]

        print(m6)
        print(v6)

        e6 = {
            1: Poss(Nec(Eq(Var("x"), Var("x")))),
            2: Nec(Disj(Atm(Pred("P"), tuple()), Neg(Atm(Pred("P"), tuple())))),
            3: Disj(Nec(Atm(Pred("P"), tuple())), Nec(Neg(Atm(Pred("P"), tuple()))))
        }

        for nr, e in e6.items():
            # print()
            # print("[[" + repr(e) + "]]^M6,v6,w1 =")
            # print(e.denot(m6, v6, "w1"))
            # depth = 0
            # print()
            # print("[[" + repr(e) + "]]^M6,v6,w2 =")
            # print(e.denot(m6, v6, "w2"))
            # depth = 0
            print("[[" + repr(e) + "]]^M6,v6 =")
            print(e.denotW(m6, v6))
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
        i7 = {"w1": {"P": {("a",)}},
              "w2": {"P": {("b",)}}}
        m7 = VarModalModel(w7, r7, d7, i7)

        print(m7)
        print(m7.vs)

        e7 = {
            1: Exists(Var("x"), Exists(Var("y"), Neg(Eq(Var("x"), Var("y")))))
        }

        for nr, e in e7.items():
            print()
            print("[[" + repr(e) + "]]^M7,w1 =")
            print(e.denot(m7, m7.vs["w1"][0], "w1"))
            depth = 0
            print()
            print("[[" + repr(e) + "]]^M7,w2 =")
            print(e.denot(m7, m7.vs["w2"][0], "w2"))
            depth = 0
            # print(e.denotV(m7))
            # print(e.denotW(m7, v7))
            # print(e.denotVW(m7))
            # depth = 0


    if 8 in active:
        #############################
        print("\n---------------------------------\n")
        #############################

        print("Example #8 (logic for computer scientists lecture 07)")
        print()

        d8a = {"m1", "m2"}
        i8a = {"S": {("m1", )},
               "R": {("m1", "m1"), ("m2", "m1")}
              }
        m8a = PredModel(d8a, i8a)

        d8b = {"m1", "m2"}
        i8b = {"S": {("m2", )},
               "R": {("m1", "m1"), ("m2", "m1")}
              }
        m8b = PredModel(d8b, i8b)

        print(m8a)
        print()
        print(m8b)

        e7 = {
            1: Forall(Var("x"), Exists(Var("y"),
                                       Conj(Atm(Pred("S"), (Var("y"), )), Atm(Pred("R"), (Var("x"), Var("y"))))))
        }

        for nr, e in e7.items():
            print()
            print("[[" + repr(e) + "]]^M =")
            print(e.denotV(m8a))
            depth = 0
            print()
            print("[[" + repr(e) + "]]^M' =")
            print(e.denotV(m8b))
            depth = 0


    #############################
    print("\n---------------------------------\n")
    #############################


if __name__ == "__main__":
    print(__doc__)
    compute()
    print("\nScroll up for help information.")
