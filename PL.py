# -*- coding: utf-8 -*-
"""
Simple modal first-order logic interpreter.
© Natalie Clarius <natalie.clarius@student.uni-tuebingen.de>

Features:
 - specification of expressions in a language of FOL
   - accepts languages with with 0-place predicates, function symbols, term equality and modal operators ◻, ◇
 - specification of models of FOL with domain, interpretation function and assignment functions
   - accepts models without possible worlds, modal models with constant domains and modal models with varying domains
 - evaluation of expressions (non-log. symbols, terms, open formulas, closed formulas)
   relative to models, assignment functions and possible worlds

Restrictions:
 - works only on models with finite domains (obviously)
 - works only on languages with a finite set of individual variables
 - can't infer universal validity, logical inference etc., only truth in a given model

Known issues:
 - name of model, domain, interpr. func. and variable assignment is not systematically recognized,
   instead always 'M', 'D', 'F', 'g', 'w' used in printout
 - efficiency: assignment functions have to be specified on all variables of the language;
   the domain is not restricted expression-wise to those variables that actually occur in the expression
 - depth has to be reset manually after each call of denot

Wish list:
 - print out detailed derivation rather than just final result of evaluation, possibly with LaTeX mode
 - more user-friendly input:
   - expression parser instead of the cumbersome PNF specification
   - a better way of dealing with singleton tuples
   - interactive mode/API instead of need to edit source code in order to set up input
"""

verbose = True  # set this to True if you'd like intermediate steps to be printed out, and False otherwise


class Expr:
    """
    Well-formed expression of predicate logic.
    α, β, ...

    @method freevars: the set of the free variable occurrences in the expression
    @method boundvars: the set of bound variable occurrences in the expression
    @method subst: substitution of a term for a variable in the expression
    @method denot: denotation of the expression relative to a model m and assignment g
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

    def subst(self, v, a):
        """
        Substitute all occurrences of the variable v for the term a in self.

        @param v: the variable to be substituted
        @type v: Var
        @param a: the term to substitute
        @type a: Term
        @return: the result of substituting all occurrences of the variable v for the term a in self
        @rtype Expr
        """
        pass

    def denot(self, m, g, w=None):
        """
        Compute the denotation of the expression relative to a model m and assignment g.

        @param m: the model to evaluate the formula against
        @type m: Model
        @param g: the assignment to evaluate the formula against
        @type g: dict[str,str]
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

    def denot(self, m, g, w=None):
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

    def subst(self, v, a):
        return self

    def denot(self, m, g, w=None):
        """
        The denotation of a constant is that individual that the interpretation function f assigns it.
        """
        f = m.f
        if isinstance(m, ModalModel):
            f = m.f[w]
        return f[self.c]


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
        return {}

    def subst(self, v, a):
        if self.v == v:
            return Var(repr(a))
        else:
            return self

    def denot(self, m, g, w=None):
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

    def subst(self, v, a):
        return self

    def denot(self, m, g, w=None):
        """
        The denotation of a constant is that individual that the assignment function g assigns it.
        """
        f = m.f
        if isinstance(m, ModalModel):
            f = m.f[w]
        return f[self.f]


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

    def subst(self, v, a):
        return FuncTerm(self.f, map(lambda t: t.subst(v, a), self.terms))

    def denot(self, m, g, w=None):
        """
        The denotation of a function symbol applied to an appropriate number of terms is that individual that the
        interpretation function f assigns to the application.
        """
        f = m.f
        if isinstance(m, ModalModel):
            f = m.f[w]
        return f[self.f.f][tuple([t.denot(m, g, w) for t in self.terms])]


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

    def subst(self, v, a):
        return self

    def denot(self, m, g, w=None):
        """
        The denotation of a predicate is the set of ordered tuples of individuals that the interpretation function f
        assigns it.
        """
        f = m.f
        if isinstance(m, ModalModel):
            f = m.f[w]
        return f[self.p]


depth = 0  # keep track of the level of nesting


