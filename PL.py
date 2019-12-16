# -*- coding: utf-8 -*-
"""
Simple interpreter for first-order logic with function symbols and equality.
Works only on models with finite domains (obviously) and languages with a finite set of individual variables.
© Natalie Clarius <natalie.clarius@student.uni-tuebingen.de>

Known issues:
- No interactive mode; source code has to be edited in order to set up input.
- Entering expressions is cumbersome.
- Entering singleton tuples is cumbersome.
- depth has to be reset manually after each call of denot.
- Efficiency: assignment functions are initialized once per model;
  the domain is not restricted expression-wise to those variables that actually occur in the expression.
- Name of model, domain, interpr. func. and variable assignment is not systematically recognized,
  instead always 'M', 'D', 'F', 'g' used in printout.
"""

verbose = False  # set this to True if you'd like intermediate steps to be printed out, and False otherwise
depth = 0  # keep track of the level of depth of quantification (don't change this)


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

    def denot(self, m, g):
        """
        Compute the denotation of the expression relative to a model m and assignment g.

        @param m: the model to evaluate the formula against
        @type m: Model
        @param g: the assignment to evaluate the formula against
        @type g: dict[str,str]
        @return: the denotation of the expression relative to the model m and assignment g
        """
        pass


class Term(Expr):
    """
    Term (constant, variable).
    t1, t2, ...
    """

    def denot(self, m, g):
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

    def denot(self, m, g):
        """
        The denotation of a constant is that individual that the interpretation function f assigns it.
        """
        return m.f[self.c]


class Var(Term):
    """
    Individual variable.
    x, y, z, u, v, w, x1, x2, ...

    @attr v: the variable name
    @type v: str
    """
    # NB: When dealing with variable occurrences in the further processing,
    # it will be  necessary to reference the variables by their name (self.v)
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

    def denot(self, m, g):
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

    def denot(self, m, g):
        """
        The denotation of a constant is that individual that the assignment function g assigns it.
        """
        return m.f[self.f]


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

    def denot(self, m, g):
        """
        The denotation of a function symbol applied to an appropriate number of terms is that individual that the
        interpretation function f assigns to the application.
        """
        return m.f[self.f.f][tuple([t.denot(m, g) for t in self.terms])]


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

    def denot(self, m, g):
        """
        The denotation of a predicate is the set of ordered tuples of individuals that the interpretation function f
        assigns it.
        """
        return m.f[self.p]


