"""
Simple predicate logic interpreter.
Works only on models with finite domains (obviously) and languages with a finite set of individual variables.
© Natalie Clarius <natalie.clarius@student.uni-tuebingen.de>
"""


class Expr:
    """
    Well-formed expressions of predicate logic.

    @method subst: substitution of a term for a variable in a formula
    @method denot: denotation of the expression relative to a model m and assignment g
    """

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
    Terms (constants, variables).
    """

    def denot(self, m, g):
        """
        @rtype: D
        """
        pass


class Const(Term):
    """
    Individual constants.

    @attr c: the constant symbol
    @type c: str
    """

    def __init__(self, c):
        self.c = c

    def __repr__(self):
        return self.c

    def subst(self, v, a):
        return self

    def denot(self, m, g):
        """
        The denotation of a constant is that individual that the interpretation function f assigns it.
        """
        return m.f[self.c]


class Var(Term):
    """
    Individual variables.

    @attr v: the variable symbol
    @type v: str
    """
    def __init__(self, v):
        self.v = v

    def __repr__(self):
        return self.v

    def subst(self, v, a):
        if self.v == v:
            return Var(a)
        else:
            return self

    def denot(self, m, g):
        """
        The denotation of a constant is that individual that the assignment function g assigns it.
        """
        return g[self.v]


class Pred(Expr):
    """
    Predicate.

    @attr p: the predicate symbol
    @type p: str
    """
    def __init__(self, p):
        self.p = p

    def __repr__(self):
        return self.p

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
    Formulas.

    @method denotm: the truth value of a formula relative to a model m (without reference to a particular assignment)
    """

    def denot(self, m, g):
        """
        @rtype: bool
        """
        pass

    def denotm(self, m):
        """The truth value of a formula relative to a model m (without reference to a particular assignment).
        A formula is true in a model m iff it is true in m under all assignment functions.

        @param m: a model
        @type m: model
        @return: the truth value of self in m
        @rtype: bool
        """
        for g in m.gs:
            if not self.denot(m, g):
                print("counter assignment: g = " + repr(g))
                return False
        return True


class Atm(Formula):
    """
    Atomic formula (predicate symbol applied to a number of terms).
    P(t_1, ..., t_n)

    @attr pred: the predicate symbol
    @type pred: str
    @attr terms: the terms to apply the predicate symbol to
    @type terms: tuple[Term]
    """
    def __init__(self, pred, terms):
        self.pred = pred
        self.terms = terms

    def __repr__(self):
        return self.pred + "(" + ",".join([repr(t) for t in self.terms]) + ")"

    def subst(self, v, a):
        return Atm(self.pred, map(lambda t: t.subst(v, a), self.terms))

    def denot(self, m, g):
        """
        The denotation of an atomic predicate P(t_1, ..., t_n) is true iff the tuple of the denotation of the terms is
        an element of the interpretation of the predicate.
        """
        # print("iff <" + ",".join([("" if isinstance(t, Var) else "[[") + repr(t) + ("" if isinstance(t, Var) else "]]") for t in terms]) + "> ∈ F(" + self.pred + ")")
        # print("iff <" + ",".join([str(t.denot()) for t in terms]) + "> ∈ " + str(f[self.pred]))
        return tuple([t.denot(m,g) for t in self.terms]) in m.f[self.pred]


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
        return "¬" + repr(self.phi)

    def subst(self, v, a):
        return Neg(self.phi.subst(v, a))

    def denot(self, m, g):
        """
        The denotation of a negated formula Neg(phi) is true iff phi is false.
        """
        # print("iff [[" + repr(self.phi) + "]] = 0")
        return not self.phi.denot(m,g)


