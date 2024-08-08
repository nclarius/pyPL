#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tableau proofs and model extraction.
"""

# Workflow:
# - set initial settings, add assumptions (`init`)
# - while there are applicable rules: expand the tree (`expand`)
#    - check whether tree expansion can be stopped
#       - tree gets too big or
#       - requested number of models found
#    - recompute list of applicable rules
#      - traverse all source nodes (= lines to potentially expand)
#      - compile applicability entry
#        - get applicable rules (rule type, rule name, formulas to add) from
#        class belonging to formula in expr.py
#        - select target nodes (= nodes to append the new lines to)
#        - compute additional function arguments (such as list of constants
#        occurring on the branch)
#      - add rule of form (target, source, rule name, rule type, arguments,
#      num of applications) to list of applicable
#      - remove inactive branches form applicable
#      - rank list according to specified criteria
#    - pick the topmost of the prioritized applicable rules
#    - apply the rule by calling the rule type function (`rule_alpha` etc.)
#      - if appropriate, pick constant/world instantiation
#      - add new node to target (`add_node`)
#        - extend tree object
#        - check if branch is now closed, terminally open, or probably infinite
#        - if open, extract model (`model`)
#          - collect propositional variables, constants (-> D), worlds (-> W)
#          and accessiblity tuples (-> R) on  branch
#          - collect literals (atoms and negated atoms) on the branch and
#          turn into valuation/interpret. func. (-> V/I)
# - print results (`show`)


from expr import *
from parser import FmlParser

import itertools
import os
from datetime import datetime
from itertools import chain
from subprocess import DEVNULL, STDOUT, check_call

# todo specify partial model to start with?
# todo documentation
# todo make non-K modal logics work
# todo tableaux for IL
# todo formulas with free variables?

debug = False

def least(lst, cond):
    return min([x for x in lst if cond(x)])


class Tableau(object):
    """
    A tableau tree.
    """

    def __init__(self,
                 conclusion=None, premises=[], axioms=[],
                 validity=True, satisfiability=True, linguistic=False,
                 classical=True, propositional=False, modal=False,
                 vardomains=False, local=True, frame="K",
                 threevalued=False, weakthreevalued=True,
                 num_models=1, size_limit_factor=2, sequent_style=False,
                 file=True, latex=True, stepwise=False, hide_nonopen=False,
                 underline_open=True, silent=False,
                 gui=None):

        # settings
        # todo nicer specification of settings?
        # todo check consistency of settings
        self.mode = {
                "validity":    validity, "satisfiability": satisfiability,
                "linguistic":  linguistic,
                "sequent":     sequent_style,
                "classical":   classical, "propositional": propositional,
                "modal":       modal, "vardomains": vardomains, "local": local,
                "frame":       frame,
                "threevalued": threevalued, "weakthreevalued": weakthreevalued
        }
        self.num_models, self.size_limit_factor, self.sequent_style, \
        self.silent, self.file, self.latex, self.stepwise, \
        self.hide_nonopen, self.underline_open = \
            num_models, size_limit_factor, sequent_style, silent, file, latex, \
            stepwise, hide_nonopen, underline_open  # todo support sequent style in gui
        self.num_branches = 1

        self.appl = []  # list of applicable rules
        self.models = []  # generated models
        self.steps = []  # stepwise representation
        if self.stepwise:
            # todo treat contradiction check as separate step
            self.steps.append(
                self.root.treestr() if not self.latex else self.root.treetex())

        # append initial nodes
        line = 1
        # sig = (1,) if modal or not classical else None
        # world = 1 if (modal or not classical) and validity else None
        signed = not classical or modal or sequent_style  # todo
        # reimplement with pos./neg. signed formulas
        rule = "A"
        source = None
        inst = tuple()

        # initial formulas
        (conclusion, premises, axioms) = \
            (conclusion, premises, axioms) if conclusion else (
            premises[0], premises[1:], axioms)
        action = "tp" if validity else "mg" if satisfiability else "cmg"
        negated_concl = action in ["tp", "cmg"]
        fmls = [None] * (1 + len(premises) + len(axioms))
        vs = [None] * (1 + len(premises) + len(axioms))
        ws = [None] * (1 + len(premises) + len(axioms))
        for i, el in enumerate([conclusion] + premises + axioms):
            initial_world = (modal or not classical) and (
                        (action in ["tp", "cmg"] and i == 0) or local)
            all_worlds = not initial_world
            if isinstance(el, tuple):  # v and w given
                fmls[i], vs[i], ws[i] = el[0], el[1], el[2]
                ws[i] = int(ws[i][1:]) if ("w" in ws[i] or "k" in ws[i]) else int(ws[i]) if ws[
                    i] else None
            else:  # only fml given
                fmls[i] = el
                vs[i] = None
                ws[i] = (0 if not classical else 1) if initial_world else (
                    0 if (modal or not classical) else None)
            if (
                    modal or not classical) and all_worlds:  # make fml true
                # in all worlds
                fmls[i] = AllWorlds(fmls[i])

        self.root = Node(None, self, line, ws[0], not negated_concl, fmls[0], rule, source, inst, len(premises + axioms) > 0)
        self.conclusion = conclusion if not isinstance(conclusion, tuple) else \
        conclusion[0]
        self.premises = [self.root.leaves()[0].add_child(
                (self, i + 1, ws[i], True, fmls[i], rule, source, inst, 
                i < len(premises), []))
                         for i in range(1, len(premises) + 1)]
        max_line = max([node.line for node in self.root.nodes() if node.line])
        self.axioms = [self.root.leaves()[0].add_child(
                (self, i + max_line + 1, ws[i], True, fmls[i], "Ax", source, inst, 
                True, []))
                       for i in range(1 + len(premises),
                                      1 + len(premises) + len(axioms))]

        for node in [self.root] + self.premises + self.axioms:
            node.context = [self.root] + self.premises + self.axioms

        self.gui = gui
        if not self.gui:
            self.gui = __import__("gui").PyPLGUI(True)
        
        # run the tableau
        print("Computing...")
        try:
            from timeit import default_timer as timer
            self.start = timer()
            self.expand()
            self.end = timer()
        except ImportError as e:
            self.start, self.end = None, None
            self.expand()
        if not self.silent:
            self.show()

    def __str__(self):
        return self.root.treestr()

    def __len__(self):
        return max([int(node.line) for node in self.root.nodes() if node.line])

    def show(self):
        """
        Print tableau info.
        """
        res = ""
        # create preamble
        if self.latex:
            path_preamble = os.path.join(os.path.dirname(__file__),
                                         "preamble.tex")
            with open(path_preamble) as f:
                preamble = f.read()
                # for s in list(dict.fromkeys(chain([chain(node.fml.nonlogs())
                #                             for node in self.axioms +
                #                             self.premises + [
                #                             self.conclusion]]))):
                #     preamble += "\\DeclareMathOperator{\\nl" + str(s) + "}{
                #     " + str(s) + "}"
                preamble += "\n\\begin{document}"
                res += preamble

        # print usage info
        info = "\n"
        info += "You are using " + \
                ("analytic tableau " if not self.sequent_style else "sequent calculus ") + \
                ("proof search" if self.mode["validity"] else
                 ("model" if self.mode[
                     "satisfiability"] else "countermodel") + " generation") + \
                " for " + \
                ("classical " if self.mode[
                    "classical"] else "intuitionistic ") + \
                ("two-valued " if not self.mode["threevalued"] else ((
                                                                         "weak Kleene " if
                                                                         self.mode[
                                                                             "weakthreevalued"] else "strong Kleene") + "three-valued")) + \
                ("modal " if self.mode["modal"] else "") + \
                ("propositional " if self.mode[
                    "propositional"] else "predicate ") + \
                "logic" + \
                (" with " + ("varying " if self.mode[
                    "vardomains"] else "constant ") + "domains"
                 if self.mode["modal"] and not self.mode[
                    "propositional"] else "") + \
                ((" and " if not self.mode["propositional"] else " with ") +
                 ("local " if self.mode["local"] else "global ") + "validity"
                 if self.mode["modal"] and (
                            self.mode["validity"] or not self.mode[
                        "satisfiability"]) else "") + \
                (" in a " + self.mode["frame"] + " frame"
                 if self.mode["modal"] else "") + \
                "." + ("\\\\" if self.latex else "") + "\n\n"

        if not self.latex:
            axs = ["  " + str(node.fml) for node in self.axioms]
            prems = ["  " + str(self.root.fml)] if not self.conclusion else [] + \
                                                                            [
                                                                                    "  " + str(
                                                                                        node.fml)
                                                                                    for
                                                                                    node
                                                                                    in
                                                                                    self.premises]
            prems += [("  " if len(prems) > 0 else "") + str(self.conclusion)] \
                if self.conclusion and not self.mode["validity"] and self.mode[
                "satisfiability"] else []
            concl = str(self.conclusion) if \
                self.conclusion and (self.mode["validity"] or not self.mode[
                    "satisfiability"]) else ""
            lhs = axs + prems + ([concl] if concl else [])
            inf = ("⊢" if self.mode["validity"] else "⊬")
            info += ("Tableau" if not self.sequent_style else "Sequent") + \
                    "tree for \n" + \
                    ", \n".join(axs) + (
                        " + \n" if axs and prems else "\n" if axs else "") + \
                    ", \n".join(prems) + (
                        "\n" if len(lhs) > 1 else " " if not concl else "") + \
                    inf + \
                    (" " if concl else "") + concl + ":" + "\n\n"
        else:
            # axs = ["\\phantom{\\vdash\ }" + node.fml.tex() for node in
            # self.axioms]
            axs = []
            prems = [
                    "\\phantom{\\vdash\\ }" + self.root.fml.tex()] if not \
                self.conclusion else [] + \
                                                                                              [
                                                                                                      "\\phantom{" \
                                                                                                      "\\vdash\\ }" +
                                                                                                      node.fml.tex()
                                                                                                      for
                                                                                                      node
                                                                                                      in
                                                                                                      self.premises
                                                                                                      + self.axioms]
            prems += [("\\phantom{\\vdash\\ }" if len(
                prems) > 0 else "") + self.conclusion.tex()] \
                if self.conclusion and not self.mode["validity"] and self.mode[
                "satisfiability"] else []
            concl = self.conclusion.tex() if \
                self.conclusion and (self.mode["validity"] or not self.mode[
                    "satisfiability"]) else ""
            lhs = axs + prems + ([concl] if concl else [])
            inf = ("\\vdash" if self.mode["validity"] else "\\nvdash")
            info += ("Tableau" if not self.sequent_style else "Sequent") + \
                    " tree for $\\\\\n" + \
                    ", \\\\\n".join(axs) + (
                        " + \\\\\n" if axs and prems else "\\\\\n" if axs
                        else "") + \
                    ", \\\\\n".join(prems) + ("\\\\\n" if len(
                lhs) > 1 else " " if not concl else "") + \
                    inf + \
                    (" " if concl else "") + concl + ":" + "$\\\\\n"

        if self.stepwise:
            if not self.latex:
                res += info + "\n\n"
                res += "\n\n".join([step for step in self.steps])
            else:
                res += "\n\n\\pagebreak\n\n".join([info + step for step in
                                                   self.steps]) + \
                       "\n\n\\pagebreak\n\n"

        res += info

        # print the tableau
        if not self.latex:
            res += self.root.treestr()
        else:
            res += self.root.treetex() + "\\ \\\\\n\\ \\\\\n\\ \\\\\n"

        # print result
        result = ""
        if self.closed():
            if not self.sequent_style:
                result += "The tableau is closed:" + (
                    "\\\\" if self.latex else "") + "\n"
            if self.mode["validity"]:
                result += "The " + (
                    "inference" if self.premises else "sentence") + " is valid."
            else:
                if self.mode["satisfiability"]:
                    result += "The " + (
                        "set of sentences" if self.premises else "sentence") \
                              + " is unsatisfiable."
                else:
                    result += "The " + (
                        "inference" if self.premises else "sentence") + " is " \
                                                                        "valid."
        elif self.open():
            result += "The tableau is open:" + (
                "\\\\" if self.latex else "") + "\n"
            if self.mode["validity"]:
                result += "The " + (
                    "inference" if self.premises else "sentence") + " is " \
                                                                    "invalid."
            else:
                if self.mode["satisfiability"]:
                    result += "The " + (
                        "set of sentences" if self.premises else "sentence") \
                              + " is satisfiable."
                else:
                    result += "The " + (
                        "inference" if self.premises else "sentence") + " is " \
                                                                        "invalid."
        elif self.infinite():
            result += "The tableau is potentially infinite:" + (
                "\\\\" if self.latex else "") + "\n"
            if self.mode["validity"]:
                result += "The " + (
                    "inference" if self.premises else "sentence") + " may or " \
                                                                    "may not " \
                                                                    "be valid."
            else:
                if self.mode["satisfiability"]:
                    result += "The " + \
                              (
                                  "set of sentences" if self.premises else
                                  "sentence") + \
                              " may or may not be satisfiable."
                else:
                    result += "The " + (
                        "inference" if self.premises else "sentence") + " may " \
                                                                        "or may not be refutable."
        result += "\\\\\n\\\\\n" if self.latex else "\n\n"
        res += result

        # generate and print models
        mdls = ""
        if self.models:
            mdls += ("Countermodels:" \
                         if self.mode["validity"] or not self.mode[
                "validity"] and not self.mode["satisfiability"] \
                         else "Models:") + ("\\\\\n" if self.latex else "\n\n")
            if self.latex:
                mdls += "% alignment for structures\n"
                mdls += "\\renewcommand{\\arraystretch}{1}  % decrease " \
                        "spacing between rows\n"
                mdls += "\\setlength{\\tabcolsep}{1.5pt}  % decrease spacing " \
                        "between columns\n"
                mdls += "\n"
            for model in sorted(self.models, key=lambda m:
            {n.line: i for (i, n) in enumerate(self.root.nodes(preorder=True))}[
                int(m.s[1:])]):
                if not self.latex:
                    mdls += str(model) + "\n"
                else:
                    mdls += model.tex() + "\\ \\\\\n\\ \\\\\n"
            res += mdls

        # measures size and time
        # size = len(self)
        if self.start and self.end:
            elapsed = self.end - self.start
            if self.latex:
                res += "\\ \\\\\n"
            res += "This computation took " + str(
                round(elapsed, 4)) + " seconds, " + \
                   str(self.num_branches) + " branch" + (
                       "es" if self.num_branches > 1 else "") + \
                   " and " + str(len(self)) + " nodes.\n\n"

        # # github link
        # url = "https://github.com/nclarius/pyPL"
        # if self.latex:
        #     res += "\\ \\\\\n" + "\\textcircled{\\scriptsize{i}} " + url
        # else:
        #     res += "🛈 " + url + "\n"

        if self.latex:
            postamble = "\\end{document}\n"
            res += postamble
        if not self.latex and not self.file:
            sep = 80 * "-"
            res += sep

        self.gui.write_output(res, self.latex)

    rule_names = {"α": "alpha", "β": "beta",  # connective rules
                  "γ": "gamma", "δ": "delta", "η": "eta", "θ": "theta",
                  "ε": "epsilon",  # quantifier rules
                  "μ": "mu", "ν": "nu", "π": "pi", "κ": "kappa", "λ": "lambda",
                  "ι": "iota",  # modal rules
                  "ξ": "xi", "χ": "chi", "ο": "omicron", "u": "ypsilon",
                  "ω": "omega"  # intuitionistic rules
                  }

    def expand(self):
        """
        Recursively expand all nodes in the tableau.
        """
        if debug:
            print()
            print(self.root.treestr())
            print("--------")
            print()
        while applicable := self.applicable():
            # todo stop search when only contradictions found after all new
            #  instantiations

            # todo bad order of application for sequent calculus?

            # check whether to continue expansion
            len_assumptions = sum(
                    [len(str(node.fml)) for node in self.root.nodes()
                     if node.rule == "A"])
            num_nodes = len(self.root.nodes(True))

            # the tree gets too big; stop execution
            # todo when size limit factor is not high enough and no model is
            #  found,
            #  result should be "pot. inf." rather than closed
            # todo more models often just creates isomorphisms, rather than
            #  increasing the domain size
            if num_nodes > self.size_limit_factor * len_assumptions * \
                    self.num_models:
                # mark abandoned branches
                for leaf in self.root.leaves(True):
                    leaf.add_child(
                            (self, None, None, None, Infinite(), None, None, None))
                return

            # enough models have been found; stop the execution
            if not self.mode["validity"] and len(
                    self.models) >= self.num_models:
                # mark abandoned branches
                for leaf in self.root.leaves(True):
                    leaf.add_child(
                            (self, None, None, None, Infinite(), None, None, None))
                return

            # expand
            if debug:
                pass
                print("applicable:")
                print("(prio, target, source, name, type, arguments, apps)")
                print("\n".join([", ".join([
                        str(i), str(itm[0].line), str(itm[1].line), itm[2],
                        str(itm[3]), str(itm[5]), str(itm[6])])
                        for i, itm in enumerate(applicable)]))
            # get first applicable rule from prioritized list
            (target, source, rule_name, rule_type, fmls, args, insts) = \
            applicable[0]
            rule_type_func = getattr(self,
                                     "rule_" + Tableau.rule_names[rule_type])
            if debug:
                pass
                input()
                print("expanding:")
                print(str(source), " with ", rule_name, " on ", str(target))
            # apply the rule
            new_children = rule_type_func(target, source, rule_name, fmls, args)

            # # check properties of new children
            # for child in new_children:
            #     # todo yields open branch if only first child is contradictory
            #     if not isinstance(child.fml, Pseudo):
            #         child.branch_closed()
            #         child.branch_infinite()
            if debug:
                print()
                print(self.root.treestr())
                print("--------")
                print()
            if self.stepwise:
                self.steps.append(
                    self.root.treestr() if not self.latex else
                    self.root.treetex())

    parameters = list("abcdefghijklmnopqrst") + ["c" + str(i) for i in
                                                 range(1, 1000)]

    def applicable(self):
        """
        A prioritized list of applicable rules in the tree in the format
        {(target, source, rule name, rule type, arguments, number of
        applications)}

        @rtype: list[tuple[node,node,str,str,list[Any],int]]
        """
        # collect the applicable rules in the tree
        applicable = []
        # traverse all nodes that could be expandable
        for source in [node for node in self.root.nodes() if
                       not isinstance(node.fml, Pseudo)]:
            for rule_name, rule in source.rules().items():
                rule_type, fmls = rule

                def applied(
                        node):  # nodes in the branch that this rule has
                    # already been applied on
                    return node and \
                           node.rule and node.rule == rule_name and \
                           node.source and node.source.line and \
                           node.source.line == source.line

                # nodes to append the application's children to (usually leaves)
                targets = [node for node in source.leaves(True) if
                           not isinstance(node.fml, Pseudo)]

                # whether or not the source is a subformula of a universal
                # statement
                universal = True if source.inst and source.inst[
                    0] or rule_name == "∀" else False

                # connective rules
                if rule_type in ["α", "β"]:
                    # the rule is applicable to those branches it has not
                    # already been applied on
                    for target in targets:
                        branch = target.branch
                        if not any([applied(node) for node in branch]):
                            # whether or not the source is an instance of an
                            # implication
                            # whose antecedent does not occur on the target's
                            # branch
                            irrelevant = universal and \
                                         ((rule_name == "→" and
                                           str(fmls[0][1].phi) not in [
                                                   str(node.fml) for node in
                                                   branch]) or \
                                          (rule_name == "-∧" and
                                           str(fmls[0][1]) not in [str(node.fml)
                                                                for node in
                                                                branch] and
                                           str(fmls[1][1]) not in [str(node.fml)
                                                                for node in
                                                                branch]))
                            new = False
                            unneeded = False
                            # compose arguments
                            args = universal, irrelevant, unneeded, new
                            insts = 0
                            applicable.append((target, source, rule_name,
                                               rule_type, fmls, args, insts))

                # quantifier rules
                elif rule_type in ["γ", "δ", "η", "θ", "ε"]:
                    irrelevant = False

                    if rule_type in [
                            "θ"]:  # special treatement of targets for theta
                        # rule
                        targets = []
                        instantiations = dict()
                        for node in source.nodes():
                            if applied(node):
                                # the rule has already been applied:
                                # append the parent of the first
                                # instantiation as a target,
                                # but only if the parent is not already
                                # declared infinite,
                                # and the node to the instantiations of all
                                # its leaves
                                parent = node.branch[-2]
                                if not isinstance(parent.children[-1].fml,
                                                  Pseudo):
                                    if parent not in targets:
                                        targets.append(parent)
                                if parent not in instantiations:
                                    instantiations[parent] = []
                                if node.inst and len(node.inst) > 3:
                                    instantiations[parent].append(node)
                        for leaf in source.leaves(True):
                            if not any([node in instantiations for node in
                                        leaf.branch]):
                                # the rule has not yet been applied on this
                                # branch:
                                # add each leaf as a target if it is not
                                # finished
                                targets.append(leaf)
                                instantiations[leaf] = []

                    for target in targets:
                        branch = [node for node in target.branch if
                                  not isinstance(node.fml, Pseudo)]

                        # check if indexed constants are required (for modal
                        # PL with var. domains and IL)
                        indexed = (self.mode["modal"] and self.mode[
                            "vardomains"] or not self.mode["classical"]) and \
                                  not self.mode["propositional"]

                        # collect the constants this rule has been
                        # instantiated with in the branch/level
                        if rule_type not in ["θ"]:
                            used = list(dict.fromkeys(
                                    [str(node.inst[3]) for node in branch if
                                     applied(node)]))
                        else:
                            used = list(dict.fromkeys(
                                    [str(node.inst[3]) for node in
                                     instantiations[target]]))

                        # collect the constants occurring in the branch;
                        # for modal logic with var. domains, restricted to
                        # the constants associated with this world
                        occurring_ass = list(chain(*[[str(c)
                                                      for c in
                                                      node.fml.nonlogs()[0]]
                                                     for node in branch
                                                     if node.rule == "A"]))
                        occurring_insts = [node.inst[3] for node in branch if
                                           node.inst and
                                           len(node.inst) > 3 and isinstance(
                                                   node.inst[3], str)]
                        occurring_global = list(
                            dict.fromkeys(occurring_ass + occurring_insts))
                        if indexed:
                            occurring_local = [c for c in occurring_global if
                                               c.endswith(
                                                   "_" + str(source.world))]
                            occurring_global = [c for c in occurring_global]
                            if not self.mode["validity"]:
                                occurring_local = [(c if "_" not in c else c[
                                                                           :c.index(
                                                                               "_")])
                                                   for c in occurring_local]
                                occurring_global = [(c if "_" not in c else c[
                                                                            :c.index(
                                                                                "_")])
                                                    for c in occurring_global]
                        else:
                            occurring_local = occurring_global

                        # check if the rule requires a new constant to be
                        # instantiated,
                        # and whether this is not required by the rule type
                        if rule_type in ["γ", "θ"]:
                            new = len(used) >= len(occurring_local)
                            unneeded = new
                        elif rule_type in ["δ", "ε"]:
                            new = True
                            unneeded = False
                        elif rule_type in ["η"]:
                            new = len(occurring_local) == 0
                            unneeded = False

                        # count instantiations
                        insts = len(used)
                        # compose the arguments
                        args = universal, irrelevant, unneeded, new, indexed, used, \
                               occurring_local, occurring_global

                        if rule_type in ["γ", "δ", "θ", "ε"]:
                            # the rule is applied with some constant
                            applicable.append((target, source, rule_name,
                                               rule_type, fmls, args, insts))

                        elif rule_type in ["η"]:
                            # the rule can only be applied to nodes and
                            # constants it has not already been applied with,
                            # and only if there are constants occurring in
                            # the branch or needed for additional models
                            # yet to be instantiated;
                            # except there are no constants at all, then it
                            # may be applied with an arbitrary parameter
                            if any([not any([node.inst[3] == c + (
                            "_" + str(source.world) if indexed else "")
                                             for node in branch if
                                             applied(node)]) for c in
                                    occurring_local]) or \
                                    not occurring_local:
                                applicable.append((target, source, rule_name,
                                                   rule_type, fmls, args,
                                                   insts))

                # modal rules
                elif rule_type in ["μ", "ν", "π", "κ", "λ", "ι"]:
                    irrelevant = False
                    unneeded = False # todo check for unnnecessary new world introductions

                    if rule_type in [
                            "κ"]:  # special treatement of targets for kappa
                        # rule
                        targets = []
                        instantiations = dict()
                        for node in source.nodes():
                            if applied(node):
                                # the rule has already been applied:
                                # append the parent of the first
                                # instantiation as a target,
                                # but only if the parent is not already
                                # declared infinite,
                                # and the node to the instantiations of all
                                # its leaves
                                parent = node.branch[-2]
                                if not isinstance(parent.children[-1].fml,
                                                  Pseudo):
                                    if parent not in targets:
                                        targets.append(parent)
                                if parent not in instantiations:
                                    instantiations[parent] = []
                                if node.inst and len(node.inst) > 3:
                                    instantiations[parent].append(node)
                        for leaf in source.leaves(True):
                            if not any([node in instantiations for node in
                                        leaf.branch]):
                                # the rule has not yet been applied on this
                                # branch:
                                # add each leaf as a target if it is not
                                # finished
                                targets.append(leaf)
                                instantiations[leaf] = []

                    for target in targets:
                        branch = [node for node in target.branch if
                                  not isinstance(node.fml, Pseudo)]

                        # # collect the signatures this rule has been
                        # instantiated with in the branch/on this level
                        # used = list(dict.fromkeys([node.inst[1] for node in
                        # branch if applied(node)])) \
                        #     if rule_type not in ["κ"] else \
                        #     list(dict.fromkeys([node.inst[1] for node in
                        #     siblings]))
                        # # collect the signatures occurring in the branch
                        # occurring = list(dict.fromkeys([node.sig for node
                        # in branch if node.sig]))
                        # # collect the signatures occurring in the branch
                        # that are extensions of the source signature
                        # extensions = list(dict.fromkeys([node.sig for node
                        # in branch if node.sig and
                        #                                  len(node.sig) ==
                        #                                  len(source.sig) +
                        #                                  1 and
                        #                                  node.sig[:-1] ==
                        #                                  source.sig]))

                        # collect the worlds this rule has been instantiated
                        # with in the branch/on this level
                        if rule_type not in ["κ"]:
                            used = list(dict.fromkeys(
                                    [node.inst[3] for node in branch if
                                     applied(node)]))
                        else:
                            used = list(dict.fromkeys([node.inst[3] for node in
                                                       instantiations[target]
                                                       if node.inst and len(
                                        node.inst) > 3]))

                        # collect the worlds occurring in the branch
                        occurring_global = list(dict.fromkeys(
                                [node.world for node in branch if node.world]))
                        if rule_type in ["λ", "ι"] and not occurring_global:
                            occurring_global = [1]

                        # additional worlds to use
                        fresh = [i for i in range(1, 100) if
                                 i not in occurring_global]

                        # collect the signatures occurring in the branch that
                        # are accessible from the source world
                        extensions = list(
                            dict.fromkeys([node.inst[3] for node in branch
                                           if
                                           node.inst and len(node.inst) > 3 and
                                           node.inst[2] == source.world]))
                        if not extensions and rule_type in ["λ"]:
                            extensions = occurring_global
                        if rule_type == "ι":
                            extensions = occurring_global
                        # # for model finding, add at least one world
                        # if not self.mode["validity"] and not extensions:
                        #     extensions = occurring[:1]
                        # collect the signatures occurring in the branch that
                        # the source world is accessible from
                        reductions = list(
                            dict.fromkeys([node.inst[2] for node in branch
                                           if node.inst and len(node.inst) > 3
                                           and node.inst[3] == source.world]))

                        # check if the rule requires a new world or
                        # accessibility to be instantiated
                        if rule_type in ["μ"]:
                            new = True
                        elif rule_type in ["ν", "π", "ι"]:
                            new = False
                        elif rule_type in ["κ"]:
                            new = len(used) >= len(
                                extensions) or rule_name == "A"
                        elif rule_type in ["λ"]:
                            new = len(extensions) == 0

                        # count instantiations
                        insts = len(used)
                        # compose the arguments
                        args = universal, irrelevant, unneeded, new, used, \
                               occurring_global, extensions, reductions

                        # todo not correctly reusing already introduced
                        #  accessible worlds

                        if rule_type in ["μ"]:
                            # the rules can be applied with any new signature
                            # extension,
                            # and for satisfiability only if it has not already been used
                            if self.mode["validity"] or not used:
                                applicable.append((target, source, rule_name,
                                               rule_type, fmls, args, insts))

                        if rule_type in ["κ"]:
                            # the rules can be applied with any new signature
                            # extension,
                            applicable.append((target, source, rule_name,
                                           rule_type, fmls, args, insts))

                        elif rule_type in ["ν"]:
                            # the rule can only be applied if there are sig.
                            # ext.s in the branch yet to be instantiated
                            if any([s not in used for s in extensions]):
                                applicable.append((target, source, rule_name,
                                                   rule_type, fmls, args,
                                                   insts))

                        elif rule_type in ["π"]:
                            # the rule can only be applied if the signature
                            # has a predecessor
                            if len(source.sig) > 1:
                                applicable.append((target, source, rule_name,
                                                   rule_type, fmls, args,
                                                   insts))

                        elif rule_type in ["λ"]:
                            # the rule can only be applied to nodes and
                            # signatures it has not already been applied with,
                            # and only if there are extensions occurring in
                            # the branch or needed for additional models
                            # yet to be instantiated
                            if any([not any([node.inst[3] == w
                                             for node in branch if
                                             applied(node)])
                                    for w in
                                    extensions + fresh[:self.num_models - 1]]):
                                applicable.append((target, source, rule_name,
                                                   rule_type, fmls, args,
                                                   insts))

                        elif rule_type in ["ι"]:
                            # the rule can only be applied to nodes and
                            # signatures it has not already been applied with,
                            # and only if there are extensions occurring in
                            # the branch or needed for additional models
                            # yet to be instantiated,
                            # except when there are no signatures in the
                            # branch at all and the rule is an assumption
                            if any([not any([node.inst[3] == w
                                             for node in branch if
                                             applied(node)])
                                    for w in occurring_global]):
                                applicable.append((target, source, rule_name,
                                                   rule_type, fmls, args,
                                                   insts))

                # intuitionistic rules
                elif rule_type in ["ξ", "χ", "ο", "u", "ω"]:

                    irrelevant = False
                    unneeded = False # todo check for unnnecessary new state introductions

                    for target in targets:

                        # collect the nodes on this target branch
                        branch = [node for node in target.branch if
                                  not isinstance(node.fml, Pseudo)]

                        # collect the worlds this rule has been instantiated
                        # with in the branch/on this level
                        used = list(dict.fromkeys(
                                [node.inst[3] for node in branch if
                                 applied(node)]))

                        # collect the worlds occurring in the branch
                        occurring_global = list(dict.fromkeys(
                                [node.world for node in branch if node.world]))

                        # additional worlds to use
                        fresh = [i for i in range(1, 100) if
                                 i not in occurring_global]

                        # collect the signatures occurring in the target's branch
                        # that are accessible from the source world
                        # including the reflexive and transitive closure
                        def find_extensions(w):
                            return [w] + list(
                            dict.fromkeys([node.inst[3] for node in branch
                                           if
                                           node.inst and len(node.inst) > 3 and
                                           node.inst[2] == w]))
                        found_extensions = []
                        extensions = find_extensions(source.world)
                        for w in extensions:
                            if not found_extensions:
                                extensions += find_extensions(w)
                                found_extensions.append(w)

                        # collect the signatures occurring in the target's
                        # branch that the source world is accessible from
                        reductions = list(
                            dict.fromkeys([node.inst[2] for node in branch
                                           if node.inst and len(node.inst) > 3
                                           and node.inst[3] == source.world]))

                        # count instantiations
                        insts = len(used)

                        if rule_type in ["ξ"]:
                            # the rules can only be applied with new extensions
                            new = True

                        elif rule_type in ["χ"]:
                            # the rule can only be applied with existing extensions
                            new = False

                        # compose the arguments
                        args = universal, irrelevant, unneeded, new, used, \
                               occurring_global, extensions, reductions

                        if rule_type in ["ξ"]:
                            # the rules can only be applied with new extensions,
                            # and for satisfiability only if it has not already been used
                            if self.mode["validity"] or not used:
                                applicable.append((target, source, rule_name,
                                               rule_type, fmls, args, insts))

                        elif rule_type in ["χ"]:
                            # the rule can only be applied with existing extensions,
                            # and for satisfiability only if it has not already been used
                            # with this world
                            if [w for w in extensions if w not in used]:
                                applicable.append((target, source, rule_name,
                                                   rule_type, fmls, args, insts))

                        elif rule_type in ["ο", "u", "ω"]:
                            pass  # todo applicability for intuitionistic quantifier rules


        # if the only rules applicable to an unfinished branch are
        # δ, θ, ε or κ rules that have already been applied on this branch,
        # it is declared open and, in the case of validity tableaus,
        # its applicable rules cleared
        for leaf in [node for node in self.root.leaves() if
                     node and node.fml != None and not (
                     isinstance(node.fml, Pseudo))]:
            if all([appl[6] and appl[3] in ["δ", "θ", "ε", "κ"]
                    for appl in applicable if appl[0] in leaf.branch]):
                if not isinstance(leaf.fml, Pseudo):
                    leaf.branch_open()
                    self.models.append(self.model(leaf))
                if self.mode["validity"]:
                    applicable = [appl for appl in applicable if
                                  appl[0] not in leaf.branch]

        # if all nodes have been applied and every theta/kappa formula has
        # been inst. with a new constant/world,
        # as in a validity tableau, and the branch is still contradictory,
        # then the sequent is unsatisfiable, and the appplicable rules of the
        # entire tree are cleared
        # todo correct implementation
        # for leaf in [node for node in self.root.leaves() if isinstance(
        # node.fml, Closed)]:
        #     appl_on_branch = [appl for appl in applicable if appl[0] in
        #     leaf.branch]
        #     nary_on_branch = [node for node in leaf.branch if node.rule in
        #     ["∃", "¬∀", "◇", "¬◻"]]
        #     if all([appl[6] for appl in appl_on_branch]) and all([
        #     node.inst[2] for node in nary_on_branch]):
        #         applicable = []

        # decide which boolean values are good and bad
        rank_univ_irrel = {(True, True): 0, (False, False): 1, (True, False): 2}
        rank_new = {True: 1, False: 0}
        rank_unneeded = {True: 1, False: 0}
        # define a preference order for rule types
        rule_order = {r: i for (i, r) in enumerate(
                ["ι", "η", "λ", "α", "β", "γ", "δ", "θ", "ε", "π", "μ", "ν",
                 "κ", "ξ", "χ", "ο", "u", "ω"])}
        branching = {  # rank by branching
                "ι": 0,  # forcing rules
                "α": 0, "β": 1,  # connective rules
                "γ": 0, "δ": 0, "η": 0, "θ": 1, "ε": 1,  # quantifier rules
                "μ": 0, "ν": 0, "π": 0, "κ": 1, "λ": 0,  # modal rules
                "ξ": 1, "χ": 1, "ο": 0, "u": 0, "ω": 0  # intuitionistic rules
        }
        operator = {  # rank by operator type
                "ι": 0,  # forcing rules
                "α": 1, "β": 1,  # connective rules
                "γ": 2, "δ": 2, "η": 2, "θ": 2, "ε": 2,  # quantifier rules
                "μ": 2, "ν": 2, "π": 2, "κ": 2, "λ": 2,  # modal rules
                "ξ": 2, "χ": 2, "ο": 3, "u": 3, "ω": 3  # intuitionistic rules
        }
        # enumerate the nodes level-order so nodes can be prioritized by
        # position in the tree
        pos = {node: i for (i, node) in enumerate(self.root.nodes())}
        pos_rev = {node: i for (i, node) in
                   enumerate(self.root.nodes(True)[::-1])}
        pos_by_type = {
                "ι": pos,  # forcing rules,
                "α": pos, "β": pos,  # connective rules
                "γ": pos, "δ": pos, "η": pos_rev, "θ": pos_rev, "ε": pos_rev,
                # quantifier rules
                "μ": pos, "ν": pos, "π": pos, "κ": pos_rev, "λ": pos_rev,
                # modal rules
                "ξ": pos, "χ": pos, "ο": pos, "u": pos, "ω": pos
                # intuitionistic rules
        }

        # sort the applicable rules by ...
        sort_v1 = lambda i: (  # for validity tableaus:
                i[6],
                # 1. number of times the rule has already been applied on
                # this branch (prefer least used)
                rank_unneeded[i[5][2]],
                # 2. whether the application would unnecessarily introduce a
                # new constant or world (prefer not to)
                rule_order[i[3]],
                # 3. formula complexity (prefer getting to atoms faster)
                len(i[1].fml),
                # 4. rule type rank (prefer earlier in order)
                pos[i[1]],
                # 5. position of the source node in the tree (prefer leftmost
                # highest)
                pos[i[0]]
                # 6. position of the target node in the tree (prefer leftmost
                # highest)
        )
        sort_v2 = lambda i: (  # for satisfiability tableaus:
                i[6],
                # 1. number of times the rule has already been applied on
                # this branch (prefer least used)
                rank_univ_irrel[(i[5][0], i[5][1])],
                # 2. whether the formula comes from a relevant axiom (prefer
                # yes)
                branching[i[3]],
                # 4. whether the rules branches (prefer non-branching)
                rank_unneeded[i[5][2]],
                # 3. whether the application would unnecessarily introduce a
                # new constant or world (prefer not to)
                rank_new[i[5][3]],
                # 3. whether to introduce a new constant or world (prefer not
                # to)
                operator[i[3]],
                # 5. what type of operator the rule belongs to (connective >
                # quant., modal > int.)
                rule_order[i[3]],
                # 6. remaining rule type rank (prefer earlier in order)
                pos_by_type[i[3]][i[1]],
                # 7. position of the source node in the tree
                # (prefer leftmost lowest for sat. quant. and mod. rules,
                # leftmost highest for others)
                pos[i[0]],  # 8. position of the target node in the tree
        )
        # sort_v2 = lambda i: (  # for satisfiability tableaus:
        #     i[6],              # 1. number of times the rule has already
        #     been applied on this branch (prefer least
        #     used)
        #     rule_order[i[3]],  # 2. rule type rank (prefer earlier in order)
        #     pos_rev[i[0]],     # 3. position of the target node in the tree
        #     (prefer leftmost lowest)
        #     pos_rev[i[1]]      # 4. position of the source node in the tree
        #     (prefer leftmost lowest)
        # )
        appl_sorted = list(k for k, _ in itertools.groupby([itm for itm in
                                                            sorted(applicable,
                                                                   key=(
                                                                           sort_v1 if
                                                                           self.mode[
                                                                               "validity"] else sort_v2))]))
        self.appl = appl_sorted
        return appl_sorted

    # def update_applicable(self, node):
    #     """
    #     Inherit applicable rules from the parent and add applicable rules
    #     of the new node.
    #     """
    #     parent = node.branch[-2]
    #     rules = node.rules()
    #
    #     appl_parent = [a for a in self.applicable_ if a[0] == parent]
    #     for (target, source, rule_name, rule_type, insts, num_appls) in
    #     appl_parent:
    #
    #         # connective rules:
    #         # inherit the rule, provided the node is not itself an
    #         application of that rule
    #         if rule_type in ["α", "β"]:
    #
    #             if node.source != parent:
    #                 self.applicable_.append((node, source, rule_name,
    #                 rule_type, insts, num_appls))
    #             self.applicable_.remove((parent, source, rule_name,
    #             rule_type, insts, num_appls))
    #
    #         # quantifier rules
    #         elif rule_type in ["γ", "δ", "η", "θ"]:
    #             # todo add instantiations to applied
    #
    #             # validity tableau quant. rules:
    #             # inherit applicability
    #             if rule_type in ["γ", "δ"]:
    #                 self.applicable_.append((node, source, rule_name,
    #                 rule_type, insts, num_appls))
    #                 self.applicable_.remove((parent, source, rule_name,
    #                 rule_type, insts, num_appls))
    #
    #             # satisfiability tableau quant. rules:
    #             # inherit if unapplied, else leave unchanged
    #             elif rule_type in ["η", "θ"]:
    #                 if node.soure != parent:
    #                     self.applicable_.append((node, source, rule_name,
    #                     rule_type, insts, num_appls))
    #                     self.applicable_.remove((parent, source, rule_name,
    #                     rule_type, insts, num_appls))
    #
    #         # modal rules
    #         elif rule_type in ["μ", "ν", "π", "κ", "λ"]:
    #
    #             # validity tableau modal rules:
    #             # inherit applicability
    #             if rule_type in ["μ", "ν", "π"]:
    #                 self.applicable_.append((node, source, rule_name,
    #                 rule_type, insts, num_appls))
    #                 self.applicable_.remove((parent, source, rule_name,
    #                 rule_type, insts, num_appls))
    #
    #             # validity tableau modal rules:
    #             # inherit if unapplied, else leave unchanged
    #             elif rule_type in ["κ", "λ"]:
    #                 if node.soure != parent:
    #                     self.applicable_.append((node, source, rule_name,
    #                     rule_type, insts, num_appls))
    #                     self.applicable_.remove((parent, source, rule_name,
    #                     rule_type, insts, num_appls))
    #
    #         # intuitionistic rules
    #         elif rule_type in ["ξ", "χ", "ο", "u", "ω"]:
    #             pass  # not yet implemented

    def rule_alpha(self, target, source, rule, fmls, args):
        """
        α
        Branch unary.
        """
        line = max([node.line for node in self.root.nodes() if node.line])
        # sig = tuple([s for s in source.sig]) if source.sig else None
        world = source.world

        # append (top) node
        top = child = target.add_child(
                (self, line := line + 1, world, *fmls[0], rule, source, None, 
                len(fmls) > 1, target.context))

        # append bottom node
        if len(fmls) == 2:
            bot = top.add_child(
                    (self, line := line + 1, world, *fmls[1], rule, source, None,
                    False, top.context + [top]))

        if len(fmls) == 2 and bot:
            return [top, bot]
        else:
            return [top]

    def rule_beta(self, target, source, rule, fmls, args):
        """
        β
        Branch binary.
        """
        line = max([node.line for node in self.root.nodes() if node.line])
        # sig = tuple([s for s in source.sig]) if source.sig else None
        world = source.world

        # append (top) left node
        topleft = child = target.add_child((self, line := line + 1, world,
                                            *fmls[0], rule, source, None))

        # append bottom left node
        if len(fmls) == 4 and topleft:
            botleft = topleft.add_child((
                                        self, line := line + 1, world, *fmls[2],
                                        rule, source, None))

        # append (top) right node
        topright = child = target.add_child((self, line := line + 1, world,
                                             *fmls[1], rule, source,
                                             None))

        # append bottom right node
        if len(fmls) == 4 and topright:
            botright = topright.add_child((self, line := line + 1, world,
                                           *fmls[3], rule, source, None))

        self.num_branches += 1

        if len(fmls) == 4 and topleft and topright:
            return [topleft, botleft, topright, botright]
        else:
            return [topleft, topright]

    def rule_gamma(self, target, source, rule, fmls, args):
        """
        γ
        Branch unary with an arbitrary constant.
        """
        sign, phi, var = fmls[0]
        universal, irrelevant, unneeded, new, indexed, used, occurring_local, \
        occurring_global = args
        line = max([node.line for node in self.root.nodes() if node.line])
        # sig = tuple([s for s in source.sig]) if source.sig else None
        world = source.world

        # find a constant to substitute
        # for modal predicate logic with varying domains: add signature
        # subscript to constant
        # subscript = "_" + ".".join([str(s) for s in source.sig]) if indexed
        # else ""
        subscript = "_" + str(source.world) if indexed else ""
        usable = [c + (subscript if "_" not in c else "") for c in
                  occurring_local]
        usable += [c + subscript for c in Tableau.parameters if c not in
                   [c if "_" not in c else c[:c.index("_")] for c in
                    occurring_global]]
        usable = list(dict.fromkeys(usable))
        # choose first symbol from constants and parameters that has not
        # already been used with this particular rule
        # const_symbol = usable[least(range(len(usable)), lambda i: usable[i]
        # not in used)]
        const_symbol = usable[
            (min([i for i in range(len(usable)) if usable[i] not in used]))]
        # todo prevent arg is empty sequence error when running out of
        #  symbols to use
        const = Const(const_symbol)
        new = True if const_symbol not in occurring_local else False

        # compute formula
        inst = (universal, new, str(var), str(const))
        fml = phi.subst(var, const)

        # add node
        child = child = target.add_child(
                (self, line + 1, world, sign, fml, rule, source, inst))

        return [child]

    def rule_delta(self, target, source, rule, fmls, args):
        """
        δ
        Branch unary with a new constant.
        """
        sign, phi, var = fmls[0]
        universal, irrelevant, unneeded, new, indexed, used, occurring_local, \
        occurring_global = args
        line = max([node.line for node in self.root.nodes() if node.line])
        # sig = tuple([s for s in source.sig]) if source.sig else None
        world = source.world

        # find a constant to substitute
        # for modal predicate logic with varying domains: add signature
        # subscript to constant
        # subscript = "_" + ".".join([str(s) for s in source.sig]) if indexed
        # else ""
        subscript = "_" + str(source.world) if indexed else ""
        usable = [c + (subscript if "_" not in c else "") for c in
                  Tableau.parameters if c not in
                  [c if "_" not in c else c[:c.index("_")] for c in
                   occurring_global]]
        usable = list(dict.fromkeys(usable))
        # choose first symbol from list of parameters that does not yet occur
        # in this branch
        const_symbol = usable[(min([i for i in range(len(usable)) if
                                    usable[i] not in occurring_local]))]
        const = Const(const_symbol)
        new = True

        # compute formula
        inst = (universal, new, str(var), str(const))
        fml = phi.subst(var, const)

        # add node
        child = target.add_child(
                (self, line + 1, world, sign, fml, rule, source, inst))

        return [child]

    def rule_eta(self, target, source, rule, fmls, args):
        """
        η
        Branch n-ary with an existing constant.
        """
        sign, phi, var = fmls[0]
        universal, irrelevant, unneeded, new, indexed, used, occurring_local, \
        occurring_global = args
        line = max([node.line for node in self.root.nodes() if node.line])
        # sig = tuple([s for s in source.sig]) if source.sig else None
        world = source.world

        # find a constant to substitute
        # for modal predicate logic with varying domains: add signature
        # subscript to constant
        # subscript = "_" + ".".join([str(s) for s in source.sig]) if indexed
        # else ""
        subscript = "_" + str(source.world) if indexed else ""
        used = [c if "_" not in c else c[:c.index("_")] for c in used]
        usable = occurring_local
        usable = list(dict.fromkeys(usable))
        if not usable:
            usable += [c for c in Tableau.parameters if
                       c not in occurring_global]
        # choose first symbol from occurring that has not already been used
        # with this particular rule
        const_symbol = usable[
            (min([i for i in range(len(usable)) if usable[i] not in used]))]
        const = Const(const_symbol)
        new = True if const_symbol not in occurring_local else False

        # compute formula
        inst = (universal, new, str(var), const_symbol + subscript)
        fml = phi.subst(var, const)

        # add node
        child = target.add_child(
                (self, line + 1, world, sign, fml, rule, source, inst))

        return [child]

    def rule_theta(self, target, source, rule, fmls, args):
        """
        θ
        Branch n-ay with an arbitrary constant.
        """
        sign, phi, var = fmls[0]
        universal, irrelevant, unneeded, new, indexed, used, occurring_local, \
        occurring_global = args
        line = max([node.line for node in self.root.nodes() if node.line])
        # sig = tuple([s for s in source.sig]) if source.sig else None
        world = source.world

        # find a constant to substitute
        # for modal predicate logic varying domains: add signature subscript
        # to constant
        # subscript = "_" + ".".join([str(s) for s in source.sig]) if indexed
        # else ""
        subscript = "_" + str(source.world) if indexed else ""
        used = [c if "_" not in c else c[:c.index("_")] for c in used]
        usable = occurring_local + occurring_global + [c for c in
                                                       Tableau.parameters if
                                                       c not in
                                                       occurring_global]
        usable = list(dict.fromkeys(usable))
        # choose first symbol from occurring and parameters that has not
        # already been used with this particular rule
        const_symbol = usable[
            (min([i for i in range(len(usable)) if usable[i] not in used]))]
        const = Const(const_symbol)
        new = True if const_symbol not in occurring_local else False

        # compute formula
        inst = (universal, new, str(var), const_symbol + subscript)
        fml = phi.subst(var, const)

        # add pseudo-node to indicate branching
        if not target.children:
            pseudo = target.add_child(
                    (self, None, None, None, Empty(), rule, source, None))

        # add node
        child = target.add_child(
                (self, line + 1, world, sign, fml, rule, source, inst))

        self.num_branches += 1 if len(target.children) > 2 else 0

        return [child]

    def rule_epsilon(self, target, source, rule, fmls, args):
        """
        θ
        Branch n-ay with a new constant.
        """
        sign, phi, var = fmls[0]
        universal, irrellevant, unneeded, new, indexed, used, occurring_local, \
        occurring_global = args
        line = max([node.line for node in self.root.nodes() if node.line])
        # sig = tuple([s for s in source.sig]) if source.sig else None
        world = source.world

        # find a constant to substitute
        # for modal predicate logic varying domains: add signature subscript
        # to constant
        # subscript = "_" + ".".join([str(s) for s in source.sig]) if indexed
        # else ""
        subscript = "_" + str(source.world) if indexed else ""
        used = [c if "_" not in c else c[:c.index("_")] for c in used]
        usable = [c + (subscript if "_" not in c else "") for c in
                  Tableau.parameters if c not in
                  [c if "_" not in c else c[:c.index("_")] for c in
                   occurring_global]]
        usable = list(dict.fromkeys(usable))
        # choose first symbol from list of parameters that does not yet occur
        # in this branch
        const_symbol = usable[(min([i for i in range(len(usable)) if
                                    usable[i] not in occurring_local]))]
        const = Const(const_symbol)
        new = True

        # compute formula
        inst = (universal, new, str(var), const_symbol + subscript)
        fml = phi.subst(var, const)

        # add pseudo-node to indicate branching
        if not target.children:
            pseudo = target.add_child(
                    (self, None, None, None, Empty(), rule, source, None))

        # add node
        child = target.add_child(
                (self, line + 1, world, sign, fml, rule, source, inst))

        self.num_branches += 1 if len(target.children) > 2 else 0

        return [child]

    def rule_mu(self, target, source, rule, fmls, args):
        """
        μ
        Branch unary with a new signature.
        """
        universal, irrellevant, unneeded, new, used, occurring, extensions, reductions =\
            args
        line = max([node.line for node in self.root.nodes() if node.line])

        # choose a signature that does not already occur in this branch
        # sig = None
        # for i in range(1, 1000):
        #     if (sig_ := tuple([s for s in source.sig]) + (i,)) not in
        #     occurring:
        #         sig = sig_
        #         break
        # inst = (source.sig, sig)
        world = min([i for i in range(1, 1000) if i not in occurring])
        new = True
        inst = (universal, new, source.world, world)

        # add (top) node
        top = child = target.add_child(
                (self, line := line + 1, world, *fmls[0], rule, source, inst))

        # add bottom node
        if len(fmls) == 2 and top:
            bot = top.add_child((self, line := line + 1, world, *fmls[1], rule,
                                 source, inst))

        if len(fmls) == 2 and top:
            return [top, bot]
        else:
            return [top]

    def rule_nu(self, target, source, rule, fmls, args):
        """
        ν
        Branch unary with an existing signature.
        """
        universal, irrellevant, unneeded, new, used, occurring, extensions, reductions =\
            args
        max_line = max([node.line for node in self.root.nodes() if node.line])
        line = max_line

        # choose the first signature that already occurs in this branch but
        # has not already been used with this rule
        # sig = None
        # for i in range(1, 1000):
        #     if (sig_ := tuple([s for s in source.sig]) + (i,
        #     )) in extensions and sig_ not in used:
        #         sig = sig_
        #         break
        # inst = (source.sig, sig)
        world = min([i for i in extensions if i not in used])
        # todo correct to use extensions rather than occurring?
        new = True if world not in extensions else False
        inst = (universal, new, source.world, world)

        # add (top) node
        top = child = target.add_child(
                (self, line := line + 1, world, *fmls[0], rule, source, inst))

        # add bottom node
        if len(fmls) == 2 and top:
            bot = top.add_child((self, line := line + 1, world, *fmls[1], rule,
                                 source, inst))

        if len(fmls) == 2 and top:
            return [top, bot]
        else:
            return [top]

    def rule_kappa(self, target, source, rule, fmls, args):
        """
        κ
        Branch n-ay with an arbitrary signature.
        """
        universal, irrellevant, unneeded, new, used, occurring, extensions, reductions =\
            args
        line = max([node.line for node in self.root.nodes() if node.line])

        # choose a signature that has not already been used with this rule
        # sig = None
        # for i in range(1, 1000):
        #     if (sig_ := tuple([s for s in source.sig]) + (i,)) not in used:
        #         sig = sig_
        #         break
        # inst = (source.sig, sig)
        usable = extensions + [i for i in range(1, 100)]
        world = usable[
            min([i for i in range(len(usable)) if usable[i] not in used])]
        new = True if world not in extensions else False
        inst = (universal, new, source.world, world)

        # add pseudo-node to indicate branching
        if not target.children:
            child = target.add_child(
                    (self, None, None, None, Empty(), rule, source, None))

        # add (top) node
        top = child = target.add_child(
                (self, line := line + 1, world, *fmls[0], rule, source, inst))

        # add bottom node
        if len(fmls) == 2 and top:
            bot = top.add_child((self, line := line + 1, world, *fmls[1], rule,
                                 source, inst))

        self.num_branches += 1 if len(target.children) > 2 else 0

        if len(fmls) == 2 and top:
            return [top, bot]
        else:
            return [top]

    def rule_lambda(self, target, source, rule, fmls, args):
        """
        λ
        Branch unary with an existing signature.
        """
        universal, irrellevant, unneeded, new, used, occurring, extensions, reductions =\
            args
        max_line = max([node.line for node in self.root.nodes() if node.line])
        line = max_line

        # choose the first signature that already occurs in this branch but
        # has not already been used with this rule
        # sig = None
        # for i in range(1, 1000):
        #     if (sig_ := tuple([s for s in source.sig]) + (i,
        #     )) in extensions and sig_ not in used:
        #         sig = sig_
        #         break
        # inst = (source.sig, sig)
        usable = extensions + [i for i in range(1, 100)][:self.num_models - 1]
        world = usable[
            min([i for i in range(len(usable)) if usable[i] not in used])]
        new = True if world not in extensions else False
        inst = (universal, new, source.world, world)

        # add (top) node
        top = child = target.add_child(
                (self, line := line + 1, world, *fmls[0], rule, source, inst))

        # add bottom node
        if len(fmls) == 2 and top:
            bot = top.add_child((self, line := line + 1, world, *fmls[1], rule,
                                 source, inst))

        if len(fmls) == 2 and top:
            return [top, bot]
        else:
            return [top]

    def rule_iota(self, target, source, rule, fmls, args):
        """
        ι
        Branch unary with an existing signature.
        """
        universal, irrellevant, unneeded, new, used, occurring, extensions, reductions =\
            args
        max_line = max([node.line for node in self.root.nodes() if node.line])
        line = max_line

        # choose the first signature that already occurs in this branch but
        # has not already been used with this rule
        # sig = None
        # for i in range(1, 1000):
        #     if (sig_ := tuple([s for s in source.sig]) + (i,
        #     )) in extensions and sig_ not in used:
        #         sig = sig_
        #         break
        # inst = (source.sig, sig)
        usable = extensions + [i for i in range(1, 100)][:self.num_models - 1]
        world = usable[
            min([i for i in range(len(usable)) if usable[i] not in used])]
        new = True if world not in extensions else False
        inst = (universal, new, source.world, world)

        # add (top) node
        top = child = target.add_child(
                (self, line := line + 1, world, *fmls[0], rule, source, inst))

        # add bottom node
        if len(fmls) == 2 and top:
            bot = top.add_child((self, line := line + 1, world, *fmls[1], rule,
                                 source, inst))

        if len(fmls) == 2 and top:
            return [top, bot]
        else:
            return [top]

    def rule_pi(self, target, source, rule, fmls, args):
        """
        π
        Branch unary with a previous signature.
        """
        universal, irrellevant, unneeded, new, used, occurring, extensions, reductions =\
            args
        max_line = max([node.line for node in self.root.nodes() if node.line])
        line = max_line

        # reduce the signature
        # sig = tuple([s for s in source.sig[:-1]])
        # inst = (source.sig, sig)
        world = min([i for i in occurring if str(i) in reductions])
        new = False
        inst = (universal, new, source.world, world)

        # add (top) node
        top = child = target.add_child(
                (self, line := line + 1, world, *fmls[0], rule, source, inst))

        # add bottom node
        if len(fmls) == 2 and top:
            bot = top.add_child((self, line := line + 1, world, *fmls[1], rule,
                                 source, inst))

        if len(fmls) == 2 and top:
            return [top, bot]
        else:
            return [top]

    def rule_xi(self, target, source, rule, fmls, args):
        """
        ξ
        Branch binary with a new signature.
        """
        universal, irrellevant, unneeded, new, used, occurring, extensions, reductions =\
            args
        line = max([node.line for node in self.root.nodes() if node.line])

        # find a signature that does not already occur in this branch
        # sig = None
        # for i in range(1, 1000):
        #     if (sig_ := tuple([s for s in source.sig]) + (i,)) not in used:
        #         sig = sig_
        #         break
        # inst = (source.sig, sig)
        world = min([i for i in range(1, 1000) if str(i) not in occurring])
        new = True
        inst = (universal, new, source.world, world)

        # add left node
        left = target.add_child(
                (self, line := line + 1, world, *fmls[0], rule, source, inst))

        # add right node
        right = target.add_child(
                (self, line := line + 1, world, *fmls[1], rule, source, inst))

        return [left, right]

    def rule_chi(self, target, source, rule, fmls, args):
        """
        χ
        Branch binary with an existing signature.
        """
        universal, irrellevant, unneeded, new, used, occurring, extensions, reductions =\
            args
        max_line = max([node.line for node in self.root.nodes() if node.line])
        line = max_line

        # choose the first signature that already occurs in this branch but
        # has not already been used with this rule
        # sig = None
        # for i in range(1, 1000):
        #     if (sig_ := tuple([s for s in source.sig]) + (i,
        #     )) in extensions and sig_ not in used:
        #         sig = sig_
        #         break
        # inst = (source.sig, sig)
        world = min([i for i in extensions if i not in used])
        new = False
        inst = (universal, new, source.world, world)

        # add left node
        left = child = target.add_child(
                (self, line := line + 1, world, *fmls[0], rule, source, inst))

        # add right node
        right = child = target.add_child(
                (self, line := line + 1, world, *fmls[1], rule, source, inst))

        return [left, right]

    def rule_omicron(self, target, source, rule, fmls, args):
        """
        ο
        Branch unary with an existing signature and an arbitrary constant.
        """
        pass

    def rule_upsilon(self, target, source, rule, fmls, args):
        """
        υ
        Branch unary with a new signature and a new constant.
        """
        pass

    def rule_omega(self, target, source, rule, fmls, args):
        """
        ω
        Branch unary with an existing signature and an existing constant.
        """
        pass

    def closed(self) -> bool:
        """
        A tableau is closed iff all branches are closed.

        @return True if all branches are closed, and False otherwise
        @rtype: bool
        """
        return all([isinstance(leaf.fml, Closed) for leaf in self.root.leaves()
                    if
                    leaf.fml is not None and not isinstance(leaf.fml, Empty)])

    def open(self) -> bool:
        """
        A tableau is open iff at least one branch is open.

        @return True if at least one branch is open, and False otherwise
        @rtype: bool
        """
        return any([isinstance(leaf.fml, Open) for leaf in self.root.leaves()
                    if
                    leaf.fml is not None and not isinstance(leaf.fml, Empty)])

    def infinite(self) -> bool:
        """
        A tableau is (probably) infinite iff at least one branch is (
        probably) infinite.

        @return True if all at least one branch is infinite, and False otherwise
        @rtype: bool
        """
        return any(
                [isinstance(leaf.fml, Infinite) for leaf in self.root.leaves()
                 if leaf.fml is not None and not isinstance(leaf.fml, Empty)])

    def model(self, leaf):
        """
        The models for a tableau are the models associated with its open
        branches.
        A model for an open branch is one that satisfies all atoms in the
        branch.

        @return The models associated with the open branches the tableau.
        @rtype set[Structure]
        """
        structure = __import__("structure")

        branch = [node for node in leaf.branch if
                  not isinstance(node.fml, Pseudo)]
        # s = "S" + str(len(self.models)+1)
        s = "S" + str(leaf.line)

        def remove_sig(term):
            if "_" not in term:
                return term
            else:
                return term[:term.index("_")]

        if self.mode["classical"]:  # classical logic

            if self.mode["modal"]:  # classical modal logic
                # sigs = list(dict.fromkeys([tuple(node.sig) for node in
                # branch]))
                # sigs_ = list(dict.fromkeys([tuple(node.sig) for node in
                # branch if node.fml.liteal()]))
                # # use w1, ..., wn as ss for worlds instead of signatures
                # worlds = {sig: "w" + str(i) for (i, sig) in enumerate(sigs)}
                # w = {worlds[sig] for sig in sigs}
                # r_ = {(sig[:-1], sig) for sig in sigs if len(sig) > 1}
                # r = {(worlds[sig1], worlds[sig2]) for (sig1, sig2) in r_}
                worlds = list(dict.fromkeys(
                        [node.world for node in branch if node.world]))
                worlds_ = list(dict.fromkeys(
                        [node.world for node in branch if node.world and
                         node.fml.literal()]))
                w = {"w" + str(w) for w in worlds}
                r_ = list(dict.fromkeys([node.inst[2:] for node in branch if
                                         node.inst and len(
                                             node.inst) > 3 and isinstance(
                                                 node.inst[2], int)]))
                r = {("w" + str(tpl[0]), "w" + str(tpl[1])) for tpl in r_}

            if self.mode["propositional"]:  # classical propositional logic
                if not self.mode[
                    "modal"]:  # classical non-modal propositional logic
                    # atoms = all unnegated propositional variables
                    atoms = [node.fml.p for node in branch
                             if node.fml.atom()
                             and node.sign]
                    # todo add literals for other prop. log.s
                    natoms = [node.fml.phi.p for node in branch if
                              node.fml.literal() and not node.fml.atom()
                              and node.sign]
                    # valuation = make all positive propositional variables
                    # true and all others false
                    v = {p: (True if p in atoms else False) for p in
                         list(dict.fromkeys(atoms + natoms))}
                    model = structure.PropStructure(s, v)

                else:  # classical modal propositional logic

                    # # atoms = all unnegated propositional variables
                    # atoms = {
                    #     sig: [node.fml.p for node in branch if isinstance(
                    #     node.fml, Prop) and node.sig == sig]
                    #     for sig in sigs}
                    # # valuation = make all positive propositional variables
                    # true and all others false
                    # v = {
                    #     worlds[sig]: {p: (True if p in atoms[sig] else
                    #     False) for p in self.root.fml.propvars()}
                    #     for sig in sigs_}
                    # atoms = all unnegated propositional variables
                    atoms = {
                            w: [node.fml.p for node in branch if
                                node.fml.atom() and node.world == w
                                and node.sign]
                            for w in worlds}
                    # valuation = make all positive propositional variables
                    # true and all others false
                    v = {p: {"w" + str(w): (True if p in atoms[w] else False)
                             for w in worlds}
                         for p in self.root.fml.propvars()}
                    model = structure.PropModalStructure(s, w, r, v)

            else:  # classical predicate logic
                # predicates = all predicates occurring in the conclusion and
                # premises
                constants = set(chain(self.root.fml.nonlogs()[0],
                                      *[ass.fml.nonlogs()[0] for ass in
                                        [self.root] + self.premises]))
                # todo show constants in interpret.?
                funcsymbs = set(chain(self.root.fml.nonlogs()[1],
                                      *[ass.fml.nonlogs()[1] for ass in
                                        [self.root] + self.premises]))
                # todo take care of function symbols in domain and
                #  interpretation
                predicates = set(chain(self.root.fml.nonlogs()[2],
                                       *[ass.fml.nonlogs()[2] for ass in
                                         [self.root] + self.premises]))

                if not self.mode[
                    "modal"]:  # classical non-modal predicate logic
                    # atoms = all unnegated atomic predications
                    atoms = [(node.fml.pred, node.fml.terms) for node in branch
                             if
                             node.fml.atom() and not isinstance(node.fml, Eq)
                             and node.sign]
                    # domain = all const.s occurring in formulas
                    d = set(list(
                        chain(*[[remove_sig(t) for t in node.fml.nonlogs()[0]]
                                for node in branch if node.fml.nonlogs()])))
                    # interpretation = make all unnegated predications true
                    # and all others false
                    i = {p: {tuple([remove_sig(str(t)) for t in a[1]]) for a in
                             atoms if (Pred(p), a[1]) in atoms}
                         for p in predicates}
                    model = structure.PredStructure(s, d, i)

                else:  # classical modal predicate logic
                    # todo test
                    # atoms = all unnegated atomic predications
                    # atoms = {sig: [(node.fml.pred, node.fml.terms) for node
                    # in branch
                    #                if isinstance(node.fml, Atm) and
                    #                node.sig == sig]
                    #          for sig in sigs}
                    # i = {worlds[sig]: {p: {tuple([str(t) for t in a[1]])
                    # for a in atoms[sig]
                    #                        if (Pred(p), a[1]) in atoms[sig]}
                    #                    for p in predicates}
                    #      for sig in sigs}
                    atoms = {w: [(node.fml.pred, node.fml.terms) for node in
                                 branch
                                 if node.fml.atom() and not isinstance(node.fml,
                                                                       Eq)
                                 and node.world == w
                                 and node.sign]
                             for w in worlds}
                    i = {p: {"w" + str(w): {
                            tuple([remove_sig(str(t)) for t in a[1]]) for a in
                            atoms[w]
                            if (Pred(p), a[1]) in atoms[w]}
                             for w in worlds}
                         for p in predicates}

                    if not self.mode[
                        "vardomains"]:  # classical modal predicate logic
                        # with constant domains
                        d = set(chain(
                            *[[remove_sig(t) for t in node.fml.nonlogs()[0]] for
                              node in branch]))
                        model = structure.ConstModalStructure(s, w, r, d, i)

                    else:  # classical modal predicate logic with varying
                        # domains
                        # d = {worlds[sig]: set(chain(*[node.fml.nonlogs()[0]
                        # for node in branch
                        #                       if node.sig == sig]))
                        #      for sig in sigs}
                        d_ = set(list(
                            chain(*[[c + "_0" for c in node.fml.nonlogs()[0]]
                                    for node in branch if node.rule == "A"])) +
                                 [node.inst[3] for node in branch
                                  if node.inst and len(
                                     node.inst) > 3 and isinstance(node.inst[3],
                                                                   str)])
                        d = {"w" + str(w): set([c[:c.index("_")] for c in d_ if
                                                c.endswith("_" + str(w))]) for w
                             in
                             worlds}
                        model = structure.VarModalStructure(s, w, r, d, i)

        else:  # intuitionistic logic
            # sigs = [tuple(node.sig) for node in branch]
            # # use k1, ..., kn as ss for states instead of signatures
            # states = {sig: "k" + str(i) for (i, sig) in enumerate(sigs)}
            # k = {states[sig] for sig in sigs}
            # r_ = {(sig[:-1], sig) for sig in sigs if len(sig) > 1}
            # r = {(states[sig1], states[sig2]) for (sig1, sig2) in r_}
            states = list(dict.fromkeys([node.world for node in branch]))
            states_ = list(dict.fromkeys(
                    [node.world for node in branch if node.fml.literal()]))
            k = {"k" + str(w) for w in states}
            r_ = list(dict.fromkeys([node.inst[2:] for node in branch if
                                     node.inst and len(
                                         node.inst) > 3 and isinstance(
                                             node.inst[2], int)]))
            r = {("k" + str(tpl[0]), "k" + str(tpl[1])) for tpl in r_}

            if self.mode["propositional"]:  # intuitionstic propositional logic
                # # atoms = all unnegated propositional variables
                # atoms = {sig: [node.fml.p for node in branch if isinstance(
                # node.fml, Prop) and node.sig == sig]
                #          for sig in sigs}
                # # valuation = make all positive propositional variables
                # true and all others false
                # v = {states[sig]: {p: (True if p in atoms[sig] else False)
                # for p in self.root.fml.propvars()}
                #      for sig in sigs}
                # atoms = all unnegated propositional variables
                atoms = {k: [node.fml.p for node in branch
                             if node.fml.atom() and not isinstance(node.fml,
                                                                   Eq) and
                             node.world == k
                             and node.sign]
                         for k in states}
                # valuation = make all positive propositional variables true
                # and all others false
                v = {p: {"k" + str(k): (True if p in atoms[k] else False)
                         for k in states}
                     for p in self.root.fml.propvars()}
                model = structure.KripkePropStructure(s, k, r, v)

            else:  # intuitionistic predicate logic
                # predicates = all predicates occurring in the conclusion and
                # premises
                constants = set(chain(self.root.fml.nonlogs()[0],
                                      *[ass.fml.nonlogs()[0] for ass in
                                        [self.root] + self.premises]))
                funcsymbs = set(chain(self.root.fml.nonlogs()[1],
                                      *[ass.fml.nonlogs()[1] for ass in
                                        [self.root] + self.premises]))
                predicates = set(chain(self.root.fml.nonlogs()[2],
                                       *[ass.fml.nonlogs()[2] for ass in
                                         [self.root] + self.premises]))
                # # atoms = all unnegated atomic predications
                # atoms = {sig: [(node.fml.pred, node.fml.terms) for node in
                # branch
                #                if isinstance(node.fml, Atm) and node.sig ==
                #                sig]
                #          for sig in sigs}
                # d = {states[sig]: set(chain(*[node.fml.nonlogs()[0] for
                # node in branch
                #                               if node.sig == sig]))
                #      for sig in sigs}
                # i = {states[sig]: {p: {tuple([str(t) for t in a[1]]) for a
                # in atoms[sig]
                #                        if (Pred(p), a[1]) in atoms[sig]}
                #                    for p in predicates}
                #      for sig in sigs}
                # atoms = all unnegated atomic predications
                atoms = {k: [(node.fml.pred, node.fml.terms) for node in branch
                             if isinstance(node.fml, Atm) and node.world == k
                             and node.sign]
                         for k in states}
                d = {"k" + str(k): set(chain(
                    *[[remove_sig(t) for t in node.fml.nonlogs()[0]] for node in
                      branch
                      if node.world == k]))
                     for k in states}
                i = {p: {
                        "k" + str(k): {tuple([remove_sig(str(t)) for t in a[1]])
                                       for a in atoms[k]
                                       if (Pred(p), a[1]) in atoms[k]}
                        for k in states}
                     for p in predicates}
                model = structure.KripkePredStructure(s, k, r, d, i)

        return model


