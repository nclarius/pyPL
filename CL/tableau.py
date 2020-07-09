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

    def __init__(self, conclusion, premises=[], propositional=False, modal=False):
        self.root = Node(1, [1], Neg(conclusion), "(A)", None)
        self.premises = [self.root.leaves()[0].add_child((i+2, [1], premise, "(A)"))
                         for i, premise in enumerate(premises)]
        self.propositional = propositional  # todo detect automatically?
        self.modal = modal  # todo detect automatically?

    def __str__(self):
        return self.root.treestr()[:-1]

    def generate(self):
        """
        Expand the tableau, generate the associate models and print some info.
        """
        # todo systematic error handling
        if not self.propositional and self.root.fml.freevars():
            print("ERROR: You may only enter closed formulas.")
            return
        print("Tableau for " +
              ", ".join([str(premise.fml) for premise in self.premises]) + " ⊨ " + str(self.root.fml.phi) + ":\n")
        self.expand()  # recursively apply the rules
        models = self.models()  # collect branches that are still open
        print(self)  # print the tableau
        print("The tableau is " + ("open" if models else "closed") + ":\n"
              "The " + ("inference" if self.premises else "formula") + " is " + ("in" if models else "") + "valid.")
        if models:
            print("\nCounter models:")
            for model in models:
                print(model)  # print counter model
        print("\n")

    def expand(self, node=None):
        """
        Recursively expand all nodes in the tableau.
        """
        # todo expand tableau systematically rather than in preorder
        if not node:
            node = self.root  # value on initialization
            for node in self.root.leaves()[0].branch:
                node.check_contradiction()  # check for contradictions in assumptions
        node.expand()  # expand node
        for child in node.children:
            self.expand(child)  # recursively expand children

    def closed(self) -> bool:
        """
        A tableau is closed iff all branches are closed.

        @return True if all branches are closed, and False otherwise
        @rtype: bool
        """
        return not self.models()

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
            if not isinstance(leaf.fml, Closed):
                # open branch
                leaf.add_open()
                leaf = leaf.branch[-2]

                if self.propositional:
                    # atoms = all unnegated propositional variables
                    atoms = [node.fml.p for node in leaf.branch if isinstance(node.fml, Prop)]
                    # valuation = make all positive propositional variables true and all others false
                    v = {p: (True if p in atoms else False) for p in self.root.fml.propvars()}
                    model = PropStructure(v)
                    res.append(model)

                else:
                    # atoms = all unnegated atomic predications
                    atoms = [(node.fml.pred, node.fml.terms) for node in leaf.branch if isinstance(node.fml, Atm)]
                    # predicates = all predicates occurring in the conclusion and premises
                    constants = set(chain(self.root.fml.nonlogs()[0],
                                          *[prem.fml.nonlogs()[0] for prem in self.premises]))
                    # todo show constants in interpret.?
                    funcsymbs = set(chain(self.root.fml.nonlogs()[1],
                                          *[prem.fml.nonlogs()[1] for prem in self.premises]))
                    # todo take care of function symbols in domain and interpretation
                    predicates = set(chain(self.root.fml.nonlogs()[2],
                                           *[prem.fml.nonlogs()[2] for prem in self.premises]))
                    # domain = all const.s occurring in formulas
                    d = set(chain(*[node.fml.nonlogs()[0] for node in leaf.branch]))
                    # interpretation = make all unnegated predications true and all others false
                    i = {p: {tuple([str(t) for t in a[1]]) for a in atoms if (Pred(p), a[1]) in atoms}
                         for p in predicates}
                    model = PredStructure(d, i)
                    res.append(model)

        return res

