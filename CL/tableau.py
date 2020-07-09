# -*- coding: utf-8 -*-

"""
Tableau proofs.
"""


# This part is still under construction.

# todo predicate logic
# todo modal logic
# todo integration in main module gives class not defined errors -- circular imports?


from main import *
from expr import *
from structure import *

from typing import List, Dict, Set, Tuple
import itertools


class Tableau(object):
    """
    A tableau tree.
    """

    def __init__(self, root_fml, propositional=False, modal=False):
        self.root = Node(1, [1], root_fml, "(A)", None)
        self.propositional = propositional  # todo detect automatically?
        self.modal = modal  # todo detect automatically?

    def __str__(self):
        return self.root.treestr()

    def generate(self):
        """
        Expand the tableau, generate the associate models and print some info.
        """
        if not self.propositional and self.root.fml.freevars():
            print("ERROR: You may only enter closed formulas.")
            return
        print("Tableau for " + str(self.root.fml) + ":\n")
        self.expand()
        print(self)
        print("The tableau is " + ("open" if (models := self.models()) else "closed") + ".")
        if models:
            print("Models:")
            for model in models:
                print(model)
        print("\n")

    def expand(self, node=None):
        """
        Recursively expand all nodes in the tableau.
        """
        # todo expand tableau systematically rather than preorder
        if not node:
            node = self.root
        node.expand()
        for child in node.children:
            self.expand(child)

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

                if self.propositional:
                    # atoms = all unnegated propositional variables
                    atoms = [node.fml.p for node in leaf.branch if isinstance(node.fml, Prop)]
                    # valuation = make all positive propositional variables true and all others false
                    v = {p: (True if p in atoms else False) for p in self.root.fml.propvars()}
                    model = PropStructure(v)
                    res.append(model)

                else:
                    # atoms = all unnegated atomic predications
                    atoms = [node.fml for node in leaf.branch if isinstance(node.fml, Atm)]
                    # domain = all const.s occurring in formulas
                    d = set(itertools.chain(*[node.fml.constants() for node in leaf.branch]))
                    # todo take care of function symbols
                    # interpretation = make all unnegated predications true and all others false
                    i = {a.pred.p: {tuple([term.c for term in a.terms if Atm(a.pred, a.terms) in atoms])} for a in atoms}
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
               # (".".join([str(i) for i in self.sig]) + "\t" if self.sig else "") + \

    def treestr(self, indent="", binary=False, last=True) -> str:
        """
        String representation of the tree whose root is this node.
        """
        # todo nicer overall representation?
        # todo carry | into unary children of binary parents
        res = indent
        if binary:
            res += "|--"
        elif not last:
            res += "|  "
        else:
            res += "   "
        res += str(self) + "\n"
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
        node.check_contradictions()
        return node

    def branch_unary(self, fmls, rule):
        """
        Branch this line unary in all of this node's subordinary branches.
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

    def branch_binary(self, fmls_left, fmls_right, rule):
        """
        Branch this current line binary in all this node's subordinary branches.
        """
        sig = None
        max_line = max([node.line for node in self.branch[0].preorder() if node.line])
        line = max_line

        # get last nodes of current branch
        for leaf in self.leaves():
            if not isinstance(leaf.fml, Closed):  # skip branches that are already closed

                # append (top) left node
                line += 1
                fml = fmls_left[0]
                cite = "(" + rule + ", " + str(leaf.line) + ")"
                node1 = leaf.add_child((line, sig, fml, cite))

                # append bottom left node
                if len(fmls_left) == 2:
                    leafleaf = node1
                    if not (leafleaf.children and isinstance(leafleaf.children[0].fml, Closed)):
                        line += 1
                        fml = fmls_left[1]
                        cite = "(" + rule + ", " + str(leaf.line) + ")"
                        node3 = leafleaf.add_child((line, sig, fml, cite))

                # append (top) right node
                line += 1
                fml = fmls_right[0]
                cite = "(" + rule + ", " + str(leaf.line) + ")"
                node2 = leaf.add_child((line, sig, fml, cite))

                # append bottom right node
                if len(fmls_right) == 2:
                    leafleaf = node2
                    if not (leafleaf.children and isinstance(leafleaf.children[0].fml, Closed)):
                        line += 1
                        fml = fmls_right[1]
                        cite = "(" + rule + ", " + str(leaf.line) + ")"
                        node4 = leafleaf.add_child((line, sig, fml, cite))

    def branch_delta(self, phi, var, rule):
        """
        Extend the current line according to the gamma schema (with a new param.) in all this node's subord. branches.
        """
        # ! dummy & doesn't work yet
        # todo specify rule application adequately
        sig = None
        max_line = max([node.line for node in self.branch[0].preorder() if node.line])
        line = max_line

        for leaf in self.leaves():  # visit each branch
            if not isinstance(leaf.fml, Closed):  # skip already closed branches
                line += 1
                constants = list(itertools.chain(*[node.fml.constants() for node in leaf.branch]))  # all existing constants in the curr. branch
                param = Const("c" + str(min([i for i in range(1, 10) if "c" + str(i) not in constants])))  # choose new
                fml = phi.subst(var, param)  # substitute the parameter vor the variable
                # todo subst not working
                # todo wrong expansion, skipping inner quantifier?
                cite = "(" + rule + ", " + str(leaf.line) + ")" + " " + "[" + var.u + "/" + param.c + "]"
                node = leaf.add_child((line, sig, fml, cite))  # add node

    def branch_gamma(self, phi, var, rule):
        """
        Extend the current line according to the delta schema (with an arb. param.) in all this node's subord. branches.
        """
        # ! dummy, & doesn't work yet
        # todo specify rule application adequately
        sig = None
        max_line = max([node.line for node in self.branch[0].preorder() if node.line])
        line = max_line

        for leaf in self.leaves():  # visit each branch
            if not isinstance(leaf.fml, Closed):  # skip already closed branches
                line += 1
                constants = list(itertools.chain(*[node.fml.constants() for node in leaf.branch]))  # all existing constants in the curr. branch
                param = Const(constants[0] if constants else "c1")  # choose old parameter
                fml = phi.subst(var, param)  # substitute the parameter vor the variable
                # todo subst not working
                # todo wrong expansion, skipping inner quantifier?
                cite = "(" + rule + ", " + str(leaf.line) + ")" + " " + "[" + var.u + "/" + param.c + "]"
                node = leaf.add_child((line, sig, fml, cite))  # add node

    def branch_mu(self, fml, rule):
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

    def branch_nu(self, fml, rule):
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

    def expand(self):
        self.fml.tableau_pos(self)

    def check_contradictions(self):

        # ⊥
        if isinstance(self.fml, Falsum):
            self.add_child((None, None, Closed(), "(" + ", " + str(self.line) + ")"))

        # a = b
        if isinstance(self.fml, Eq) and not self.fml.t1 == self.fml.t2:
            self.add_child((None, None, Closed(), "(" + ", " + str(self.line) + ")"))

        # ¬(a = a)
        if isinstance(self.fml, Neg) and isinstance(self.fml.phi, Eq) and self.fml.phi.t1 == self.fml.phi.t2:
            self.add_child((None, None, Closed(), "(" + ", " + str(self.line) + ")"))

        # contradiction to another formula in the same branch
        for other in self.branch:
            #  φ ... ¬φ                      ¬φ ... φ
            if Neg(self.fml) == other.fml or self.fml == Neg(other.fml):
                self.add_child((None, None, Closed(), "(" + str(other.line) + ", " + str(self.line) + ")"))


####################

if __name__ == "__main__":
    fml1 = Conj(Imp(Prop("p"), Prop("q")), Prop("r"))
    tab1 = Tableau(fml1, propositional=True)
    tab1.generate()

    fml2 = Biimp(Neg(Conj(Prop("p"), Prop("q"))), Disj(Neg(Prop("p")), Neg(Prop("q"))))
    tab2 = Tableau(Neg(fml2), propositional=True)
    tab2.generate()

    fml3 = Disj(Atm(Pred("P"), (Const("a"), Const("b"))), Atm(Pred("P"), (Const("b"), Const("a"))))
    tab3 = Tableau(fml3)
    tab3.generate()

    # fml4 = Exists(Var("x"), Forall(Var("y"), Atm(Pred("P"), (Var("x"), Var("y")))))
    # tab4 = Tableau(fml4)
    # tab4.generate()
    #
    # fml5 = Forall(Var("x"), Exists(Var("y"), Atm(Pred("P"), (Var("x"), Var("y")))))
    # tab5 = Tableau(fml5)
    # tab5.generate()

