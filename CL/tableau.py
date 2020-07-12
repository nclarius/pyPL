#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tableau proofs and model extraction.
THIS PART IS STILL UNDER CONSTRUCTION.
"""

from main import *
from expr import *
from structure import *

from typing import List, Dict, Set, Tuple
from itertools import chain

# todo
# - make modal rules work
# - var for mode in expr
# - merge with IL
# - tex

classical = True


class Tableau(object):
    """
    A tableau tree.
    """

    def __init__(self, conclusion=None, premises=[], validity=True,
                 classical=True, propositional=False, modal=False, vardomain=False, frame="K"):
        # todo documentation
        # settings
        self.validity = validity
        # todo check consistency of settings
        self.classical = classical
        self.propositional = propositional
        self.modal = modal
        self.vardomain = vardomain
        self.frame = frame
        sig = [1] if modal else None

        # append initial nodes
        root_fml = conclusion if conclusion else premises[0]
        self.root = Node(1, sig, (Neg(root_fml) if validity else root_fml), "(A)", None, self)
        if rules := self.root.rules():
            for rule in rules:
                self.root.set_applicable(self.root, rule[0], rule[1])
        self.premises = [self.root.leaves()[0].add_child((i + 2, sig, premise, "(A)"))
                         for i, premise in (enumerate(premises) if conclusion else enumerate(premises[1:]))]

    def __str__(self):
        """
        Expand the tableau, generate the associate models and print some info.
        """
        # todo systematic error handling
        if not self.propositional and self.root.fml.freevars():
            print("ERROR: You may only enter closed formulas.")
            return

        res = "\n"

        # print info
        res += "You are using " + \
               ("classical " if self.classical else "intuitionistic ") + \
               ("modal " if self.modal else "") + \
               ("propositional " if self.propositional else "predicate ") + \
               "logic" + \
               (" with " + ("varying " if self.vardomain else "constant ") + "domains"
                if self.modal and not self.propositional else "") + \
               (" in a " + self.frame + " frame" if self.modal else "") + \
               ".\n\n"
        if self.validity:
            res += "Tableau for " + \
                   ", ".join([str(premise.fml) for premise in self.premises]) + " ⊨ " + str(self.root.fml.phi) + ":\n\n"
        else:
            res += "Tableau for " + \
                   ", ".join([str(node.fml) for node in [self.root] + self.premises]) + " ⊭ ⊥:\n\n"

        # recursively apply the rules
        self.expand()

        # print the tableau
        res += self.root.treestr()

        # print result
        if self.closed():
            res += "The tableau is closed:\n"
            if self.validity:
                res += "The " + ("inference" if self.premises else "formula") + " is valid.\n"
            else:
                res += "The " + ("set of sentences is inconsistent\n." if self.premises else
                                 "formula is unsatisfiable.\n")
        elif self.open():
            res += "The tableau is open:\n"
            if self.validity:
                res += "The " + ("inference" if self.premises else "formula") + " is invalid.\n"
            else:
                res += "The " + ("set of sentences is consistent.\n" if self.premises else
                                 "formula is satisfiable.\n")
        elif self.infinite():
            res += "The tableau is potentially infinite:\n"
            if self.validity:
                res += "The " + ("inference" if self.premises else "formula") + " may or may not be valid.\n"
            else:
                res += "The " + ("set of sentences" if self.premises else "formula") + " may or may not be " + \
                       ("consistent.\n" if self.premises else "satisfiable.\n")

        # generate and print models
        if models := self.models():
            res += "\nCounter models:\n" if self.validity else "\nModels:\n"
            for model in models:
                res += "\n"
                res += str(model) + "\n"

        res += "\n" + 80 * "-"
        return res

    def tex(self):
        """
        Expand the tableau, generate the associate models and print some info.
        """
        # todo systematic error handling
        if not self.propositional and self.root.fml.freevars():
            print("ERROR: You may only enter closed formulas.")
            return

        res = "\\documentclass[a4paper]{article}\n\n\\usepackage{amssymb}\n\n\\begin{document}\n\n"

        # print info
        res += "You are using " + \
               ("classical " if self.classical else "intuitionistic ") + \
               ("modal " if self.modal else "") + \
               ("propositional " if self.propositional else "predicate ") + \
               "logic" + \
               (" with " + ("varying " if self.vardomain else "constant ") + "domains"
                if self.modal and not self.propositional else "") + \
               (" in a " + self.frame + " frame" if self.modal else "") + \
               ".\\\\\\\\\n\n"
        if self.validity:
            res += "Tableau for " + \
                   "$" + ", ".join([premise.fml.tex() for premise in self.premises]) + \
                   " \\vDash " + self.root.fml.phi.tex() + "$:\\\\\n\n"
        else:
            res += "Tableau for " + \
                   "$" + ", ".join([node.fml.tex() for node in [self.root] + self.premises]) + \
                   " \\not \\vDash \\bot$:\\\\\n\n"

        # recursively apply the rules
        self.expand()

        # print the tableau
        res += self.root.treestr()  # todo latex for trees

        # print result
        if self.closed():
            res += "The tableau is closed:\\\\\n"
            if self.validity:
                res += "The " + ("inference" if self.premises else "formula") + " is valid.\\\\\n"
            else:
                res += "The " + ("set of sentences is inconsistent.\\\\\n" if self.premises else
                                 "formula is unsatisfiable.\\\\\n")
        elif self.open():
            res += "The tableau is open:\\\\\\n"
            if self.validity:
                res += "The " + ("inference" if self.premises else "formula") + " is invalid.\\\\\n"
            else:
                res += "The " + ("set of sentences is consistent.\\\\\n" if self.premises else
                                 "formula is satisfiable.\\\\\n")
        elif self.infinite():
            res += "The tableau is potentially infinite:\\\\\n"
            if self.validity:
                res += "The " + ("inference" if self.premises else "formula") + " may or may not be valid.\\\\\n"
            else:
                res += "The " + ("set of sentences" if self.premises else "formula") + " may or may not be " + \
                       ("consistent.\\\\\n" if self.premises else "satisfiable.\\\\\n")

        # generate and print models
        if models := self.models():
            res += "\\ \\\\\nCounter models:" if self.validity else "\nModels:"
            for model in models:
                res += "\\ \\\\"
                res += str(model)  # todo latex for structures

        res += "\n\\end{document}"
        return res

    def __len__(self):
        return len(self.root.nodes())

    def expand(self, node=None):
        """
        Recursively expand all nodes in the tableau.
        """
        if not node:
            node = self.root  # value on initialization
        while applicable := self.applicable():
            (target, source, rule) = applicable[0]
            # print("expanding:")
            # print(str(target), " -> ", rule, " from ", str(source))
            target.expand(source, rule)
            # print("--------")

    def applicable(self):
        """
        A prioritized list of applicable rules in the tree in the format
        {(target,source)}

        @rtype: list[tuple[node,node]]
        """
        #                   (0: target, 1: source, 2: rule, 3: rule_type, 4: params, 5: delayed)
        appl = list(chain(*[[(leaf, *appl)
                             for appl in leaf.applicable]
                            for leaf in self.root.leaves() if leaf.applicable]))
        # print(appl)
        # todo improve prioritization
        rule_order = {r: i for (i, r) in enumerate(["alpha", "beta", "delta", "gamma", "epsilon", "zeta", "mu", "nu"])}
        pos = {node: i for (i, node) in enumerate(self.root.nodes())}  # enumerate the nodes breadth-first
        #                    num_appls, src pos,    targ pos,   rule_type
        sort_v1 = lambda i: (len(i[4]), pos[i[1]], pos[i[0]], rule_order[i[3]])
        #                    rule_type,        num_appls, src_line,  targ_line
        sort_v2 = lambda i: (rule_order[i[3]], len(i[4]), pos[i[1]], pos[i[0]])
        appl_sorted = [itm for itm in sorted(appl, key=sort_v1)]
        # print("applicable:")
        # print("\n".join([", ".join([str(itm[0].line), str(itm[1].line), itm[2], str(itm[4]), str(itm[5])])
        #                  for itm in appl_sorted]) + "\n")
        return [itm[:3] for itm in appl_sorted]

    def closed(self) -> bool:
        """
        A tableau is closed iff all branches are closed.

        @return True if all branches are closed, and False otherwise
        @rtype: bool
        """
        return all([isinstance(leaf.fml, Closed) for leaf in self.root.leaves()])

    def open(self) -> bool:
        """
        A tableau is open iff at least one branch is open.

        @return True if at least one branch is open, and False otherwise
        @rtype: bool
        """
        return any([isinstance(leaf.fml, Open) for leaf in self.root.leaves()])

    def infinite(self) -> bool:
        """
        A tableau is (probably) infinite iff at least one branch is (probably) infinite.

        @return True if all at least one branch is infinite, and False otherwise
        @rtype: bool
        """
        return any([isinstance(leaf.fml, Infinite) for leaf in self.root.leaves()])

    def models(self) -> Set[Structure]:
        """
        The models for a tableau are the models associated with its open branches.
        A model for an open branch is one that satisfies all atoms in the branch.

        @return The models associated with the open branches the tableau.
        @rtype set[Structure]
        """
        # todo minimal models
        res = []
        count = 0
        for leaf in self.root.leaves():

            if isinstance(leaf.fml, Open):
                # open branch
                leaf = leaf.branch[-2]
                branch = leaf.branch
                count += 1
                name = "M" + str(count)

                if self.modal:
                    sigs = {node.sig for node in branch}
                    # w1, ..., wn as names for worlds instead of signatures
                    worlds = {sig: "w" + str(i + 1) for (i, sig) in enumerate(sigs)}
                    w = {worlds[sig] for sig in sigs}
                    r_ = {(sig[:-1], sig[-1]) for sig in sigs if len(sig) > 1}
                    r = {(worlds[sig1], worlds[sig2]) for (sig1, sig2) in r_}

                if self.propositional:

                    if not self.modal:  # non-modal propositional
                        # atoms = all unnegated propositional variables
                        atoms = [node.fml.p for node in branch if isinstance(node.fml, Prop)]
                        # valuation = make all positive propositional variables true and all others false
                        v = {p: (True if p in atoms else False) for p in self.root.fml.propvars()}
                        model = PropStructure(name, v)
                        res.append(model)

                    else:  # modal propositional
                        # atoms = all unnegated propositional variables
                        atoms = {sig: [node.fml.p for node in branch if isinstance(node.fml, Prop) and node.sig == sig]
                                 for sig in sigs}
                        # valuation = make all positive propositional variables true and all others false
                        v = {sig: {p: (True if p in atoms[sig] else False) for p in self.root.fml.propvars()}
                             for sig in sigs}
                        model = PropModalStructure(name, w, r, v)
                        res.append(model)


                else:
                    # predicates = all predicates occurring in the conclusion and premises
                    constants = set(chain(self.root.fml.nonlogs()[0],
                                          *[prem.fml.nonlogs()[0] for prem in self.premises]))
                    # todo show constants in interpret.?
                    funcsymbs = set(chain(self.root.fml.nonlogs()[1],
                                          *[prem.fml.nonlogs()[1] for prem in self.premises]))
                    # todo take care of function symbols in domain and interpretation
                    predicates = set(chain(self.root.fml.nonlogs()[2],
                                           *[prem.fml.nonlogs()[2] for prem in self.premises]))

                    if not self.modal:  # non-modal predicational
                        # atoms = all unnegated atomic predications
                        atoms = [(node.fml.pred, node.fml.terms) for node in branch if isinstance(node.fml, Atm)]
                        # domain = all const.s occurring in formulas
                        d = set(list(chain(*[node.fml.nonlogs()[0] for node in branch if node.fml.nonlogs()])))
                        # interpretation = make all unnegated predications true and all others false
                        i = {p: {tuple([str(t) for t in a[1]]) for a in atoms if (Pred(p), a[1]) in atoms}
                             for p in predicates}
                        model = PredStructure(name, d, i)
                        res.append(model)

                    else:
                        # atoms = all unnegated atomic predications
                        atoms = {sig: [(node.fml.pred, node.fml.terms) for node in branch
                                       if isinstance(node.fml, Atm) and node.sig == sig]
                                 for sig in sigs}
                        i = {sig: {p: {tuple([str(t) for t in a[1]]) for a in atoms[sig]
                                       if (Pred(p), a[1]) in atoms[sig]}
                                   for p in predicates}
                             for sig in sigs}

                        if not self.vardomain:  # modal predicational with constant domain
                            d = set(chain(*[node.fml.nonlogs()[0] for node in branch]))
                            model = ConstModalStructure(name, w, r, d, i)
                            res.append(model)

                        else:  # modal predicational with varying domain
                            d = {sig: set(chain(*[node.fml.nonlogs()[0] for node in branch
                                                  if node.sig == sig]))
                                 for sig in sigs}
                            model = VarModalStructure(name, w, r, d, i)
                            res.append(model)

        return res


class Node(object):
    """
    A node in a tree.
    """

    def __init__(self, line: int, sig: List[int], fml: Formula, cite: str, parent, tableau):
        self.line = line
        self.sig = sig
        self.fml = fml
        self.cite = cite
        self.branch = (parent.branch if parent else []) + [self]
        self.children = []
        self.tableau = tableau
        self.applicable = []  # (0: source, 1: rule, 2: rule_type, 3: params, 4. delayed)

    def __str__(self):
        """
        String representation of this line.
        """
        return (str(self.line) + "." if self.line else "") + "\t" + \
               (".".join([str(s) for s in self.sig]) + "\t" if self.sig else "") + \
               str(self.fml) + "\t" + \
               self.cite

    def __repr__(self):
        """
        String representation of this line.
        """
        return (str(self.line) + "." if self.line else "") + "\t" + \
               (".".join([str(s) for s in self.sig]) + "\t" if self.sig else "") + \
               str(self.fml) + "\t" + \
               self.cite

    def treestr(self, indent="", binary=False, last=True) -> str:
        """
        String representation of the tree whose root is this node.
        """
        # todo non-rotated visualization?

        # compute lengths of columns
        len_line = max([len(str(node.line)) for node in self.root().nodes()]) + 2
        len_sig = max([len(".".join([str(s) for s in node.sig])) for node in self.root().nodes() if node.sig]) \
            if self.tableau.modal else None
        len_fml = max([len(str(node.fml)) for node in self.root().nodes()]) + 1
        len_cite = max([len(str(node.cite)) for node in self.root().nodes()])
        # compute columns
        str_line = "{:<{len}}".format(str(self.line) + "." if self.line else "", len=len_line)
        str_sig = "{:<{len}}".format(".".join([str(s) for s in self.sig]) if self.sig else "", len=len_sig) \
            if self.tableau.modal else ""
        str_fml = "{:^{len}}".format(str(self.fml), len=len_fml)
        str_cite = "{:<{len}}".format(str(self.cite), len=len_cite)
        selfstr = str_line + str_sig + str_fml + str_cite + "\n"

        res = indent
        res += "|--" if binary else ""
        res += selfstr
        if self.children:  # self branches
            if binary:
                if not last:
                    indent += "|  "
                else:
                    indent += "   "
            if len(self.children) == 1:  # unary branching
                if childstr := self.children[0].treestr(indent, False, True):
                    res += childstr
            elif len(self.children) == 2:  # binary branching
                if childstr1 := self.children[0].treestr(indent, True, False):
                    res += childstr1
                if childstr2 := self.children[1].treestr(indent, True, True):
                    res += childstr2
        else:  # self is leaf
            res += indent + "\n"
        return res

    def nodes(self):
        """
        Level-order traversal:
        First the nodes on a level from left to right, then recurse through the nodes' children.
        """
        res = []
        # visit root
        queue = [self]
        while queue:
            # visit front of queue
            res.append(queue[0])
            # go to next element
            node = queue.pop(0)
            # visit children
            for child in node.children:
                queue.append(child)
        return res

        # """
        # Pre-order traversal:
        # First visit the node itself, then recurse through its children.
        # """
        # res = [self]
        # for child in self.children:
        #     res += child.nodes()
        # return res
        # return [self] + [child.preorder() for child in self.children]

    def branches(self):
        """
        Get the branches starting from this node.
        """
        return [leaf.branch for leaf in self.leaves()]

    def leaves(self):
        """
        Get the leave nodes descending from the this node.
        """
        leaves = []

        def collect_leaves(node):
            if node is not None:
                if not node.children:
                    leaves.append(node)
                else:
                    for child in node.children:
                        collect_leaves(child)

        collect_leaves(self)
        return leaves

    def root(self):
        """
        The root of this node (= root of the tableau).
        """
        return self.branch[0]

    def add_child(self, spec):
        """
        Add a child to the current node.
        """
        # todo sometimes adds None nodes (?)
        # don't add children to branches that are already closed, open or declard infinite
        if self.children and (isinstance(self.children[0].fml, Closed) or isinstance(self.children[0].fml, Open) or
                              isinstance(self.children[0].fml, Infinite)):
            return

        (line, sig, fml, cite) = spec
        child = Node(line, sig, fml, cite, self, self.tableau)
        # add the child
        self.children.append(child)

        if not (isinstance(fml, Closed) or isinstance(fml, Open) or isinstance(fml, Infinite)):
            # check properties of new child
            if not (child.contradiction() or child.infinite()):
                # transfer applicable rules to new leaf
                child.applicable = [itm for itm in self.applicable]
                # if the child formula has applicable rules, add it to its own applicable rules
                if rules := child.rules():
                    for rule in rules:
                        child.set_applicable(child, rule[0], rule[1])
                # print("adding:")
                # print(str(self) + " + " + str(child))
                # print(self.applicable, child.applicable)
                # print("children:")
                # print("\n".join([str(node) + ": " + str(node.children) for node in self.root().preorder()]))
                # print()
                # print(self.root().treestr())
                # todo generically handle reset of parent applicable rules after all children have been added?
        return child

    def rules(self):
        return self.fml.tableau_pos() if self.fml.tableau_pos() else None

    def expand(self, source, rule):
        """
        Expand the source line on this node.
        """
        candidates = [(rule_name, rule_type, args) for (rule_name, rule_type, args) in source.rules()
                      if rule_name == rule] if source.rules() else []
        if len(candidates) == 1:
            (rule_name, rule_type, args) = candidates[0]
            rule_func = getattr(self, "rule_" + rule_type)
            rule_func(source, rule, args)  # apply the rule

            # check if expansion leaves open branches
            for leaf in self.leaves():
                if not (isinstance(leaf.fml, Closed) or isinstance(leaf.fml, Open) or isinstance(leaf.fml, Infinite)):
                    # if the child has no applicable or only delayed rules, the branch is open
                    if not leaf.applicable or all([appl[4] for appl in leaf.applicable]):
                        leaf.add_open()
        else:
            print("ERROR: rule " + rule + " for " + str(source) + " on " + str(self) + " not found")

    def rule_alpha(self, source, rule, args):
        """
        Expand the source node unary in this branch.
        """
        fmls = args
        max_line = max([node.line for node in self.root().nodes() if node.line])
        line = max_line
        sig = source.sig

        # rule is now being applied; remove from list of applicable
        self.remove_applicable(source, rule)

        # append (top) node
        line += 1
        fml = fmls[0]
        cite = "(" + (" " if len(rule) == 1 else "") + rule + ", " + str(source.line) + ")"
        node1 = self.add_child((line, sig, fml, cite))

        # append bottom node
        if len(fmls) == 2:
            line += 1
            fml = fmls[1]
            cite = "(" + (" " if len(rule) == 1 else "") + rule + ", " + str(source.line) + ")"
            node2 = node1.add_child((line, sig, fml, cite))
            node1.empty_applicable()

        # self is now no longer leaf, so has no applicable rules
        self.empty_applicable()

    def rule_beta(self, source, rule, args):
        """
        Expand the source node binary in this branch.
        """
        fmls = args
        max_line = max([node.line for node in self.root().nodes() if node.line])
        line = max_line
        sig = source.sig

        # rule is now being applied; remove from list of applicable
        self.remove_applicable(source, rule)

        # append (top) left node
        line += 1
        fml = fmls[0][0]
        cite = "(" + (" " if len(rule) == 1 else "") + rule + ", " + str(source.line) + ")"
        node1 = self.add_child((line, sig, fml, cite))

        # append bottom left node
        if len(fmls[0]) == 2 and node1:
            line += 1
            fml = fmls[0][1]
            cite = "(" + (" " if len(rule) == 1 else "") + rule + ", " + str(source.line) + ")"
            node3 = node1.add_child((line, sig, fml, cite))
            node1.empty_applicable()

        # append (top) right node
        line += 1
        fml = fmls[1][0]
        cite = "(" + (" " if len(rule) == 1 else "") + rule + ", " + str(source.line) + ")"
        node2 = self.add_child((line, sig, fml, cite))

        # append bottom right node
        if len(fmls[1]) == 2 and node2:
            line += 1
            fml = fmls[1][1]
            cite = "(" + (" " if len(rule) == 1 else "") + rule + ", " + str(source.line) + ")"
            node4 = node2.add_child((line, sig, fml, cite))
            node2.empty_applicable()

        # self is now no longer leaf, so has no applicable rules
        self.empty_applicable()

    def rule_gamma(self, source, rule, args):
        """
        Expand the source node with an arbitrary parameter in this branch.
        """
        # todo doesn't work yet
        phi, var = args
        max_line = max([node.line for node in self.root().nodes() if node.line])
        line = max_line
        sig = source.sig
        parameters = list("abcdefghijklmnopqrst")

        # find a constant to substitute
        constants = list(chain(*[node.fml.nonlogs()[0] for node in self.branch]))
        # all constants and parameters
        usable = constants + parameters
        # all parameters already used with this rule
        used = self.get_applicable(source, rule)[3]
        # alternative formulation: only use constants that already occur in the branch, no parameters
        # usable = [c for c in (constants if constants else parmeters[0]) if c not in used]
        # if not usable:
        #     # # all constants have already been used: rule can not be applied at this point; delay it
        #     # self.set_applicable(source, rule, "gamma", used, True)
        #     # return
        # for modal predicate logic with varying domains: add signature subscript to constant
        subscript = ""
        if self.tableau.modal and not self.tableau.propositional and self.tableau.vardomain:
            subscript = ".".join([str(s) for s in source.sig])
        # choose first symbol from constants and parameters that has not already been used with this particular rule
        const_symbol = usable[(min([i for i in range(len(usable))
                                    if usable[i] + subscript not in used]))] + subscript
        const = Const(const_symbol)

        # rule is now being applied; add chosen constant to already used ones
        self.set_applicable(source, rule, "gamma", used + [const_symbol])

        # add node
        line += 1
        sig = source.sig
        fml = phi.subst(var, const)  # substitute the constant for the variable
        cite = "(" + (" " if len(rule) == 1 else "") + rule + ", " + str(source.line) + ", " + \
               "[" + var.u + "/" + const.c + "]" + ")"
        node = self.add_child((line, source.sig, fml, cite))

        # self is now no longer leaf, so has no applicable rules
        self.empty_applicable()

    def rule_delta(self, source, rule, args):
        """
        Expand the source node with a new parameter in this branch.
        """
        # todo doesn't work yet
        phi, var = args
        sig = source.sig
        max_line = max([node.line for node in self.root().nodes() if node.line])
        line = max_line
        parameters = list("abcdefghijklmnopqrst")

        # find a constant to substitue
        # all existing constants in the curr. branch
        constants = list(chain(*[node.fml.nonlogs()[0] for node in self.branch]))
        # all parameters already used with this rule
        used = self.get_applicable(source, rule)[3]
        # for modal predicate logic with varying domains: add signature subscript to constant
        subscript = ""
        if self.tableau.modal and not self.tableau.propositional and self.tableau.vardomain:
            subscript = ".".join([str(s) for s in source.sig])
        # choose first symbol from list of parameters that does not yet occur in this branch
        const_symbol = parameters[(min([i for i in range(len(parameters))
                                        if parameters[i] + subscript not in constants]))] + subscript
        const = Const(const_symbol)

        # rule is now being applied; add chosen constant to already used ones
        self.set_applicable(source, rule, "delta", used + [const_symbol])
        # alternative formulation: rule may only be applied once; remove from applicable
        # self.remove_applicable(source, "rule_delta")

        # add node
        line += 1
        fml = phi.subst(var, const)  # substitute the constant for the variable
        cite = "(" + (" " if len(rule) == 1 else "") + rule + ", " + str(source.line) + ", " + \
               "[" + var.u + "/" + const.c + "]" + ")"
        node = self.add_child((line, sig, fml, cite))

        # self is now no longer leaf, so has no applicable rules
        self.empty_applicable()

    def rule_mu(self, source, rule, args):
        """
        Expand the source node in this branch by extending the signature with a new signature.
        """
        # todo not tested yet
        fml = args
        max_line = max([node.line for node in self.root().nodes() if node.line])
        line = max_line

        # find a signature
        # all signature extensions for the source signature existing in the current branch
        signatures = {node.sig for node in self.branch if node.sig[:-1] == source.sig}
        # all parameters already used with this rule
        used = self.get_applicable(source, rule)[3]
        # choose a signature that does not already occur in this branch
        sig = source.sig.append(min([i for i in range(1, )
                                     if source.sig.append(i) not in signatures]))

        # rule is now being applied; add chosen signature to already used ones
        self.set_applicable(source, rule, "mu", used + [sig])

        # add node
        line += 1
        cite = "(" + (" " if len(rule) == 1 else "") + rule + str(source.line) + ", " + \
               "⟨" + ".".join([str(s) for s in source.sig]) + ", " + ".".join([str(s) for s in sig]) + "⟩" + ")"
        node = self.add_child((line, sig, fml, cite))

        # self is now no longer leaf, so has no applicable rules
        self.empty_applicable()

    def rule_nu(self, source, rule, args):
        """
        Expand the source node in this branch by extending the signature with an existing signature.
        """
        # todo not tested yet
        fml = args
        max_line = max([node.line for node in self.root().nodes() if node.line])
        line = max_line

        # find a signature
        # all signature extensions for the source signature existing in the current branch
        signatures = {node.sig for node in self.branch if node.sig[:-1] == source.sig}
        # all parameters already used with this rule
        used = self.get_applicable(source, rule)[3]
        if signatures:
            # choose the first signature that already occurs in this branch but has not already been used with this rule
            sig = source.sig.append(min([i for i in range(1, )
                                         if source.sig.append(i) in signatures and source.sig.append(i) not in used]))
        else:
            # if there are no suitable signatures, the rule can not be applied here; mark it as delayed
            self.set_applicable(source, rule, "nu", used, True)
            return

        # rule is now being applied; add chosen signature to already used ones
        self.set_applicable(source, rule, "nu", used + [sig])

        # add node
        line += 1
        cite = "(" + (" " if len(rule) == 1 else "") + rule + str(source.line) + ", " + \
               "⟨" + ".".join([str(s) for s in source.sig]) + ", " + ".".join([str(s) for s in sig]) + "⟩" + ")"
        node = self.add_child((line, sig, fml, cite))

        # self is now no longer leaf, so has no applicable rules
        self.empty_applicable()

    def rule_zeta(self, source, rule, args):
        """
        Expand the source node in this branch by reducing the signature.
        """
        # todo actual name for this rule type?
        fml = args
        max_line = max([node.line for node in self.root().nodes() if node.line])
        line = max_line

        # number of times the rule has already been used
        used = self.get_applicable(source, rule)[3]
        if len(source.sig) < 2:
            # the signature can not be reduced: the rule is not applicable; delay it
            self.set_applicable(source, rule, "zeta", used, True)
            return
        # reduce the signature
        sig = source.sig[:-1]

        # rule is now being applied; remember usage
        self.set_applicable(source, rule, "zeta", used + [1])

        # add node
        line += 1
        cite = "(" + (" " if len(rule) == 1 else "") + rule + str(source.line) + ")"
        node = self.add_child((line, sig, fml, cite))

        # self is now no longer leaf, so has no applicable rules
        self.empty_applicable()

    def rule_epsilon(self, source, rule, args):
        """
        Expand the source node in this branch by repeating the signature.
        """
        # todo actual name for this rule type?

        fml = args
        max_line = max([node.line for node in self.root().nodes() if node.line])
        line = max_line

        # number of times the rule has already been used
        used = self.get_applicable(source, rule)[3]
        # signature is source signature
        sig = source.sig

        # rule is now being applied; remember usage
        self.set_applicable(source, rule, "epsilon", used + [1])

        # add node
        line += 1
        cite = "(" + (" " if len(rule) == 1 else "") + rule + str(source.line) + ")"
        node = self.add_child((line, sig, fml, cite))

        # self is now no longer leaf, so has no applicable rules
        self.empty_applicable()

    def get_applicable(self, source, rule):
        candidates = [tpl for tpl in self.applicable if tpl[0] == source and tpl[1] == rule]
        if candidates:
            return candidates[0]

    def set_applicable(self, source, rule, rule_type, params=[], delayed=False):
        candidates = [tpl for tpl in self.applicable if tpl[0] == source and tpl[1] == rule]
        for candidate in candidates:
            self.applicable.remove(candidate)
        self.applicable.append((source, rule, rule_type, params, delayed))

    def remove_applicable(self, source, rule):
        candidates = [tpl for tpl in self.applicable if tpl[0] == source and tpl[1] == rule]
        for candidate in candidates:
            self.applicable.remove(candidate)

    def empty_applicable(self):
        self.applicable = []

    def contradiction(self):
        """
        Check for a contradiction with this node.
        """
        # print(self)
        # print("\n".join([str(node) for node in self.branch]))
        # print()
        return self.fml.tableau_contradiction_pos(self)

    def infinite(self):
        """
        A branch is judged potentially infinite if it is longer than there are symbols in the assumptions.
        """
        # todo smarter implementation (check for loops in rule appls.)
        if len(self.branch) >= sum([len(node.fml) for node in self.branch if node.cite == "(A)"]):
            self.add_infinite()
            return True
        return False

    def add_closed(self, lines):
        """
        Add a pseudo-node for a contradictory branch.
        """
        self.add_child((None, None, Closed(), "(" + ", ".join([str(line) for line in lines]) + ")"))

    def add_open(self):
        """
        Add a pseudo-node for a contradictory branch.
        """
        self.add_child((None, None, Open(), ""))

    def add_infinite(self):
        """
        Add a pseudo-node for a probably infinite branch.
        """
        self.add_child((None, None, Infinite(), ""))


