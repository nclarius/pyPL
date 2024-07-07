#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Define proof construction programs (lambda mu terms) associated with formulas.
"""

class Constr:
    def __repr__(self):
        return str(self)

    def tex(self) -> str:
        """
        The expression formatted in LaTeX code.

        @return self in LaTeX code
        @rtype str
        """

class CVar(Constr):
    def __init__(self, var: str):
        self.var = var

    def __str__(self):
        return self.var

    def tex(self) -> str:
        return self.var

    def __eq__(self, other):
        return isinstance(other, IVar) and self.u == other.u

    def __len__(self):
        return 1


class Unit(Constr):
    def __str__(self):
        return 'unit'

    def tex(self) -> str:
        return f'\\text{{unit}}'

    def __eq__(self, other):
        return isinstance(other, Unit)

    def __len__(self):
        return 1

class Empty(Constr):
    def __str__(self):
        return 'empty'

    def tex(self) -> str:
        return f'\\empty'

    def __eq__(self, other):
        return isinstance(other, Empty)

    def __len__(self):
        return 1

class Pair(Constr):
    def __init__(self, x: Constr, y: Constr):
        self.x = x
        self.y = y

    def __str__(self):
        return f'⟨{str(self.x)}, {str(self.y)}⟩'

    def tex(self) -> str:
        return f'\\langle{self.x.tex()}, {self.y.tex()}\\rangle'

    def __eq__(self, other):
        return isinstance(other, Pair) and self.x == other.x and self.y == other.y

    def __len__(self):
        return 1 + len(self.x) + len(self.y)

class Fst(Constr):
    def __init__(self, p: Constr):
        self.p = p

    def __str__(self):
        return f'π₁ {str(self.p)}'

    def tex(self) -> str:
        return f'\\pi_1 {self.p.tex()}'

    def __eq__(self, other):
        return isinstance(other, Fst) and self.p == other.p

    def __len__(self):
        return 1 + len(self.p)

class Snd(Constr):
    def __init__(self, p: Constr):
        self.p = p

    def __str__(self):
        return f'π₂ {str(self.p)}'

    def tex(self) -> str:
        return f'\\pi_2 {self.p.tex()}'

    def __eq__(self, other):
        return isinstance(other, Snd) and self.p == other.p

    def __len__(self):
        return 1 + len(self.p)

class Either(Constr):
    def __init__(self,Constr, r: Constr):
        self.l = l
        self.r = r

    def __str__(self):
        return f'[{str(self.l)}, {str(self.r)}]'

    def tex(self) -> str:
        return f'\\lbrack {self.l.tex()}, {self.r.tex()} \\rbrack'

    def __eq__(self, other):
        return isinstance(other, Case) and self.l == other.l and self.r == other.r

    def __len__(self):
        return 1 + len(self.x) + len(self.l) + len(self.r)

class Inl(Constr):
    def __init__(self, x: Constr):
        self.x = x

    def __str__(self):
        return f'ι₁ {str(self.x)}'

    def tex(self) -> str:
        return f'\\iota_1 {self.x.tex()}'

    def __eq__(self, other):
        return isinstance(other, Inl) and self.x == other.x

    def __len__(self):
        return 1 + len(self.x)

class Inr(Constr):
    def __init__(self, x: Constr):
        self.x = x

    def __str__(self):
        return f'ι₂ {str(self.x)}'

    def tex(self) -> str:
        return f'\\iota_2 {self.x.tex()}'

    def __eq__(self, other):
        return isinstance(other, Inr) and self.x == other.x

    def __len__(self):
        return 1 + len(self.x)

class Abstr(Constr):
    def __init__(self, var: CVar, body: Constr):
        self.var = var
        self.body = body

    def __str__(self):
        return f'(λ{str(self.var)}.{str(self.body)})'

    def tex(self) -> str:
        return f'(\\lambda {self.var.tex()}.{self.body.tex()})'

    def __eq__(self, other):
        return isinstance(other, Abstr) and self.var == other.var and self.body == other.body

    def __len__(self):
        return 1 + len(self.body)

class Appl(Constr):
    def __init__(self, f: Constr, x: Constr):
        self.f = f
        self.x = x

    def __str__(self):
        return f'({str(self.f)} {str(self.x)})'

    def tex(self) -> str:
        return f'({self.f.tex()} {self.x.tex()})'

    def __eq__(self, other):
        return isinstance(other, Appl) and self.f == other.f and self.x == other.x

    def __len__(self):
        return 1 + len(self.f) + len(self.x)