class Formula(Expr):
    """
    Formula.
    φ, ψ, ...

    @method denotG: the truth value of a formula relative to a model m (without reference to a particular assignment)
    """

    def denot(self, m, g, w=None):
        """
        @rtype: bool
        """
        pass

    def denotG(self, m, w=None):
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
        # for efficiency, restrict the domain of the assignment functions to the vars that actually occur in the formula
        var_occs = self.freevars().union(self.boundvars())
        gs_ = m.gs
        if isinstance(m, VarModalModel):
            gs_ = m.gs[w]
        gs__ = [{v: g[v] for v in g if v in var_occs} for g in gs_]
        m.gs_ = [dict(tpl) for tpl in {tuple(g.items()) for g in gs__}]  # filter out now duplicate assignment functions

        if not self.freevars():  # if the formula is closed,
            # spare yourself the quantification over all assignment functions and pick an arbitrary assignment
            # (here: the first)
            return self.denot(m, m.gs_[0])

        for g in m.gs_:  # otherwise, check the denotation for all assignment functions
            depth += 1
            if verbose:
                print((depth * " ") + "checking g = " + repr(g) + " ...")
            witness = self.denot(m, g, w)
            if witness:
                if verbose:
                    print((depth * 2 * " ") + "✓")
                depth -= 1
            else:
                if verbose:
                    print((depth * 2 * " ") + "✗")
                    print((depth * " ") + "counter assignment: g = " + repr(g))
                depth -= 1
                return False
        return True

    def denotW(self, m, g):
        """
        The truth value of a formula relative to a model M and assmnt. g (without reference to a particular world).
        A formula is true in a model M iff it is true in M and g in all possible worlds w.

        @param m: a model
        @type m: ModalModel
        @attr g: an assignment function
        @type g: dict[str,str]
        @return: the truth value of self in m under g
        @rtype: bool
        """
        global depth
        # # for efficiency, restrict the domain of the assignment functions to the vars that actually occur in the formula
        # var_occs = self.freevars().union(self.boundvars())
        # gs_ = [{v: g[v] for v in g if v in var_occs} for g in m.gs]
        # m.gs_ = [dict(tpl) for tpl in {tuple(g.items()) for g in gs_}]  # filter out duplicate assignment functions

        for w in m.w:
            depth += 1
            if verbose:
                print((depth * "  ") + "checking w = " + repr(w) + " ...")
            witness = self.denot(m, g, w)
            if witness:
                if verbose:
                    print((depth * 2 * " ") + "✓")
                depth -= 1
            else:
                if verbose:
                    print((depth * 2 * " ") + "✗")
                    print((depth * " ") + "counter world: w = " + repr(w))
                depth -= 1
                return False
        return True

    def denotGW(self, m):
        """
        The truth value of a formula relative to a model M (without reference to a particular assignment and world).
        A formula is true in a model M iff it is true in M and g under all assignments g and all possible worlds w.

        @param m: a model
        @type m: ModalModel
        @attr g: an assignment function
        @type g: dict[str,str]
        @return: the truth value of self in m under g
        @rtype: bool
        """
        # todo doesn't work for modal models with varying domain yet (due different structure of assignment functions)
        global depth
        # for efficiency, restrict the domain of the assignment functions to the vars that actually occur in the formula
        var_occs = self.freevars().union(self.boundvars())
        gs_ = [{v: g[v] for v in g if v in var_occs} for g in m.gs]
        m.gs_ = [dict(tpl) for tpl in {tuple(g.items()) for g in gs_}]  # filter out now duplicate assignment functions

        if not self.freevars():  # if the formula is closed,
            # spare yourself the quantification over all assignment functions and pick an arbitrary assignment
            # (here: the first)
            return self.denot(m, m.gs_[0])

        for g in m.gs_:  # otherwise, check the denotation for all assignment functions
            depth += 1
            if verbose:
                print((depth * " ") + "checking g = " + repr(g) + " ...")
            witness = self.denotW(m, g)
            if witness:
                if verbose:
                    print((depth * 2 * " ") + "✓")
                depth -= 1
            else:
                if verbose:
                    print((depth * 2 * " ") + "✗")
                    print((depth * " ") + "counter assignment: g = " + repr(g))
                depth -= 1
                return False
        return True


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
        return self.t1.freevars().union(self.t2.freevars())

    def boundvars(self):
        return self.t1.boundvars().union(self.t2.boundvars())

    def subst(self, v, a):
        return Eq(self.t1.subst(v, a), self.t2.subst(v, a))

    def denot(self, m, g, w=None):
        """
        The denotation of a term equality t1 = t2 is true iff t1 and t2 denote the same individual.
        """
        return self.t1.denot(m, g, w) == self.t2.denot(m, g, w)


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

    def subst(self, v, a):
        return Atm(self.pred, map(lambda t: t.subst(v, a), self.terms))

    def denot(self, m, g, w=None):
        """
        The denotation of an atomic predication P(t1, ..., tn) is true iff the tuple of the denotation of the terms is
        an element of the interpretation of the predicate.
        """
        return tuple([t.denot(m, g, w) for t in self.terms]) in self.pred.denot(m, g, w)


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

    def subst(self, v, a):
        return Neg(self.phi.subst(v, a))

    def denot(self, m, g, w=None):
        """
        The denotation of a negated formula Neg(phi) is true iff phi is false.
        """
        return not self.phi.denot(m, g, w)


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
        return self.phi.freevars().union(self.psi.freevars())

    def boundvars(self):
        return self.phi.boundvars().union(self.psi.boundvars())

    def subst(self, v, a):
        return Conj(self.phi.subst(v, a), self.psi.subst(v, a))

    def denot(self, m, g, w=None):
        """
        The denotation of a conjoined formula Con(phi,psi) is true iff phi is true and psi is true.
        """
        return self.phi.denot(m, g, w) and self.psi.denot(m, g, w)


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
        return self.phi.freevars().union(self.psi.freevars())

    def boundvars(self):
        return self.phi.boundvars().union(self.psi.boundvars())

    def subst(self, v, a):
        return Disj(self.phi.subst(v, a), self.psi.subst(v, a))

    def denot(self, m, g, w=None):
        """
        The denotation of a conjoined formula Disj(phi,psi) is true iff phi is true or psi is true.
        """
        return self.phi.denot(m, g, w) or self.psi.denot(m, g, w)


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
        return self.phi.freevars().union(self.psi.freevars())

    def boundvars(self):
        return self.phi.boundvars().union(self.psi.boundvars())

    def subst(self, v, a):
        return Imp(self.phi.subst(v, a), self.psi.subst(v, a))

    def denot(self, m, g, w=None):
        """
        The denotation of an implicational formula Imp(phi,psi) is true iff phi is false or psi is true.
        """
        return not self.phi.denot(m, g, w) or self.psi.denot(m, g, w)


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
        return self.phi.freevars().union(self.psi.freevars())

    def boundvars(self):
        return self.phi.boundvars().union(self.psi.boundvars())

    def subst(self, v, a):
        return Biimp(self.phi.subst(v, a), self.psi.subst(v, a))

    def denot(self, m, g, w=None):
        """
        The denotation of an biimplicational formula Biimp(phi,psi) is true iff phi and psi have the same truth value.
        """
        return self.phi.denot(m, g, w) == self.psi.denot(m, g, w)


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
        return self.phi.freevars().difference({self.v.v})

    def boundvars(self):
        return self.phi.boundvars().union({self.v.v})

    def subst(self, v, a):
        if v == self.v:
            return self
        else:
            return self.phi.subst(v, a)

    def denot(self, m, g, w=None):
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
        for d in d_:
            # compute the x-alternative g'
            g_ = {**g, self.v.v: d}  # unpack g and overwrite the dictionary value for v with d
            # check whether the current indiv. d under consideration makes phi true
            if verbose:
                print((depth * 2 * " ") + "checking g" + (depth * "'") + "(" + repr(self.v) + ") := " + repr(d) + " ...")
            witness = self.phi.denot(m, g_, w)
            # if yes, we found a witness, the existential statement is true, and we can stop checking
            if witness:
                if verbose:
                    print((depth * 2 * " ") + "✓")
                    print((depth * 2 * " ") + "witness: g" + (depth * "'") + "(" + repr(self.v) + ") = " + repr(d))
                depth -= 1
                return True
            if not witness:
                if verbose:
                    print((depth * 2 * " ") + "✗")
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
        return self.phi.freevars().difference({self.v.v})

    def boundvars(self):
        return self.phi.boundvars().union({self.v.v})

    def subst(self, v, a):
        if v == self.v:
            return self
        else:
            return self.phi.subst(v, a)

    def denot(self, m, g, w=None):
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
        for d in d_:
            # compute the x-alternative g'
            g_ = {**g, self.v.v: d}  # unpack g and overwrite the dictionary value for v with d
            # check whether the current indiv. d under consideration makes phi true
            if verbose:
                print((depth * 2 * " ") + "checking g" + (depth * "'") + "(" + repr(self.v) + ") := " + repr(d) + " ...")
            witness = self.phi.denot(m, g_, w)
            if witness:
                if verbose:
                    print((depth * 2 * " ") + "✓")
            # if not, we found a counter witness, the universal statement is false, and we can stop checking
            else:
                if verbose:
                    print((depth * 2 * " ") + "✗")
                    print((depth * 2 * " ") + "counter witness: g" + (depth * "'") + "(" + repr(self.v) + ") = " + repr(d))
                depth -= 1
                return False
        # if no counter witness has been found, the universal statement is true
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

    def subst(self, v, a):
        return Poss(self.phi.subst(v, a))

    def freevars(self):
        return self.phi.freevars()

    def boundvars(self):
        return self.phi.boundvars()

    def denot(self, m, g, w):
        """
        The denotation of a possiblity formula is true iff
        phi is true at at least one world accessible from w.

        @param m: the model to evaluate the formula in
        @type m: ModalModel
        @param g: the assignment function to evaluate the formula in
        @type g: dict[str,str]
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
                print((depth * "  ") + "checking w" + (depth * "'") + " = " + repr(w_) + " ...")
            witness = self.phi.denot(m, g, w_)
            # if yes, we found a witnessing neighbor, the possibility statement is true, and we can stop checking
            if witness:
                if verbose:
                    print((depth * 2 * " ") + "✓")
                    print((depth * 2 * " ") + "neighbor: w" + (depth * "'") + " = " + repr(w_))
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

    def subst(self, v, a):
        return Poss(self.phi.subst(v, a))

    def freevars(self):
        return self.phi.freevars()

    def boundvars(self):
        return self.phi.boundvars()

    def denot(self, m, g, w):
        """
        The denotation of a necessity formula is true iff
        phi is true at all worlds accessible from w.

        @param m: the model to evaluate the formula in
        @type m: ModalModel
        @param w: the world to evaluate the formula in
        @type w: str
        @param g: the assignment function to evaluate the formula in
        @type g: dict[str,str]
        """
        global depth
        # iterate over all possible worlds w' which are accessible from w
        neighbors = [w_ for w_ in m.w if (w, w_) in m.r]
        for w_ in neighbors:
            depth += 1
            # check whether phi is true in w
            if verbose:
                print((depth * "  ") + "checking w" + (depth * "'") + " = " + repr(w_) + " ...")
            witness = self.phi.denot(m, g, w_)
            if witness:
                if verbose:
                    print((depth * 2 * " ") + "✓")
                depth -= 1
            # if not, we found a counter neighbor, the necessity statement is false, and we can stop checking
            else:
                if verbose:
                    print((depth * 2 * " ") + "✗")
                    print((depth * 2 * " ") + "counter neighbor: w" + (depth * "'") + " = " + repr(w_))
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
    @attr f: an interpretation function
    """
    pass