class Formula(Expr):
    """
    Formula.
    φ, ψ, ...

    @method denot_: the truth value of a formula relative to a model m (without reference to a particular assignment)
    """

    def denot(self, m, g):
        """
        @rtype: bool
        """
        pass

    def denot_(self, m):
        """
        The truth value of a formula relative to a model M (without reference to a particular assignment).
        A formula is true in a model M iff it is true in M under all assignment functions g.

        @param m: a model
        @type m: Model
        @return: the truth value of self in m
        @rtype: bool
        """
        global depth
        # for efficiency, restrict the domain of the assignment functions to the vars that actually occur in the formula
        var_occs = self.freevars().union(self.boundvars())
        gs_ = [{v: g[v] for v in g if v in var_occs} for g in m.gs]
        m.gs_ = [dict(tpl) for tpl in {tuple(g.items()) for g in gs_}]  # filter out duplicate assignment functions

        if not self.freevars():  # if the formula is closed,
            # spare yourself the quantification over all assignment functions and pick an arbitrary assignment
            # (here: the first)
            return self.denot(m, m.gs_[0])

        for g in m.gs_:  # otherwise, check the denotation for all assignment functions
            depth += 1
            if verbose:
                print((depth * " ") + "checking g = " + repr(g) + " ...")
            witness = self.denot(m, g)
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

    def denot(self, m, g):
        """
        The denotation of a term equality t1 = t2 is true iff t1 and t2 denote the same individual.
        """
        return self.t1.denot(m, g) == self.t2.denot(m, g)


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

    def denot(self, m, g):
        """
        The denotation of an atomic predication P(t1, ..., tn) is true iff the tuple of the denotation of the terms is
        an element of the interpretation of the predicate.
        """
        return tuple([t.denot(m,g) for t in self.terms]) in self.pred.denot(m, g)


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

    def denot(self, m, g):
        """
        The denotation of a negated formula Neg(phi) is true iff phi is false.
        """
        return not self.phi.denot(m,g)


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

    def denot(self, m, g):
        """
        The denotation of a conjoined formula Con(phi,psi) is true iff phi is true and psi is true.
        """
        return self.phi.denot(m,g) and self.psi.denot(m,g)


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

    def denot(self, m, g):
        """
        The denotation of a conjoined formula Disj(phi,psi) is true iff phi is true or psi is true.
        """
        return self.phi.denot(m,g) or self.psi.denot(m,g)


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

    def denot(self, m, g):
        """
        The denotation of an implicational formula Imp(phi,psi) is true iff phi is false or psi is true.
        """
        return not self.phi.denot(m,g) or self.psi.denot(m,g)


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

    def denot(self, m, g):
        """
        The denotation of an biimplicational formula Biimp(phi,psi) is true iff phi and psi have the same truth value.
        """
        return self.phi.denot(m,g) == self.psi.denot(m,g)


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

    def denot(self, m, g):
        """
        The denotation of an existentially quantified formula Exists(x, phi) is true
        iff phi is true under at least one x-alternative of g.
        """
        global depth
        depth += 1
        # quantify over the individuals in the domain
        for d in m.d:
            # compute the x-alternative g' (unpack g and overwrite the value for v with d)
            g_ = {**g, self.v.v: d}
            # check whether the current indiv. d under consideration makes phi true
            if verbose:
                print((depth * 2 * " ") + "checking g" + (depth * "'") + "(" + repr(self.v) + ") := " + repr(d) + " ...")
            witness = self.phi.denot(m, g_)
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

    def denot(self, m, g):
        """
        The denotation of universally quantified formula Forall(x, phi) is true iff
        phi is true under all x-alternatives of g.
        """
        global depth
        depth += 1
        # quantify over the individuals in the domain
        for d in m.d:
            # compute the x-alternative g' (unpack g and overwrite the value for v with d)
            g_ = {**g, self.v.v: d}
            # check whether the current indiv. d under consideration makes phi true
            if verbose:
                print((depth * 2 * " ") + "checking g" + (depth * "'") + "(" + repr(self.v) + ") := " + repr(d) + " ...")
            witness = self.phi.denot(m, g_)
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
    A model with domain and interpretation function.

    - The domain D is a set of objects, specified as strings:
       D = {'a', 'b', 'c', ...}

    - The interpretation function F is a dictionary with
      - non-logical symbols (specified as strings) as keys and
      - members/subsets/functions of D as values

       {'c': 'a', 'P': {('a', ), ('b', )}, 'f': {('c1',): 'a', ('c2',): 'b'}}

        - The denotation of individual constants has to be specified as a string:
           'c': 'a'

        - The denotation of predicates has to be specified as a set of tuples of members (strings) of D:
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

        - The denotation of function symbols has to be specified as a dictionary with tuples as keys:
           'f': {('c1',): 'a', ('c2',): 'b'}
           'h': {('c1', 'c2'): 'a'}

    @attr d: the domain of discourse
    @type d: set[str]
    @attr f: the interpretation function assigning denotations to the non-logical symbols
    @type f: dict[str,str]
    @type gs: the assignment functions associated with the model
    @type gs: list[Assmnt]
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


if __name__ == "__main__":
    # testset = ['a', 'b']
    # print(cart_prod(testset, 0))
    # print(cart_prod(testset, 1))# -*- coding: utf-8 -*-
"""
Simple interpreter for first-order logic with function symbols and equality.
Works only on models with finite domains (obviously) and languages with a finite set of individual variables.
© Natalie Clarius <natalie.clarius@student.uni-tuebingen.de>

Known issues:
- No interactive mode; source code has to be edited in order to set up input.
- Entering expressions is cumbersome.
- Entering singleton tuples is cumbersome.
- depth has to be reset manually after each call of denot.
- Efficiency: assignment functions are initialized once per model;
  the domain is not restricted expression-wise to those variables that actually occur in the expression.
- Name of model, domain, interpr. func. and variable assignment is not systematically recognized,
  instead always 'M', 'D', 'F', 'g' used in printout.
"""