class Node(object):
    """
    A node in a tree.
    """

    def __init__(self, parent, tableau: Tableau, line: int, world: int,
                 sign: bool, fml: Formula, rule: str, source, inst: tuple, 
                 contextual: bool = False, context: list = []):
        self.tableau = tableau
        self.line = line
        # self.sig = sig
        self.world = world
        self.sign = sign
        self.fml = fml
        self.source = source
        self.rule = rule
        self.inst = inst
        self.contextual = contextual  # for sequent calculus: 
            # whether the formula is represented in the left or right context  
            # of another node and does not need to be printed
        self.context = []  # for sequent calculus: 
            # left and right context (formulas to still be expanded)
        self.branch = (parent.branch if parent else []) + [self]
        self.children = []

    def __repr__(self):
        """
        String representation of this line.
        """
        return str(self)

    def __str__(self):
        """
        String representation of this line.
        """
        open_branches = [leaf.branch for leaf in self.root().leaves() if
                         isinstance(leaf.fml, Open)]
        
        # todo plain text printout for sequent calculus

        # compute lengths of columns  # todo inefficient to recalculate for
        #  every node
        len_line = max([len(str(node.line)) for node in self.root().nodes() if
                        node.line]) + 2
        # len_sig = max(([len(".".join([str(s) for s in node.sig])) for node
        # in self.root().nodes() if node.sig])) + 1 \
        #     if [self.root.sig] else 0
        len_world = max([len(str(node.world)) for node in self.root().nodes() if
                         node.world]) + 2 \
            if any([node.world for node in self.root().nodes()]) else 0
        # len_sign = 2 if self.root().sign else 0
        len_sign = 1
        len_fml = max([len(str(node.fml)) for node in self.root().nodes()]) + 1
        len_rule = max([len(str(node.rule)) for node in self.root().nodes() if
                        node.rule])
        len_source = max(
                [len(str(node.source.line)) for node in self.root().nodes() if
                 node.source]) \
            if [node for node in self.root().nodes() if node.source] else 0

        # compute columns

        line = str(self.line) + "."
        # underline lines of open branches in MG
        if self.tableau.underline_open and not self.tableau.hide_nonopen and \
                not self.tableau.file and not self.tableau.mode["validity"] \
                and \
                any([self in branch for branch in open_branches]):
            line = "\033[4m" + line + "\033[0m" + ((len(line) - 1) * " ")
        str_line = "{:<{len}}".format((line if self.line else ""), len=len_line)

        # str_sig = "{:<{len}}".format(".".join([str(s) for s in self.sig])
        # if self.sig else "", len=len_sig) \
        #     if len_sig else ""
        label_w = "w" if self.tableau.mode["classical"] else "k"
        str_world = (label_w + str(self.world)) if self.world is not None else ""
        str_sign = ("+" if self.sign else "-") if self.sign is not None else ""
        str_fml = str(self.fml)

        # underline atoms of open branches in MG
        if self.tableau.underline_open and not self.tableau.file and \
                not self.tableau.mode["validity"] and \
                any([self in branch for branch in
                     open_branches]) and self.fml.atom():
            # todo not properly center aligned; to little padding
            str_world = (len(str_world) * " ") + "\033[4m" + str_world + "\033[0m" + \
                  (len(str_world) * " ")
            str_sign = (len(str_sign) * " ") + "\033[4m" + str_sign + "\033[0m" + \
                  (len(str_sign) * " ")
            str_fml = (len(str_fml) * " ") + "\033[4m" + str_fml + "\033[0m" + \
                  (len(str_fml) * " ")
        str_world = "{:<{len}}".format(str_world, len=len_world)
        str_sign = "{:<{len}}".format(str_sign, len=len_sign)
        str_fml = "{:^{len}}".format(str_fml, len=len_fml)

        if isinstance(self.fml, Open) or isinstance(self.fml, Infinite):
            str_cite = ""
        elif self.rule in ["A", "Ax"]:
            str_cite = "(" + self.rule + ")"
        elif not self.rule:
            str_cite = "(" + str(self.source.line) + ")"
        else:
            str_rule = "{:>{len}}".format((str(self.rule) if self.rule else ""),
                                          len=len_rule)
            str_comma = ", " if self.rule and self.source else ""
            str_source = "{:>{len}}".format(
                str(self.source.line) if self.source else "", len=len_source)
            if self.inst and len(self.inst) > 3 and self.rule != "A":
                if isinstance(self.inst[-1], str):
                    str_inst = ", " + "[" + str(self.inst[2]) + "/" + str(
                            self.inst[3]) + "]" \
                               + ("*" if self.inst[1] else "")
                elif isinstance(self.inst[-1], int):
                    str_inst = ", " + "⟨" + label_w + str(
                            self.inst[2]) + "," + label_w + str(self.inst[3]) + \
                               "⟩" \
                               + ("*" if self.inst[1] else "")
            else:
                str_inst = ""
            str_cite = "(" + str_rule + str_comma + str_source + str_inst + ")"

        # compute str
        return str_line + str_world + str_sign + str_fml + str_cite

    def tex(self):
        """
        LaTeX representation of this line.
        """
        open_branches = [leaf.branch for leaf in self.root().leaves() if
                         isinstance(leaf.fml, Open)]
        str2tex = {
                "A":  "\\mathrm{A}",
                "Ax": "\\mathrm{Ax}",
                "¬":  "\\neg",
                "∧":  "\\wedge",
                "∨":  "\\vee",
                "→":  "\\rightarrow",
                "↔":  "\\leftrightarrow",
                "⊕":  "\\oplus",
                "∃":  "\\exists",
                "∀":  "\\forall",
                "◇":  "\\Diamond",
                "◻":  "\\Box",
                "+":  "\\Vdash",
                "-":  "\\nVdash"
        }

        if self.tableau.sequent_style:
            if isinstance(self.fml, Pseudo):
                return "$\\ $"
            ctxt_l = list(dict.fromkeys(
                [node for node in self.context + [self] if node.sign]))
            ctxt_r = list(dict.fromkeys(
                [node for node in self.context + [self] if not node.sign]))
            fml = "$" + \
                "{,} ".join([node.fml.tex().\
                    replace(",", "{,}\\ \\!").replace("=", "{\\ =\\ }") 
                    for node in ctxt_l]) + \
                " \\vdash " + \
                "{,}".join([node.fml.tex()\
                    .replace(",", "{,}\\ \\!").replace("=", "{\\ =\\ }") 
                    for node in ctxt_r]) + \
                "$"
            return fml

        str_line = str(self.line) + "." if self.line else ""
        # underline lines/atoms of open branches in MG
        if self.tableau.underline_open and \
                    not self.tableau.hide_nonopen and \
                    not self.tableau.mode["validity"] and \
                    any([self in branch for branch in open_branches]):
            str_line = "\\underline{" + str_line + "}"
        
        label_w = "w" if self.tableau.mode["classical"] else "k"
        str_world = ("$" + label_w + "_" + "{" + str(
            self.world) + "}" + "$") if self.world is not None else ""
        str_sign = "$\\Vdash$" if self.sign else "$\\nVdash$" \
            if self.sign is not None and not self.tableau.sequent_style else ""
        str_fml = "$" + self.fml.tex()\
            .replace(",", "{,}\\ \\!").replace("=", "{\\ =\\ }") + "$"
        if self.tableau.underline_open and \
                    not self.tableau.mode["validity"] and \
                    any([self in branch for branch in open_branches]) and \
                    self.fml.atom():
            str_world = "\\underline{" + str_world + "}"
            str_sign = "\\underline{" + str_sign + "}"
            str_fml = "\\underline{" + str_fml + "}"
        str_cite = ""
        if isinstance(self.fml, Open) or isinstance(self.fml, Infinite):
            str_cite = ""
        elif self.rule in ["A", "Ax"] and not self.source:
            str_cite = "($" + str2tex[self.rule] + "$)"
        elif not self.rule:
            str_cite = "(" + str(self.source.line) + ")"
        else:
            str_rule = ("\\! ".join(
                    [str2tex[c] if c in str2tex else c for c in str(
                            self.rule)]) \
                            if not str(self.rule).isnumeric() else str(
                self.rule)) \
                .replace("\\neg\\! \\", "\\neg \\") if self.rule else ""
            str_comma = "{,}\\ " if self.rule and self.source else ""
            str_source = str(self.source.line) if self.source else ""
            if self.inst and len(self.inst) > 3 and self.rule != "A":
                if isinstance(self.inst[-1], str):
                    str_inst = "{,}\\ " + "\\lbrack " + str(
                            self.inst[2]) + "/" + str(
                            self.inst[3]) + " \\rbrack" \
                            + (" *" if self.inst[1] else "")
                elif isinstance(self.inst[-1], int):
                    str_inst = "{,}\\ " + "\\tpl{" + \
                            label_w + "_" + "{" + str(
                            self.inst[2]) + "}" + "{,}" + label_w + "_" + "{" + str(
                            self.inst[3]) + "}" + "}" \
                            + (" *" if self.inst[1] else "")
            else:
                str_inst = ""
            str_cite = "($" + str_rule + str_comma + str_source + str_inst + \
                    "$)"
        return " & ".join([str_line, str_world, str_sign, str_fml, str_cite]) \
            if not self.tableau.mode["classical"] or self.tableau.mode[
            "modal"] \
            else " & ".join([str_line, str_sign, str_fml, str_cite])

    def treestr(self, indent="", binary=False, last=True) -> str:
        """
        String representation of the tree whose root is this node.
        """
        if isinstance(self.fml, Empty):  # self is empty pseudo-node
            return ""
        open_branches = [leaf.branch for leaf in self.root().leaves() if
                         isinstance(leaf.fml, Open)]
        # hide non-open branches
        if self.tableau.hide_nonopen and not self.tableau.mode["validity"] and \
                not any([self in branch for branch in open_branches]):
            return ""

        res = indent
        res += "|--" if binary else ""
        res += str(self) + "\n"
        if self.children:  # self branches
            if binary:
                if not last:
                    indent += "|  "
                else:
                    indent += "   "
            if len(self.children) == 1:  # unary branching
                if childstr := self.children[0].treestr(indent, False, True):
                    res += childstr
            else:  # n-ary branching
                for child in self.children[:-1]:  # first children
                    if childstr1 := child.treestr(indent, True, False):
                        res += childstr1
                if childstr2 := self.children[-1].treestr(indent, True,
                                                          True):  # last child
                    res += childstr2
        else:  # self is leaf
            res += indent + "\n"
        return res

    def treetex(self, indent="", first=True, root=True) -> str:

        if self.tableau.sequent_style:
            res = ""
            if root:
                res += "\\ \\\\"

            str2tex = {
                    "A":  "\\mathrm{A}",
                    "Ax": "\\mathrm{Ax}",
                    "¬":  "\\neg",
                    "∧":  "\\wedge",
                    "∨":  "\\vee",
                    "→":  "\\rightarrow",
                    "↔":  "\\leftrightarrow",
                    "⊕":  "\\oplus",
                    "∃":  "\\exists",
                    "∀":  "\\forall",
                    "◇":  "\\Diamond",
                    "◻":  "\\Box",
                    "+":  "\\mathrm{L}",
                    "-":  "\\mathrm{R}"
            }
            str_rule = self.children[0].rule if self.children else ""
            if str_rule.startswith("+"):
                str_rule = str2tex[self.children[0].rule[1:]] + "\\vdash"
            elif str_rule.startswith("-"):
                str_rule = "\\vdash" + str2tex[self.children[0].rule[1:]]
            else:
                str_rule = str2tex[str_rule] if str_rule in str2tex else ""

            if self.contextual:
                # context alrady represented in another node: skip
                res += self.children[0].treetex(indent + "    ", first=True, root=False)
            elif len(self.children) == 0:
                res += indent + "\\AxiomC{" + self.tex() + "}\n"
            elif len(self.children) == 1:
                if isinstance(self.children[0].fml, Closed):  # axiom
                    res += "\\AxiomC{}\n"
                    res += indent + "\\RightLabel{($\\_\\vdash\\_$)}\n"
                    res += indent + "\\UnaryInfC{" + self.tex() + "}\n"
                elif isinstance(self.children[0].fml, Pseudo):  # open assumption
                    res += indent + "\\AxiomC{" + self.tex() + "}\n"
                else:
                    res += self.children[0].treetex(indent + "    ", first=True, root=False)
                    res += indent + "\\RightLabel{($" + str_rule + \
                        "$)}\n"
                    res += indent + "\\UnaryInfC{" + self.tex() + "}\n"
            elif len(self.children) == 2:
                res += self.children[0].treetex(indent + "    ", first=True, root=False)
                res += self.children[1].treetex(indent + "    ", first=True, root=False)
                res += indent + "\\RightLabel{($" + str_rule + "$)}\n"
                res += indent + "\\BinaryInfC{" + self.tex() + "}\n"
            if root:
                res += "\\DisplayProof\n\n"
            return res

        open_branches = [leaf.branch for leaf in self.root().leaves() if
                         isinstance(leaf.fml, Open)]
        # hide non-open branches
        if self.tableau.hide_nonopen and not self.tableau.mode["validity"] and \
                not any([self in branch for branch in open_branches]):
            return ""
        colspec = ("{R{4.5em}L{1em}cL{4.5em}}" if self.tableau.mode[
            "propositional"] else "{R{7.5em}L{1em}cL{7.5em}}") \
            if not (self.tableau.mode["modal"] or not self.tableau.mode[
            "classical"]) else "{R{5.4em}L{1.6em}L{1em}cL{12em}}"
        ssep = ("-4em" if self.tableau.mode["propositional"] else "-7em") if \
            not \
        self.tableau.mode["modal"] else \
            "-4.5em"
        hoffset = (
            "-4.5em" if self.tableau.mode["propositional"] else "-7.5em") if \
            not \
        self.tableau.mode["modal"] else \
            "-4.5em"  # todo not entirely accurate
        res = ""
        if root:
            res += "\\hspace*{%s}\n" % hoffset
            res += "\\begin{forest}\n"
            res += "for tree={"
            res += "anchor=north, l sep=2em, s sep=" + ssep
            res += "}\n"
            indent += "    "
            res += indent + "[\n"
        if first:
            res += indent + "\\begin{tabular}" + colspec + "\n"
        res += indent + self.tex()
        if self.children:
            if len(self.children) == 1:  # no branching
                res += "\\\\\n"
                res += self.children[0].treetex(indent, first=False, root=False)
            else:  # branching
                res += "\n" + indent + "\\end{tabular}\n"
                for child in self.children:
                    if child.fml is not None and child.fml.tex() and \
                            not isinstance(child.fml, Empty) and \
                            not (self.tableau.hide_nonopen and 
                                not self.tableau.mode["validity"] and 
                                not any([child in branch for branch in
                                      open_branches])):
                        indent += "    "
                        res += indent + "[\n"
                        res += child.treetex(indent, first=True, root=False)
                        res += indent + "]\n"
                        indent = indent[:-4]
        else:  # leaf
            res += indent + "\\end{tabular}\n"
        if root:
            res += indent + "]\n"
            indent = indent[:-4]
            res += "\\end{forest}\n"
        return res

    def nodes(self, root=True, reverse=False, preorder=False):
        """
        Pre-order traversal:
          First visit the node itself, then recurse through its children.
        Level-order traversal:
          Not reversed: First visit the nodes on a level from left to right,
          then recurse through the nodes' children.
          Reversed:     First visit the nodes on a level from left to right,
          then recurse through the nodes' parents.
        """
        res = []
        if preorder:  # preorder
            res = [self]
            for child in self.children:
                res += child.nodes()
            return res
        else:
            if not reverse:  # forwards level-order
                if root:
                    res.append(self)
                for child in self.children:
                    res.append(child)
                    res += child.nodes(False, False)
            else:  # reverse level order
                if root:
                    res.append(self)
                for child in self.children[::-1]:
                    res.append(child)
                    res += child.nodes(False, True)
                if root:
                    res = res[::-1]
            return res

    def leaves(self, excludepseudo=False):
        """
        Get the leaf nodes descending from the this node.
        """
        if not excludepseudo:
            return [node for node in self.nodes() if not node.children]
        else:
            return [node for node in self.nodes() if
                    not node.children and not isinstance(node.fml, Pseudo)]

    def root(self):
        """
        The root of this node (= root of the tableau).
        """
        return self.branch[0]

    def add_child(self, spec):
        """
        Add a child to the current node.
        """
        # don't add children to branches that are empty, already closed,
        # open or declared infinite
        if isinstance(self.fml, Pseudo) or \
                (self.children and
                 (isinstance(self.children[0].fml, Pseudo) and not isinstance(
                         self.children[0].fml, Empty) or
                  isinstance(self.children[-1].fml, Pseudo) and not isinstance(
                                 self.children[-1].fml, Empty))):
            return

        # add the child
        child = Node(self, *spec)
        if self.tableau.sequent_style:
            child.context += list(dict.fromkeys(
                # formulas still expandable on the node attached to, 
                # passing siblings of the same rule applications,
                # excluding the source itself
                [entry[1] for entry in self.tableau.appl if 
                    entry[0] in [node.branch[-2] for node in child.branch 
                        if node.source == child.source and 
                        len(node.branch) >= 2] and
                    not entry[1] == child.source] + \
                # literals
                [node for node in self.branch if node.fml.atom()] + \
                # sibling nodes of alpha rules collapsed into the same node
                [node for node in self.branch if node.source == child.source]
                ))
        self.children.append(child)

        if not isinstance(child.fml, Pseudo):
            # check properties of new child
            child.branch_closed()
            child.branch_infinite()

        return child

    def rules(self):
        mode = self.tableau.mode
        if self.sign:
            return self.fml.tableau_pos(mode) if self.fml and self.fml.tableau_pos(
            mode) else dict()
        else:
            return self.fml.tableau_neg(mode) if self.fml and self.fml.tableau_neg(
            mode) else dict()
    
    def branch_closed(self):
        """
        Check for a contradiction with this node and i.a. add a respective
        label to the branch.

        @return: True iff there is a contradiction in this node or between
        this node and some other node on the branch
        @rtype bool
        """
        if isinstance(self.fml, Pseudo):
            return
        for node in self.branch[::-1]:
            if self.fml and self.world == node.world and (
                    (self.sign and self.fml.tableau_contradiction_pos(node.fml,
                                                                      node.sign)) or
                    (not self.sign and self.fml.tableau_contradiction_neg(
                            node.fml, node.sign))
            ):
                rule = str(node.line) if node != self else ""
                source = self
                self.add_child((
                               self.tableau, None, None, None, Closed(), rule, source,
                               None))
                return True
        return False

    def branch_open(self):
        """
        Check if a branch is terminally open and i.a. add a respective label
        to the branch.
        A branch is terminally open if it has no undelayed unapplied or
        undelayed gamma rules.

        @return: True if the branch is not closed and there are no more rules
        applicable
        @rtype bool
        """
        if isinstance(self.fml, Pseudo):
            return
        self.add_child((self.tableau, None, None, None, Open(), None, None, None))
        return True

    def branch_infinite(self):
        """
        Check if a branch is potentially infinite and i.a. add a respective
        label to the branch.
        A branch or level is judged potentially infinite iff
        it there are more constants or worlds introduced than are symbols in
        the assumptions.

        @return: True if the branch is potentially infinite
        @rtype bool
        """
        if isinstance(self.fml, Pseudo):
            return
        # todo smarter implementation (check for loops in rule appls.)
        len_assumptions = sum([len(node.fml) for node in self.branch
                               if node.rule == "A"])
        height = len(self.branch)
        width = len(self.branch[-2].children)
        if height > self.tableau.size_limit_factor * len_assumptions:
            self.add_child(
                    (self.tableau, None, None, None, Infinite(), None, None, None))
            return True
        if width > self.tableau.size_limit_factor * len_assumptions:
            self.branch[-2].add_child(
                    (self.tableau, None, None, None, Infinite(), None, None, None))
            return True
        # num_consts_vertical = len(dict.fromkeys(chain(*[node.fml.nonlogs()[0]
        #                                                 for node in
        #                                                 self.branch
        #                                                 if not isinstance(
        #                                                 node.fml, Pseudo)
        #                                                 and
        #                                                 node.fml.nonlogs()])))
        # num_consts_horizontal = len(dict.fromkeys(chain(*[node.fml.nonlogs(
        # )[0]
        #                                                   for node in
        #                                                   self.branch[
        #                                                   -2].children
        #                                                   if not
        #                                                   isinstance(
        #                                                   node.fml, Pseudo)
        #                                                   and
        #                                                   node.fml.nonlogs(
        #                                                   )])))
        # num_worlds_vertical = len(dict.fromkeys([node.world
        #                                          for node in self.branch if
        #                                          node.world]))
        # num_worlds_horizontal = len(dict.fromkeys([node.world
        #                                            for node in self.branch[
        #                                            -2].children if
        #                                            node.world]))
        # if num_consts_vertical > len_assumptions or num_worlds_vertical >
        # len_assumptions:
        #     self.add_child((None, None, Infinite(), None, None, None))
        #     return True
        # if num_consts_horizontal > len_assumptions or num_worlds_horizontal
        # > len_assumptions:
        #     self.branch[-2].add_child((None, None, Infinite(), None, None,
        #     None))
        #     return True
        return False


