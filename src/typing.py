
from expr import *
from construction import *

def typecheck(e: Expr, c: Constr, g: dict[str, Formula]) -> bool:
    match (e, c):
        case (Prop(p=p), Assmpt(phi=phi)):
            return (phi, Prop(p)) in g.items()

        case (Imp(phi=phi, psi=psi), Abstr(phi=x, t=t, psi=m)):
            return typecheck(psi, m, g | {x.phi: phi}) 

        case (Formula(), Appl(phi=phi, psi=psi)):
            match(typecheck(e, g) )
            return typecheck(_, phi, g) and typecheck(_, psi, g)

print(typecheck(Prop('p'), Assmpt('x'), {'x': Prop('p')})) # True
print(typecheck(Imp(Prop('p'), Prop('p')), Abstr(Assmpt('x'), Assmpt('x')), {})) # True
print(typecheck(Imp(Prop('q'), Imp(Prop('p'), Prop('q'))), Abstr(Assmpt('x'), Abstr(Assmpt('y'), Assmpt('x'))), {})) # True