verbose = False  # set this to True if you'd like intermediate steps to be printed out, and False otherwise
depth = 0  # keep track of the level of depth of quantification (don't change this)


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

    def denot(self, m, g):
        """
        Compute the denotation of the expression relative to a model m and assignment g.

        @param m: the model to evaluate the formula against
        @type m: Model
        @param g: the assignment to evaluate the formula against
        @type g: dict[str,str]
        @return: the denotation of the expression relative to the model m and assignment g
        """
        pass


class Term(Expr):
    """
    Term (constant, variable).
    t1, t2, ...
    """

    def denot(self, m, g):
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

    def denot(self, m, g):
        """
        The denotation of a constant is that individual that the interpretation function f assigns it.
        """
        return m.f[self.c]


class Var(Term):
    """
    Individual variable.
    x, y, z, u, v, w, x1, x2, ...

    @attr v: the variable name
    @type v: str
    """
    # NB: When dealing with variable occurrences in the further processing,
    # it will be  necessary to reference the variables by their name (self.v)
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

    def denot(self, m, g):
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

    def denot(self, m, g):
        """
        The denotation of a constant is that individual that the assignment function g assigns it.
        """
        return m.f[self.f]


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

    def denot(self, m, g):
        """
        The denotation of a function symbol applied to an appropriate number of terms is that individual that the
        interpretation function f assigns to the application.
        """
        return m.f[self.f.f][tuple([t.denot(m, g) for t in self.terms])]


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

    def denot(self, m, g):
        """
        The denotation of a predicate is the set of ordered tuples of individuals that the interpretation function f
        assigns it.
        """
        return m.f[self.p]


