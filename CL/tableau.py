# This program is still under construction.

# todo modal logic
# todo predicate logic

from expr import *

from typing import List, Dict, Set, Tuple

propositional = True  # set this to True if the formula contains propositional variables, and False otherwise
modal = False  # set this to True if the formula contains modal operators, and False otherwise

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

    def treestr(self, indent="", binary=False, last=True):
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
        # """
        res = [self]
        for child in self.children:
            res += child.preorder()
        return res
        # return [self] + [child.preorder() for child in self.children]

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

    def branches(self):
        """
        Get the branches starting from this node.
        """
        return [leaf.branch for leaf in self.leaves()]

    def contradiction(self):
        # todo: if contradiction encountered, stop extending this branch
        # ⊥
        if isinstance(self.fml, Falsum):
            self.add_child((None, None, Closed(), "(" + ", " + str(self.line) + ")"))
            return True
        # a = b
        if isinstance(self.fml, Eq) and not self.fml.t1 == self.fml.t2:
            self.add_child((None, None, Closed(), "(" + ", " + str(self.line) + ")"))
            return True
        # ¬(a = a)
        if isinstance(self.fml, Neg) and isinstance(self.fml.phi, Eq) and self.fml.phi.t1 == self.fml.phi.t2:
            self.add_child((None, None, Closed(), "(" + ", " + str(self.line) + ")"))
            return True
        for other in self.branch:
            #  φ ... ¬φ                     ¬φ ... φ
            if Neg(self.fml) == other.fml or self.fml == Neg(other.fml):
                self.add_child((None, None, Closed(), "(" + str(other.line) + ", " + str(self.line) + ")"))
                return True

    def add_child(self, spec):
        """
        Add a child to the current node.
        """
        # todo sometimes adds None nodes (?)
        (line, sig, fml, cite) = spec
        node = Node(line, sig, fml, cite, self)
        self.children.append(node)
        node.contradiction()
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
            if not isinstance(leaf.fml, Closed):

                # append (top) node
                line += 1
                spec1 = (line, sig, fmls[0], "(" + rule + ", " + str(leaf.line) + ")")
                node1 = leaf.add_child(spec1)

                # append bottom node
                if len(fmls) == 2:
                    leafleaf = node1
                    if not (leafleaf.children and isinstance(leafleaf.children[0].fml, Closed)):
                        line += 1
                        spec2 = (line, sig, fmls[1], "(" + rule + ", " + str(leaf.line) + ")")
                        node2 = leafleaf.add_child(spec2)

    def branch_binary(self, fmls_left, fmls_right, rule):
        """
        Branch this current line binary in all this node's subordinary branches.
        """
        sig = None
        max_line = max([node.line for node in self.branch[0].preorder() if node.line])
        line = max_line

        # get last nodes of current branch
        for leaf in self.leaves():
            if not isinstance(leaf.fml, Closed):

                # append (top) left node
                line += 1
                spec1 = (line, sig, fmls_left[0], "(" + rule + ", " + str(leaf.line) + ")")
                node1 = leaf.add_child(spec1)

                # append bottom left node
                if len(fmls_left) == 2:
                    leafleaf = node1
                    if not (leafleaf.children and isinstance(leafleaf.children[0].fml, Closed)):
                        line += 1
                        spec3 = (line, sig, fmls_left[1], "(" + rule + ", " + str(leaf.line) + ")")
                        node3 = leafleaf.add_child(spec3)

                # append (top) right node
                line += 1
                spec2 = (line, sig, fmls_right[0], "(" + rule + ", " + str(leaf.line) + ")")
                node2 = leaf.add_child(spec2)

                # append bottom right node
                if len(fmls_right) == 2:
                    leafleaf = node2
                    if not (leafleaf.children and isinstance(leafleaf.children[0].fml, Closed)):
                        line += 1
                        spec4 = (line, sig, fmls_right[1], "(" + rule + ", " + str(leaf.line) + ")")
                        node4 = leafleaf.add_child(spec4)

    def expand(self):
        self.fml.tableau_pos(self)

    def update_applicable(self):
        pass

# under construction
class Branch(object):
    """
    A list of nodes representing a branch in a tree.
    """

    def __init__(self, root: Node):
        self.nodes = []
        self.consts = []
        self.sigs = []
        self.model = None
        self.add_node(root)

    def add_node(self, node: Node):
        self.nodes[-1].branches.append([node])
        self.nodes.append(node)
        self.sigs.append(node.sig)
        self.consts.append(node.fml.constants())
        node.branch = self


class Tableau(object):
    """
    A tableau.
    """

    def __init__(self, root_fml: Formula):
        self.root = Node(1, [1], root_fml, "(A)", None)

    def __str__(self):
        return self.root.treestr()

    def closed(self):
        return not self.models()

    def models(self):
        res = []
        for leaf in self.root.leaves():
            if not isinstance(leaf.fml, Closed):
                if propositional:
                    atoms = [node.fml.p for node in leaf.branch if isinstance(node.fml, Prop)]
                    v = {p: (True if p in atoms else False) for p in self.root.fml.propvars()}
                    model = PropStructure(v)
                    res.append(model)
        return res

    def expand(self, node=None):
        # todo expand tableau systematically rather than preorder
        if not node:
            node = self.root
        node.expand()
        for child in node.children:
            self.expand(child)

    def apply(self):
        print("Tableau for " + str(self.root.fml) + ":\n")
        self.expand()
        print(self)
        print("The tableau is " + ("open" if (models := self.models()) else "closed") + ".")
        if models:
            print("Models:")
            for model in models:
                print(model)
        print("\n")


####################


# fml1 =  Conj(Prop("p"), Prop("q"))
# tab1 = Tableau(fml1)
# tab1.expand()
# print(tab1.root.treestr())
#
# fml2 = Neg(Conj(Prop("p"), Prop("q")))
# tab2 = Tableau(fml2)
# tab2.expand()
# print(tab2.root.treestr())

fml = Biimp(Neg(Conj(Prop("p"), Prop("q"))), Disj(Neg(Prop("p")), Neg(Prop("q"))))
tab3 = Tableau(Neg(fml))
tab3.apply()

fml4 = Conj(Conj(Prop("p"), Prop("q")), Prop("r"))
tab4 = Tableau(fml4)
tab4.apply()
