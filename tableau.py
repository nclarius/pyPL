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
import itertools
from itertools import chain

# todo count rule applications relative to branch
# todo documentation
# todo improve model generation
# todo make non-K modal logics work
# todo tableaux for IL

debug = False

rule_names = {"α": "alpha", "β": "beta",  # connective rules
              "γ": "gamma", "δ": "delta", "η": "eta", "θ": "theta",  # quantifier rules
              "μ": "mu", "ν": "nu", "π": "pi", "κ": "kappa", "λ": "lambda",  # modal rules
              "ξ": "xi", "χ": "chi", "ο": "omicron", "u": "ypsilon", "ω": "omega"  # intuitionistic rules
              }
parameters = list("abcdefghijklmnopqrst") + ["c" + str(i) for i in range(1, 1000)]
num_mdls = 1  # number of models to generate  # todo doesn't really work
latex = False


class Tableau(object):
    """
    A tableau tree.
    """

    def __init__(self,
                 conclusion=None, premises=[], axioms=[],
                 validity=True, satisfiability=True,
                 classical=True, propositional=False, modal=False, vardomains=False, frame="K"):
        # settings
        # todo nicer specification of settings?
        # todo check consistency of settings
        self.mode = {
            "latex": latex,
            "validity": validity, "satisfiability": satisfiability,
            "classical": classical, "propositional": propositional,
            "modal": modal, "vardomains": vardomains, "frame": frame
        }

        # append initial nodes
        line = 1
        # sig = (1,) if modal or not classical else None
        world = 1 if validity and (modal or not classical) else None
        signed = True if not classical or modal else False  # todo reimplement with signed formulas
        rule = "A"
        source = None
        inst = tuple()
        negative = True if validity or not validity and not satisfiability else False
        root_fml, premise_fmls, axiom_fmls = \
            (conclusion, premises, axioms) if conclusion else (premises[0], premises[1:], axioms)
        if classical and (not modal or validity):  # default: no forcing sign
            root_fml = root_fml if not negative else Neg(root_fml)
        else:  # ML MG and IL: forcing sign
            root_fml = Forces(root_fml) if not negative else NotForces(root_fml)
            premise_fmls = [Forces(prem) for prem in premise_fmls]
            axiom_fmls = [Forces(ax) for ax in axiom_fmls]
        self.conclusion = conclusion
        self.root = Node(None, line, world, root_fml, rule, source, inst)
        self.premises = [self.root.leaves()[0].add_child((i + 2, world, premise_fml, rule, source, inst))
                         for i, premise_fml in enumerate(premise_fmls)]
        max_line = max([node.line for node in self.root.nodes() if node.line])
        self.axioms = [self.root.leaves()[0].add_child((i + max_line + 1, world, axiom, "Ax", source, inst))
                       for i, axiom in enumerate(axiom_fmls)]
        # todo formulas with free variables?

        self.models = []

        # run the tableau
        self.run()

    def __str__(self):
        return self.root.treestr()

    def __len__(self):
        return len(self.root.nodes())

    def run(self):
        """
        Expand the tableau, generate the associate models and print some info.
        """
        # create preamble
        if latex:
            preamble = "\\documentclass[a4paper]{article}\n\n\\usepackage{amssymb, amsmath}\n\n\\begin{document}\n\n"
            print(preamble)

        # print info
        info = "\n"
        info += "You are using " + \
                ("proof search" if self.mode["validity"] else
                 ("model" if self.mode["satisfiability"] else "countermodel") + " generation") + "\nfor " + \
                ("classical " if self.mode["classical"] else "intuitionistic ") + \
                ("modal " if self.mode["modal"] else "") + \
                ("propositional " if self.mode["propositional"] else "predicate ") + \
                "logic" + \
                (" with " + ("varying " if self.mode["vardomains"] else "constant ") + "domains"
                 if self.mode["modal"] and not self.mode["propositional"] else "") + \
                (" in a " + self.mode["frame"] + " frame" if self.mode["modal"] else "") + \
                ".\n\n"
        if self.mode["validity"]:
            info += "Tableau for " + \
                   ", ".join([str(premise.fml) for premise in self.axioms + self.premises]) + \
                   " ⊨ " + str(self.conclusion) + ":\n"
        else:
            info += "Tableau for " + \
                    ", ".join([str(node.fml) for node in self.premises + self.axioms]) + \
                    " ⊭" + (" " + str(self.conclusion) if self.conclusion else "") + ":\n\n"
        info = info.replace("⊩ ", "").replace("⊮ ", "")
        if latex:
            info.replace("\n", "\\\\\n")
        print(info)

        # recursively apply the rules
        self.expand()

        # print the tableau
        print(self.root.treestr()[:-1])  # todo latex for trees

        # print result
        result = ""
        if self.closed():
            result += "The tableau is closed:\n"
            if self.mode["validity"]:
                result += "The " + ("inference" if self.premises else "formula") + " is valid.\n"
            else:
                if self.mode["satisfiability"]:
                    result += "The " + ("set of sentences" if self.premises else "formula") + " is unsatisfiable.\n"
                else:
                    result += "The " + ("inference" if self.premises else "formula") + " is irrefutable.\n"
        elif self.open():
            result += "The tableau is open:\n"
            if self.mode["validity"]:
                result += "The " + ("inference" if self.premises else "formula") + " is invalid.\n"
            else:
                if self.mode["satisfiability"]:
                    result += "The " + ("set of sentences" if self.premises else "formula") + " is satisfiable.\n"
                else:
                    result += "The " + ("inference" if self.premises else "formula") + " is refutable.\n"
        elif self.infinite():
            result += "The tableau is potentially infinite:\n"
            if self.mode["validity"]:
                result += "The " + ("inference" if self.premises else "formula") + " may or may not be valid.\n"
            else:
                if self.mode["satisfiability"]:
                    result += "The " + \
                              ("set of sentences" if self.premises else "formula") + \
                           " may or may not be satisfiable.\n"
                else:
                    result += "The " + ("inference" if self.premises else "formula") + " may or may not be refutable.\n"
        if latex:
            result.replace("\n", "\\\\\n")
        print(result)

        # generate and print models
        if self.models:
            mdls = ""
            mdls += "Countermodels:\n" \
                if self.mode["validity"] or not self.mode["validity"] and not self.mode["satisfiability"] \
                else "Models:\n"
            for model in self.models:
                mdls += "\n"
                mdls += str(model) + "\n"  # todo latex for models
            if latex:
                mdls.replace("\n", "\\\\\n")
            print(mdls)

        if not latex:
            sep = "\n" + 80 * "-"
            print(sep)
        if latex:
            postamble = "\\end{document}"
            print(postamble)

    def applicable(self):
        """
        A prioritized list of applicable rules in the tree in the format
        {(target, source, rule name, rule type, formulas, arguments, instantiations)}

        @rtype: list[tuple[node,node,str,list[Any],int]]
        """
        # collect the applicable rules in the tree
        applicable = []
        # traverse all nodes that could be expandable
        for source in [node for node in self.root.nodes() if node.fml]:
            for rule_name, rule in source.rules(self.mode).items():
                rule_type, fmls = rule

                def applied(node):  # nodes in the branch that this rule has already been applied on
                    return node and node.rule == rule_name and node.source and node.source.line == source.line

                # connective rules
                if rule_type in ["α", "β"]:
                    # the rule is applicable to those branches it has not already been applied on
                    targets = [node for node in source.leaves(True) if node.fml]
                    for target in targets:
                        branch = target.branch
                        if not any([applied(node) for node in branch]):
                            args = ([],)
                            insts = 0
                            applicable.append((target, source, rule_name, rule_type, fmls, args, insts))

                # quantifier rules
                elif rule_type in ["γ", "δ", "η", "θ"]:
                    targets = [node for node in source.leaves(True) if node.fml]
                    if rule_type in ["θ"]:
                        targets = []
                        for leaf in [leaf for leaf in source.leaves() if leaf.fml]:
                            # the rule branches on the node of its first instantiation rather than the leaves
                            # find nodes on the branch which are expansions of this source and their parents
                            instantiations = [node for node in leaf.branch
                                              if node and node.source and node.source.line and
                                              node.source.line == source.line]
                            if instantiations:
                                # the rule has already been applied:
                                # append the parent of the first instantiation as a target,
                                # but only if the parent is not already declared infinite
                                parent = instantiations[0].branch[-2]
                                if not parent.children[-1].pseudo():
                                    targets.append(parent)
                            else:
                                # the rule has not yet been applied:
                                # add the leaf as a target if it is not finished
                                if not leaf.pseudo():
                                    targets.append(leaf)

                    for target in targets:
                        branch = [node for node in target.branch if node.fml]
                        # collect the constants this rule has been instantiated with in the branch/level
                        used = list(dict.fromkeys([str(node.inst[1]) for node in branch if applied(node)])) \
                            if rule_type not in ["θ"] else \
                            list(dict.fromkeys([str(node.inst[1]) for node in instantiations if node.inst]))
                        # collect the constants occurring in the branch
                        occurring = list(dict.fromkeys(chain(*[[str(c)
                                                               for c in node.fml.nonlogs()[0]] for node in branch])))
                        # check if indexed constants are required (for modal PL with var. domains and IL)
                        indexed = self.mode["modal"] and not self.mode["propositional"] and self.mode["vardomains"] or \
                                  not self.mode["classical"]
                        # compose the arguments
                        args = used, occurring, indexed
                        # count instantiations
                        insts = len(used) if rule_type not in ["θ"] else len(instantiations)

                        if rule_type in ["γ", "δ", "θ"]:
                            # the rule is applied with some constant
                            applicable.append((target, source, rule_name, rule_type, fmls, args, insts))

                        elif rule_type in ["η"]:
                            # the rule can only be applied to nodes and constants it has not already been applied with,
                            # and only if there are constants occurring in the branch or needed for additional models
                            # yet to be instantiated;
                            # except there are no constants at all, then it may be applied with an arbitrary parameter
                            if any([not any([node.inst[1] == c for node in branch if applied(node)])
                                    for c in occurring + parameters[:num_mdls-1]]) \
                                    or not occurring:
                                applicable.append((target, source, rule_name, rule_type, fmls, args, insts))

                # modal rules
                elif rule_type in ["μ", "ν", "π", "κ", "λ"]:
                    targets = [node for node in source.leaves(True) if node.fml]
                    if rule_type in ["κ"]:
                        targets = []
                        for leaf in [leaf for leaf in source.leaves() if leaf.fml]:
                            # the rule branches on the node of its first instantiation rather than the leaves
                            # find nodes on the branch which are expansions of this source and their parents
                            instantiations = [node for node in leaf.branch
                                              if node and node.source and node.source.line and
                                              node.source.line == source.line]
                            if instantiations:
                                # the rule has already been applied:
                                # append the parent of the first instantiation as a target,
                                # but only if the parent is not already declared infinite
                                parent = instantiations[0].branch[-2]
                                if not isinstance(parent.children[-1].fml, Infinite):
                                    targets.append(parent)
                            else:
                                # the rule has not yet been applied:
                                # add the leaf as a target if it is not finished
                                if not leaf.pseudo():
                                    targets.append(leaf)

                    for target in targets:
                        branch = [node for node in target.branch if node.fml]
                        # # collect the signatures this rule has been instantiated with in the branch/on this level
                        # used = list(dict.fromkeys([node.inst[1] for node in branch if applied(node)])) \
                        #     if rule_type not in ["κ"] else \
                        #     list(dict.fromkeys([node.inst[1] for node in siblings]))
                        # # collect the signatures occurring in the branch
                        # occurring = list(dict.fromkeys([node.sig for node in branch if node.sig]))
                        # # collect the signatures occurring in the branch that are extensions of the source signature
                        # extensions = list(dict.fromkeys([node.sig for node in branch if node.sig and
                        #                                  len(node.sig) == len(source.sig) + 1 and
                        #                                  node.sig[:-1] == source.sig]))
                        # collect the worlds this rule has been instantiated with in the branch/on this level
                        used = list(dict.fromkeys([node.inst[1] for node in branch if applied(node)])) \
                            if rule_type not in ["κ"] else \
                            list(dict.fromkeys([node.inst[1] for node in instantiations if node.inst]))
                        # collect the worlds occurring in the branch
                        occurring = list(dict.fromkeys([node.world for node in branch if node.world]))
                        # additional worlds to use
                        fresh = [i for i in range(1, 100) if i not in occurring]
                        # collect the signatures occurring in the branch that are accessible from the source world
                        extensions = list(dict.fromkeys([node.inst[1] for node in branch
                                                         if node.inst and node.inst[0] == source.world]))
                        if not extensions and rule_name == "A":
                            extensions = fresh
                        # # for model finding, add at least one world
                        # if not self.mode["validity"] and not extensions:
                        #     extensions = occurring[:1]
                        # collect the signatures occurring in the branch that the source world is accessible from
                        reductions = list(dict.fromkeys([node.inst[0] for node in branch
                                                         if node.inst and node.inst[1] == source.world]))
                        # compose the arguments
                        args = used, occurring, extensions, reductions
                        # count instantiations
                        insts = len(used) if rule_type not in ["κ"] else len(instantiations)

                        if rule_type in ["μ", "κ"]:
                            # the rules can be applied with any new signature extension
                            applicable.append((target, source, rule_name, rule_type, fmls, args, insts))

                        elif rule_type in ["ν"]:
                            # the rule can only be applied if there are sig. ext.s in the branch yet to be instantiated
                            if any([s not in used for s in extensions]):
                                applicable.append((target, source, rule_name, rule_type, fmls, args, insts))

                        elif rule_type in ["π"]:
                            # the rule can only be applied if the signature has a predecessor
                            if len(source.sig) > 1:
                                applicable.append((target, source, rule_name, rule_type, fmls, args, insts))

                        elif rule_type in ["λ"]:
                            # the rule can only be applied to nodes and signatures it has not already been applied with,
                            # and only if there are extensions occurring in the branch or needed for additional models
                            # yet to be instantiated,
                            # except when there are no signatures in the branch at all and the rule is an assumption
                            if any([not any([node.inst[1] == w
                                             for node in branch if applied(node)])
                                    for w in extensions + fresh[:num_mdls-1]]) or \
                                    rule_name == "A" and not occurring:
                                applicable.append((target, source, rule_name, rule_type, fmls, args, insts))

                # intuitionistic rules
                elif rule_type in ["ξ", "χ", "ο", "u", "ω"]:
                    pass  # not yet implemented

        # if the only rules applicable to an unfinished branch are
        # δ, θ or κ rules that have already been applied on this branch,
        # it is declared open and, in the case of validity tableaus, its applicable rules cleared
        for leaf in [node for node in self.root.leaves() if node.fml
                     if not (isinstance(node.fml, Closed) or isinstance(node.fml, Infinite))]:
            if all([appl[6] and appl[3] in ["δ", "θ", "κ"]
                    for appl in applicable if appl[0] in leaf.branch]):
                if not leaf.pseudo():
                    leaf.open()
                    self.models.append(self.model(leaf))
                if self.mode["validity"]:
                    applicable = [appl for appl in applicable if appl[0] not in leaf.branch]

        # define a preference order for rule types
        rule_order = {r: i for (i, r) in enumerate(
            ["η", "λ", "α", "β", "δ", "γ", "θ", "π", "μ", "ν", "κ", "ξ", "χ", "ο", "u", "ω"])}
        # enumerate the nodes level-order so nodes can be prioritized by position in the tree
        pos = {node: i for (i, node) in enumerate(self.root.nodes())}
        pos_rev = {node: i for (i, node) in enumerate(self.root.nodes(True)[::-1])}
        # sort the applicable rules by ...
        sort_v1 = lambda i: (  # for validity tableaus:
            i[6],              # 1. number of times the rule has already been applied on this branch (prefer least used)
            pos[i[1]],         # 2. position of the source node in the tree (prefer leftmost highest)
            pos[i[0]],         # 3. position of the target node in the tree (prefer leftmost highest)
            rule_order[i[3]]   # 4. rule type rank (prefer earlier in order)
        )
        sort_v2 = lambda i: (  # for satisfiability tableaus:
            i[6],              # 1. number of times the rule has already been applied on this branch (prefer least used)
            rule_order[i[3]],  # 2. rule type rank (prefer earlier in order)
            pos_rev[i[0]],     # 3. position of the target node in the tree (prefer leftmost lowest)
            pos_rev[i[1]]      # 4. position of the source node in the tree (prefer leftmost lowest)

        )
        appl_sorted = list(k for k, _ in itertools.groupby([itm for itm in
                                                            sorted(applicable, key=(
                                                                sort_v1 if self.mode["validity"] else sort_v2))]))
        return appl_sorted

    def expand(self):
        """
        Recursively expand all nodes in the tableau.
        """
        while applicable := self.applicable():
            len_assumptions = sum([len(str(node.fml)) for node in self.root.nodes()
                                   if node.rule == "A" and not node.world])
            num_nodes = len(self.root.nodes(True))
            # the tree gets too big; stop execution
            if num_nodes > 3 * len_assumptions:
                # mark abandoned branches
                for leaf in self.root.leaves(True):
                    leaf.add_child((None, None, Infinite(), None, None, None))
                return
            if not self.mode["validity"] and len(self.models) >= num_mdls:
                # enough models have been found; stop the execution
                # mark abandoned branches
                for leaf in self.root.leaves(True):
                    leaf.add_child((None, None, Infinite(), None, None, None))
                return
            if debug:
                print("applicable:")
                print("\n".join([", ".join([
                    str(i), str(itm[0].line), str(itm[1].line), itm[2], str(itm[3]), str(itm[5]), str(itm[6])])
                    for i, itm in enumerate(applicable)]))
            # get first applicable rule from prioritized list
            (target, source, rule_name, rule_type, fmls, args, insts) = applicable[0]
            rule_func = getattr(self, "rule_" + rule_names[rule_type])
            # apply the rule
            if debug:
                input()
                print("expanding:")
                print(str(target), " with ", rule_name, " from ", str(source))
            rule_func(target, source, rule_name, fmls, args)
            if debug:
                print()
                print(self.root.treestr())
                print("--------")
                print()

    def rule_alpha(self, target, source, rule, fmls, args):
        """
        α
        Branch unary.
        """
        line = max([node.line for node in self.root.nodes() if node.line])
        # sig = tuple([s for s in source.sig]) if source.sig else None
        world = source.world

        # append (top) node
        top = target.add_child((line := line + 1, world, fmls[0], rule, source, []))

        # append bottom node
        if len(fmls) == 2:
            bot = top.add_child((line := line + 1, world, fmls[1], rule, source, []))

    def rule_beta(self, target, source, rule, fmls, args):
        """
        β
        Branch binary.
        """
        line = max([node.line for node in self.root.nodes() if node.line])
        # sig = tuple([s for s in source.sig]) if source.sig else None
        world = source.world

        # append (top) left node
        topleft = target.add_child((line := line + 1, world, fmls[0], rule, source, []))

        # append bottom left node
        if len(fmls) == 4 and topleft:
            botleft = topleft.add_child((line := line + 1, world, fmls[2], rule, source, []))

        # append (top) right node
        topright = target.add_child((line := line + 1, world, fmls[1], rule, source, []))

        # append bottom right node
        if len(fmls) == 4 and topright:
            botright = topright.add_child((line := line + 1, world, fmls[3], rule, source, []))

    def rule_gamma(self, target, source, rule, fmls, args):
        """
        γ
        Branch unary with an arbitrary constant.
        """
        phi, var = fmls
        used, occurring, indexed = args
        line = max([node.line for node in self.root.nodes() if node.line])
        # sig = tuple([s for s in source.sig]) if source.sig else None
        world = source.world

        # find a constant to substitute
        # limit the occurring constants to those belong to the domain of the current world
        occurring = [c for c in occurring if "_" + str(world) in c]
        # for modal predicate logic with varying domains: add signature subscript to constant
        # subscript = "_" + ".".join([str(s) for s in source.sig]) if indexed else ""
        subscript = "_" + str(source.world) if indexed else ""
        usable = [c + (subscript if "_" not in c else "") for c in occurring + parameters]
        usable += ["a"] if not usable else []
        # choose first symbol from constants and parameters that has not already been used with this particular rule
        const_symbol = usable[(min([i for i in range(len(usable)) if usable[i] not in used]))]
        const = Const(const_symbol)
        new = True if const_symbol not in occurring else False

        # compute formula
        inst = (str(var), str(const), new)
        fml = phi.subst(var, const)

        # add node
        target.add_child((line + 1, world, fml, rule, source, inst))

    def rule_delta(self, target, source, rule, fmls, args):
        """
        δ
        Branch unary with a new constant.
        """
        phi, var = fmls
        used, occurring, indexed = args
        line = max([node.line for node in self.root.nodes() if node.line])
        # sig = tuple([s for s in source.sig]) if source.sig else None
        world = source.world

        # find a constant to substitute
        # for modal predicate logic with varying domains: add signature subscript to constant
        # subscript = "_" + ".".join([str(s) for s in source.sig]) if indexed else ""
        subscript = "_" + str(source.world) if indexed else ""
        usable = [c + (subscript if "_" not in c else "") for c in parameters]
        # choose first symbol from list of parameters that does not yet occur in this branch
        const_symbol = usable[(min([i for i in range(len(usable)) if usable[i] not in occurring]))]
        const = Const(const_symbol)
        new = True

        # compute formula
        inst = (str(var), str(const), new)
        fml = phi.subst(var, const)

        # add node
        target.add_child((line + 1, world, fml, rule, source, inst))

    def rule_eta(self, target, source, rule, fmls, args):
        """
        η
        Branch unary with an existing constant.
        """
        phi, var = fmls
        used, occurring, indexed = args
        line = max([node.line for node in self.root.nodes() if node.line])
        # sig = tuple([s for s in source.sig]) if source.sig else None
        world = source.world

        # find a constant to substitute
        # for modal predicate logic with varying domains: add signature subscript to constant
        # subscript = "_" + ".".join([str(s) for s in source.sig]) if indexed else ""
        subscript = "_" + str(source.world) if indexed else ""
        usable = [c + (subscript if "_" not in c else "")
                  for c in (occurring + parameters[:num_mdls-1] if occurring + parameters[:num_mdls-1] else ["a"])]
        # choose first symbol from occurring that has not already been used with this particular rule
        const_symbol = usable[(min([i for i in range(len(usable)) if usable[i] not in used]))]
        const = Const(const_symbol)
        new = True if const_symbol not in occurring else False

        # compute formula
        inst = (str(var), str(const), new)
        fml = phi.subst(var, const)

        # add node
        target.add_child((line + 1, world, fml, rule, source, inst))

    def rule_theta(self, target, source, rule, fmls, args):
        """
        θ
        Branch n-ay with an arbitrary constant.
        """
        phi, var = fmls
        used, occurring, indexed = args
        line = max([node.line for node in self.root.nodes() if node.line])
        # sig = tuple([s for s in source.sig]) if source.sig else None
        world = source.world

        # find a constant to substitute
        # for modal predicate logic varying domains: add signature subscript to constant
        # subscript = "_" + ".".join([str(s) for s in source.sig]) if indexed else ""
        subscript = "_" + str(source.world) if indexed else ""
        usable = [c + (subscript if "_" not in c else "") for c in occurring + parameters]
        # choose first symbol from occurring and parameters that has not already been used with this particular rule
        const_symbol = usable[(min([i for i in range(len(usable)) if usable[i] not in used]))]
        const = Const(const_symbol)
        new = True if const_symbol not in occurring else False

        # compute formula
        inst = (str(var), str(const), new)
        fml = phi.subst(var, const)

        # add pseudo-node to indicate branching (the rule branches on the source rather than the leaves)
        target.add_child((None, None, None, rule, source, None))
        # add node
        target.add_child((line + 1, world, fml, rule, source, inst))

    def rule_mu(self, target, source, rule, fmls, args):
        """
        μ
        Branch unary with a new signature.
        """
        used, occurring, extensions, reductions = args
        line = max([node.line for node in self.root.nodes() if node.line])

        # choose a signature that does not already occur in this branch
        # sig = None
        # for i in range(1, 100):
        #     if (sig_ := tuple([s for s in source.sig]) + (i,)) not in occurring:
        #         sig = sig_
        #         break
        # inst = (source.sig, sig)
        world = min([i for i in range(1, 1000) if i not in occurring])
        new = True
        inst = (source.world, world, new)

        # add (top) node
        top = target.add_child((line := line + 1, world, fmls[0], rule, source, inst))

        # add bottom node
        if len(fmls) == 2 and top:
            bot = top.add_child((line := line + 1, world, fmls[1], rule, source, inst))

    def rule_nu(self, target, source, rule, fmls, args):
        """
        ν
        Branch unary with an existing signature.
        """
        used, occurring, extensions, reductions = args
        max_line = max([node.line for node in self.root.nodes() if node.line])
        line = max_line

        # choose the first signature that already occurs in this branch but has not already been used with this rule
        # sig = None
        # for i in range(1, 100):
        #     if (sig_ := tuple([s for s in source.sig]) + (i,)) in extensions and sig_ not in used:
        #         sig = sig_
        #         break
        # inst = (source.sig, sig)
        world = min([i for i in occurring if i not in used])
        new = True if world not in extensions else False
        inst = (source.world, world, new)

        # add (top) node
        top = target.add_child((line := line + 1, world, fmls[0], rule, source, inst))

        # add bottom node
        if len(fmls) == 2 and top:
            bot = top.add_child((line := line + 1, world, fmls[1], rule, source, inst))

    def rule_kappa(self, target, source, rule, fmls, args):
        """
        κ
        Branch n-ay with an arbitrary signature.
        """
        used, occurring, extensions, reductions = args
        line = max([node.line for node in self.root.nodes() if node.line])

        # choose a signature that has not already been used with this rule
        # sig = None
        # for i in range(1, 100):
        #     if (sig_ := tuple([s for s in source.sig]) + (i,)) not in used:
        #         sig = sig_
        #         break
        # inst = (source.sig, sig)
        world = min([i for i in range(1, 100) if i not in used])
        new = True if world not in extensions else False
        inst = (source.world, world, new)

        # add pseudo-node to indicate branching (the rule branches on the source rather than the leaves)
        target.add_child((None, None, None, rule, source, None))

        # add (top) node
        top = target.add_child((line := line + 1, world, fmls[0], rule, source, inst))

        # add bottom node
        if len(fmls) == 2 and top:
            bot = top.add_child((line := line + 1, world, fmls[1], rule, source, inst))

    def rule_lambda(self, target, source, rule, fmls, args):
        """
        λ
        Branch unary with an existing signature.
        """
        used, occurring, extensions, reductions = args
        max_line = max([node.line for node in self.root.nodes() if node.line])
        line = max_line

        # choose the first signature that already occurs in this branch but has not already been used with this rule
        # sig = None
        # for i in range(1, 100):
        #     if (sig_ := tuple([s for s in source.sig]) + (i,)) in extensions and sig_ not in used:
        #         sig = sig_
        #         break
        # inst = (source.sig, sig)
        usable = extensions + [i for i in range(1, 1000)][:num_mdls-1]
        world = min([i for i in usable if i not in used])
        new = True if world not in extensions else False
        inst = (source.world, world, new)

        # add (top) node
        top = target.add_child((line := line + 1, world, fmls[0], rule, source, inst))

        # add bottom node
        if len(fmls) == 2 and top:
            bot = top.add_child((line := line + 1, world, fmls[1], rule, source, inst))

    def rule_pi(self, target, source, rule, fmls, args):
        """
        π
        Branch unary with a previous signature.
        """
        used, occurring, extensions, reductions = args
        max_line = max([node.line for node in self.root.nodes() if node.line])
        line = max_line

        # reduce the signature
        # sig = tuple([s for s in source.sig[:-1]])
        # inst = (source.sig, sig)
        world = min([i for i in occurring if i in reductions])
        new = False
        inst = (source.world, world, new)

        # add (top) node
        top = target.add_child((line := line + 1, world, fmls[0], rule, source, inst))

        # add bottom node
        if len(fmls) == 2 and top:
            bot = top.add_child((line := line + 1, world, fmls[1], rule, source, inst))

    def rule_xi(self, target, source, rule, fmls, args):
        """
        ξ
        Branch binary with a new signature.
        """
        used, occurring, extensions, reductions = args
        line = max([node.line for node in self.root.nodes() if node.line])

        # find a signature that does not already occur in this branch
        # sig = None
        # for i in range(1, 100):
        #     if (sig_ := tuple([s for s in source.sig]) + (i,)) not in used:
        #         sig = sig_
        #         break
        # inst = (source.sig, sig)
        world = min([i for i in range(1, 1000) if i not in occurring])
        new = True
        inst = (source.world, world, new)

        # add left node
        left = target.add_child((line := line + 1, world, fmls[0], rule, source, inst))

        # add right node
        right = target.add_child((line := line + 1, world, fmls[1], rule, source, inst))

    def rule_chi(self, target, source, rule, fmls, args):
        """
        χ
        Branch binary with an existing signature.
        """
        used, occurring, extensions, reductions = args
        max_line = max([node.line for node in self.root.nodes() if node.line])
        line = max_line

        # choose the first signature that already occurs in this branch but has not already been used with this rule
        # sig = None
        # for i in range(1, 100):
        #     if (sig_ := tuple([s for s in source.sig]) + (i,)) in extensions and sig_ not in used:
        #         sig = sig_
        #         break
        # inst = (source.sig, sig)
        world = min([i for i in occurring if i not in used])
        new = False
        inst = (source.world, world, new)

        # add left node
        left = target.add_child((line := line + 1, world, fmls[0], rule, source, inst))

        # add right node
        right = target.add_child((line := line + 1, world, fmls[1], rule, source, inst))

    def rule_omicron(self, target, source, rule, fmls, args):
        """
        ο
        Branch unary with an existing signature and an arbitrary constant.
        """
        pass  # todo implement omicron rule

    def rule_upsilon(self, target, source, rule, fmls, args):
        """
        υ
        Branch unary with a new signature and a new constant.
        """
        pass  # todo implement upsilon rule

    def rule_omega(self, target, source, rule, fmls, args):
        """
        ω
        Branch unary with an existing signature and an existing constant.
        """
        pass  # todo implement omega rule

    def closed(self) -> bool:
        """
        A tableau is closed iff all branches are closed.

        @return True if all branches are closed, and False otherwise
        @rtype: bool
        """
        return all([isinstance(leaf.fml, Closed) for leaf in self.root.leaves() if leaf.fml])

    def open(self) -> bool:
        """
        A tableau is open iff at least one branch is open.

        @return True if at least one branch is open, and False otherwise
        @rtype: bool
        """
        return any([isinstance(leaf.fml, Open) for leaf in self.root.leaves() if leaf.fml])

    def infinite(self) -> bool:
        """
        A tableau is (probably) infinite iff at least one branch is (probably) infinite.

        @return True if all at least one branch is infinite, and False otherwise
        @rtype: bool
        """
        return any([isinstance(leaf.fml, Infinite) for leaf in self.root.leaves() if leaf.fml])

    def model(self, leaf) -> Structure:
        """
        The models for a tableau are the models associated with its open branches.
        A model for an open branch is one that satisfies all atoms in the branch.

        @return The models associated with the open branches the tableau.
        @rtype set[Structure]
        """
        def atom(fml):
            return isinstance(fml, Prop) or isinstance(fml, Atm)

        def literal(fml):
            return atom(fml) or isinstance(fml, Neg) and atom(fml.phi)

        branch = [node for node in leaf.branch if node.fml]
        name = "S" + str(len(self.models)+1)

        if self.mode["classical"]:  # classical logic

            if self.mode["modal"]:  # classical modal logic
                # sigs = list(dict.fromkeys([tuple(node.sig) for node in branch]))
                # sigs_ = list(dict.fromkeys([tuple(node.sig) for node in branch if literal(node.fml)]))
                # # use w1, ..., wn as names for worlds instead of signatures
                # worlds = {sig: "w" + str(i) for (i, sig) in enumerate(sigs)}
                # w = {worlds[sig] for sig in sigs}
                # r_ = {(sig[:-1], sig) for sig in sigs if len(sig) > 1}
                # r = {(worlds[sig1], worlds[sig2]) for (sig1, sig2) in r_}
                worlds = list(dict.fromkeys([node.world for node in branch if node.world]))
                worlds_ = list(dict.fromkeys([node.world for node in branch if node.world and
                                              literal(node.fml)]))
                w = {"w" + str(w) for w in worlds}
                r_ = list(dict.fromkeys([node.inst for node in branch
                                         if len(node.inst) > 0 and isinstance(node.inst[0], int)]))
                r = {("w" + str(tpl[0]), "w" + str(tpl[1])) for tpl in r_}

            if self.mode["propositional"]:  # classical propositional logic
                if not self.mode["modal"]:  # classical non-modal propositional logic
                    # atoms = all unnegated propositional variables
                    atoms = [node.fml.p for node in branch if atom(node.fml)]
                    # valuation = make all positive propositional variables true and all others false
                    v = {p: (True if p in atoms else False) for p in self.root.fml.propvars()}
                    model = PropStructure(name, v)

                else:  # classical modal propositional logic

                    # # atoms = all unnegated propositional variables
                    # atoms = {
                    #     sig: [node.fml.p for node in branch if isinstance(node.fml, Prop) and node.sig == sig]
                    #     for sig in sigs}
                    # # valuation = make all positive propositional variables true and all others false
                    # v = {
                    #     worlds[sig]: {p: (True if p in atoms[sig] else False) for p in self.root.fml.propvars()}
                    #     for sig in sigs_}
                    # atoms = all unnegated propositional variables
                    atoms = {
                        w: [node.fml.p for node in branch if atom(node.fml) and node.world == w]
                        for w in worlds}
                    # valuation = make all positive propositional variables true and all others false
                    v = {
                        "w" + str(w): {p: (True if p in atoms[w] else False) for p in self.root.fml.propvars()}
                        for w in worlds}
                    model = PropModalStructure(name, w, r, v)

            else:  # classical predicate logic
                # predicates = all predicates occurring in the conclusion and premises
                constants = set(chain(self.root.fml.nonlogs()[0],
                                      *[ass.fml.nonlogs()[0] for ass in [self.root] + self.premises]))
                # todo show constants in interpret.?
                funcsymbs = set(chain(self.root.fml.nonlogs()[1],
                                      *[ass.fml.nonlogs()[1] for ass in [self.root] + self.premises]))
                # todo take care of function symbols in domain and interpretation
                predicates = set(chain(self.root.fml.nonlogs()[2],
                                       *[ass.fml.nonlogs()[2] for ass in [self.root] + self.premises]))

                if not self.mode["modal"]:  # classical non-modal predicate logic
                    # atoms = all unnegated atomic predications
                    atoms = [(node.fml.pred, node.fml.terms) for node in branch if atom(node.fml)]
                    # domain = all const.s occurring in formulas
                    d = set(list(chain(*[node.fml.nonlogs()[0] for node in branch if node.fml.nonlogs()])))
                    # interpretation = make all unnegated predications true and all others false
                    i = {p: {tuple([str(t) for t in a[1]]) for a in atoms if (Pred(p), a[1]) in atoms}
                         for p in predicates}
                    model = PredStructure(name, d, i)

                else:  # classical modal predicate logic
                    # todo test
                    # atoms = all unnegated atomic predications
                    # atoms = {sig: [(node.fml.pred, node.fml.terms) for node in branch
                    #                if isinstance(node.fml, Atm) and node.sig == sig]
                    #          for sig in sigs}
                    # i = {worlds[sig]: {p: {tuple([str(t) for t in a[1]]) for a in atoms[sig]
                    #                        if (Pred(p), a[1]) in atoms[sig]}
                    #                    for p in predicates}
                    #      for sig in sigs}
                    atoms = {w: [(node.fml.pred, node.fml.terms) for node in branch
                                 if atom(node.fml) and node.world == w]
                             for w in worlds}
                    i = {"w" + str(w): {p: {tuple([str(t) for t in a[1]]) for a in atoms[w]
                                            if (Pred(p), a[1]) in atoms[w]}
                                        for p in predicates}
                         for w in worlds}

                    if not self.mode["vardomains"]:  # classical modal predicate logic with constant domains
                        d = set(chain(*[node.fml.nonlogs()[0] for node in branch]))
                        model = ConstModalStructure(name, w, r, d, i)

                    else:  # classical modal predicate logic with varying domains
                        # d = {worlds[sig]: set(chain(*[node.fml.nonlogs()[0] for node in branch
                        #                       if node.sig == sig]))
                        #      for sig in sigs}
                        d = {"w" + str(w): set(chain(*[node.fml.nonlogs()[0] for node in branch
                                                       if node.world == w]))
                             for w in worlds}
                        model = VarModalStructure(name, w, r, d, i)

        else:  # intuitionistic logic
            # sigs = [tuple(node.sig) for node in branch]
            # # use k1, ..., kn as names for states instead of signatures
            # states = {sig: "k" + str(i) for (i, sig) in enumerate(sigs)}
            # k = {states[sig] for sig in sigs}
            # r_ = {(sig[:-1], sig) for sig in sigs if len(sig) > 1}
            # r = {(states[sig1], states[sig2]) for (sig1, sig2) in r_}
            states = list(dict.fromkeys([node.world for node in branch]))
            states_ = list(dict.fromkeys([node.world for node in branch if literal(node.fml)]))
            k = {"k" + str(w) for w in worlds}
            r_ = list(dict.fromkeys([node.inst for node in branch if isinstance(node.inst[0], int)]))
            r = {("w" + str(tpl[0]), "w" + str(tpl[1])) for tpl in r_}

            if self.mode["propositional"]:  # intuitionstic propositional logic
                # # atoms = all unnegated propositional variables
                # atoms = {sig: [node.fml.p for node in branch if isinstance(node.fml, Prop) and node.sig == sig]
                #          for sig in sigs}
                # # valuation = make all positive propositional variables true and all others false
                # v = {states[sig]: {p: (True if p in atoms[sig] else False) for p in self.root.fml.propvars()}
                #      for sig in sigs}
                # atoms = all unnegated propositional variables
                atoms = {k: [node.fml.p for node in branch if atom(node.fml) and node.world == k]
                         for k in states}
                # valuation = make all positive propositional variables true and all others false
                v = {k: {p: (True if p in atoms[k] else False) for p in self.root.fml.propvars()}
                     for k in states}
                model = KripkePropStructure(name, k, r, v)

            else:  # intuitionistic predicate logic
                # predicates = all predicates occurring in the conclusion and premises
                constants = set(chain(self.root.fml.nonlogs()[0],
                                      *[ass.fml.nonlogs()[0] for ass in [self.root] + self.premises]))
                funcsymbs = set(chain(self.root.fml.nonlogs()[1],
                                      *[ass.fml.nonlogs()[1] for ass in [self.root] + self.premises]))
                predicates = set(chain(self.root.fml.nonlogs()[2],
                                       *[ass.fml.nonlogs()[2] for ass in [self.root] + self.premises]))
                # # atoms = all unnegated atomic predications
                # atoms = {sig: [(node.fml.pred, node.fml.terms) for node in branch
                #                if isinstance(node.fml, Atm) and node.sig == sig]
                #          for sig in sigs}
                # d = {states[sig]: set(chain(*[node.fml.nonlogs()[0] for node in branch
                #                               if node.sig == sig]))
                #      for sig in sigs}
                # i = {states[sig]: {p: {tuple([str(t) for t in a[1]]) for a in atoms[sig]
                #                        if (Pred(p), a[1]) in atoms[sig]}
                #                    for p in predicates}
                #      for sig in sigs}
                # atoms = all unnegated atomic predications
                atoms = {k: [(node.fml.pred, node.fml.terms) for node in branch
                             if isinstance(node.fml, Atm) and node.world == k]
                         for k in states}
                d = {"k" + str(k): set(chain(*[node.fml.nonlogs()[0] for node in branch
                                               if node.world == k]))
                     for k in states}
                i = {"k" + str(k): {p: {tuple([str(t) for t in a[1]]) for a in atoms[k]
                                        if (Pred(p), a[1]) in atoms[k]}
                                    for p in predicates}
                     for k in states}
                model = KripkePredStructure(name, k, r, d, i)

        return model


