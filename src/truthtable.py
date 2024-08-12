#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Truth tables.
"""

from expr import *

import os
from itertools import product

# todo plain text output

class Truthtable():

    def __init__(self, e: Expr, premises=[], latex=True, silent=False, gui=None):
        self.e = e
        self.prems = premises
        self.inf = Inf(self.e, self.prems) if e else Neg(Inf(self.e, self.prems))
        self.latex = latex
        self.silent = silent
        self.gui = gui
        if not self.gui:
            self.gui = __import__("gui").PyPLGUI(True)
        
        if not self.silent:
            self.show()

    def truthtable(self):
        pvs = sorted(list((self.e.propvars() if self.e else set()).union(*[p.propvars() for p in self.prems])))
        vprod = list(product([True, False], repeat=len(pvs)))
        valuations = [{p: v for (p, v) in zip(pvs, valuation)} for valuation in vprod]
        syms = [c for c in " ".join([f.tex() for f in self.prems + [self.inf] + ([self.e] if self.e else [])]).split(" ")]
        parens = [c for c in " ".join([f.tex() for f in self.prems + [self.inf] + ([self.e] if self.e else [])]) if c in ["(", ")"]]

        if not self.latex:
            tt = ""
            # heading
            tt += ((len(str(len(valuations))) + 2) * " ") + " ".join(pvs) + " | "
            tt += " | ".join([str(p).replace("¬", "¬ ") for p in self.prems])
            tt += " | " + str(Inf()) + " | "
            tt += str(self.e).replace("¬", "¬ ") + "\n"
            # line
            tt += ((len(str(len(valuations))) + 2) * "-") + (2 * len(pvs)) * "-" + "|-"
            tt += "-|-".join([self.truthrowsep(p, True) for p in self.prems])
            tt += "-|" + self.truthrowsep(Inf(), True) + "|-"
            tt += self.truthrowsep(fml, True) + "\n"
            # rows
            tt += "\n".join(["V" + str(i+1) + " "+ \
                             " ".join([self.truthvalue(b) for b in val.values()]) + " | " + \
                            " | ".join([self.truthrow(p, val, True) for p in self.prems]) + \
                            " | " + self.truthrow(Inf(), val, True) + " | " + \
                             self.truthrow(self.e, val, True)
                             for i, val in enumerate(valuations)])
        else:
            tt = ""
            tt += "\\begin{tabular}{c" + len(pvs) * "c" + "|"
            tt += "|".join([(len(f.tex().split(" ")) + len([c for c in f.tex() if c in ["(", ")"]])) * "c" for f in 
                self.prems + [self.inf] + ([self.e] if self.e else [])]) + "}\n"
            # todo decrease spacing between parentheses columns
            # heading
            tt += " & " + " & ".join("$" + p + "$" for p in pvs) + " & " + \
                  (" & ".join(["$" + c + "$" for c in 
                    " ".join([f.tex() for f in 
                        self.prems + [self.inf] + ([self.e] if self.e else [])])
                        .split(" ")]))\
                   .replace("(", "($ & $").replace(")", "$ & $)") + \
                  "\\\\ \\hline\n"
            # rows
            tt += "\\\\\n".join(["$V_{" + str(i+1) + "}$ & " +
                                 " & ".join([self.truthvalue(b) for b in val.values()]) + " & " +
                                 " & ".join([self.truthrow(p, val, True) for p in self.prems]) + (" & " if self.prems else "") +
                                 self.truthrow(self.inf, val, True) + (" & " if self.e else "") +
                                 (self.truthrow(self.e, val, True) if self.e else "")
                                 for i, val in enumerate(valuations)])
            tt += "\\\\\n" + "\\end{tabular}"
        return tt
    
    def truthrowsep(self, e, mainconn=False):
        if not self.latex:
            if isinstance(e, Inf):
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
        try:
            from timeit import default_timer as timer
            start = timer()
            tt = self.truthtable()
            end = timer()
        except ImportError as e:
            start, end = None, None
            tt = self.truthtable()
        if start and end:
            comptime = "This computation took " + str(round(end - start, 4)) + " seconds."
        else:
            comptime = None

        # heading
        if not self.latex:
            heading = "Truth table for "
            heading += ", ".join([str(p) for p in self.prems])
            heading += " " + str(self.inf) + " "
            heading += str(self.e) + ":\n\n"
        else:
            heading = "Truth table for $"
            heading += ", ".join([p.tex() for p in self.prems])
            heading += " " + self.inf.tex() + " "
            heading += (self.e.tex() if self.e else "") + "$:\\\\ \\ \\\\ \n"

        # load preamble
        if self.latex:
            path_preamble = os.path.join(os.path.dirname(__file__), "preamble.tex")
            with open(path_preamble) as f:
                preamble = f.read()
                preamble += "\n\n\\setlength\\tabcolsep{3pt}\n"

        # assemble string
        if not self.latex:
            res = heading + tt + ("\n\n" + comptime if comptime else "") + "\n"
        else:
            res = preamble + \
                  "\n\n\\begin{document}\n\n" + \
                  heading + \
                  tt + \
                  ("\\\\ \\ \\\\ \\ \\\\ \n" + comptime if comptime else "") +\
                  "\n\n\\end{document}"

        # write and open output
        self.gui.write_output(res, self.latex)

if __name__ == "__main__":
    pass
    parse_f = __import__("parser").FmlParser().parse

    fml = parse_f("((p & q) | ~ r)")
    tt = Truthtable(fml, silent=True)

    fml1 = parse_f("p -> q")
    fml2 = parse_f("~ p")
    fml = parse_f("~ q")
    tt = Truthtable(fml, premises=[fml1, fml2], silent=True)

    fml1 = parse_f("p v q")
    fml2 = parse_f("~ (p & q)")
    tt = Truthtable(None, premises=[fml1, fml2], silent=True)