class Formula(Expr):
    """
    Formula.
    φ, ψ, ...

    @method denot_: the truth value of a formula relative to a model m (without reference to a particular assignment)
    """

    def denot(self, m, g):
        """
        @rtype: bool
        """
        pass

    def denot_(self, m):
        """
        The truth value of a formula relative to a model M (without reference to a particular assignment).
        A formula is true in a model M iff it is true in M under all assignment functions g.

        @param m: a model
        @type m: Model
        @return: the truth value of self in m
        @rtype: bool
        """
        global depth
        # for efficiency, restrict the domain of the assignment functions to the vars that actually occur in the formula
        var_occs = self.freevars().union(self.boundvars())
        gs_ = [{v: g[v] for v in g if v in var_occs} for g in m.gs]
        m.gs_ = [dict(tpl) for tpl in {tuple(g.items()) for g in gs_}]  # filter out duplicate assignment functions

        if not self.freevars():  # if the formula is closed,
            # spare yourself the quantification over all assignment functions and pick an arbitrary assignment
            # (here: the first)
            return self.denot(m, m.gs_[0])

        for g in m.gs_:  # otherwise, check the denotation for all assignment functions
            depth += 1
            if verbose:
                print((depth * " ") + "checking g = " + repr(g) + " ...")
            witness = self.denot(m, g)
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

    def denot(self, m, g):
        """
        The denotation of a term equality t1 = t2 is true iff t1 and t2 denote the same individual.
        """
        return self.t1.denot(m, g) == self.t2.denot(m, g)


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

    def denot(self, m, g):
        """
        The denotation of an atomic predication P(t1, ..., tn) is true iff the tuple of the denotation of the terms is
        an element of the interpretation of the predicate.
        """
        return tuple([t.denot(m,g) for t in self.terms]) in self.pred.denot(m, g)


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

    def denot(self, m, g):
        """
        The denotation of a negated formula Neg(phi) is true iff phi is false.
        """
        return not self.phi.denot(m,g)


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

    def denot(self, m, g):
        """
        The denotation of a conjoined formula Con(phi,psi) is true iff phi is true and psi is true.
        """
        return self.phi.denot(m,g) and self.psi.denot(m,g)


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

    def denot(self, m, g):
        """
        The denotation of a conjoined formula Disj(phi,psi) is true iff phi is true or psi is true.
        """
        return self.phi.denot(m,g) or self.psi.denot(m,g)


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

    def denot(self, m, g):
        """
        The denotation of an implicational formula Imp(phi,psi) is true iff phi is false or psi is true.
        """
        return not self.phi.denot(m,g) or self.psi.denot(m,g)


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

    def denot(self, m, g):
        """
        The denotation of an biimplicational formula Biimp(phi,psi) is true iff phi and psi have the same truth value.
        """
        return self.phi.denot(m,g) == self.psi.denot(m,g)


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

    def denot(self, m, g):
        """
        The denotation of an existentially quantified formula Exists(x, phi) is true
        iff phi is true under at least one x-alternative of g.
        """
        global depth
        depth += 1
        # quantify over the individuals in the domain
        for d in m.d:
            # compute the x-alternative g' (unpack g and overwrite the value for v with d)
            g_ = {**g, self.v.v: d}
            # check whether the current indiv. d under consideration makes phi true
            if verbose:
                print((depth * 2 * " ") + "checking g" + (depth * "'") + "(" + repr(self.v) + ") := " + repr(d) + " ...")
            witness = self.phi.denot(m, g_)
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

    def denot(self, m, g):
        """
        The denotation of universally quantified formula Forall(x, phi) is true iff
        phi is true under all x-alternatives of g.
        """
        global depth
        depth += 1
        # quantify over the individuals in the domain
        for d in m.d:
            # compute the x-alternative g' (unpack g and overwrite the value for v with d)
            g_ = {**g, self.v.v: d}
            # check whether the current indiv. d under consideration makes phi true
            if verbose:
                print((depth * 2 * " ") + "checking g" + (depth * "'") + "(" + repr(self.v) + ") := " + repr(d) + " ...")
            witness = self.phi.denot(m, g_)
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
    A model with domain and interpretation function.

    - The domain D is a set of objects, specified as strings:
       D = {'a', 'b', 'c', ...}

    - The interpretation function F is a dictionary with
      - non-logical symbols (specified as strings) as keys and
      - members/subsets/functions of D as values

       {'c': 'a', 'P': {('a', ), ('b', )}, 'f': {('c1',): 'a', ('c2',): 'b'}}

        - The denotation of individual constants has to be specified as a string:
           'c': 'a'

        - The denotation of predicates has to be specified as a set of tuples of members (strings) of D:
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

        - The denotation of function symbols has to be specified as a dictionary with tuples as keys:
           'f': {('c1',): 'a', ('c2',): 'b'}
           'h': {('c1', 'c2'): 'a'}

    @attr d: the domain of discourse
    @type d: set[str]
    @attr f: the interpretation function assigning denotations to the non-logical symbols
    @type f: dict[str,str]
    @type gs: the assignment functions associated with the model
    @type gs: list[Assmnt]
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