class Node(object):
    """
    A node in a tree.
    """

    def __init__(self, parent, line: int, world: int, fml: Formula, rule: str, source, inst: Tuple):
        self.line = line
        # self.sig = sig
        self.world = world
        self.fml = fml
        self.source = source
        self.rule = rule
        self.inst = inst
        self.branch = (parent.branch if parent else []) + [self]
        self.children = []

    def __str__(self):
        """
        String representation of this line.
        """
        # compute lengths of columns  # todo inefficient to recalculate for every node
        len_line = max([len(str(node.line)) for node in self.root().nodes() if node.line]) + 2
        # len_sig = max(([len(".".join([str(s) for s in node.sig])) for node in self.root().nodes() if node.sig])) + 1 \
        #     if [self.root.sig] else 0
        len_world = max([len(str(node.world)) for node in self.root().nodes() if node.world]) + 2 \
            if any([node.world for node in self.root().nodes()]) else 0
        # len_sign = 2 if self.root().sign else 0
        len_fml = max([len(str(node.fml)) for node in self.root().nodes()]) + 1
        len_rule = max([len(str(node.rule)) for node in self.root().nodes() if node.rule])
        len_source = max([len(str(node.source.line)) for node in self.root().nodes() if node.source]) \
            if [node for node in self.root().nodes() if node.source] else 0
        # compute columns
        str_line = "{:<{len}}".format(str(self.line) + "." if self.line else "", len=len_line)
        # str_sig = "{:<{len}}".format(".".join([str(s) for s in self.sig]) if self.sig else "", len=len_sig) \
        #     if len_sig else ""
        str_world = "{:<{len}}".format("w" + str(self.world) if self.world else "", len=len_world)
        # str_sign = "{:<{len}}".format(("⊩" if self.sign == "+" else "⊮") if self.sign else "", len=len_sign)
        str_fml = "{:^{len}}".format(str(self.fml), len=len_fml)
        if isinstance(self.fml, Open) or isinstance(self.fml, Infinite):
            str_cite = ""
        elif self.rule in ["A", "Ax"]:
            str_cite = "(" + self.rule + ")"
        elif not self.rule:
            str_cite = "(" + str(self.source.line) + ")"
        else:
            str_rule = "{:>{len}}".format((str(self.rule) if self.rule else ""), len=len_rule)
            str_comma = ", " if self.rule and self.source else ""
            str_source = "{:>{len}}".format(str(self.source.line) if self.source else "", len=len_source)
            if self.inst:
                if isinstance(self.inst[0], str):
                    str_inst = ", " + "[" + str(self.inst[0]) + "/" + str(self.inst[1]) + "]" \
                        + ("*" if self.inst[2] else " ")
                elif isinstance(self.inst[0], int):
                    str_inst = ", " + "⟨" + str(self.inst[0]) + "," + str(self.inst[1]) + "⟩" \
                        + ("*" if self.inst[2] else " ")
            else:
                str_inst = ""
            str_cite = "(" + str_rule + str_comma + str_source + str_inst + ")"
        # compute str
        return str_line + str_world + str_fml + str_cite

    def tex(self):
        """
        LaTeX representation of this line.
        """
        # todo
        pass

    def __repr__(self):
        """
        String representation of this line.
        """
        return str(self)

    def treestr(self, indent="", binary=False, last=True) -> str:
        """
        String representation of the tree whose root is this node.
        """
        if not self.fml:  # self is empty pseudo-node
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
                if childstr2 := self.children[-1].treestr(indent, True, True):  # last child
                    res += childstr2
        else:  # self is leaf
            res += indent + "\n"
            # res += indent + ("|  " if binary else "") + "\n"
        return res

    def nodes(self, root=True, reverse=False):
        """
        Level-order traversal:
        if not reversed: First visit the nodes on a level from left to right, then recurse through the nodes' children.
        if reversed: First visit the nodes on a level from right to left, then recurse through the nodes' children.
                     (Afterwards, the obtained list should be reversed to receive an order from bottom to top.)
        """
        res = []
        if not reverse:
            if root:
                res.append(self)
            for child in self.children:
                res.append(child)
                res += child.nodes(False, False)
        else:
            if root:
                res.append(self)
            for child in self.children[::-1]:
                res.append(child)
                res += child.nodes(False, True)
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

    def leaves(self, excludepseudo=False):
        """
        Get the leaf nodes descending from the this node.
        """
        if not excludepseudo:
            return [node for node in self.nodes() if not node.children]
        else:
            return [node for node in self.nodes() if not node.children and not node.pseudo()]

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
        # don't add children to branches that are already closed, open or declared infinite
        if self.children and (self.children[0].pseudo() or self.children[-1].pseudo()):
            return

        # add the child
        child = Node(self, *spec)
        self.children.append(child)

        if not child.pseudo():
            # check properties of new child
            child.closed()
            child.infinite()
        return child

    def rules(self, mode):
        return self.fml.tableau_pos(mode) if self.fml and self.fml.tableau_pos(mode) else dict()

    def closed(self):
        """
        Check for a contradiction with this node and i.a. add a respective label to the branch.

        @return: True iff there is a contradiction in this node or between this node and some other node on the branch
        @rtype bool
        """
        # todo sign
        if self.pseudo():
            return
        for node in self.branch:
            if self.fml and self.world == node.world and self.fml.tableau_contradiction_pos(node.fml):
                rule = str(node.line) if node != self else ""
                source = self
                self.add_child((None, None, Closed(), rule, source, None))
                return True
        return False

    def open(self):
        """
        Check if a branch is terminally open and i.a. add a respective label to the branch.
        A branch is terminally open if it has no undelayed unapplied or undelayed gamma rules.

        @return: True if the branch is not closed and there are no more rules applicable
        @rtype bool
        """
        if self.pseudo():
            return
        self.add_child((None, None, Open(), None, None, None))
        return True

    def infinite(self):
        """
        Check if a branch is potentially infinite and i.a. add a respective label to the branch.
        A branch or level is judged potentially infinite iff
        it there are more constants or worlds introduced than are symbols in the assumptions.

        @return: True if the branch is potentially infinite
        @rtype bool
        """
        if self.pseudo() or not self.fml:
            return
        # todo smarter implementation (check for loops in rule appls.)
        len_assumptions = sum([len(str(node.fml)) for node in self.branch if node.rule == "A" and not node.world])
        height = len(self.branch)
        width = len(self.branch[-2].children)
        if height > len_assumptions:
            self.add_child((None, None, Infinite(), None, None, None))
            return True
        if width > len_assumptions:
            self.branch[-2].add_child((None, None, Infinite(), None, None, None))
            return True
        # num_consts_vertical = len(dict.fromkeys(chain(*[node.fml.nonlogs()[0]
        #                                                 for node in self.branch
        #                                                 if node.fml and node.fml.nonlogs()])))
        # num_consts_horizontal = len(dict.fromkeys(chain(*[node.fml.nonlogs()[0]
        #                                                   for node in self.branch[-2].children
        #                                                   if node.fml and node.fml.nonlogs()])))
        # num_worlds_vertical = len(dict.fromkeys([node.world
        #                                          for node in self.branch if node.world]))
        # num_worlds_horizontal = len(dict.fromkeys([node.world
        #                                            for node in self.branch[-2].children if node.world]))
        # if num_consts_vertical > len_assumptions or num_worlds_vertical > len_assumptions:
        #     self.add_child((None, None, Infinite(), None, None, None))
        #     return True
        # if num_consts_horizontal > len_assumptions or num_worlds_horizontal > len_assumptions:
        #     self.branch[-2].add_child((None, None, Infinite(), None, None, None))
        #     return True
        return False

    def pseudo(self):
        """
        Check if a node is a psuedo-node.

        @return: True if the node is an.pseudo for closed, open, infinite, or an empty node
        @rtype bool
        """
        return isinstance(self.fml, Pseudo)


