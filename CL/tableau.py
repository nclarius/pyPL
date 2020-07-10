#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tableau proofs.
THIS PART IS STILL UNDER CONSTRUCTION.
"""


from main import *
from expr import *
from structure import *

from typing import List, Dict, Set, Tuple
from itertools import chain


# todo documentation
# todo predicate logic
# todo modal logic
# todo parser


class Tableau(object):
    """
    A tableau tree.
    """

    def __init__(self, conclusion, premises=[], propositional=False, modal=False, vardomain=False):
        # settings
        self.propositional = propositional  # todo detect automatically?
        self.modal = modal  # todo detect automatically?
        self.vardomain = vardomain
        sig = [1] if modal else None

        # insert nodes
        self.root = Node(1, sig if modal else None, Neg(conclusion), "(A)", None, self)
        if self.root.rule():
            self.root.applicable[self.root] = self.root.rule()
        self.premises = [self.root.leaves()[0].add_child((i+2, sig, premise, "(A)"))
                         for i, premise in enumerate(premises)]

    def __str__(self):
        return self.root.treestr()[:-1]

    def nodes(self):
        return self.root.preorder()

    def generate(self):
        """
        Expand the tableau, generate the associate models and print some info.
        """
        # todo systematic error handling
        if not self.propositional and self.root.fml.freevars():
            print("ERROR: You may only enter closed formulas.")
            return

        # print info
        print("Tableau for " +
              ", ".join([str(premise.fml) for premise in self.premises]) + " ⊨ " + str(self.root.fml.phi) + ":\n")

        # recursively apply the rules
        self.expand()

        # print the tableau
        print(self)

        # print results
        if self.closed():
            print("The tableau is closed:\n"
                  "The " + ("inference" if self.premises else "formula") + " is valid.")
        elif self.open():
            print("The tableau is open:\n"
                  "The " + ("inference" if self.premises else "formula") + " is invalid.")
        elif self.infinite():
            print("The tableau is possibly infinite:\n"
                  "The " + ("inference" if self.premises else "formula") + " may or may not be valid.")
        # print the counter models
        if models := self.models():
            print("\nCounter models:")
            for model in models:
                print(model)
        print("\n")

    def expand(self, node=None):
        """
        Recursively expand all nodes in the tableau.
        """
        if not node:
            node = self.root  # value on initialization

        # threshold of total rule applications to avoid non-termination
        limit = 100
        count = 0
        while (applicable := self.applicable()) and count < limit:
            top = applicable[0]
            (target, source) = (top[0], top[1])
            # print("expanding:")
            # print(str(target) + " -> " + str(source))
            target.expand(source)
            # print("--------")
            count += 1

    def applicable(self):
        """
        A prioritized list of applicable rules in the tree in the format
        {(leaf,source)}

        @rtype: list[node,node]
        """
        appl = {leaf: leaf.applicable for leaf in self.root.leaves() if leaf.applicable}
        res = list(chain(*[[(leaf, source) for source in appl[leaf]] for leaf in appl]))
        # print("applicable:")
        # print("\n".join([str(r[0]) + ": " + str(r[1]) for r in res]))
        # todo prioritize
        # priority:
        # - 1. rule type: alpha > delta > nu > gamma > mu > beta
        # - 2. number of rule applications: low > high
        # - 3. line number: low > high
        return res

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

        @return True if all branches are closed, and False otherwise
        @rtype: bool
        """
        return any([isinstance(leaf.fml, Open) for leaf in self.root.leaves()])

    def infinite(self) -> bool:
        """
        A tableau is (probably) infinite iff at least one branch is (probably) infinite.

        @return True if all branches are closed, and False otherwise
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
        for leaf in self.root.leaves():

            if isinstance(leaf.fml, Open):
                # open branch
                leaf = leaf.branch[-2]
                branch = leaf.branch

                if self.modal:
                    sigs = [node.sig for node in branch]
                    w = {".".join(sig) for sig in sigs}
                    r = {(".".join(sig[:-1]), sig[-1]) for sig in sigs if len(sig) > 1}

                if self.propositional:

                    if not self.modal:  # non-modal propositional
                        # atoms = all unnegated propositional variables
                        atoms = [node.fml.p for node in branch if isinstance(node.fml, Prop)]
                        # valuation = make all positive propositional variables true and all others false
                        v = {p: (True if p in atoms else False) for p in self.root.fml.propvars()}
                        model = PropStructure(v)
                        res.append(model)

                    else:  # modal propositional
                        # atoms = all unnegated propositional variables
                        atoms = {sig: [node.fml.p for node in branch if isinstance(node.fml, Prop) and node.sig == sig]
                                 for sig in sigs}
                        # valuation = make all positive propositional variables true and all others false
                        v = {sig: {p: (True if p in atoms[sig] else False) for p in self.root.fml.propvars()}
                             for sig in sigs}
                        model = PropModalStructure(w, r, v)
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
                        d = set(chain(*[node.fml.nonlogs()[0] for node in branch]))
                        # interpretation = make all unnegated predications true and all others false
                        i = {p: {tuple([str(t) for t in a[1]]) for a in atoms if (Pred(p), a[1]) in atoms}
                             for p in predicates}
                        model = PredStructure(d, i)
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
                            model = ConstModalStructure(w, r, d, i)
                            res.append(model)

                        else:  # modal predicational with varying domain
                            d = {sig: set(chain(*[node.fml.nonlogs()[0] for node in branch
                                                  if node.sig == sig]))
                                 for sig in sigs}
                            model = VarModalStructure(w, r, d, i)
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
        self.applicable = dict()

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
        len_line = max([len(str(node.line)) for node in self.branch[0].preorder()])
        len_sig = max([len(".".join([str(s) for s in node.sig])) for node in self.branch[0].preorder() if node.sig]) \
            if self.tableau.modal else None
        len_fml = max([len(str(node.fml)) for node in self.branch[0].preorder()]) + 1
        len_cite = max([len(str(node.cite)) for node in self.branch[0].preorder()])
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

    def preorder(self):
        """
        Pre-order traversal:
        First visit the node itself, then recurse through its children.
        """
        res = [self]
        for child in self.children:
            res += child.preorder()
        return res
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

    def leaf(self):
        """
        The last non-contradiction node belonging to the branch of this node.
        """
        return self.branch[-1] if not isinstance(self.branch[-1].fml, Closed) else self.branch[-2]

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
        # don't add children to branches that are already closed or terminally open
        if self.children and (isinstance(self.children[0].fml, Closed) or isinstance(self.children[0].fml, Open)):
            return
        (line, sig, fml, cite) = spec
        child = Node(line, sig, fml, cite, self, self.tableau)
        # add the child
        self.children.append(child)

        # check properties of new child
        if not child.contradiction() and not child.infinite() and not isinstance(fml, Open):
            # transfer applicable rules to new leaf
            child.applicable = {key: val for (key, val) in self.applicable.items()}
            # print("adding:")
            # print(str(self) + " + " + str(child))
            # print(self.applicable, child.applicable)
            # print("children:")
            # print("\n".join([str(node) + ": " + str(node.children) for node in self.root().preorder()]))
            # print()
            # print(self.root().treestr())
            # if the child formula has applicable rules, add it to its own applicable rules
            if child.rule():
                child.applicable[child] = child.rule()
            # todo generically handle reset of parent applicable rules after all children have been added
        return child

    def rule(self):
        return self.fml.tableau_pos()[0] if self.fml.tableau_pos() else None

    def expand(self, source):
        """
        Expand the source line on this node.
        """
        if val := source.fml.tableau_pos():  # check which rule application the formula defines, if any
            (rule_type, args, rule) = val
            rule_func = getattr(self, rule_type)
            rule_func(source, args, rule)  # apply the rule

            # check if expansion leaves open branches
            for leaf in self.leaves():
                # if the child has no applicable (or only delayed) rules, the branch is open
                if not isinstance(leaf.fml, Closed) and (not leaf.applicable or \
                        all([isinstance(leaf.applicable[key], tuple) and leaf.applicable[key][0] == leaf.rule_nu
                             and leaf.applicable[key][3] for key in leaf.applicable])):
                    leaf.add_open()

    def rule_alpha(self, source, args, rule):
        """
        Extend the source node unary in this branch.
        """
        fmls = args
        max_line = max([node.line for node in self.branch[0].preorder() if node.line])
        line = max_line
        sig = source.sig

        # rule is now being applied; remove from list of applicable
        self.applicable.pop(source, None)

        # append (top) node
        line += 1
        fml = fmls[0]
        cite = "(" + rule + ", " + str(source.line) + ")"
        node1 = self.add_child((line, sig, fml, cite))

        # append bottom node
        if len(fmls) == 2:
            line += 1
            fml = fmls[1]
            cite = "(" + rule + ", " + str(source.line) + ")"
            node2 = node1.add_child((line, sig, fml, cite))
            node1.applicable = dict()

        # self is now no longer leaf, so has no applicable rules
        self.applicable = dict()

    def rule_beta(self, source, args, rule):
        """
        Extend the source node binary in this branch.
        """
        fmls = args
        max_line = max([node.line for node in self.branch[0].preorder() if node.line])
        line = max_line
        sig = source.sig

        # rule is now being applied; remove from list of applicable
        self.applicable.pop(source, None)

        # append (top) left node
        line += 1
        fml = fmls[0][0]
        cite = "(" + rule + ", " + str(source.line) + ")"
        node1 = self.add_child((line, sig, fml, cite))

        # append bottom left node
        if len(fmls[0]) == 2 and node1:
            line += 1
            fml = fmls[0][1]
            cite = "(" + rule + ", " + str(source.line) + ")"
            node3 = node1.add_child((line, sig, fml, cite))
            node1.applicable = dict()

        # append (top) right node
        line += 1
        fml = fmls[1][0]
        cite = "(" + rule + ", " + str(source.line) + ")"
        node2 = self.add_child((line, sig, fml, cite))

        # append bottom right node
        if len(fmls[1]) == 2 and node2:
            line += 1
            fml = fmls[1][1]
            cite = "(" + rule + ", " + str(source.line) + ")"
            node4 = node2.add_child((line, sig, fml, cite))
            node2.applicable = dict()

        # self is now no longer leaf, so has no applicable rules
        self.applicable = dict()

    def rule_gamma(self, source, args, rule):
        """
        Extend the source node according to the delta schema (with an arb. param.) in this branch.
        """
        # ! dummy, & doesn't work yet
        # todo specify rule application adequately
        phi, var = args
        max_line = max([node.line for node in self.branch[0].preorder() if node.line])
        line = max_line
        sig = source.sig
        parameters = list("abcdefghijklmnopqrst")

        # find a constant to substitue
        # if there is no list of constants already used with this rule, create it
        if not isinstance(self.applicable[source], tuple):
            self.applicable[source] = (self.rule_gamma, [])
        # all existing constants in the curr. branch
        constants = list(chain(*[node.fml.nonlogs()[0] for node in self.branch]))
        # all constants and parameters
        useable = constants + parameters
        # all parameters already used with this rule
        used = self.applicable[source][1]
        # for modal predicate logic with varying domains: add signature subscript to constant
        subscript = ""
        if self.tableau.modal and not self.tableau.propositional and self.tableau.vardomain:
            subscript = ".".join([str(s) for s in source.sig])
        # choose first symbol from constants and parameters that has not already been used with this particular rule
        # todo correct?
        const = Const(useable[(min([i for i in range(len(useable))
                                    if useable[i] + subscript not in used]))]
                      + subscript)

        # rule is now being applied; add chosen constant to already used ones
        self.applicable[source] = (self.rule_beta, used + [const])

        # add node
        line += 1
        sig = source.sig
        fml = phi.subst(var, const)  # substitute the constant for the variable
        cite = "(" + rule + ", " + str(source.line) + ")" + " " + "[" + var.u + "/" + const.c + "]"
        node = self.add_child((line, source.sig, fml, cite))

        # self is now no longer leaf, so has no applicable rules
        self.applicable = dict()

    def rule_delta(self, source, args, rule):
        """
        Extend the source line according to the gamma schema (with a new param.) in this branch.
        """
        # ! dummy & doesn't work yet
        # todo specify rule application adequately
        phi, var = args
        sig = source.sig
        max_line = max([node.line for node in self.branch[0].preorder() if node.line])
        line = max_line
        parameters = list("abcdefghijklmnopqrst")

        # find a constant to substitue
        # if there is no list of constants already used with this rule, create it
        if not isinstance(self.applicable[source], tuple):
            self.applicable[source] = (self.rule_delta, [])
        # all existing constants in the curr. branch
        constants = list(chain(*[node.fml.nonlogs()[0] for node in self.branch]))
        # all parameters already used with this rule
        used = self.applicable[source][1]
        # for modal predicate logic with varying domains: add signature subscript to constant
        subscript = ""
        if self.tableau.modal and not self.tableau.propositional and self.tableau.vardomain:
            subscript = ".".join([str(s) for s in source.sig])
        # choose first symbol from list of parameters that does not yet occur in this branch
        const = Const(parameters[(min([i for i in range(len(parameters))
                                       if parameters[i] + subscript not in constants]))]
                      + subscript)

        # rule is now being applied; add chosen constant to already used ones
        self.applicable[source] = (self.rule_beta, used + [const])

        # add node
        line += 1
        fml = phi.subst(var, const)  # substitute the constant for the variable
        cite = "(" + rule + ", " + str(source.line) + ")" + " " + "[" + var.u + "/" + const.c + "]"
        node = self.add_child((line, sig, fml, cite))

        # self is now no longer leaf, so has no applicable rules
        self.applicable = dict()

    def rule_mu(self, source, args, rule):
        """
        Extend the source node according to the mu schema (with a new sig.) in all this branch.
        """
        fml = args
        max_line = max([node.line for node in self.branch[0].preorder() if node.line])
        line = max_line

        # find a signature
        # if there is no list of signatures already used with this rule, create it
        if not isinstance(self.applicable[source], tuple):
            self.applicable[source] = (self.rule_mu, [])
        # all signature extensions for the source signature existing in the current branch
        signatures = [node.sig for node in self.branch if node.sig[:-1] == source.sig]
        # all parameters already used with this rule
        used = self.applicable[source][1]
        # choose a signature that does not already occur in this branch
        sig = source.sig.append(min([i for i in range(1,)
                                     if source.sig.append(i) not in signatures]))

        # rule is now being applied; add chosen signature to already used ones
        self.applicable[source] = (self.rule_beta, used + [sig])

        # add node
        line += 1
        cite = "(" + rule + ", " + str(source.line) + ")"
        node = self.add_child((line, sig, fml, cite))

        # self is now no longer leaf, so has no applicable rules
        self.applicable = dict()

    def rule_nu(self, source, args, rule):
        """
        Extend the source node according to the nu schema (with an old sig.) in this branch.
        """
        fml = args
        max_line = max([node.line for node in self.branch[0].preorder() if node.line])
        line = max_line
        # if there is no list of signatures already used with this rule, create it
        if not isinstance(self.applicable[source], tuple):
            self.applicable[source] = (self.rule_nu, [], False)
        # reset the delayed label
        if not isinstance(self.applicable[source], tuple):
            self.applicable[source] = (self.rule_nu, self.applicable[source][1], False)

        # find a signature
        # all signature extensions for the source signature existing in the current branch
        signatures = [node.sig for node in self.branch if node.sig[:-1] == source.sig]
        # all parameters already used with this rule
        used = self.applicable[source][1]
        if signatures:
            # choose the first signature that already occurs in this branch but has not already been used with this rule
            sig = source.sig.append(min([i for i in range(1,)
                                         if source.sig.append(i) in signatures and source.sig.append(i) not in used]))
        else:
            # if there are no suitable signatures, the rule can not be applied here; mark it as delayed
            self.applicable[source] = (self.rule_beta, used, True)
            return

        # rule is now being applied; add chosen signature to already used ones
        self.applicable[source] = (self.rule_beta, used + [sig])

        # add node
        line += 1
        cite = "(" + rule + ", " + str(source.line) + ")"
        node = self.add_child((line, sig, fml, cite))

        # self is now no longer leaf, so has no applicable rules
        self.applicable = dict()

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
        A branch is declared infinite if it is longer than 15.
        """
        if len(self.branch) > 15:
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

    fml1 = Neg(Conj(Imp(Prop("p"), Prop("q")), Prop("r")))
    tab1 = Tableau(fml1, propositional=True)
    tab1.generate()

    fml2 = Biimp(Neg(Conj(Prop("p"), Prop("q"))), Disj(Neg(Prop("p")), Neg(Prop("q"))))
    tab2 = Tableau(fml2, propositional=True)
    tab2.generate()

    fml3 = Neg(Disj(Atm(Pred("P"), (Const("a"), Const("b"))), Atm(Pred("P"), (Const("b"), Const("a")))))
    tab3 = Tableau(fml3)
    tab3.generate()
    #
    # fml4 = Neg(Conj(Atm(Pred("P"), (Const("a"), Const("a"))), Neg(Eq(Const("a"), Const("a")))))
    # tab4 = Tableau(fml4)
    # tab4.generate()
    #
    # fml5 = Exists(Var("x"), Forall(Var("y"), Atm(Pred("P"), (Var("x"), Var("y")))))
    # tab5 = Tableau(fml5)
    # tab5.generate()
    #
    # fml6 = Forall(Var("x"), Exists(Var("y"), Atm(Pred("P"), (Var("x"), Var("y")))))
    # tab6 = Tableau(fml6)
    # tab6.generate()

    fml7a = Imp(Prop("p"), Prop("q"))
    fml7b = Imp(Prop("q"), Prop("r"))
    fml7 = Imp(Prop("p"), Prop("r"))
    tab7 = Tableau(fml7, premises=[fml7a, fml7b], propositional=True)
    tab7.generate()

    fml8a = Imp(Atm(Pred("P"), (Const("a"), Const("b"))), Atm(Pred("Q"), (Const("a"), Const("c"))))
    fml8 = Atm(Pred("R"), (Const("a"), Const("a")))
    tab8 = Tableau(fml8, premises=[fml8a])
    tab8.generate()
