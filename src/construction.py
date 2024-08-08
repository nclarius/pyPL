#!/usr/bin/env ppsithon
# -*- coding: utf-8 -*-

"""
Define proof construction programs (lambda mu terms) associated with formulas.
"""

class Constr(object):
    def __init__(self, constrtype = None, phi = None, psi = None):
        self.type = constrtype
        self.phi = phi
        self.psi = psi
        self.var = None
        self.inst = None
    
    def mirror(self, other):
        for attr in dir(other):
            if getattr(other, attr) is not None and not attr.startswith("__") and not attr in ["inst", "mirror"]:
                setattr(self, attr, getattr(other, attr))
    
    def getType(self):
        return self.type
    
    def getPhi(self):
        return self.phi
    
    def getPsi(self):
        return self.psi

    def getVar(self):
        return self.var
    
    def setType(self, constrtype):
        self.type = constrtype
    
    def setPhi(self, phi):
        self.phi = phi
    
    def setPsi(self, psi):
        self.psi = psi
    
    def setVar(self, var):
        self.var = var

class Assmpt(Constr):
    def __init__(self, var: str):
        self.var = var

    def __str__(self):
        return self.var

    def tex(self) -> str:
        return self.var

    def __eq__(self, other):
        return isinstance(other, Assmpt) and self.u == other.u

    def __len__(self):
        return 1


class Pair(Constr):
    def __init__(self, phi: Constr, psi: Constr):
        self.phi = phi
        self.psi = psi

    def __str__(self):
        return f'⟨{str(self.phi.inst)}, {str(self.psi.inst)}⟩'

    def tex(self) -> str:
        return f'\\langle{self.phi.inst.tex()}, {self.psi.inst.tex()}\\rangle'

    def __eq__(self, other):
        return isinstance(other, Pair) and self.phi == other.phi and self.psi == other.psi

    def __len__(self):
        return 1 + len(self.phi) + len(self.psi)

class Fst(Constr):
    def __init__(self, phi: Constr):
        self.phi = phi

    def __str__(self):
        return f'π₁ {str(self.phi.inst)}'

    def tex(self) -> str:
        return f'\\pi_1 {self.phi.inst.tex()}'

    def __eq__(self, other):
        return isinstance(other, Fst) and self.phi == other.p

    def __len__(self):
        return 1 + len(self.phi)

class Snd(Constr):
    def __init__(self, phi: Constr):
        self.phi = phi

    def __str__(self):
        return f'π₂ {str(self.phi.inst)}'

    def tex(self) -> str:
        return f'\\pi_2 {self.phi.inst.tex()}'

    def __eq__(self, other):
        return isinstance(other, Snd) and self.phi == other.p

    def __len__(self):
        return 1 + len(self.phi)

class Either(Constr):
    def __init__(self, phi: Constr, psi: Constr):
        self.phi = phi
        self.psi = psi

    def __str__(self):
        return f'[{str(self.phi.inst)}, {str(self.psi.inst)}]'

    def tex(self) -> str:
        return f'\\lbrack {self.phi.inst.tex()}, {self.psi.inst.tex()} \\rbrack'

    def __eq__(self, other):
        return isinstance(other, Case) and self.phi == other.l and self.psi == other.r

    def __len__(self):
        return 1 + len(self.phi) + len(self.phi) + len(self.psi)

class Inl(Constr):
    def __init__(self, phi: Constr):
        self.phi = phi

    def __str__(self):
        return f'ι₁ {str(self.phi.inst)}'

    def tex(self) -> str:
        return f'\\iota_1 {self.phi.inst.tex()}'

    def __eq__(self, other):
        return isinstance(other, Inl) and self.phi == other.phi

    def __len__(self):
        return 1 + len(self.phi)

class Inr(Constr):
    def __init__(self, phi: Constr):
        self.phi = phi

    def __str__(self):
        return f'ι₂ {str(self.phi.inst)}'

    def tex(self) -> str:
        return f'\\iota_2 {self.phi.inst.tex()}'

    def __eq__(self, other):
        return isinstance(other, Inr) and self.phi == other.phi

    def __len__(self):
        return 1 + len(self.phi)

class Abstr(Constr):
    def __init__(self, phi: Assmpt, psi: Constr):
        self.phi = phi
        self.psi = psi

    def __str__(self):
        return f'(λ{str(self.phi.inst)}.{str(self.psi.inst)})'

    def tex(self) -> str:
        return f'(\\lambda {self.phi.inst.tex()}.{self.psi.inst.tex()})'

    def __eq__(self, other):
        return isinstance(other, Abstr) and self.phi == other.phi and self.psi == other.psi

    def __len__(self):
        return 1 + len(self.bodpsi)

class Appl(Constr):
    def __init__(self, phi: Constr, psi: Constr):
        self.phi = phi
        self.psi = psi

    def __str__(self):
        return f'({str(self.phi.inst)} {str(self.phi.inst)})'

    def tex(self) -> str:
        return f'({self.phi.inst.tex()} {self.phi.inst.tex()})'

    def __eq__(self, other):
        return isinstance(other, Appl) and self.phi == other.phi and self.phi == other.psi

    def __len__(self):
        return 1 + len(self.phi) + len(self.phi)