class Conj(Formula):
    """
    Conjunciton.
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
        return "(" + repr(self.phi) + "∧" + repr(self.psi) + ")"

    def subst(self, v, a):
        return Conj(self.phi.subst(v, a), self.psi.subst(v, a))

    def denot(self, m, g):
        """
        The denotation of a conjoined formula Con(phi,psi) is true iff phi is true and psi is true.
        """
        # print("iff [[" + repr(self.phi) + "]] = 1 and [[" + repr(self.psi) + "]] = 1")
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
        return "(" + repr(self.phi) + "∨" + repr(self.psi) + ")"

    def subst(self, v, a):
        return Disj(self.phi.subst(v, a), self.psi.subst(v, a))

    def denot(self, m, g):
        """
        The denotation of a conjoined formula Disj(phi,psi) is true iff phi is true or psi is true.
        """
        # print("iff [[" + repr(self.phi) + "]] = 1 or [[" + repr(self.psi) + "]] = 1")
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
        return "(" + repr(self.phi) + "→" + repr(self.psi) + ")"

    def subst(self, v, a):
        return Imp(self.phi.subst(v, a), self.psi.subst(v, a))

    def denot(self, m, g):
        """
        The denotation of an implicational formula Imp(phi,psi) is true iff phi is false or psi is true.
        """
        # print("iff [[" + repr(self.phi) + "]] = 0 or [[" + repr(self.psi) + "]] = 1")
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
        return "(" + repr(self.phi) + "↔" + repr(self.psi) + ")"

    def subst(self, v, a):
        return Biimp(self.phi.subst(v, a), self.psi.subst(v, a))

    def denot(self, m, g):
        """
        The denotation of an biimplicational formula Biimp(phi,psi) is true iff phi and psi have the same truth value.
        """
        # print("iff [[" + repr(self.phi) + "]] = [[" + repr(self.psi) + "]]")
        return (self.phi.denot(m,g) and self.psi.denot(m,g)) or (not self.phi.denot(m,g) and not self.psi.denot(m,g))


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
        return "∃" + repr(self.v) + repr(self.phi)

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
        xalts = [{**g, **{str(self.v.v):a}} for a in m.d]  # compute the x-alternatives (variant assignments)
        # print("iff f.a. d ∈ D: [[" + repr(self.phi) + "]]d = 1")
        for h in xalts:  # quantify over the x-alternatives
            # print("checking g(" + self.v + ") = " + j[self.v] + " ...")
            # print("• " + a + ":"
            witness = self.phi.denot(m,h)  # check whether the current indiv. under consideration makes phi true
            # print(witness)
            if witness:  # if yes, we found a witness, the existential statement is true, and we can stop checking
                print("witness: g(" + repr(self.v) + ") = " + h[self.v.v])
                return True
        return False  # if no witness has been found, the existential statement is false


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
        return "∀" + repr(self.v) + repr(self.phi)

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
        xalts = [{**g, **{str(self.v.v):a}} for a in m.d]  # x-alternatives (variant assignments)
        # print("iff f.a. d ∈ D: [[" + repr(self.phi) + "]]d = 1")
        # quantify over the x-alternatives
        for h in xalts:
            # print("checking g(" + self.v + ") = " + j[self.v] + " ...")
            # print("• " + a + ":")
            witness = self.phi.denot(m,h)  # check whether the current indiv. under consideration makes phi true
            # print(witness)
            if not witness:  # if not, we found a counter witness, the universal statement is false, and we can stop checking
                print("counter witness: g(" + repr(self.v) + ") = " + h[self.v.v])
                return False
        return True  # if no counter witness has been found, the universal statement is true


def cart_prod(s,n):
    """
    Compute the n-fold cartesian product of a set s.
    S x ... x S (n times)

    @param s: the set to form the cartesian product of
    @type s: set
    @param n: the arity of the cartesian product
    @type n: int
    @return: S^n
    @rtype: set[tuple]
    """
    if n == 0:
        res = []
    else:
        res = [[s] for s in s]
        for i in range(n-1):
            res = [t+[a] for t in res for a in s]
    res = [tuple(el) for el in res]
    return res


var = [Var("x"), Var("y"), Var("z"), Var("u"), Var("v"), Var("w")]  # the individual variables of the language


class Model:
    """
    A model with domain and interpretation function.

    Note that the denotation of 1-place predicates (set of individuals) has to be specified as
    'P': {('a', ), ('b', ), ('c', )}
    rather than
    'P': {('a'), ('b'), ('c')}
    or
    'P': {'a','b','c'}.

    @attr d: the domain of discourse
    @type d: set[str]
    @attr f: the interpretation function assigning denotations to the non-logical symbols
    @type f: dict[str,str]
    @type gs: the assignment functions associated with the model
    @type gs: list[dict[str,str]]
    """
    def __init__(self, d, f):
        self.d = d
        self.f = f
        varprod = cart_prod(d, len(var))
        self.gs = [{str(v):a for (v,a) in zip(var, p)} for p in varprod]


if __name__ == "__main__":
    # testset = ['a', 'b']
    # print(cart_prod(testset, 0))
    # print(cart_prod(testset, 1))
    # print(cart_prod(testset, 2))
    # print(cart_prod(testset, 3))
    # print()

    ##########
    # Examples
    ##########

    d = {"Mary", "John", "Susan"}
    f = {"m": "Mary", "j": "John", "s": "Susan",
         "woman": {("Mary",), ("Susan",)}, "man": {("John",)},
         "love": {("John", "Mary"), ("Mary", "Susan"), ("Susan", "Mary"), ("Susan", "Susan")},
         "jealous": {("John", "Susan", "Mary")}}
    m = Model(d, f)
    g = m.gs[30]

    print("M = (D,F) where")
    print("D = " + repr(d))
    print("F = " + repr(f))
    # for g in m.gs:
    #     print(g)
    print("g = " + repr(g))

    e01 = Var("x")
    e02 = Const("j")
    e03 = Pred("love")
    e04 = Atm("love", (Const("j"), Const("m")))
    e05 = Atm("love", (Var("x"), Const("m")))
    e06 = Exists(Var("x"), Atm("love", (Const("j"), Var("x"))))
    e07 = Forall(Var("x"), Atm("love", (Const("j"), Var("x"))))
    e08 = Conj(Atm("love", (Const("m"), Const("s"))), Atm("love", (Const("s"), Const("m"))))
    e09 = Forall(Var("x"), Imp(Atm("love", (Const("s"), Var("x"))), Atm("woman", (Var("x"),))))
    e10 = Neg(Exists(Var("x"), Atm("love", (Var("x"), Var("x")))))
    e11 = Neg(Forall(Var("x"), Atm("love", (Var("x"), Var("x")))))
    e12 = Forall(Var("x"), Imp(Atm("woman", (Var("x"), )),
                                  Exists(Var("y"), Conj(Atm("man", (Var("y"), )),
                                      Atm("love", (Var("x"), Var("y")))))))

    print()
    print(e01)
    print(e01.denot(m, g))
    print()
    print(e02)
    print(e02.denot(m, g))
    print()
    print(e03)
    print(e03.denot(m, g))
    print()
    print(e03)
    print(e03.denot(m, g))
    print()
    print()
    print(e04)
    print(e04.denot(m, g))
    print()
    print(e05)
    print(e05.denot(m, g))
    print()
    print(e05)
    print(e05.denotm(m))
    print()
    print(e06)
    print(e06.denot(m, g))
    print()
    print(e07)
    print(e07.denot(m, g))
    print()
    print(e08)
    print(e08.denot(m, g))
    print()
    print(e09)
    print(e09.denot(m, g))
    print()
    print(e10)
    print(e10.denot(m, g))
    print()
    print(e11)
    print(e11.denot(m, g))
    print()
    print(e12)
    print(e12.denot(m, g))
