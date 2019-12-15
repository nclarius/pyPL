"""
Simple interpreter for first-order logic with function symbols and equality.
Works only on models with finite domains (obviously) and languages with a finite set of individual variables.
© Natalie Clarius <natalie.clarius@student.uni-tuebingen.de>
"""


class Expr:
    """
    Well-formed expression of predicate logic.

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
    Term (constants, variables).
    """

    def denot(self, m, g):
        """
        @rtype: str
        """
        pass


class Const(Term):
    """
    Individual constant.
    j, m, ... c1, c2, ...

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

    When dealing with free and bound variables,
    it is necessary to reference the variables by their name (self.v)
    rather than the variable objects themselves (self)
    in order for variables with the same name to be identified, as desired in the theory.

    @attr v: the variable name
    @type v: str
    """
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
        The denotation of a function symbol applied to an appropriate number of terms is the individual that the
        interpretation function f assigns to the application.
        """
        return m.f[self.f.f][tuple([t.denot(m, g) for t in self.terms])]


class Pred(Expr):
    """
    Predicate.

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

    @method denotm: the truth value of a formula relative to a model m (without reference to a particular assignment)
    @type denotm: bool
    """

    def denot(self, m, g):
        """
        @rtype: bool
        """
        pass

    def denot_(self, m):
        """The truth value of a formula relative to a model m (without reference to a particular assignment).
        A formula is true in a model m iff it is true in m under all assignment functions.

        @param m: a model
        @type m: Model
        @return: the truth value of self in m
        @rtype: bool
        """
        # if the formula is closed, spare yourself the quantification over all assignment functions and pick an
        # arbitrary assignment (here: the first)
        if not self.freevars():
            return self.denot(m, m.gs[0])
        for g in m.gs:
            if not self.denot(m, g):
                print("counter assignment: g = " + repr(g))
                return False
        return True


class Eq(Formula):
    """
    Equality between terms.
    t_1 = t_2

    @attr t1: the left equality term
    @type t1: Term
    @attr t2: the right equality term
    @type t2: Term
    """

    def __init__(self, t1, t2):
        self.t1 = t1
        self.t2 = t2

    def __repr__(self):
        return repr(self.t1) + "=" + repr(self.t2)

    def freevars(self):
        return self.t1.freevars().union(self.t2.freevars())

    def boundvars(self):
        return self.t1.boundvars().union(self.t2.boundvars())

    def subst(self, v, a):
        return Eq(self.t1.subst(v, a), self.t2.subst(v, a))

    def denot(self, m, g):
        """
        The denotation of an equality t1 = t2 is true iff t1 and t2 denote the same individual.
        """
        return self.t1.denot(m, g) == self.t2.denot(m, g)


class Atm(Formula):
    """
    Atomic formula (predicate symbol applied to a number of terms).
    P(t_1, ..., t_n)

    Note that 1-place predications have to be specified as
    Atm('P', (t_1, ))
    rather than
    Atm('P', (t_1))
    or
    Atm('P', t_1).

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
        The denotation of an atomic predicate P(t_1, ..., t_n) is true iff the tuple of the denotation of the terms is
        an element of the interpretation of the predicate.
        """
        # print("iff <" + ",".join([("" if isinstance(t, Var) else "[[") + repr(t) + ("" if isinstance(t, Var) else "]]") for t in terms]) + "> ∈ F(" + self.pred + ")")
        # print("iff <" + ",".join([str(t.denot()) for t in terms]) + "> ∈ " + str(f[self.pred]))
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
        # for efficiency, restrict the domain of g to the variables that actually occur in the formula
        g_ = {v: g[v] for v in g if v in {self.v.v}.union(self.phi.freevars(), self.phi.boundvars())}
        xalts = [{**g_, str(self.v.v): d} for d in m.d]  # compute the x-alternatives (variant assignments)
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
        # for efficiency, restrict the domain of g to the variables that actually occur in the formula
        g_ = {v: g[v] for v in g if v in {self.v.v}.union(self.phi.freevars(), self.phi.boundvars())}
        xalts = [{**g_, str(self.v.v): d} for d in m.d]  # x-alternatives (variant assignments)
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


def cart_prod(a,n):
    """
    Compute the n-fold cartesian product of a list A.
    A x ... x A (n times)

    @param a: the list to form the cartesian product of
    @type a: list
    @param n: the arity of the cartesian product
    @type n: int
    @return: A^n
    @rtype: list[tuple]
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
    @type gs: list[Assmnt]
    """

    def __init__(self, d, f):
        self.d = d
        self.f = f
        varprod = cart_prod(d, len(vars))
        self.gs = [{str(v):a for (v,a) in zip(vars, p)} for p in varprod]

    def __repr__(self):
        return "Model M = (D,F) with\n" \
               "D = {" + ", ".join([repr(d) for d in self.d]) + "}\n" \
               "F = {\n" + ", \n".join(["     " + repr(key) + " ↦ " +
                                        (repr(val) if isinstance(val, str) or isinstance(val, dict) else
                                        ("{" +
                                         ", ".join(["(" + ", ".join([repr(t) for t in s]) + ")" for s in val]) +
                                         "}"))
                                        for (key, val) in self.f.items()]) +\
               "\n    }"


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
    
    d3 = {"Mary", "Peter", "Susan", "Jane"}
    f3 = {"m": "Mary", "s": "Susan", "j": "Jane",
          "mother": {("Mary", ): "Susan", ("Peter", ): "Susan", ("Susan", ): "Jane"}}
    m3 = Model(d3, f3)
    g3 = {"x": "Susan", "y": "Mary", "z": "Peter"}
    
    print(m3)
    print("g = " + repr(g3))
    
    e3 = {
        1: FuncTerm(Func("mother"), (Const("m"), )),  # Susan
        2: FuncTerm(Func("mother"), (FuncTerm(Func("mother"), (Const("m"),)), )),  # Jane
        3: Eq(FuncTerm(Func("mother"), (Const("m"), )), Const("s")),  # true
        4: Neg(Eq(Var("x"), Const("m")))  # true
    }

    for nr, e in e3.items():
        print()
        print(e)
        print(e.denot(m3, g3))

    print("\n---------------------------------\n")

    d1 = {"Mary", "John", "Susan"}
    f1 = {"m": "Mary", "j": "John", "s": "Susan",
         "woman": {("Mary",), ("Susan",)}, "man": {("John",)},
         "love": {("John", "Mary"), ("Mary", "Susan"), ("Susan", "Mary"), ("Susan", "Susan")},
         "jealous": {("John", "Susan", "Mary")}}
    m1 = Model(d1, f1)
    g1 = m1.gs[5]

    print(m1)
    print("g = " + repr(g1))
    
    e1 = {
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
    12: Forall(Var("x"), Imp(Atm(Pred("woman"), (Var("x"), )),
                                  Exists(Var("y"), Conj(Atm(Pred("man"), (Var("y"), )),
                                      Atm(Pred("love"), (Var("x"), Var("y"))))))),  # false
    13: Forall(Var("x"), Forall(Var("y"), Forall(Var("z"), Imp(
                                                     Conj(Conj(Atm(Pred("love"), (Var("x"), Var("y"))),
                                                          Atm(Pred("love"), (Var("y"), Var("z")))),
                                                          Neg(Atm(Pred("love"), (Var("y"), Var("x"))))),
                                                     Atm(Pred("jealous"), (Var("x"), Var("z"), Var("y")))
                                                     )))),  # true
    14: Conj(Exists(Var("x"), Atm(Pred("love"), (Var("x"), Var("x")))), Atm(Pred("woman"), (Var("x"), )))
    }

    for nr, e in e1.items():
        print()
        print(e)
        # evaluate expressions 1-4 relative to m1 and g1
        if 1 <= nr <= 4:
            print(e.denot(m1, g1))
        # evaluate expressions 4-13 relative to m1
        if 4 <= nr <= 13:
            print(e.denot_(m1))
        if nr == 14:
            print(e.freevars())
            print(e.boundvars())

    print("\n---------------------------------\n")

    d2 = {"Mary", "Jane", "MMiL"}
    f2 = {"m": "mary",
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
        5: Forall(Var("y"), Imp(Atm(Pred("student"), (Var("y"), )),
                                Exists(Var("x"),
                                       Conj(Atm(Pred("book"), (Var("x"), )),
                                            Atm(Pred("read"), (Var("y"), Var("z"))))))),
           # false, since Mary doesn't read a book
        6: Neg(Exists(Var("y"), Conj(Atm(Pred("student"), (Var("y"), )),
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
        # evaluate expressions 4-6 relative to m2
        if nr >= 4:
            print(e.denot_(m2))
