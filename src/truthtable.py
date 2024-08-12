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

    def __init__(self, e: Expr, latex=True, silent=False, gui=None):
        self.e = e
        self.latex = latex
        self.silent = silent
        self.gui = gui
        if not self.gui:
            self.gui = __import__("gui").PyPLGUI(True)
        
        if not self.silent:
            self.show()

    def truthtable(self):
        pvs = sorted(list(self.e.propvars()))
        vprod = list(product([True, False], repeat=len(pvs)))
        valuations = [{p: v for (p, v) in zip(pvs, valuation)} for valuation in vprod]
        syms = [c for c in self.e.tex().split(" ")]
        parens = [c for c in self.e.tex() if c in ["(", ")"]]

        if not self.latex:
            tt = ""
            tt += ((len(str(len(valuations))) + 2) * " ") + " ".join(pvs) + " | " + str(self.e) + "\n"
            tt += (len(tt)-1) * "-" + "\n"
            tt += "\n".join(["V" + str(i+1) + " "+ \
                             " ".join([self.truthvalue(b) for b in val.values()]) + " | " + \
                             self.truthrow(self.e, val, True)
                             for i, val in enumerate(valuations)])
        else:
            tt = ""
            tt += "\\begin{tabular}{c" + len(pvs) * "c" + "|" + (len(syms) + len(parens)) * "c" + "}\n"
            # todo decrease spacing between parentheses columns
            tt += " & " + " & ".join("$" + p + "$" for p in pvs) + " & " + \
                  " & ".join(["$" + c + "$" for c in self.e.tex().split(" ")])\
                      .replace("(", "($ & $").replace(")", "$ & $)")\
                  + "\\\\ \\hline\n"
            tt += "\\\\\n".join(["$V_{" + str(i+1) + "}$ & " +
                                 " & ".join([self.truthvalue(b) for b in val.values()]) + " & " +
                                 self.truthrow(self.e, val, True)
                                 for i, val in enumerate(valuations)])
            tt += "\\\\\n" + "\\end{tabular}"
        return tt
    
    def truthrow(self, e, v, mainconn=False):
        s = PropStructure("S", v)
        if not self.latex:
            # todo columns not properly aligned (extra space inserted when component is compound expression)
            if hasattr(e, "phi"):
                if hasattr(e, "psi"):
                    # binary connective
                    return " " + self.truthrow(e.phi, v) + \
                           " " + self.truthvalue(e.denot(s, v), mainconn) + " " + \
                           self.truthrow(e.psi, v) + " "
                else:
                    # unary connective
                    return self.truthvalue(e.denot(s, v), mainconn) + "" +\
                           self.truthrow(e.phi, v)
            else:
                if not hasattr(e, "p"):
                    # nullary connective
                    return self.truthvalue(e.denot(s, v), mainconn)
                else:
                    # prop. var.
                    return self.truthvalue(e.denot(s, v), mainconn)
        else:
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
    
    def truthvalue(self, b, mainconn=False):
        if not self.latex:
            return "1" if b else "0"  # todo mark main connective
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
            heading = "Truth table for " + str(self.e) + ":\n\n"
        else:
            heading = "Truth table for $" + self.e.tex() + "$:\\\\ \\ \\\\ \n"

        # load preamble
        if self.latex:
            path_preamble = os.path.join(os.path.dirname(__file__), "preamble.tex")
            with open(path_preamble) as f:
                preamble = f.read()
                preamble += "\n\n\setlength\\tabcolsep{3pt}\n"

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
