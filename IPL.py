# -*- coding: utf-8 -*-
"""
A naive model checker for intuitionistic first-order logic with Kripke semantics.
© Natalie Clarius <natalie.clarius@student.uni-tuebingen.de>

Features:
 - specification of expressions in a language of FOL
   - accepts languages with with propositional variables, 0-place predicates, function symbols and term equality
 - specification of Kripke models of IFOL with states, domain, interpretation function and variable assignments
 - evaluation of expressions (non-log. symbols, terms, open formulas, closed formulas)
   relative to models, states and variable assignments

Restrictions:
 - works only on finite models (obviously)
 - works only on languages with a finite set of individual variables
 - can't infer universal validity, logical inference etc., only truth in a given model

Known issues:
 - name of model, domain, interpr. func., variable assignment and state is not systematically recognized,
   instead always 'M', 'D', 'F', 'g', 'k' used in printout
 - efficiency: assignment functions have to be specified on all variables of the language;
   the domain is not restricted expression-wise to those variables that actually occur in the expression
 - depth has to be reset manually after each call of denot

Wish list:
 - print out detailed derivation rather than just final result of evaluation, possibly with LaTeX mode
 - more user-friendly input:
   - expression parser instead of the cumbersome PNF specification
   - a better way of dealing with singleton tuples
   - interactive mode/API instead of need to edit source code in order to set up input
 - model generation?
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
        Compute the denotation of the expression relative to a model m and assignment g.

        @param m: the model to evaluate the formula against
        @type m: Model
        @param g: the assignment to evaluate the formula against
        @type g: dict[str,str]
        @param k: the state to evaluate the formula against
        @type k: str
        @return: the denotation of the expression relative to the model m and assignment g
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
        f = m.f[k][k]
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
        f = m.f[k][k]
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

    def subst(self, v, t):
        return FuncTerm(self.f, map(lambda t: t.subst(v, t), self.terms))

    def denot(self, m, k, g):
        """
        The denotation of a function symbol applied to an appropriate number of terms is that individual that the
        interpretation function f assigns to the application.
        """
        f = m.f[k][k]
        return f[self.f.f][tuple([t.denot(m, k, g) for t in self.terms])]


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
        f = m.f[k]
        return f[self.p]


depth = 0  # keep track of the level of nesting


class Formula(Expr):
    """
    Formula.
    φ, ψ, ...

    @method denot: the truth value of a formula relative to a model m (without reference to a particular state)
    """

    def denot(self, m, k, g):
        """
        @rtype: bool
        """
        pass

    def denotK(self, m):
        """
        The truth value of a formula relative to a model M (without reference to a particular state).
        A formula is true in a model M iff it is true in M in the root state.

        @param m: a model
        @type m: KripkeModel
        @return: the truth value of self in m
        @rtype: bool
        """
        global depth

        # a formula is true in a model M iff it is true in the root state k0
        return self.denotG(m, "k0")

    def denotG(self, m, k):
        """
        The truth value of a formula relative to a model M and state k (w/o reference to a particular var. ass.).
        A formula is true in a model M and state k iff it is true in M and k under all assignments g.

        @param m: a model
        @type m: KripkeModel
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
        else:  # propositional model, compute empty assignment functions
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
        return (m.f[k][self.p] or
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
                print((depth * 2 * " ") + "checking g" + (depth * "'") + "(" + repr(self.v) + ") := " + repr(d) + " ...")
            witness = self.phi.denot(m, k, g_)
            # if yes, we found a witness, the existential statement is true, and we can stop checking
            if witness:
                if verbose:
                    print(((depth+1) * 2 * " ") + "✓")
                    print(((depth+1) * 2 * " ") + "witness: g" + (depth * "'") + "(" + repr(self.v) + ") := " + repr(d))
                depth -= 1
                return True
            if not witness:
                if verbose:
                    print(((depth+1) * 2 * " ") + "✗")
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
                    print((depth * 2 * " ") + "checking g" + (depth * "'") + "(" + repr(self.v) + ") := " + repr(d) + " ...")
                witness = self.phi.denot(m, k_, g_)
                if witness:
                    if verbose:
                        print(((depth+1) * 2 * " ") + "✓")
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


class KripkeModel():
    """
    A Kripke model of intuitionistic predicate logic.

    A ConstModalModel is a quadrupel <K,R,D,F> with
      - K = set of states
      - R = the accessibility relation, a binary relation on K
      - D = an assignment of possible worlds to domains of discourse
      - F = interpretation function assigning to each member of K and each non-logical symbol a denotation
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

         F = {'k0':  {'c': 'a', 'P': {('a', )}}, 'k0': {'c': 'a',  'P': {('a', ), ('b', )}}}

    @attr w: the set of states
    @type w: set[str]
    @attr r: the accessibility relation on self.k
    @type r: set[tuple[str,str]]
    @attr d: the mapping of states to domains of discourse
    @type d: dict[str,set[str]]
    @attr f: the interpretation function
    @type f: dict[str,dict[str,Any]]
    """

    def __init__(self, k, r, d, f):
        self.k = k
        self.r = r
        self.d = d
        self.f = f
        dprods = {k: cart_prod(list(self.d[k]), len(vars)) for k in self.k} if d else {}  # all ways of forming sets of |vars| long combinations of elements from D
        self.gs = {k: [{str(v): a for (v, a) in zip(vars, distr)} for distr in dprods[k]] for k in self.k} if d else {}

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
        return "Model M = (K,R,D,F) with\n" \
               "K = {" + ", ".join([repr(k) for k in self.k]) + "}\n" \
               "R = {" + ", ".join([repr(r) for r in self.r]) + "}\n" \
               "D = {\n" + \
                    (", \n".join([repr(k) + " ↦ " + \
                            ", ".join([repr(d) for d in self.d[k]]) + "}"
                    for k in self.k]) if self.d else "") +\
                    "}\n" \
               "F = {\n" + \
                    ", \n".join(["    " + repr(k) + " ↦ \n" +\
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
                                 for (keyF, valF) in self.f[k].items()]) + \
                            "\n    }"
                            for (k, fk) in self.f.items()]) + \
                    "}"