class Node(object):
    """
    A node in a tree.
    """

    def __init__(self, line: int, sig: List[int], fml: Formula, cite: str, parent):
        self.line = line
        self.sig = sig
        self.fml = fml
        self.cite = cite
        self.branch = (parent.branch if parent else []) + [self]
        self.children = []

    def __str__(self):
        """
        String representation of this line.
        """
        return (str(self.line) + "." if self.line else "") + "\t" + \
               str(self.fml) + "\t" + \
               self.cite

    def treestr(self, indent="", binary=False, last=True) -> str:
        """
        String representation of the tree whose root is this node.
        """
        # todo better overall representation?
        # todo carry "|" into unary children of binary parents
        len_col1 = max([len(str(node.line)) for node in self.branch[0].preorder()])
        len_col2 = max([len(str(node.fml)) for node in self.branch[0].preorder()]) + 1
        len_col3 = max([len(str(node.cite)) for node in self.branch[0].preorder()])

        res = indent
        if binary:
            res += "|--"
        elif not last:
            res += "|  "
        else:
            res += "   "
        res += "{:<{len}}".format(str(self.line) + "." if self.line else "", len=len_col1) + \
               "{:^{len}}".format(str(self.fml), len=len_col2) + \
               "{:<{len}}".format(str(self.cite), len=len_col3) + \
               "\n"
        if self.children:
            if not last:
                if len(self.children) == 1:  # unary branching; dont indent
                    if childstr := self.children[0].treestr(indent, False, True):
                        res += childstr
                elif len(self.children) == 2:  # binary branching; indent
                    if childstr1 := self.children[0].treestr(indent + "|  ", True, False):
                        res += childstr1
                    if childstr2 := self.children[1].treestr(indent + "|  ", True, True):
                        res += childstr2
            else:
                if len(self.children) == 1:  # unary branching; dont indent
                    if childstr := self.children[0].treestr(indent, False, True):
                        res += childstr
                elif len(self.children) == 2:  # binary branching; indent
                    if childstr1 := self.children[0].treestr(indent + "   ", True, False):
                        res += childstr1
                    if childstr2 := self.children[1].treestr(indent + "   ", True, True):
                        res += childstr2
        else:
            if last:
                res += indent + "   \n"
            else:
                res += indent + "   \n"
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

    def add_child(self, spec):
        """
        Add a child to the current node.
        """
        # todo sometimes adds None nodes (?)
        (line, sig, fml, cite) = spec
        node = Node(line, sig, fml, cite, self)
        self.children.append(node)
        node.check_contradiction()
        return node

    def expand(self):
        if val := self.fml.tableau_pos(self):  # check which rule application the formula defines, if any
            (rule_type, args, rule) = val
            rule_type(args, rule)  # apply the rule

    def rule_alpha(self, fmls, rule):
        """
        Extend the current line unary in all of this node's subordinary branches.
        """
        sig = None
        max_line = max([node.line for node in self.branch[0].preorder() if node.line])
        line = max_line

        for branch in self.branches():
            # get last node of current branch
            leaf = branch[-1]
            if not isinstance(leaf.fml, Closed):  # skip branches that are already closed

                # append (top) node
                line += 1
                fml = fmls[0]
                cite = "(" + rule + ", " + str(leaf.line) + ")"
                node1 = leaf.add_child((line, sig, fml, cite))

                # append bottom node
                if len(fmls) == 2:
                    leafleaf = node1
                    if not (leafleaf.children and isinstance(leafleaf.children[0].fml, Closed)):
                        line += 1
                        fml = fmls[1]
                        cite = "(" + rule + ", " + str(leaf.line) + ")"
                        node2 = leafleaf.add_child((line, sig, fml, cite))

    def rule_beta(self, fmls, rule):
        """
        Extend the current line binary in all this node's subordinary branches.
        """
        sig = None
        max_line = max([node.line for node in self.branch[0].preorder() if node.line])
        line = max_line

        # get last nodes of current branch
        for leaf in self.leaves():
            if not isinstance(leaf.fml, Closed):  # skip branches that are already closed

                # append (top) left node
                line += 1
                fml = fmls[0][0]
                cite = "(" + rule + ", " + str(leaf.line) + ")"
                node1 = leaf.add_child((line, sig, fml, cite))

                # append bottom left node
                if len(fmls[0]) == 2:
                    leafleaf = node1
                    if not (leafleaf.children and isinstance(leafleaf.children[0].fml, Closed)):
                        line += 1
                        fml = fmls[0][1]
                        cite = "(" + rule + ", " + str(leaf.line) + ")"
                        node3 = leafleaf.add_child((line, sig, fml, cite))

                # append (top) right node
                line += 1
                fml = fmls[1][0]
                cite = "(" + rule + ", " + str(leaf.line) + ")"
                node2 = leaf.add_child((line, sig, fml, cite))

                # append bottom right node
                if len(fmls[1]) == 2:
                    leafleaf = node2
                    if not (leafleaf.children and isinstance(leafleaf.children[0].fml, Closed)):
                        line += 1
                        fml = fmls[1][1]
                        cite = "(" + rule + ", " + str(leaf.line) + ")"
                        node4 = leafleaf.add_child((line, sig, fml, cite))

    def rule_gamma(self, args, rule):
        """
        Extend the current line according to the delta schema (with an arb. param.) in all this node's subord. branches.
        """
        # ! dummy, & doesn't work yet
        # todo specify rule application adequately
        phi, var = args
        sig = None
        max_line = max([node.line for node in self.branch[0].preorder() if node.line])
        line = max_line

        for leaf in self.leaves():  # visit each branch
            if not isinstance(leaf.fml, Closed):  # skip already closed branches
                line += 1
                constants = list(chain(*[node.fml.nonlogs()[0] for node in leaf.branch]))  # all existing constants in the curr. branch
                param = Const(constants[0] if constants else "c1")  # choose old parameter
                fml = phi.subst(var, param)  # substitute the parameter vor the variable
                # todo wrong expansion, skipping inner quantifier?
                cite = "(" + rule + ", " + str(leaf.line) + ")" + " " + "[" + var.u + "/" + param.c + "]"
                node = leaf.add_child((line, sig, fml, cite))  # add node

    def rule_delta(self, args, rule):
        """
        Extend the current line according to the gamma schema (with a new param.) in all this node's subord. branches.
        """
        # ! dummy & doesn't work yet
        # todo specify rule application adequately
        phi, var = args
        sig = None
        max_line = max([node.line for node in self.branch[0].preorder() if node.line])
        line = max_line

        for leaf in self.leaves():  # visit each branch
            if not isinstance(leaf.fml, Closed):  # skip already closed branches
                line += 1
                constants = list(chain(*[node.fml.nonlogs()[0] for node in leaf.branch]))  # all existing constants in the curr. branch
                param = Const("c" + str(min([i for i in range(1, 10) if "c" + str(i) not in constants])))  # choose new
                fml = phi.subst(var, param)  # substitute the parameter vor the variable
                # todo wrong expansion, skipping inner quantifier?
                cite = "(" + rule + ", " + str(leaf.line) + ")" + " " + "[" + var.u + "/" + param.c + "]"
                node = leaf.add_child((line, sig, fml, cite))  # add node

    def rule_mu(self, fml, rule):
        """
        Extend the current line according to the mu schema (with a new sig.) in all this node's subord. branches.
        """
        # todo dummy -- specify rule application adequately
        sig = self.sig
        max_line = max([node.line for node in self.branch[0].preorder() if node.line])
        line = max_line

        for leaf in self.leaves():  # visit each branch
            if not isinstance(leaf.fml, Closed):  # skip already closed branches
                line += 1
                signatures = [node.sig for node in leaf.branch]  # all existing signatures in the current branch
                sig = sig.append(min([i for i in range(1,) if sig.append(i) not in signatures]))  # choose new sig.
                cite = "(" + rule + ", " + str(leaf.line) + ")"
                node = leaf.add_child((line, sig, fml, cite))  # add node

    def rule_nu(self, fml, rule):
        """
        Extend the current line according to the nu schema (with an old sig.) in all this node's subord. branches.
        """
        # todo dummy -- specify rule application adequately
        sig = self.sig
        max_line = max([node.line for node in self.branch[0].preorder() if node.line])
        line = max_line

        for leaf in self.leaves():  # visit each branch
            if not isinstance(leaf.fml, Closed):  # skip already closed branches
                line += 1
                signatures = [node.sig for node in leaf.branch]  # all existing signatures in the current branch
                sig = signatures[0] if signatures else sig.append(1)  # choose old signature
                cite = "(" + rule + ", " + str(leaf.line) + ")"
                node = leaf.add_child((line, sig, fml, cite))  # add node

    def check_contradiction(self):
        self.fml.tableau_contradiction_pos(self)

    def add_close(self, lines):
        """
        Add a pseudo-node for a contradictory branch.
        """
        self.add_child((None, None, Closed(), "(" + ", ".join([str(line) for line in lines]) + ")"))

    def add_open(self):
        """
        Add a pseudo-node for a contradictory branch.
        """
        self.add_child((None, None, Open(), ""))


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

    fml4 = Neg(Conj(Atm(Pred("P"), (Const("a"), Const("a"))), Neg(Eq(Const("a"), Const("a")))))
    tab4 = Tableau(fml4)
    tab4.generate()

    fml5 = Exists(Var("x"), Forall(Var("y"), Atm(Pred("P"), (Var("x"), Var("y")))))
    tab5 = Tableau(fml5)
    tab5.generate()

    fml6 = Forall(Var("x"), Exists(Var("y"), Atm(Pred("P"), (Var("x"), Var("y")))))
    tab6 = Tableau(fml6)
    tab6.generate()

    fml7a = Imp(Prop("p"), Prop("q"))
    fml7b = Imp(Prop("q"), Prop("r"))
    fml7 = Imp(Prop("p"), Prop("r"))
    tab7 = Tableau(fml7, premises=[fml7a, fml7b], propositional=True)
    tab7.generate()

    fml8a = Imp(Atm(Pred("P"), (Const("a"), Const("b"))), Atm(Pred("Q"), (Const("a"), Const("c"))))
    fml8 = Atm(Pred("R"), (Const("a"), Const("a")))
    tab8 = Tableau(fml8, premises=[fml8a])
    tab8.generate()
