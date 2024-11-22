#!/usr/bin/env ppsithon
# -*- coding: utf-8 -*-

"""
Define proof construction programs (lambda mu terms) associated with formulas.
"""

class ConstrScheme(Object):
    def __init__(self, constrtype = None, phi = None, psi = None):
        self.type = constrtype
        self.phi = phi
        self.psi = psi

class Constr(object):    
    def __eq__(self, other: Constr) -> bool:
        """
        Whether the construction is equal to another construction.

        @param other: the other construction
        @type other: Constr
        @return: True iff self is equal to other
        @rtype: bool
        """
        return type(self) == type(other) and \
            all([getattr(self, attr) == getattr(other, attr) for attr in vars(self).keys()
                 if not attr.startswith("__") and not callable(getattr(self, attr))])

    def __len__(self) -> int:
        """
        The length of the construction.

        @return the length of the construction
        @rtype int
        """
        return len(self.subconstrs())
    
    def __contains__(self, other: Constr) -> bool:
        """
        Whether the construction contains another construction.

        @param other: the other construction
        @type other: Constr
        @return: True iff other occurs in the subconstrs of self
        @rtype: bool
        """
        return other in self.subconstrs()

    def imm_subconstrs(self) -> list[Constr]:
        """
        The immediate subconstructions of the construction.

        @return the immediate subconstructions of the construction
        @rtype list[Constr]
        """
        return vars(self).values()

    def proper_subconstrs(self) -> list[Constr]:
        """
        The proper subconstructions of the construction.

        @return the proper subconstructions of the construction
        @rtype list[Constr]
        """
        res = self.imm_subconstrs()
        for subconstr in self.imm_subconstrs():
            res += subconstr.proper_subconstrs()
        return res

    def subconstrs(self) -> list[Constr]:
        """
        The recursive subconstructions of the construction.

        @return the subconstructions of the construction
        @rtype list[Constr]
        """
        return [self] + self.proper_subconstrs()

class Assmpt(Constr):
    def __init__(self, phi: str):
        self.phi = phi

    def __str__(self):
        return self.phi

    def tex(self) -> str:
        return self.phi

class Pair(Constr):
    def __init__(self, phi: Constr, psi: Constr):
        self.phi = phi
        self.psi = psi

    def __str__(self):
        return f'⟨{str(self.phi)}, {str(self.psi)}⟩'

    def tex(self) -> str:
        return f'\\langle{self.phi.tex()}, {self.psi.tex()}\\rangle'

class Fst(Constr):
    def __init__(self, phi: Constr):
        self.phi = phi

    def __str__(self):
        return f'π₁ {str(self.phi)}'

    def tex(self) -> str:
        return f'\\pi_1 {self.phi.tex()}'

class Snd(Constr):
    def __init__(self, phi: Constr):
        self.phi = phi

    def __str__(self):
        return f'π₂ {str(self.phi)}'

    def tex(self) -> str:
        return f'\\pi_2 {self.phi.tex()}'

class Inl(Constr):
    def __init__(self, phi: Constr):
        self.phi = phi

    def __str__(self):
        return f'ι₁ {str(self.phi)}'

    def tex(self) -> str:
        return f'\\iota_1 {self.phi.tex()}'

class Inr(Constr):
    def __init__(self, phi: Constr):
        self.phi = phi

    def __str__(self):
        return f'ι₂ {str(self.phi)}'

    def tex(self) -> str:
        return f'\\iota_2 {self.phi.tex()}'

class Case(Constr):
    def __init__(self, chi : Constr, x : Assmpt, phi: Constr, y : Assmpt, psi : Constr):
        self.chi = chi
        self.x = x
        self.phi = phi
        self.y = y
        self.psi = psi
    
    def __str__(self):
        return f'case {str(self.chi)} | {str(self.x)} : {str(self.chi)} | {str(self.y)} : {str(self.psi)}'
    
    def __str__(self):
        return "\\text{case} " + self.chi.tex() + " \\mid " + self.x.tex() + " : " + self.chi.tex() + " \\mid " + self.y.tex() + " : " + self.psi.tex()
    
class Abstr(Constr):
    def __init__(self, phi: Assmpt, psi: Constr):
        self.phi = phi
        self.psi = psi

    def __str__(self):
        return f'(λ{str(self.phi)}.{str(self.psi)})'

    def tex(self) -> str:
        return f'(\\lambda {self.phi.tex()}.{self.psi.tex()})'

class Appl(Constr):
    def __init__(self, phi: Constr, psi: Constr):
        self.phi = phi
        self.psi = psi

    def __str__(self):
        return f'({str(self.phi)} {str(self.phi)})'

    def tex(self) -> str:
        return f'({self.phi.tex()} {self.phi.tex()})'

class Cond(Constr):
    def __init__(self, chi: Constr, phi: Constr, psi: Constr):
        self.chi = chi
        self.phi = phi
        self.psi = psi
    
    def __str__(self):
        return f'if {str(self.chi)} then {str(self.phi)} else {str(self.psi)}'
    
    def tex(self) -> str:
        return '\\text{if} ' + self.chi.tex() + ' \\text{then} ' + self.phi.tex() + ' \\text{else} ' + self.psi.tex()

class BTrue(Constr):
    def __str__(self):
        return 'true'

    def tex(self) -> str:
        return '\\text{true}'

class BFalse(Constr):
    def __str__(self):
        return 'false'

    def tex(self) -> str:
        return '\\text{false}'

class Unit(Constr):
    def __str__(self):
        return 'unit'

    def tex(self) -> str:
        return '\\text{unit}'