####################

# todo integration in main module gives class not defined errors -- circular imports?
if __name__ == "__main__":
    pass

    #############
    # Basic examples
    ############

    # fml = Biimp(Neg(Conj(Prop("p"), Prop("q"))), Disj(Neg(Prop("p")), Neg(Prop("q"))))
    # tab = Tableau(fml, propositional=True)
    #     #
    # fml = Conj(Imp(Prop("p"), Prop("q")), Prop("r"))
    # tab = Tableau(fml, validity=True, propositional=True)
    # tab = Tableau(fml, validity=False, satisfiability=True, propositional=True)
    # tab = Tableau(fml, validity=False, satisfiability=False, propositional=True)
    # 
    # fml1 = Imp(Prop("p"), Prop("q"))
    # fml2 = Imp(Prop("q"), Prop("r"))
    # fml = Imp(Prop("p"), Prop("r"))
    # tab = Tableau(fml, premises=[fml1, fml2], propositional=True)
    # 
    # fml1 = Atm(Pred("P"), (Const("a"), Const("a")))
    # fml2 = Neg(Eq(Const("a"), Const("a")))
    # tab = Tableau(premises=[fml1, fml2], validity=False)
    #     #
    # fml1 = Imp(Atm(Pred("P"), (Const("a"), Const("b"))), Atm(Pred("Q"), (Const("a"), Const("c"))))
    # fml = Atm(Pred("R"), (Const("a"), Const("a")))
    # tab = Tableau(fml, premises=[fml1])
    # 
    # fml = Conj(Exists(Var("x"), Atm(Pred("P"), (Var("x"),))), Neg(Forall(Var("x"), Atm(Pred("P"), (Var("x"),)))))
    # tab = Tableau(fml, validity=True)
    # tab = Tableau(fml, validity=False, satisfiability=True)
    # tab = Tableau(fml, validity=False, satisfiability=False)
    # 
    # fml = Biimp(Forall(Var("x"), Atm(Pred("P"), (Var("x"),))), Neg(Exists(Var("x"), Neg(Atm(Pred("P"), (Var("x"),))))))
    # tab = Tableau(fml)
    # fml1 = Exists(Var("y"), Forall(Var("x"), Atm(Pred("R"), (Var("x"), Var("y")))))
    # fml2 = Forall(Var("x"), Exists(Var("y"), Atm(Pred("R"), (Var("x"), Var("y")))))
    # tab = Tableau(fml2, premises=[fml1])
    # tab = Tableau(fml1, premises=[fml2])

    # commutativity

    # fml1 = Exists(Var("y"), Forall(Var("x"), Atm(Pred("R"), (Var("x"), Var("y")))))
    # fml2 = Forall(Var("x"), Exists(Var("y"), Atm(Pred("R"), (Var("x"), Var("y")))))
    # # tab = Tableau(fml, premises=[fml1])
    # tab = Tableau(fml1, premises=[fml2], validity=False, satisfiability=False)
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
    # tab = Tableau(fml1, premises=[fml2, fml3], validity=False, satisfiability=False)  # todo

    # # commutativity: tupper boxes
    # fml1 = Exists(Var("y"), Conj(Atm(Pred("lid"), (Var("y"),)),
    #                               Forall(Var("x"), Imp(Atm(Pred("tupperbox"), (Var("x"),)),
    #                                                    Atm(Pred("fit"), (Var("x"), Var("y")))))))
    # fml2 = Forall(Var("x"), Imp(Atm(Pred("tupperbox"), (Var("x"),)),
    #                             Exists(Var("y"), Conj(Atm(Pred("lid"), (Var("y"),)),
    #                                                   Atm(Pred("fit"), (Var("x"), Var("y")))))))
    # tab = Tableau(fml2, premises=[fml1])
    #
    # fml1 = Exists(Var("y"), Conj(Atm(Pred("lid"), (Var("y"),)),
    #                               Forall(Var("x"), Imp(Atm(Pred("tupperbox"), (Var("x"),)),
    #                                                    Atm(Pred("fit"), (Var("x"), Var("y")))))))
    # fml2 = Forall(Var("x"), Imp(Atm(Pred("tupperbox"), (Var("x"),)),
    #                             Exists(Var("y"), Conj(Atm(Pred("lid"), (Var("y"),)),
    #                                                   Atm(Pred("fit"), (Var("x"), Var("y")))))))
    # fml3 = Exists(Var("x"), Atm(Pred("tupperbox"), (Var("x"),)))
    # tab = Tableau(fml1, premises=[fml2])
    # tab = Tableau(fml1, premises=[fml2, fml3], validity=False, satisfiability=False)

    ###############
    # Modal logic
    ###############

    # fml = Biimp(Nec(Prop("p")), Neg(Poss(Neg(Prop("p")))))
    # tab = Tableau(fml, propositional=True, modal=True)
    # 
    # fml1 = Nec(Prop("p"))
    # fml = Poss(Prop("p"))
    # tab = Tableau(fml, premises=[fml1], propositional=True, modal=True)
    #     #
    # fml1 = Poss(Exists(Var("x"), Atm(Pred("P"), (Var("x"),))))
    # fml = Exists(Var("x"), Poss(Atm(Pred("P"), (Var("x"),))))
    # tab = Tableau(fml, premises=[fml1], modal=True)
    # 
    # fml = Imp(Forall(Var("x"), Nec(Atm(Pred("P"), (Var("x"),)))), Nec(Forall(Var("x"), Atm(Pred("P"), (Var("x"),)))))
    # tab = Tableau(fml, modal=True)
    #     #
    # fml = Imp(Exists(Var("x"), Nec(Atm(Pred("P"), (Var("x"),)))), Nec(Exists(Var("x"), Atm(Pred("P"), (Var("x"),)))))
    # tab = Tableau(fml, modal=True)
    #     #
    # fml = Imp(Nec(Exists(Var("x"), Atm(Pred("P"), (Var("x"),)))), Exists(Var("x"), Nec(Atm(Pred("P"), (Var("x"),)))))
    # tab = Tableau(fml, modal=True)
    # tab = Tableau(fml, modal=True, validity=False)
    # tab = Tableau(fml, modal=True, validity=False, satisfiability=False)
    #
    # fml = Exists(Var("x"), Poss(Imp(Nec(Atm(Pred("P"), (Var("x"),))), Forall(Var("x"), Atm(Pred("P"), (Var("x"),))))))
    # tab = Tableau(fml, modal=True, vardomains=True)
    # tab = Tableau(fml, validity=False, modal=True, vardomains=True)
    # tab = Tableau(fml, validity=False, satisfiability=False, modal=True, vardomains=True)
    #     #
    # fml = Imp(Exists(Var("x"), Forall(Var("y"), Nec(Atm(Pred("Q"), (Var("x"), Var("y")))))),
    #           Forall(Var("y"), Nec(Exists(Var("x"), Atm(Pred("Q"), (Var("x"), (Var("y"))))))))
    # tab = Tableau(fml, modal=True)
    # tab = Tableau(fml, modal=True, vardomains=True)
    # tab = Tableau(fml, validity=False, modal=True, vardomains=True)
    # tab = Tableau(fml, validity=False, satisfiability=False, modal=True, vardomains=True)
    #     #
    # fml = Imp(Conj(Exists(Var("x"), Poss(Atm(Pred("P"), (Var("x"),)))),
    #                Nec(Forall(Var("x"), Imp(Atm(Pred("P"), (Var("x"),)), Atm(Pred("R"), (Var("x"),)))))),
    #           Exists(Var("x"), Poss(Atm(Pred("R"), (Var("x"),)))))
    # tab = Tableau(fml, modal=True, vardomains=True)
    # tab = Tableau(fml, validity=False, satisfiability=False, modal=True, vardomains=True)
    #     #
    # fml = Biimp(Forall(Var("x"), Forall(Var("y"), Atm(Pred("P"), (Var("x"), Var("y"))))),
    #             Forall(Var("y"), Forall(Var("x"), Atm(Pred("P"), (Var("y"), Var("x"))))))
    # tab = Tableau(fml)
    #     #
    # fml = Exists(Var("x"), Exists(Var("y"), Atm(Pred("love"), (Var("x"), Var("y")))))
    # tab = Tableau(fml, validity=False)

    #####################
    # Linguistic examples
    #####################

    # fml = Exists(Var("x"), Exists(Var("y"),
    #                               Conj(Neg(Eq(Var("x"), (Var("y")))), Atm(Pred("love"), (Var("x"), Var("y"))))))
    # tab = Tableau(fml, validity=False)
    #     #
    # fml = Forall(Var("x"), Conj(Atm(Pred("student"), (Var("x"),)),
    #                             Exists(Var("y"), Conj(Atm(Pred("book"), (Var("y"),)),
    #                                                   Atm(Pred("read"), (Var("x"), Var("y")))))))
    # fml1 = Exists(Var("x"), Atm(Pred("student"), (Var("x"),)))
    # tab = Tableau(fml, premises=[fml1], validity=False)
    #     #
    # ax1 = Forall(Var("x"), Imp(Atm(Pred("student"), (Var("x"),)), Atm(Pred("human"), (Var("x"),))))
    # ax2 = Forall(Var("x"), Imp(Atm(Pred("book"), (Var("x"),)), Atm(Pred("object"), (Var("x"),))))
    # ax3 = Forall(Var("x"), Imp(Atm(Pred("human"), (Var("x"),)), Neg(Atm(Pred("object"), (Var("x"),)))))
    # ax4 = Forall(Var("x"), Imp(Atm(Pred("object"), (Var("x"),)), Neg(Atm(Pred("human"), (Var("x"),)))))
    # prem1 = Atm(Pred("student"), (Const("m"),))
    # prem2 = Atm(Pred("student"), (Const("p"),))
    # fml = Forall(Var("x"), Imp(Atm(Pred("student"), (Var("x"),)),
    #                            Exists(Var("y"), Conj(Atm(Pred("book"), (Var("y"),)),
    #                                                  Atm(Pred("read"), (Var("x"), Var("y")))))))
    # tab = Tableau(fml, premises=[prem1, prem2], axioms=[ax1, ax2, ax3, ax4], validity=False)
    # 
    # fml1 = Forall(Var("x"), Exists(Var("y"), Atm(Pred("know"), (Var("x"), Var("y")))))
    # fml2 = Neg(Exists(Var("y"), Forall(Var("x"), Atm(Pred("know"), (Var("x"), Var("y"))))))
    # tab = Tableau(None, premises=[fml1, fml2], validity=False)
    #     #
    # ax1 = Forall(Var("x"), Imp(Atm(Pred("tupperbox"), (Var("x"),)), Neg(Atm(Pred("lid"), (Var("x"),)))))
    # ax2 = Forall(Var("x"), Imp(Atm(Pred("lid"), (Var("x"),)), Neg(Atm(Pred("tupperbox"), (Var("x"),)))))
    # fml1 = Forall(Var("x"), Imp(Atm(Pred("tupperbox"), (Var("x"),)),
    #                             Exists(Var("y"), Conj(Atm(Pred("lid"), (Var("y"),)),
    #                                                   Atm(Pred("fit"), (Var("x"), Var("y")))))))
    # fml2 = Neg(Exists(Var("y"), Conj(Atm(Pred("lid"), (Var("y"),)),
    #                             Forall(Var("x"), Imp(Atm(Pred("tupperbox"), (Var("x"),)),
    #                                                    Atm(Pred("fit"), (Var("x"), Var("y"))))))))
    # fml3 = Exists(Var("x"), Atm(Pred("tupperbox"), (Var("x"),)))
    # tab = Tableau(None, premises=[fml1, fml2, fml3], axioms=[ax1, ax2], validity=False)
    #     #
    # fml = Nec(Falsum())
    # tab = Tableau(fml, propositional=True, modal=True, validity=False)
    #     #
    # fml = Conj(Poss(Prop("p")), Poss(Neg(Prop("p"))))
    # tab = Tableau(fml, propositional=True, modal=True, validity=False)
    # 
    # fml1 = Exists(Var("x"), Imp(Atm(Pred("P"), (Var("x"),)), Atm(Pred("Q"), (Var("x"),))))
    # fml = Imp(Exists(Var("x"), Atm(Pred("P"), (Var("x"),))), Exists(Var("x"), Atm(Pred("Q"), (Var("x"),))))
    # # tab = Tableau(fml, premises=[fml1])
    # # tab = Tableau(Neg(fml), premises=[fml1], validity=False)
    # fml = Imp(Forall(Var("x"), Atm(Pred("P"), (Var("x"),))), Exists(Var("x"), Atm(Pred("Q"), (Var("x"),))))
    # tab = Tableau(fml, premises=[fml1])
    # 