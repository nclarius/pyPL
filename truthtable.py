#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Truth tables.
"""

from expr import *

import os
from subprocess import DEVNULL, STDOUT, check_call
from datetime import datetime
from timeit import default_timer as timer
from itertools import product

# todo plain text output

class Truthtable():

    def __init__(self, e: Expr, tex: bool):
        self.e = e
        self.tex = tex

    def truthtable(self):
        pvs = sorted(list(self.e.propvars()))
        vprod = list(product([True, False], repeat=len(pvs)))
        valuations = [{p: v for (p, v) in zip(pvs, valuation)} for valuation in vprod]
        syms = [c for c in self.e.tex().split(" ")]
        parens = [c for c in self.e.tex() if c in ["(", ")"]]

        if not self.tex:
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
        if not self.tex:
            # todo columns not properly aligned (extra space inserted when component is compound expression)
            if hasattr(e, "phi"):
                if hasattr(e, "psi"):
                    # binary connective
                    return " " + self.truthrow(e.phi, v) + \
                           " " + self.truthvalue(e.denot(s, v), mainconn) + " " + \
                           self.truthrow(e.psi, v) + "  "
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
        if not self.tex:
            return "1" if b else "0"  # todo mark main connective
        else:
            return "$" + ("\\boldsymbol{" if mainconn else "") + ("1" if b else "0") + ("}" if mainconn else "") + "$"

    def show(self):
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
        if not self.tex:
            heading = "Truth table for " + str(self.e) + ":\n\n"
        else:
            heading = "Truth table for $" + self.e.tex() + "$:\\\\ \\ \\\\ \n"

        # load preamble
        if self.tex:
            path_preamble = os.path.join(os.path.dirname(__file__), "preamble.tex")
            with open(path_preamble) as f:
                preamble = f.read()
                preamble += "\n\n\setlength\\tabcolsep{3pt}\n"

        # assemble string
        if not self.tex:
            res = heading + tt + ("\n\n" + comptime if comptime else "") + "\n"
        else:
            res = preamble + \
                  "\n\n\\begin{document}\n\n" + \
                  heading + \
                  tt + \
                  ("\\\\ \\ \\\\ \\ \\\\ \n" + comptime if comptime else "") +\
                  "\n\n\\end{document}"

        # generate and open output file
        if not self.tex:
            # generate the txt file and open it
            path_output = os.path.join(os.path.dirname(__file__), "output")
            if not os.path.exists(path_output):
                os.mkdir(path_output)
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M_%S%f')
            file_txt = "output_" + timestamp + ".txt"
            path_txt = os.path.join(path_output, file_txt)
            os.chdir(path_output)
            with open(path_txt, "w", encoding="utf-8") as f:
                f.write(res)
            # open file
            check_call(["xdg-open", path_txt], stdout=DEVNULL, stderr=STDOUT)
            os.chdir(os.path.dirname(__file__))
        else:
            # prepare output files
            path_output = os.path.join(os.path.dirname(__file__), "output")
            if not os.path.exists(path_output):
                os.mkdir(path_output)
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M_%S%f')
            file_tex = "output_" + timestamp + ".tex"
            file_pdf = "output_" + timestamp + ".pdf"
            path_tex = os.path.join(path_output, file_tex)
            path_pdf = os.path.join(path_output, file_pdf)
            os.chdir(path_output)
            # write LaTeX code
            with open(path_tex, "w") as texfile:
                texfile.write(res)
            # compile LaTeX to PDF
            check_call(["pdflatex", file_tex], stdout=DEVNULL, stderr=STDOUT)
            # open file
            check_call(["xdg-open", path_pdf], stdout=DEVNULL, stderr=STDOUT)
            # cleanup
            for file in os.listdir(path_output):
                path_file = os.path.join(path_output, file)
                if os.path.exists(path_file) and file.endswith(".log") or file.endswith(".aux") or file.endswith(".gz"):
                    os.remove(path_file)
            os.chdir(os.path.dirname(__file__))

if __name__ == "__main__":
    pass
    parse_f = __import__("parser").FmlParser().parse