class PredModel(Model):
    """
    A model of predicate logic with domain, interpretation function and a set of assignment functions.

    A Model is a pair <D, F> with
      - D = domain of discourse
      - F = interpretation function assigning a denotation to each non-logical symbol

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
    @attr f: the interpretation function assigning denotations to the non-logical symbols
    @type f: dict[str,Any]
    @type gs: the assignment functions associated with the model
    @type gs: list[dict[str,str]]]
    """

    def __init__(self, d, f):
        self.d = d
        self.f = f
        dprod = cart_prod(list(d), len(vars))  # all ways of forming sets of |vars| long combinations of elements from D
        self.gs = [{str(v): a for (v, a) in zip(vars, distr)} for distr in dprod]

    def __repr__(self):
        return "Model M = (D,F) with\n" \
               "D = {" + ", ".join([repr(d) for d in self.d]) + "}\n" \
               "F = {\n" + ", \n".join(["     " + repr(key) + " ↦ " +
                                        (repr(val) if isinstance(val, str) else
                                         (", ".join(["(" + repr(key2) + " ↦ " + repr(val2) + ")"
                                                     for key2, val2 in val.items()])
                                          if isinstance(val, dict) else
                                          ("{" +
                                           ", ".join(["(" + ", ".join([repr(t) for t in s]) + ")" for s in val]) +
                                           "}")))
                                        for (key, val) in self.f.items()]) +\
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

    A ConstModalModel is a quadrupel <W,R,D,F> with
      - W = set of possible worlds
      - R = the accessibility relation, a binary relation on W
      - D = domain of discourse
      - F = interpretation function assigning to each member of w and each non-logical symbol a denotation
    and a set of assignment functions gs.

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
    @attr f: the interpretation function
    @type f: dict[str,dict[str,Any]]
    """
    # todo doesnt work yet (assignment function)
    def __init__(self, w, r, d, f):
        self.w = w
        self.r = r
        self.d = d
        self.f = f
        dprod = cart_prod(list(d), len(vars))  # all ways of forming sets of |vars| long combinations of elements from D
        self.gs = [{str(v): a for (v, a) in zip(vars, distr)} for distr in dprod]

    def __repr__(self):
        return "Model M = (W,R,D,F) with\n" \
               "W = {" + ", ".join([repr(w) for w in self.w]) + "}\n"\
               "R = {" + ", ".join([repr(r) for r in self.r]) + "}\n"\
               "D = {" + ", ".join([repr(d) for d in self.d]) + "}\n" \
               "F = {\n" +\
                    " \n".join(["    " + repr(w) + " ↦ \n" + \
                        ", \n".join(
                        ["           " + repr(keyF) + " ↦ " +
                         (repr(valF) if isinstance(valF, str) else
                          (", ".join(["(" + repr(keyF2) + " ↦ " + repr(valF2) + ")"
                                      for keyF2, valF2 in valF.items()])
                           if isinstance(valF, dict) else
                           ("{" +
                            ", ".join(["(" + ", ".join([repr(t) for t in s]) + ")" for s in valF]) +
                            "}")))
                        for (keyF, valF) in self.f[w].items()]) + \
                        "\n    "
                    for (w, fw) in self.f.items()]) +\
                    "}"


class VarModalModel(ModalModel):
    """
    A model of modal predicate logic with varying domains.

    A ConstModalModel is a quadrupel <W,R,D,F> with
      - W = set of possible worlds
      - R = the accessibility relation, a binary relation on W
      - D = an assignment of possible worlds to domains of discourse
      - F = interpretation function assigning to each member of w and each non-logical symbol a denotation
    and a set of assignment functions gs.

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
    @attr f: the interpretation function
    @type f: dict[str,dict[str,Any]]
    """

    def __init__(self, w, r, d, f):
        self.w = w
        self.r = r
        self.d = d
        self.f = f
        dprods = {w: cart_prod(list(self.d[w]), len(vars)) for w in self.w}  # all ways of forming sets of |vars| long combinations of elements from D
        self.gs = {w: [{str(v): a for (v, a) in zip(vars, distr)} for distr in dprods[w]] for w in self.w}

    def __repr__(self):
        return "Model M = (W,R,D,F) with\n" \
               "W = {" + ", ".join([repr(w) for w in self.w]) + "}\n" \
               "R = {" + ", ".join([repr(r) for r in self.r]) + "}\n" \
               "D = {\n" + \
                    ", \n".join([repr(w) + " ↦ " + \
                            ", ".join([repr(d) for d in self.d[w]]) + "}"
                    for w in self.w]) +\
                    "}\n" \
               "F = {\n" + \
                    ", \n".join(["    " + repr(w) + " ↦ " +\
                            ", \n".join(
                                ["         " + repr(keyF) + " ↦ " +
                                 (repr(valF) if isinstance(valF, str) else
                                  (", ".join(["(" + repr(keyF2) + " ↦ " + repr(valF2) + ")"
                                              for keyF2, valF2 in valF.items()])
                                   if isinstance(valF, dict) else
                                   ("{" +
                                    ", ".join(["(" + ", ".join([repr(t) for t in s]) + ")" for s in valF]) +
                                    "}")))
                                 for (keyF, valF) in self.f[w].items()]) + \
                            "\n    }"
                            for (w, fw) in self.f.items()]) + \
                    "}"


if __name__ == "__main__":
    # testset = ['a', 'b']
    # print(cart_prod(testset, 0))
    # print(cart_prod(testset, 1))
    # print(cart_prod(testset, 2))
    # print(cart_prod(testset, 3))
    # print()

    # Example 1: tupperware boxes, lids and a bunny
    ############################
    print("\n---------------------------------\n")
    ############################

    d1 = {"roundbox", "roundlid", "rectbox", "rectlid", "bunny"}
    f1 = {"b1": "roundbox", "b2": "rectbox", "f": "bunny",
          "box": {("roundbox", ), ("rectbox", )},
          "lid": {("roundlid", ), ("rectlid", )},
          "fit": {("roundlid", "roundbox"), ("rectlid", "rectbox")}
    }
    m1 = PredModel(d1, f1)
    g1 = {"x": "roundbox", "y": "bunny"}
    h1 = {"x": "bunny", "y": "rectbox"}

    print(m1)
    print("g1: " + repr(g1))
    print("h1: " + repr(h1))

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
        print()
        print(e)
        if nr <= 3:
            print(e.denot(m1, g1))
            depth = 0
            print(e.denot(m1, h1))
            depth = 0
        if nr > 3:
            print(e.denotG(m1))
            depth = 0

    # Example 2: MMiL
    #############################
    print("\n---------------------------------\n")
    ############################

    d2 = {"Mary", "Jane", "MMiL"}
    f2 = {"m": "Mary",
          "student": {("Mary", ), ("Jane", )},
          "book": {("MMiL", )},
          "read": {("Mary", "MMiL")}
    }
    m2 = PredModel(d2, f2)
    g2 = {"x": "Jane", "y": "Mary", "z": "MMiL"}

    print(m2)
    print("g = " + repr(g2))

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
        print(e)
        print(e.denot(m2, g2))
        depth = 0

    # Example 3: love #1 (ExSh 9 Ex. 1)
    #############################
    print("\n---------------------------------\n")
    #############################

    d3 = {"Mary", "John", "Peter"}
    f3 = {"j": "Peter", "p": "John",
          "woman": {("Mary",)},
          "man": {("John", ), ("Peter", )},
          "love": {("Mary", "John"), ("John", "Mary"), ("John", "John"), ("Peter", "Mary"), ("Peter", "John")},
          "jealous": {("Peter", "John", "Mary"), ("Peter", "Mary", "John")}}
    m3 = PredModel(d3, f3)
    g3 = {"x": "Mary", "y": "Mary", "z": "Peter"}
    h3 = {"x": "John", "y": "Peter", "z": "John"}

    print(m3)
    print("g = " + repr(g3))
    print("h = " + repr(h3))

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
                                            ))))
    }

    for nr, e in e3.items():
        print()
        print(e)
        if nr in [1, 2, 4, 5, 7, 8, 9]:
            print(e.denot(m3, g3))
            depth = 0
        elif nr in [3, 6, 10]:
            print(e.denot(m3, h3))
            depth = 0

    # Example 4: love #2
    #############################
    print("\n---------------------------------\n")
    #############################

    d4 = {"Mary", "John", "Susan"}
    f4 = {"m": "Mary", "j": "John", "s": "Susan",
          "rain": {},
          "sun": {()},
          "woman": {("Mary",), ("Susan",)}, "man": {("John",)},
          "love": {("John", "Mary"), ("Mary", "Susan"), ("Susan", "Mary"), ("Susan", "Susan")},
          "jealous": {("John", "Susan", "Mary")}}
    m4 = PredModel(d4, f4)
    g4 = m4.gs[5]

    print(m4)
    print("g = " + repr(g4))

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
        print()
        print(e)
        if 1 <= nr <= 4:
            print(e.denot(m4, g4))
            depth = 0
        if 4 <= nr <= 16:
            print(e.denotG(m4))
            depth = 0
        # if nr == 14:
        #     print(e.freevars())
        #     print(e.boundvars())

    # Example 5: term equality and function symbols
    #############################
    print("\n---------------------------------\n")
    #############################

    d5 = {"Mary", "Peter", "Susan", "Jane"}
    f5 = {"m": "Mary", "s": "Susan", "j": "Jane",
          "mother": {("Mary",): "Susan", ("Peter",): "Susan", ("Susan",): "Jane"}}
    m5 = PredModel(d5, f5)
    g5 = {"x": "Susan", "y": "Mary", "z": "Peter"}

    print(m5)
    print("g = " + repr(g5))

    e5 = {
        1: FuncTerm(Func("mother"), (Const("m"),)),  # Susan
        2: FuncTerm(Func("mother"), (FuncTerm(Func("mother"), (Const("m"),)),)),  # Jane
        3: Eq(FuncTerm(Func("mother"), (Const("m"),)), Const("s")),  # true
        4: Neg(Eq(Var("x"), Const("m")))  # true
    }

    for nr, e in e5.items():
        print()
        print(e)
        print(e.denot(m5, g5))
        depth = 0

    # Example 6: modal logic with constant domain
    #############################
    print("\n---------------------------------\n")
    #############################

    w6 = {"w1", "w2"}
    r6 = {("w1", "w1"), ("w1", "w2"), ("w2", "w2"), ("w2", "w2")}
    d6 = {"a"}
    f6 = {"w1": {"P": {()}},
          "w2": {"P": set()}}
    m6 = ConstModalModel(w6, r6, d6, f6)
    g6 = m6.gs[0]
    
    print(m6)
    print(g6)

    e6 = {
        1: Poss(Nec(Eq(Var("x"), Var("x")))),
        3: Nec(Disj(Atm(Pred("P"), tuple()), Neg(Atm(Pred("P"), tuple())))),
        2: Disj(Nec(Atm(Pred("P"), tuple())), Nec(Neg(Atm(Pred("P"), tuple()))))
    }
    
    for nr, e in e6.items():
        print()
        print(e)
        # print(e.denot(m6, g6, "w1"))
        # depth = 0
        # print(e.denot(m6, g6, "w2"))
        # depth = 0
        print(e.denotW(m6, g6))
        depth = 0

    # Example 6: modal logic with varying domain
    #############################
    print("\n---------------------------------\n")
    #############################

    w7 = {"w1", "w2"}
    r7 = {("w1", "w1"), ("w1", "w2"), ("w2", "w2"), ("w2", "w2")}
    d7 = {"w1": {"a"},
          "w2": {"a", "b"}}
    f7 = {"w1": {"P": {("a",)}},
          "w2": {"P": {("b",)}}}
    m7 = VarModalModel(w7, r7, d7, f7)

    print(m7)
    print(m7.gs)

    e7 = {
        1: Exists(Var("x"), Exists(Var("y"), Neg(Eq(Var("x"), Var("y")))))
    }

    for nr, e in e7.items():
        print()
        print(e)
        print(e.denot(m7, m7.gs["w1"][0], "w1"))
        depth = 0
        print(e.denot(m7, m7.gs["w2"][0], "w2"))
        depth = 0
        # print(e.denotG(m7))
        # print(e.denotW(m7, g7))
        # print(e.denotGW(m7))
        # depth = 0

    #############################
    print("\n---------------------------------\n")
    #############################