####################

if __name__ == "__main__":
    pass

    # parse_f = FmlParser().parse

    #############
    # basic examples
    ############

    # fml = Biimp(Neg(Conj(Prop("p"), Prop("q"))), Disj(Neg(Prop("p")),
    # Neg(Prop("q"))))
    # tab = Tableau(fml, propositional=True)
    # 
    # fml = Conj(Imp(Prop("p"), Prop("q")), Prop("r"))
    # tab = Tableau(fml, validity=True, propositional=True)
    # tab = Tableau(fml, validity=False, satisfiability=True,
    # propositional=True)
    # tab = Tableau(fml, validity=False, satisfiability=False,
    # propositional=True)
    # 
    # fml1 = Imp(Prop("p"), Prop("q"))
    # fml2 = Imp(Prop("q"), Prop("r"))
    # fml = Imp(Prop("p"), Prop("r"))
    # tab = Tableau(fml, premises=[fml1, fml2], propositional=True)
    # 
    # fml1 = Atm(Pred("P"), (Const("a"), Const("a")))
    # fml2 = Neg(Eq(Const("a"), Const("a")))
    # tab = Tableau(premises=[fml1, fml2], validity=False)
    # 
    # fml1 = Imp(Atm(Pred("P"), (Const("a"), Const("b"))), Atm(Pred("Q"),
    # (Const("a"), Const("c"))))
    # fml = Atm(Pred("R"), (Const("a"), Const("a")))
    # tab = Tableau(fml, premises=[fml1])
    # 
    # fml = Conj(Exists(Var("x"), Atm(Pred("P"), (Var("x"),))), Neg(Forall(
    # Var("x"), Atm(Pred("P"), (Var("x"),)))))
    # tab = Tableau(fml, validity=True)
    # tab = Tableau(fml, validity=False, satisfiability=True)
    # tab = Tableau(fml, validity=False, satisfiability=False)
    # 
    # fml = Biimp(Forall(Var("x"), Atm(Pred("P"), (Var("x"),))),
    #             Neg(Exists(Var("x"), Neg(Atm(Pred("P"), (Var("x"),))))))
    # tab = Tableau(fml)
    # fml1 = Exists(Var("y"), Forall(Var("x"), Atm(Pred("R"), (Var("x"),
    # Var("y")))))
    # fml2 = Forall(Var("x"), Exists(Var("y"), Atm(Pred("R"), (Var("x"),
    # Var("y")))))
    # tab = Tableau(fml2, premises=[fml1])
    # tab = Tableau(fml1, premises=[fml2])
    # 
    # fml = Exists(Var("x"), Forall(Var("y"), Neg(Atm(Pred("P"), (Var("x"), Var("y"))))))
    # fml1 = Neg(Forall(Var("x"), Exists(Var("y"), Atm(Pred("P"), (Var("x"), Var("y"))))))
    # tab = Tableau(fml, premises=[fml1])

    # uniqueness quantifier
    # fml = Biimp(Exists(Var("x"), Conj(Atm(Pred("P"), (Var("x"),)),
    #                                   Neg(Exists(Var("y"), Conj(Atm(Pred(
    #                                   "P"), (Var("y"),)),
    #                                                             Neg(Eq(Var(
    #                                                             "x"),
    #                                                             Var(
    #                                                             "y")))))))),
    #             Exists(Var("x"), Forall(Var("y"), Biimp(Atm(Pred("P"),
    #             (Var("y"),)), Eq(Var("x"), Var("y"))))))
    # tab = Tableau(fml)

    # # logic for computer scientists SS80, sheet 07 ex. 02
    # fml1 = Exists(Var("x"), Forall(Var("y"), Conj(Atm(Pred("P"), (Var("x"),)),
    #                                               Atm(Pred("R"), (Var("x"),
    #                                               Var("y"))))))
    # tab = Tableau(fml1, validity=False, satisfiability=True)
    # tab = Tableau(fml1, validity=False, satisfiability=False)
    # fml2 = Imp(Exists(Var("x"), Forall(Var("y"), Atm(Pred("R"), (Var("x"),
    # Var("y"))))),
    #            Forall(Var("x"), Atm(Pred("R"), (Var("x"), Var("x")))))
    # tab = Tableau(fml2, validity=False, satisfiability=True, num_models=2)
    # tab = Tableau(fml2, validity=False, satisfiability=False)
    # fml3 = Disj(Exists(Var("x"), Forall(Var("y"), Atm(Pred("R"), (Var("x"),
    # Var("y"))))),
    #             Forall(Var("y"), Exists(Var("x"), Neg(Atm(Pred("R"),
    #             (Var("x"), Var("y")))))))
    # tab = Tableau(fml3, validity=False, satisfiability=True, num_models=2,
    # latex=False)
    # tab = Tableau(fml3, validity=False, satisfiability=False)

    ###############
    # modal logic
    ###############

    # fml = Biimp(Nec(Prop("p")), Neg(Poss(Neg(Prop("p")))))
    # tab = Tableau(fml, propositional=True, modal=True)
    #
    # fml1 = Nec(Prop("p"))
    # fml = Poss(Prop("p"))
    # tab = Tableau(fml, premises=[fml1], propositional=True, modal=True)
    # 
    # fml1 = Poss(Exists(Var("x"), Atm(Pred("P"), (Var("x"),))))
    # fml = Exists(Var("x"), Poss(Atm(Pred("P"), (Var("x"),))))
    # tab = Tableau(fml, premises=[fml1], modal=True)
    #
    # fml = Imp(Forall(Var("x"), Nec(Atm(Pred("P"), (Var("x"),)))), Nec(Forall(Var("x"), Atm(Pred("P"), (Var("x"),)))))
    # tab = Tableau(fml, modal=True)
    # 
    # fml = Imp(Exists(Var("x"), Nec(Atm(Pred("P"), (Var("x"),)))), Nec(Exists(Var("x"), Atm(Pred("P"), (Var("x"),)))))
    # tab = Tableau(fml, modal=True)
    #
    # fml = Nec(Falsum())
    # tab = Tableau(fml, propositional=True, modal=True, validity=False)
    # 
    # fml = Conj(Poss(Prop("p")), Poss(Neg(Prop("p"))))
    # tab = Tableau(fml, modal=True)
    # tab = Tableau(fml, propositional=True, modal=True, validity=False)

    # fml = Disj(Nec(Prop("p")), Nec(Prop("q")))
    # fml1 = Nec(Disj(Prop("p"), Prop("q")))
    # tab = Tableau(fml, premises=[fml1], validity=False, satisfiability=False, propositional=True, modal=True)

    # fml = Imp(Nec(Exists(Var("x"), Atm(Pred("P"), (Var("x"),)))), Exists(Var("x"), Nec(Atm(Pred("P"), (Var("x"),)))))
    # tab = Tableau(fml, modal=True)
    # tab = Tableau(fml, modal=True, validity=False)
    # tab = Tableau(fml, modal=True, validity=False, satisfiability=False)
    #
    # fml = Exists(Var("x"), Poss(Imp(Nec(Atm(Pred("P"), (Var("x"),))), Forall(Var("x"), Atm(Pred("P"), (Var("x"),))))))
    # tab = Tableau(fml, modal=True)
    # tab = Tableau(fml, modal=True, vardomains=True)
    # tab = Tableau(fml, validity=False, modal=True, vardomains=True)
    # tab = Tableau(fml, validity=False, satisfiability=False, modal=True, vardomains=True)
    #
    # fml = Imp(Exists(Var("x"), Forall(Var("y"), Nec(Atm(Pred("Q"), (Var("x"), Var("y")))))),
    #           Forall(Var("y"), Nec(Exists(Var("x"), Atm(Pred("Q"), (Var("x"), (Var("y"))))))))
    # tab = Tableau(fml, modal=True)
    # tab = Tableau(fml, modal=True, vardomains=True)
    # tab = Tableau(fml, validity=False, modal=True, vardomains=True)
    # tab = Tableau(fml, validity=False, satisfiability=False, modal=True, vardomains=True)
    #
    # fml = Imp(Conj(Exists(Var("x"), Poss(Atm(Pred("P"), (Var("x"),)))),
    #                Nec(Forall(Var("x"), Imp(Atm(Pred("P"), (Var("x"),)), Atm(Pred("R"), (Var("x"),)))))),
    #           Exists(Var("x"), Poss(Atm(Pred("R"), (Var("x"),)))))
    # tab = Tableau(fml, modal=True)
    # tab = Tableau(fml, modal=True, vardocanmains=True)
    # tab = Tableau(fml, validity=False, modal=True, vardomains=True)
    # tab = Tableau(fml, validity=False, satisfiability=False, modal=True, vardomains=True)
    # # todo results correct?
    # #
    # Barcan formulas
    # fml1 = Imp(Forall(Var("x"), Nec(Atm(Pred("P"), (Var("x"),)))), Nec(Forall(Var("x"), Atm(Pred("P"), (Var("x"),)))))
    # fml2 = Imp(Poss(Exists(Var("x"), Atm(Pred("P"), (Var("x"),)))), Exists(Var("x"), Poss(Atm(Pred("P"), (Var("x"),
    #                                                                                                       )))))
    # fml3 = Imp(Nec(Forall(Var("x"), Atm(Pred("P"), (Var("x"),)))), Forall(Var("x"), Nec(Atm(Pred("P"), (Var("x"),)))))
    # fml4 = Imp(Exists(Var("x"), Poss(Atm(Pred("P"), (Var("x"),)))), Poss(Exists(Var("x"), Atm(Pred("P"), (Var("x"),
    # )))))
    # tab1 = Tableau(fml1, modal=True)
    # tab2 = Tableau(fml1, modal=True)
    # tab3 = Tableau(fml2, modal=True, validity=False, satisfiability=False, vardomains=True)
    # # counter model: D(w1) = {a}, D(w2) = {a,b}, I(w1)(P) = {}, I(w2)(P) = {b}
    # tab4 = Tableau(fml4, modal=True, validity=False, satisfiability=False, vardomains=True)
    # # counter model: D(w1) = {a,b}, D(w2) = {a}, I(w1)(P) = {}, I(w2)(P) = {b}
    # tab1 = Tableau(fml2, modal=True, vardomains=True)
    # tab2 = Tableau(fml4, modal=True, vardomains=True)
    # fml5 = Poss(Exists(Var("x"), Atm(Pred("U"), (Var("x"),))))
    # fml6 = Neg(Exists(Var("x"), Poss(Atm(Pred("U"), (Var("x"),)))))
    # tab5 = Tableau(premises=[fml5, fml6], modal=True, validity=False, vardomains=True)

    #################
    # quantifier commutativity
    #################
    #
    # fml1 = Exists(Var("y"), Forall(Var("x"), Atm(Pred("R"), (Var("x"), Var("y")))))
    # fml2 = Forall(Var("x"), Exists(Var("y"), Atm(Pred("R"), (Var("x"), Var("y")))))
    # tab = Tableau(fml2, premises=[fml1])
    # tab = Tableau(fml2, premises=[fml1], validity=False, satisfiability=False)
    # tab = Tableau(fml1, premises=[fml2], validity=False, satisfiability=False, latex=True, num_models=2)
    #
    # fml1 = Exists(Var("y"), Conj(Atm(Pred("Q"), (Var("y"),)),
    #                              Forall(Var("x"), Imp(Atm(Pred("P"), (Var("x"),)),
    #                                                   Atm(Pred("R"), (Var("x"), Var("y")))))))
    #
    # fml2 = Forall(Var("x"), Imp(Atm(Pred("P"), (Var("x"),)),
    #                             Exists(Var("y"), Conj(Atm(Pred("Q"), (Var("y"),)),
    #                                                   Atm(Pred("R"), (Var("x"), Var("y")))))))
    # fml3 = Exists(Var("x"), Atm(Pred("P"), (Var("x"),)))
    # tab = Tableau(fml2, premises=[fml1])
    # tab = Tableau(fml1, premises=[fml2])
    # tab = Tableau(fml1, premises=[fml2, fml3], validity=False, satisfiability=False)
    #
    # ax1 = Forall(Var("x"), Imp(Atm(Pred("tupperbox"), (Var("x"),)), Neg(Atm(Pred("lid"), (Var("x"),)))))
    # ax2 = Forall(Var("x"), Imp(Atm(Pred("lid"), (Var("x"),)), Neg(Atm(Pred("tupperbox"), (Var("x"),)))))
    # fml1 = Exists(Var("y"), Conj(Atm(Pred("lid"), (Var("y"),)),
    #                               Forall(Var("x"), Imp(Atm(Pred("tupperbox"), (Var("x"),)),
    #                                                    Atm(Pred("fit"), (Var("x"), Var("y")))))))
    # fml2 = Forall(Var("x"), Imp(Atm(Pred("tupperbox"), (Var("x"),)),
    #                             Exists(Var("y"), Conj(Atm(Pred("lid"), (Var("y"),)),
    #                                                   Atm(Pred("fit"), (Var("x"), Var("y")))))))
    # fml3 = Exists(Var("x"), Atm(Pred("tupperbox"), (Var("x"),)))
    # tab = Tableau(fml2, premises=[fml1])
    # tab = Tableau(fml1, premises=[fml2])
    # tab = Tableau(fml1, premises=[fml2, fml3], validity=False, satisfiability=False)
    # tab = Tableau(fml1, premises=[fml2, fml3], axioms=[ax1], validity=False, satisfiability=False)
    # tab = Tableau(fml1, premises=[fml2, fml3], axioms=[ax1, ax2], validity=False, satisfiability=False)

    #####################
    # function symbols and equality
    #####################
    # fml1 = Forall(Var("x"), Forall(Var("y"), Forall(Var("z"),
    #                                                 Disj(Disj(
    #                                                     Eq(Var("x"), Var("y")),
    #                                                     Eq(Var("x"), Var("z"))),
    #                                                     Eq(Var("y"), Var("z"))))))
    # fml2 = Exists(Var("x"), Exists(Var("y"), Neg(Eq(Var("x"), Var("y")))))
    # tab = Tableau(None, premises=[fml1, fml2], validity=False, hide_nonopen=True)
    # # todo inefficient (open branch has 193 nodes)

    #####################
    # linguistic examples
    #####################

    # fml = Exists(Var("x"), Exists(Var("y"), Atm(Pred("love"), (Var("x"), Var("y")))))
    # tab = Tableau(fml, validity=False)
    # tab = Tableau(fml, validity=False, linguistic=True)
    # 
    # fml = Exists(Var("x"), Exists(Var("y"),
    #                               Conj(Neg(Eq(Var("x"), (Var("y")))), Atm(Pred("love"), (Var("x"), Var("y"))))))
    # tab = Tableau(fml, validity=False)
    # 
    # fml = Exists(Var("x"), Conj(Atm(Pred("Rabbit"), (Var("x"),)),
    #                             Exists(Var("y"), Conj(Atm(Pred("Carrot"), (Var("y"),)),
    #                                                   Atm(Pred("Eat"), (Var("x"), Var("y")))))))
    # ax1 = Forall(Var("x"), Conj(Imp(Atm(Pred("Rabbit"), (Var("x"),)), Neg(Atm(Pred("Carrot"), (Var("x"),)))),
    #                            Imp(Atm(Pred("Carrot"), (Var("x"),)), Neg(Atm(Pred("Rabbit"), (Var("x"),))))))
    # tab = Tableau(fml, axioms=[ax1], validity=False)
    # 
    # fml = Forall(Var("x"), Imp(Atm(Pred("student"), (Var("x"),)),
    #                            Exists(Var("y"), Conj(Atm(Pred("book"), (Var("y"),)),
    #                                                  Atm(Pred("read"), (Var("x"), Var("y")))))))
    # fml1 = Exists(Var("x"), Atm(Pred("student"), (Var("x"),)))
    # tab = Tableau(fml, premises=[fml1], validity=False)
    # 
    # ax1 = Forall(Var("x"), Imp(Atm(Pred("student"), (Var("x"),)), Atm(Pred("human"), (Var("x"),))))
    # ax2 = Forall(Var("x"), Imp(Atm(Pred("book"), (Var("x"),)), Atm(Pred("object"), (Var("x"),))))
    # ax3 = Forall(Var("x"), Imp(Atm(Pred("human"), (Var("x"),)), Neg(Atm(Pred("object"), (Var("x"),)))))
    # ax4 = Forall(Var("x"), Imp(Atm(Pred("object"), (Var("x"),)), Neg(Atm(Pred("human"), (Var("x"),)))))
    # prem1 = Atm(Pred("student"), (Const("m"),))
    # prem2 = Atm(Pred("student"), (Const("p"),))
    # fml = Forall(Var("x"), Imp(Atm(Pred("student"), (Var("x"),)),
    #                            Exists(Var("y"), Conj(Atm(Pred("book"), (Var("y"),)),
    #                                                  Atm(Pred("read"), (Var("x"), Var("y")))))))
    # tab = Tableau(fml, premises=[prem1, prem2], axioms=[ax1, ax2, ax3, ax4], validity=False, size_limit_factor=4)
    # 
    # fml1 = Forall(Var("x"), Exists(Var("y"), Atm(Pred("know"), (Var("x"), Var("y")))))
    # fml2 = Exists(Var("y"), Forall(Var("x"), Atm(Pred("know"), (Var("x"), Var("y")))))
    # tab = Tableau(fml2, premises=[fml1], validity=False, satisfiability=False)

    ###############
    # sequent calculus
    ###############
    prms = []
    fml = Prop("s")
    prms.append(Disj(Prop("p"), Prop("q")))
    prms.append(Imp(Prop("q"), Conj(Prop("r"), Prop("s"))))
    prms.append(Neg(Prop("p")))
    fml = Imp(Disj(Imp(Prop("p"), Prop("r")), Imp(Prop("q"), Prop("r"))), Imp(Conj(Prop("p"), Prop("q")), Prop("r")))
    fml = Disj(Prop("p"), Neg(Prop("p")))
    tab = Tableau(fml, premises=prms, sequent_style=True)


    ####################
    # parser
    ####################
    # test = r"((\all x \nec P(x) v \exi y (P(y) ^ R(c,y))) -> \falsum)"
    # print(test)
    # res = parser.parse(test)
    # print(res)
