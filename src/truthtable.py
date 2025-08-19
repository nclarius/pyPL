#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Truth tables.
"""

from expr import *
from helpers import SleepInhibitor

import os
from time import time
from itertools import product

class Truthtable():

    def __init__(self, conclusion: Formula, premises=[], latex=True, silent=False, gui=None):
        self.concl = conclusion
        self.prems = premises
        self.inf = Inf(self.concl, self.prems) if conclusion else Neg(Inf(self.concl, self.prems))
        self.latex = latex
        self.silent = silent
        self.gui = gui
        if not self.gui:
            self.gui = __import__("gui").PyPLGUI(True)
        
        self.pvs = sorted(list((self.concl.propvars() if self.concl else set()).union(*[p.propvars() for p in self.prems])))
        vprod = list(product([True, False], repeat=len(self.pvs)))
        self.valuations = [{p: v for (p, v) in zip(self.pvs, valuation)} for valuation in vprod] if vprod else [{}]

        if not self.silent:
            self.show()

    def truthtable(self):
        if not self.latex:
            tt = ""
            # heading
            tt += (((len(str(len(self.valuations))) + 2) * " ") if self.pvs else "") + " ".join(self.pvs) + (" | " if self.prems else "")
            tt += " | ".join([str(p).replace("¬", "¬ ") for p in self.prems])
            tt += " | " + str(self.inf) + (" | " if self.concl else " ")
            tt += (str(self.concl).replace("¬", "¬ ") if self.concl else "") + "\n"
            # line
            tt += (((len(str(len(self.valuations))) + 2) * "-") if self.pvs else "-") + (2 * len(self.pvs)) * "-" + "|" + ("-" if self.prems else "")
            tt += "-|-".join([self.truthrowsep(p, True) for p in self.prems]) + ("-|" if self.prems else "")
            tt += self.truthrowsep(self.inf, True)
            tt += ("|-" + self.truthrowsep(self.concl, True) if self.concl else "") + "\n"
            # rows
            tt += "\n".join([(("V" + str(i+1) + " ") if self.pvs else "") + \
                             " ".join([self.truthvalue(b) for b in val.values()]) + (" | " if self.prems else "") + \
                            " | ".join([self.truthrow(p, val, True) for p in self.prems]) + \
                            " | " + self.truthrow(self.inf, val, True) + (" | " if self.concl else "") + \
                            (self.truthrow(self.concl, val, True) if self.concl else "")
                             for i, val in enumerate(self.valuations)])
        else:
            tt = ""
            tt += "\\begin{tabular}{c" + len(self.pvs) * "c" + "|"
            tt += "|".join([(len(f.tex().split(" ")) + len([c for c in f.tex() if c in ["(", ")"]])) * "c" for f in 
                self.prems + [self.inf] + ([self.concl] if self.concl else [])]) + "}\n"
            # todo decrease spacing between parentheses columns
            # heading
            tt += " & " + " & ".join("$" + p + "$" for p in self.pvs) + " & " + \
                  (" & ".join(["$" + c + "$" for c in 
                    " ".join([f.tex() for f in 
                        self.prems + [self.inf] + ([self.concl] if self.concl else [])])
                        .split(" ")]))\
                   .replace("(", "($ & $").replace(")", "$ & $)") + \
                  "\\\\ \\hline\n"
            # rows
            tt += "\\\\\n".join(["$V_{" + str(i+1) + "}$ & " +
                                 " & ".join([self.truthvalue(b) for b in val.values()]) + " & " +
                                 " & ".join([self.truthrow(p, val, True) for p in self.prems]) + (" & " if self.prems else "") +
                                 self.truthrow(self.inf, val, True) + (" & " if self.concl else "") +
                                 (self.truthrow(self.concl, val, True) if self.concl else "")
                                 for i, val in enumerate(self.valuations)])
            tt += "\\\\\n" + "\\end{tabular}"
        return tt
    
    def truthrowsep(self, e, mainconn=False):
        if not self.latex:
            if isinstance(e, Inf) or isinstance(e, Neg) and isinstance(e.phi, Inf):
                return "-" + ("=" if mainconn else "-") + "-"
            if hasattr(e, "phi"):
                if hasattr(e, "psi"):
                    # binary connective
                    return "-" + self.truthrowsep(e.phi) + "-" + ("=" if mainconn else "-") + "-" + self.truthrowsep(e.psi) + "-"
                else:
                    # unary connective
                    return ("=" if mainconn else "-") + "-" + self.truthrowsep(e.phi)
            else:
                if not hasattr(e, "p"):
                    # nullary connective
                    return "=" if mainconn else "-"
                else:
                    # prop. var.
                    return "=" if mainconn else "-"

    
    def truthrow(self, e, v, mainconn=False):
        s = PropStructure("S", v)
        if not self.latex:
            if isinstance(e, Inf) or isinstance(e, Neg) and isinstance(e.phi, Inf):
                return self.truthvalue(e.denot(s, v, ""), mainconn, True)
            if hasattr(e, "phi"):
                if hasattr(e, "psi"):
                    # binary connective
                    return " " + self.truthrow(e.phi, v) + \
                           " " + self.truthvalue(e.denot(s, v), mainconn) + " " + \
                           self.truthrow(e.psi, v) + " "
                else:
                    # unary connective
                    return self.truthvalue(e.denot(s, v), mainconn) + " " +\
                           self.truthrow(e.phi, v)
            else:
                if not hasattr(e, "p"):
                    # nullary connective
                    return self.truthvalue(e.denot(s, v), mainconn)
                else:
                    # prop. var.
                    return self.truthvalue(e.denot(s, v), mainconn)
        else:
            if isinstance(e, Inf) or isinstance(e, Neg) and isinstance(e.phi, Inf):
                return self.truthvalue(e.denot(s, v, ""), mainconn, True)
            if hasattr(e, "phi"):
                if hasattr(e, "psi"):
                    # binary connective
                    return " & " + self.truthrow(e.phi, v) + \
                           " & " + self.truthvalue(e.denot(s, v), mainconn) + " & " + \
                           self.truthrow(e.psi, v) + " & "
                else:
                    # unary connective
                    return self.truthvalue(e.denot(s, v), mainconn) + " & " +\
                           self.truthrow(e.phi, v)
            else:
                if not hasattr(e, "p"):
                    # nullary connective
                    return self.truthvalue(e.denot(s, v), mainconn)
                else:
                    # prop. var.
                    return self.truthvalue(e.denot(s, v), mainconn)
    
    def truthvalue(self, b, mainconn=False, inf=False):
        if not self.latex:
            if inf:
                return "✓" if b else "✘"
            else:
                return "1" if b else "0"
        else:
            if inf:
                return "$" + ("\\boldsymbol{" if mainconn else "") + ("\\checkmark" if b else "\\times") + ("}" if mainconn else "") + "$"
            else:
                return "$" + ("\\boldsymbol{" if mainconn else "") + ("1" if b else "0") + ("}" if mainconn else "") + "$"

    def show(self,):
        # generate the tex file and open the compiled pdf

        # compute truth table
        with SleepInhibitor("computing a truth table"):
            self.start = time()
            tt = self.truthtable()
            self.end = time()
        if self.start and self.end:
            comptime = "This computation took " + str(round(self.end - self.start, 4)) + " seconds."
        else:
            comptime = None

        # heading
        if not self.latex:
            heading = "Truth table for "
            heading += ", ".join([str(p) for p in self.prems])
            heading += " " + str(self.inf) + " "
            heading += str(self.concl) + ":\n\n"
        else:
            heading = "Truth table for $"
            heading += ", ".join([p.tex() for p in self.prems])
            heading += " " + self.inf.tex() + " "
            heading += (self.concl.tex() if self.concl else "") + "$:\\\\ \\ \\\\ \n"
        
        # result
        subj = ("sentence" if not self.prems else ("inference" if self.concl else "theory"))
        match subj:
            case "sentence":
                prop = "valid" if self.valid() else "contingent" if self.satisfiable() else "unsatisfiable"
            case "inference":
                prop = "valid" if self.valid() else "invalid"
            case "theory":
                prop = "satisfiable" if self.satisfiable() else "unsatisfiable"
        result = "The " + subj + " is " + prop + "."

        # load preamble
        if self.latex:
            path_preamble = os.path.join(os.path.dirname(__file__), "preamble.tex")
            with open(path_preamble) as f:
                preamble = f.read()
                preamble += "\n\n\\setlength\\tabcolsep{3pt}\n"

        # assemble string
        if not self.latex:
            res = heading + tt + "\n\n" + result + ("\n\n" + comptime if comptime else "") + "\n"
        else:
            res = preamble + \
                  "\n\n\\begin{document}\n\n" + \
                  heading + \
                  tt + \
                  "\\\\ \\ \\\\ \\ \\\\ \n" + result +\
                  ("\\\\ \\ \\\\ \n" + comptime if comptime else "") +\
                  "\n\n\\end{document}"

        # write and open output
        self.gui.write_output(res, self.latex)
    
    def valid(self):
        return all([self.inf.denot(PropStructure("S", v)) for v in self.valuations])
    
    def satisfiable(self):
        return any([self.inf.denot(PropStructure("S", v)) for v in self.valuations])

if __name__ == "__main__":
    pass
    parse_f = __import__("parser").FmlParser().parse

#     fml = parse_f("((p & q) | ~ r)")
#     tt = Truthtable(fml, latex=False, silent=True)
# 
#     fml1 = parse_f("p -> q")
#     fml2 = parse_f("~ p")
#     fml = parse_f("~ q")
#     tt = Truthtable(fml, premises=[fml1, fml2], latex=False, silent=True)
# 
#     fml1 = parse_f("p v q")
#     fml2 = parse_f("~ (p & q)")
#     tt = Truthtable(None, premises=[fml1, fml2], latex=False, silent=True)