####################

# todo integration in main module gives class not defined errors -- circular imports?
if __name__ == "__main__":
    fml1 = Biimp(Neg(Conj(Prop("p"), Prop("q"))), Disj(Neg(Prop("p")), Neg(Prop("q"))))
    tab1 = Tableau(fml1, propositional=True)
    print(tab1)

    # fml2a = Imp(Prop("p"), Prop("q"))
    # fml2b = Imp(Prop("q"), Prop("r"))
    # fml2 = Imp(Prop("p"), Prop("r"))
    # tab2 = Tableau(fml2, premises=[fml2a, fml2b], propositional=True)
    # tab2.generate()

    fml3 = Neg(Conj(Imp(Prop("p"), Prop("q")), Prop("r")))
    tab3 = Tableau(fml3, validity=False, propositional=True)
    print(tab3)

    # fml4a = Atm(Pred("P"), (Const("a"), Const("a")))
    # fml4b = Neg(Eq(Const("a"), Const("a")))
    # tab4 = Tableau(premises=[fml4a, fml4b], validity=False)
    # tab4.generate()

    fml5a = Imp(Atm(Pred("P"), (Const("a"), Const("b"))), Atm(Pred("Q"), (Const("a"), Const("c"))))
    fml5 = Atm(Pred("R"), (Const("a"), Const("a")))
    tab5 = Tableau(fml5, premises=[fml5a])
    print(tab5)

    fml6 = Biimp(Forall(Var("x"), Atm(Pred("P"), (Var("x"),))), Neg(Exists(Var("x"), Neg(Atm(Pred("P"), (Var("x"),))))))
    tab6 = Tableau(fml6)
    print(tab6)

    fml7a = Exists(Var("y"), Forall(Var("x"), Atm(Pred("R"), (Var("x"), Var("y")))))
    fml7 = Forall(Var("x"), Exists(Var("y"), Atm(Pred("R"), (Var("x"), Var("y")))))
    tab7 = Tableau(fml7, premises=[fml7a])
    print(tab7)

    # fml8a = Exists(Var("y"), Conj(Atm(Pred("lid"), (Var("y"),)),
    #                               Forall(Var("x"), Imp(Atm(Pred("tupperbox"), (Var("x"),)),
    #                                                    Atm(Pred("fit"), (Var("x"), Var("y")))))))
    # fml8 = Forall(Var("x"), Imp(Atm(Pred("tupperbox"), (Var("x"),)),
    #                             Exists(Var("y"), Conj(Atm(Pred("lid"), (Var("y"),)),
    #                                                   Atm(Pred("fit"), (Var("x"), Var("y")))))))
    # tab8 = Tableau(fml8, premises=[fml8a])
    # print(tab8)

    fml9a = Forall(Var("x"), Exists(Var("y"), Atm(Pred("R"), (Var("x"), Var("y")))))
    fml9 = Exists(Var("y"), Forall(Var("x"), Atm(Pred("R"), (Var("x"), Var("y")))))
    tab9 = Tableau(fml9, premises=[fml9a])
    print(tab9)

    # fml10a = Forall(Var("x"), Imp(Atm(Pred("tupperbox"), (Var("x"),)),
    #                             Exists(Var("y"), Conj(Atm(Pred("lid"), (Var("y"),)),
    #                                                   Atm(Pred("fit"), (Var("x"), Var("y")))))))
    # fml10 = Exists(Var("y"), Conj(Atm(Pred("lid"), (Var("y"),)),
    #                               Forall(Var("x"), Imp(Atm(Pred("tupperbox"), (Var("x"),)),
    #                                                    Atm(Pred("fit"), (Var("x"), Var("y")))))))
    # tab10 = Tableau(fml10, premises=[fml10a])
    # print(tab10)
    # print(len(tab10))

    # fml9 = Biimp(Nec(Prop("p")), Neg(Poss(Neg(Prop("p")))))
    # tab9 = Tableau(fml9, propositional=True, modal=True)
    # tab9.generate()