if __name__ == "__main__":
    # testset = ['a', 'b']
    # print(cart_prod(testset, 0))
    # print(cart_prod(testset, 1))
    # print(cart_prod(testset, 2))
    # print(cart_prod(testset, 3))
    # print()

    # Example 1: tupperware boxes and lids
    ############################
    print("\n---------------------------------\n")
    ############################

    d1 = {"roundbox", "roundlid", "rectbox", "rectlid", "bunny"}
    f1 = {"b1": "roundbox", "b2": "rectbox", "f": "bunny",
          "box": {("roundbox", ), ("rectbox", )},
          "lid": {("roundlid", ), ("rectlid", )},
          "fit": {("roundlid", "roundbox"), ("rectlid", "rectbox")}
    }
    m1 = Model(d1, f1)
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
            print(e.denot_(m1))
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
    m2 = Model(d2, f2)
    g2 = {"x": "Jane", "y": "Mary"}

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
           # false, since Mary doesn't read a book
        7: Neg(Exists(Var("y"), Conj(Atm(Pred("student"), (Var("y"), )),
                                     Exists(Var("x"),
                                            Conj(Atm(Pred("book"), (Var("x"), )),
                                                 Atm(Pred("read"), (Var("y"), (Var("z")))))))))
           # false, since Mary reads a book
    }

    for nr, e in e2.items():
        print()
        print(e)
        # evaluate expressions 1-4 relative to m2 and g2
        if nr <= 4:
            print(e.denot(m2, g2))
            depth = 0
        # evaluate expressions 4-6 relative to m2
        if nr >= 4:
            print(e.denot_(m2))
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
    m3 = Model(d3, f3)
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
    m4 = Model(d4, f4)
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
        13: Forall(Var("x"), Forall(Var("y"), Forall(Var("z"), Imp(
            Conj(Conj(Atm(Pred("love"), (Var("x"), Var("y"))),
                      Atm(Pred("love"), (Var("y"), Var("z")))),
                 Neg(Atm(Pred("love"), (Var("y"), Var("x"))))),
            Atm(Pred("jealous"), (Var("x"), Var("z"), Var("y")))
        )))),  # true
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
            print(e.denot_(m4))
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
    m5 = Model(d5, f5)
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

    #############################
    print("\n---------------------------------\n")
    #############################

    # print(cart_prod(testset, 2))
    # print(cart_prod(testset, 3))
    # print()

    # Example 1: tupperware boxes and lids
    ############################
    print("\n---------------------------------\n")
    ############################

    d1 = {"roundbox", "roundlid", "rectbox", "rectlid", "bunny"}
    f1 = {"b1": "roundbox", "b2": "rectbox", "f": "bunny",
          "box": {("roundbox", ), ("rectbox", )},
          "lid": {("roundlid", ), ("rectlid", )},
          "fit": {("roundlid", "roundbox"), ("rectlid", "rectbox")}
    }
    m1 = Model(d1, f1)
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
            print(e.denot_(m1))
            depth = 0

    # # Example 2: MMiL
    # #############################
    # print("\n---------------------------------\n")
    # ############################
    #
    # d2 = {"Mary", "Jane", "MMiL"}
    # f2 = {"m": "Mary",
    #       "student": {("Mary", ), ("Jane", )},
    #       "book": {("MMiL", )},
    #       "read": {("Mary", "MMiL")}
    # }
    # m2 = Model(d2, f2)
    # g2 = {"x": "Jane", "y": "Mary"}
    #
    # print(m2)
    # print("g = " + repr(g2))
    #
    # e2 = {
    #     1: Var("x"),  # Jane
    #     2: Const("m"),  # Mary
    #     3: Pred("read"),  # {(Mary, MMiL)}
    #     4: Atm(Pred("book"), (Var("x"), )),  # false, since Jane is not a book
    #     5: Exists(Var("x"), Conj(Atm(Pred("book"), (Var("x"),)), Atm(Pred("read"), (Const("m"), Var("x"))))),  # true
    #     6: Forall(Var("y"), Imp(Atm(Pred("student"), (Var("y"), )),
    #                             Exists(Var("x"),
    #                                    Conj(Atm(Pred("book"), (Var("x"), )),
    #                                         Atm(Pred("read"), (Var("y"), Var("z"))))))),
    #        # false, since Mary doesn't read a book
    #     7: Neg(Exists(Var("y"), Conj(Atm(Pred("student"), (Var("y"), )),
    #                                  Exists(Var("x"),
    #                                         Conj(Atm(Pred("book"), (Var("x"), )),
    #                                              Atm(Pred("read"), (Var("y"), (Var("z")))))))))
    #        # false, since Mary reads a book
    # }
    #
    # for nr, e in e2.items():
    #     print()
    #     print(e)
    #     # evaluate expressions 1-4 relative to m2 and g2
    #     if nr <= 4:
    #         print(e.denot(m2, g2))
    #         depth = 0
    #     # evaluate expressions 4-6 relative to m2
    #     if nr >= 4:
    #         print(e.denot_(m2))
    #         depth = 0
    #
    # # Example 3: love #1 (ExSh 9 Ex. 1)
    # #############################
    # print("\n---------------------------------\n")
    # #############################
    #
    # d3 = {"Mary", "John", "Peter"}
    # f3 = {"j": "Peter", "p": "John",
    #       "woman": {("Mary",)},
    #       "man": {("John", ), ("Peter", )},
    #       "love": {("Mary", "John"), ("John", "Mary"), ("John", "John"), ("Peter", "Mary"), ("Peter", "John")},
    #       "jealous": {("Peter", "John", "Mary"), ("Peter", "Mary", "John")}}
    # m3 = Model(d3, f3)
    # g3 = {"x": "Mary", "y": "Mary", "z": "Peter"}
    # h3 = {"x": "John", "y": "Peter", "z": "John"}
    #
    # print(m3)
    # print("g = " + repr(g3))
    # print("h = " + repr(h3))
    #
    # e3 = {
    #     1: Const("p"),
    #     2: Var("y"),
    #     3: Var("y"),
    #     4: Atm(Pred("love"), (Const("p"), Const("j"))),
    #     5: Atm(Pred("love"), (Var("y"), Var("z"))),
    #     6: Atm(Pred("love"), (Var("y"), Var("z"))),
    #     7: Exists(Var("x"), Neg(Atm(Pred("love"), (Const("j"), Var("x"))))),
    #     8: Forall(Var("x"), Exists(Var("y"), Atm(Pred("love"), (Var("x"), Var("y"))))),
    #     9: Neg(Forall(Var("x"), Imp(Atm(Pred("woman"), (Var("x"),)),
    #                                  Exists(Var("y"), Conj(Atm(Pred("man"), (Var("y"),)),
    #                                                        Atm(Pred("love"), (Var("x"), Var("y"))))
    #                                         ))))
    # }
    #
    # for nr, e in e3.items():
    #     print()
    #     print(e)
    #     if nr in [1, 2, 4, 5, 7, 8, 9]:
    #         print(e.denot(m3, g3))
    #         depth = 0
    #     elif nr in [3, 6, 10]:
    #         print(e.denot(m3, h3))
    #         depth = 0
    #
    # # Example 4: love #2
    # #############################
    # print("\n---------------------------------\n")
    # #############################
    #
    # d4 = {"Mary", "John", "Susan"}
    # f4 = {"m": "Mary", "j": "John", "s": "Susan",
    #       "rain": {},
    #       "sun": {()},
    #       "woman": {("Mary",), ("Susan",)}, "man": {("John",)},
    #       "love": {("John", "Mary"), ("Mary", "Susan"), ("Susan", "Mary"), ("Susan", "Susan")},
    #       "jealous": {("John", "Susan", "Mary")}}
    # m4 = Model(d4, f4)
    # g4 = m4.gs[5]
    #
    # print(m4)
    # print("g = " + repr(g4))
    #
    # e4 = {
    #     1: Var("x"),  # Susan
    #     2: Const("j"),  # John
    #     3: Pred("love"),  # {(J,M), (M,S), (S,M), (S,S)}
    #     4: Atm(Pred("love"), (Var("x"), Const("m"))),  # true under g, false in m
    #     5: Atm(Pred("love"), (Const("j"), Const("m"))),  # true
    #     6: Exists(Var("x"), Atm(Pred("love"), (Const("j"), Var("x")))),  # true
    #     7: Forall(Var("x"), Atm(Pred("love"), (Const("j"), Var("x")))),  # false
    #     8: Conj(Atm(Pred("love"), (Const("m"), Const("s"))), Atm(Pred("love"), (Const("s"), Const("m")))),  # true
    #     9: Forall(Var("x"), Imp(Atm(Pred("love"), (Const("s"), Var("x"))), Atm(Pred("woman"), (Var("x"),)))),  # true
    #     10: Neg(Exists(Var("x"), Atm(Pred("love"), (Var("x"), Var("x"))))),  # false
    #     11: Neg(Forall(Var("x"), Atm(Pred("love"), (Var("x"), Var("x"))))),  # true
    #     12: Forall(Var("x"), Imp(Atm(Pred("woman"), (Var("x"),)),
    #                              Exists(Var("y"), Conj(Atm(Pred("man"), (Var("y"),)),
    #                                                    Atm(Pred("love"), (Var("x"), Var("y"))))))),  # false
    #     13: Forall(Var("x"), Forall(Var("y"), Forall(Var("z"), Imp(
    #         Conj(Conj(Atm(Pred("love"), (Var("x"), Var("y"))),
    #                   Atm(Pred("love"), (Var("y"), Var("z")))),
    #              Neg(Atm(Pred("love"), (Var("y"), Var("x"))))),
    #         Atm(Pred("jealous"), (Var("x"), Var("z"), Var("y")))
    #     )))),  # true
    #     14: Conj(Exists(Var("x"), Atm(Pred("love"), (Var("x"), Var("x")))), Atm(Pred("woman"), (Var("x"),))),
    #     15: Atm(Pred("rain"), ()),
    #     16: Atm(Pred("sun"), ())
    # }
    #
    # for nr, e in e4.items():
    #     print()
    #     print(e)
    #     if 1 <= nr <= 4:
    #         print(e.denot(m4, g4))
    #         depth = 0
    #     if 4 <= nr <= 16:
    #         print(e.denot_(m4))
    #         depth = 0
    #     # if nr == 14:
    #     #     print(e.freevars())
    #     #     print(e.boundvars())
    #
    # # Example 5: term equality and function symbols
    # #############################
    # print("\n---------------------------------\n")
    # #############################
    #
    # d5 = {"Mary", "Peter", "Susan", "Jane"}
    # f5 = {"m": "Mary", "s": "Susan", "j": "Jane",
    #       "mother": {("Mary",): "Susan", ("Peter",): "Susan", ("Susan",): "Jane"}}
    # m5 = Model(d5, f5)
    # g5 = {"x": "Susan", "y": "Mary", "z": "Peter"}
    #
    # print(m5)
    # print("g = " + repr(g5))
    #
    # e5 = {
    #     1: FuncTerm(Func("mother"), (Const("m"),)),  # Susan
    #     2: FuncTerm(Func("mother"), (FuncTerm(Func("mother"), (Const("m"),)),)),  # Jane
    #     3: Eq(FuncTerm(Func("mother"), (Const("m"),)), Const("s")),  # true
    #     4: Neg(Eq(Var("x"), Const("m")))  # true
    # }
    #
    # for nr, e in e5.items():
    #     print()
    #     print(e)
    #     print(e.denot(m5, g5))
    #     depth = 0
    #
    # #############################
    # print("\n---------------------------------\n")
    # #############################
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
    m2 = Model(d2, f2)
    g2 = {"x": "Jane", "y": "Mary"}

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
           # false, since Mary doesn't read a book
        7: Neg(Exists(Var("y"), Conj(Atm(Pred("student"), (Var("y"), )),
                                     Exists(Var("x"),
                                            Conj(Atm(Pred("book"), (Var("x"), )),
                                                 Atm(Pred("read"), (Var("y"), (Var("z")))))))))
           # false, since Mary reads a book
    }

    for nr, e in e2.items():
        print()
        print(e)
        # evaluate expressions 1-4 relative to m2 and g2
        if nr <= 4:
            print(e.denot(m2, g2))
            depth = 0
        # evaluate expressions 4-6 relative to m2
        if nr >= 4:
            print(e.denot_(m2))
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
    m3 = Model(d3, f3)
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
    m4 = Model(d4, f4)
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
        13: Forall(Var("x"), Forall(Var("y"), Forall(Var("z"), Imp(
            Conj(Conj(Atm(Pred("love"), (Var("x"), Var("y"))),
                      Atm(Pred("love"), (Var("y"), Var("z")))),
                 Neg(Atm(Pred("love"), (Var("y"), Var("x"))))),
            Atm(Pred("jealous"), (Var("x"), Var("z"), Var("y")))
        )))),  # true
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
            print(e.denot_(m4))
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
    m5 = Model(d5, f5)
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

    #############################
    print("\n---------------------------------\n")
    #############################