if __name__ == "__main__":

    # Example 1: counter model of p v -p and --p -> p
    #############################
    print("\n---------------------------------\n")
    #############################

    k1 = {"k0", "k1"}
    r1 = {("k0", "k1")}
    d1 = {}
    f1 = {"k0": {"p": False},
          "k1": {"p": True}}
    m1 = KripkeModel(k1, r1, d1, f1)

    print(m1)
    print(m1.r)
    print(m1.gs)

    e1 = {
        1: Disj(Prop("p"), Neg(Prop("p"))),
        2: Imp(Neg(Neg(Prop("p"))), Prop("p")),
        3: Neg(Neg(Disj(Prop("p"), Neg(Prop("p"))))),
        4: Prop("p"),
        5: Neg(Prop("p")),
        6: Neg(Neg(Prop("p")))
    }

    for nr, e in e1.items():
        print()
        print("[[" + repr(e) + "]]^M1 =")
        print(e.denotK(m1))
        depth = 0
        print()
        print("[[" + repr(e) + "]]^M1,k0 =")
        print(e.denotG(m1, "k0"))
        depth = 0
        print()
        print("[[" + repr(e) + "]]^M1,k1 =")
        print(e.denotG(m1, "k1"))
        depth = 0

    # Example 2: counter model of (p -> q) v (q -> p)
    #############################
    print("\n---------------------------------\n")
    #############################

    k2 = {"k0", "k1", "k2"}
    r2 = {("k0", "k1"), ("k0", "k2")}
    d2 = {}
    f2 = {"k0": {"p": False, "q": False},
          "k1": {"p": True, "q": False},
          "k2": {"p": False, "q": True}}
    m2 = KripkeModel(k2, r2, d2, f2)

    print(m2)
    print(m2.r)
    print(m2.gs)

    e2 = {
        1: Disj(Imp(Prop("p"), Prop("q")), Imp(Prop("q"), Prop("p")))
    }

    for nr, e in e2.items():
        print()
        print("[[" + repr(e) + "]]^M2 =")
        print(e.denotK(m2))
        depth = 0
    
    # Example 3: counter model of (p -> q) -> (-p v q)
    #############################
    print("\n---------------------------------\n")
    #############################

    k3 = {"k0", "k1", "k2", "k3"}
    r3 = {("k0", "k1"), ("k0", "k2"), ("k1", "k3"), ("k2", "k3")}
    d3 = {}
    f3 = {"k0": {"p": False, "q": False},
          "k1": {"p": False, "q": True},
          "k2": {"p": True, "q": True},
          "k3": {"p": True, "q": True}
          }
    m3 = KripkeModel(k3, r3, d3, f3)

    print(m3)
    print(m3.r)
    print(m3.gs)

    e3 = {
        1: Imp(Imp(Prop("p"), Prop("q")), Disj(Neg(Prop("p")), Prop("q"))),
        2: Imp(Prop("p"), Prop("q")),
        3: Disj(Neg(Prop("p")), Prop("q")),
        4: Neg(Prop("p")),
        5: Prop("q")
    }

    for nr, e in e3.items():
        print()
        if nr in [1]:
            print("[[" + repr(e) + "]]^M3 =")
            print(e.denotK(m3))
            depth = 0
        elif nr in [2]:
            print("[[" + repr(e) + "]]^M3,k3 =")
            print(e.denotG(m3, "k3"))
            depth = 0
            print("[[" + repr(e) + "]]^M3,k1 =")
            print(e.denotG(m3, "k1"))
            depth = 0
            print("[[" + repr(e) + "]]^M3,k0 =")
            print(e.denotG(m3, "k0"))
            depth = 0
        elif nr in [3, 4, 5]:
            print("[[" + repr(e) + "]]^M3,k0 =")
            print(e.denotG(m3, "k0"))
            depth = 0
