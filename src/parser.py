#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Parse a formula given as string into an Expr object.
"""

import re

debug = False


class FmlParser:
    """
    Parse a formula given as string into an Expr object.
    """

    def __init__(self):
        self.stacks = [[]]

    def parse(self, inp):
        self.stacks = [[]]
        tokens, mode = self.lex(inp)
        parsedstring = self.synt(tokens)
        return parsedstring

    def parse_(self, inp):
        self.stacks = [[]]
        tokens, mode = self.lex(inp)
        parsedstring = self.synt(tokens)
        return parsedstring, mode

    def lex(self, inp):
        """
        Lex an input string into a list of tokens.
        """
        token2regex = {
            # auxiliary symbols
            "Lbrack": r"\(",
            "Rbrack": r"\)",
            "Comma": r",",
            "Semic": r";",
            "Dsemic": r";;",
            "Period": r"\.",
            # meta symbols
            "Inf": r"(\|=||\\vDash|\\models|\\linf)",
            "Noninf": r"(\|/=||\\nvDash|\\nmodels|\\lninf)",
            # term symbols
            "Var": r"(x|y|z)(_?\d+)?",
            "Const": r"(([a-z]\w+)|(([a-e]|[i-o])(_?\d+)?))",
            "Func": r"(f|g|h)(_?\d+)?",
            # atom symbols
            "Prop": r"[p-u](_?\d+)?",
            "Eq": r"(=|\\eq)",
            "Pred": r"[A-Z]\w*",
            # connectives
            "Verum": r"(⊤|\\top|\\verum|\\ltrue)",
            "Falsum": r"(⊥|\\bot|\\falsum|\\lfalse)",
            "Neg": r"(¬|-|~|\\neg|\\lnot)",
            "Conj": r"(∧|\^|&|\\wedge|\\land)",
            "Disj": r"(∨|v|\||\\vee|\\lor)",
            "Imp": r"(→|⇒|⊃|(-|=)+>|\\rightarrow|\\Rightarrow|\\to|\\limp)",
            "Biimp": r"(↔|⇔|≡|<(-|=)+>|\\leftrightarrow|\\Leftrightarrow|\\oto|\\lbiimp)",
            "Xor": r"(⊕|⊻|\\oplus|\\lxor)",
            # quantifiers
            "Exists": r"(∃|\\exists|\\exi|\\ex)",
            "Forall": r"(∀|\\forall|\\all|\\fa)",
            "Most": r"\\most",
            "More": r"\\more",
            # modal operators
            "Poss": r"(◇|\*|\\Diamond|\\poss)",
            "Nec": r"(□|#|\\Box||\\nec)",
            "Int": r"\\int",
            "Ext": r"\\ext",
            # lambda operator
            "Abstr": r"(λ|\\lambda)"
        }
        regex2token = {v: k for k, v in token2regex.items()}

        # add whitespace around auxiliary symbols
        inp = inp.replace("(", " ( ").replace(")", " ) ").replace(",", " , ").replace(";", " ; ").replace("; ;", ";;")
        inp = re.sub("\s+", " ", inp)

        # process the input string split by whitespace
        tokens = []
        for symbol in [s for s in inp.split() if s]:
            candidates = [regex for regex in regex2token if re.compile("^" + regex + "$").match(symbol)]
            if not candidates:
                print("expression '" + symbol + "' did not match any token")
                break
            if len(candidates) > 1:
                print("expression '" + symbol + "' matched more than one token")
                break
            regex = candidates[0]
            token = regex2token[regex]
            tokens.append((token, symbol))
            if debug:
                print(token, symbol)

        # detect mode
        # todo process
        mode = dict()
        mode["classical"] = "!Int" not in [t[0] for t in tokens]
        mode["validity"] = "Noninf" not in [t[0] for t in tokens]
        mode["propositional"] = any([t[0] in ["Prop"] for t in tokens])
        mode["modal"] = any([t[0] in ["Poss", "Nec", "Int", "Ext"] for t in tokens])
        mode["vardomains"] = "!VD" in [t[0] for t in tokens]
        mode["threeval"] = False
        mode["weakval"] = True

        return tokens, mode

    def synt(self, tokens):
        """
        Parse a list of tokens into an Expr object.
        """
        # todo parse meta symbols
        # process tokens
        if not tokens:
            stacks = self.stacks
            curr_stack = stacks[-1] if stacks else None
            curr_stack.append(expr.Empty())
            self.stacks = stacks
            self.update_stacks()
        for token in tokens:
            if debug:
                input()
            self.add_symbol(token)
            self.update_stacks()
        self.update_stacks(True)
        return self.stacks[0][0]

    def add_symbol(self, token):
        t, s = token
        stacks = self.stacks
        curr_stack = stacks[-1] if stacks else None
        root_stack = stacks[0]
        top = curr_stack[-1] if curr_stack else None
        bot = curr_stack[0] if curr_stack else None
        expr = __import__("expr")
        if debug:
            print()
            print(t, s)

        # opening bracket: start new stack if begin of complex formula rather than fixed-length tuple
        if t in ["Lbrack"]:
            if bot not in ["Atm", "FuncTerm", "Most", "More"]:
                new_stack = []
                stacks.append(new_stack)
                self.stacks = stacks
                return

        # closing bracket: add closure symbol to current stack
        if t in ["Rbrack"]:
            curr_stack.append("#")
            self.stacks = stacks
            return

        # comma: continue
        if t in [","]:
            self.stacks = stacks
            return

        # flag: ignore
        if t.startswith("!"):
            self.stacks = stacks
            return

        # atomic expression: add to current stack
        if t in ["Var", "Const", "Prop"]:
            c = getattr(expr, t)
            e = c(s)
            curr_stack.append(e)
            self.stacks = stacks
            return

        # function symbol: start new stack with functerm
        if t in ["Func"]:
            c = getattr(expr, t)
            e = c(s)
            stack_ = ["FuncTerm", e]
            stacks.append(stack_)
            self.stacks = stacks
            return

        # predicate symbol: start new stack with atm
        if t in ["Pred"]:
            c = getattr(expr, t)
            e = c(s)
            stack_ = ["Atm", e]
            stacks.append(stack_)
            self.stacks = stacks
            return

        # atomic formula: add to current stack
        if t in ["Verum", "Falsum"]:
            c = getattr(expr, t)
            e = c()
            curr_stack.append(e)
            self.stacks = stacks
            return

        # prefix operator: start new stack
        if t in ["Verum", "Falsum", "Neg", "Exists", "Forall", "Most", "More", "Poss", "Nec", "Int", "Ext", "Abstr"]:
            stack_ = [t]
            stacks.append(stack_)

        # infix operator: prepend to current stack
        if t in ["Eq", "Conj", "Disj", "Imp", "Biimp", "Xor"]:
            curr_stack.insert(0, t)
            return self.stacks

    def update_stacks(self, final=False):
        # todo check well-formedness of expressions
        # todo lambda application
        # operator precedence
        prec = {"Eq": 1, "Abstr": 1, "Nec": 1, "Poss": 1, "Int": 1, "Ext": 1,
                "More": 1, "Most": 1, "Exists": 1, "Forall": 1,
                "Neg": 1, "Conj": 2, "Disj": 3, "Imp": 4, "Biimp": 5, "Xor": 6}

        stacks = self.stacks
        expr = __import__("expr")
        if debug:
            print("stacks before: ", stacks)

        for i, stack in enumerate(stacks[::-1]):
            i = len(stacks) - 1
            curr_stack = stack
            if not stack:  # skip empty stacks
                continue

            if len(stacks) == 1:
                if len(stack) == 1:  # stacks are finished; return
                    break
                else:  # outer brackets ommmited; move content to new stack
                    new_stack = [e for e in stack]
                    stacks.append(new_stack)
                    stacks[i] = []
                    i += 1
                    curr_stack = stacks[i]

            prev_stack = stacks[i - 1]
            bot = curr_stack[0]
            mid = curr_stack[1] if len(curr_stack) > 1 else None
            top = curr_stack[-1]

            # function, predicate or gen. quant. expression: close if closure symbol is on top
            if bot in ["Atm", "FuncTerm"] and top == "#":
                o = curr_stack[1]
                c = getattr(expr, bot)
                e = c(o, curr_stack[2:-1])
                prev_stack.append(e)
                stacks = stacks[:-1]
                continue
            elif bot in ["Most", "More"] and top == "#":
                o = curr_stack[1]
                c = getattr(expr, bot)
                e = c(o, *curr_stack[2:-1])
                prev_stack.append(e)
                stacks = stacks[:-1]
                continue
            # # lambda application: close if lower stack is lambda operator
            # # todo doesn't work
            # if isinstance(prev_stack[0], getattr(expr, "Abstr")):
            #     c = getattr(expr, "Appl")
            #     e = c(prev_stack[0], curr_stack[0])
            #     prev_stack.append(e)
            #     stacks = stacks[:-1]
            #     continue

            # unary operator: close if appropriate number of args is given
            if bot in ["Neg", "Poss", "Nec", "Int", "Ext"] and len(curr_stack) == 2:
                c = getattr(expr, bot)
                e = c(top)
                prev_stack.append(e)
                stacks = stacks[:-1]
                continue

            # binary operator: close if closure symbol is on top, else resolve ambiguity
            # todo doesn't work correctly, e.g. "(p -> q v r) ^ s" = "p -> ((q v r) ^ s)" instead of "(p -> q v r) ^ s"
            if bot in ["Eq", "Conj", "Disj", "Imp", "Biimp", "Xor"]:

                # operator ambiguity
                # operator clash: resolve ambigutiy
                if mid and mid in ["Conj", "Disj", "Imp", "Biimp", "Xor", "Exists", "Forall", "Most", "More",
                                   "Neg", "Poss", "Nec", "Int", "Ext", "Abstr", "Eq"]:
                    # first op has precedence over second op: take current stack as subformula. to second op
                    if prec[mid] < prec[bot]:
                        c = getattr(expr, mid)
                        e = c(*curr_stack[2:])
                        curr_stack = [bot, e]
                        stacks[i] = curr_stack
                    # second op has precedence over first op: move to new stack
                    # ops have equal precedence: apply right-associativity
                    else:
                        new_stack = [bot, curr_stack[3]]
                        stacks.append(new_stack)
                        curr_stack = [mid, curr_stack[2]]
                        stacks[i] = curr_stack

                # subformula finished
                elif len(curr_stack) == 4 and top == "#" or final:
                    c = getattr(expr, bot)
                    e = c(curr_stack[1], curr_stack[2])
                    prev_stack.append(e)
                    stacks = stacks[:-1]
                    continue

            # variable binding operator: close if appropriate number of args is given
            if bot in ["Exists", "Forall", "Abstr"] and len(curr_stack) == 3:
                c = getattr(expr, bot)
                e = c(mid, top)
                prev_stack.append(e)
                stacks = stacks[:-1]
                continue

        self.stacks = stacks
        if debug:
            print("stacks after: ", stacks)


class StructParser:
    """
    Parse a structure specification given as string into a Structure object.
    """
    def __init__(self):
        pass

    def parse(self, inp):
        # remove redundant whitespace
        inp = re.sub("\s+", " ", inp)
        # stringify content[p-u](_?\d+)
        inp = re.sub("([\w]+)", "'\\1'", inp)
        # turn functions into dicts
        inp = inp.replace("[", "{")
        inp = inp.replace("]", "}")
        # turn singleton tuples into tuples
        inp = re.sub("\('(\w+)'\)", "('\\1',)", inp)
        # turn empty sets into sets
        inp = inp.replace("{}", "set()")
        # turn intension sets into frozen sets so that they can be hashed
        inp = re.sub("(\{\('w.*?\})", "frozenset(\\1)", inp)
        # turn truth value strings into truth values
        inp = inp.replace("'True'", "True").replace("'False'", "False")
        # split lines into components
        inp = inp.replace("\n", "")
        inp = re.sub("('[A-Z]' = )", "\n\\1", inp)

        s = {eval(comp.split(" = ")[0]): eval(comp.split(" = ")[1]) for comp in inp.split("\n") if comp.strip()}
        s["S"] = "S"
        modal = "W" in s or "K" in s
        propositional = "D" not in s
        intuitionistic = "K" in s
        vardomains = "D" in s and isinstance(s["D"], dict)
        if not propositional and "V" not in s:
            s["V"] = {}

        structure = __import__("structure")
        if not intuitionistic:
            if not modal:
                if propositional:
                    return structure.PropStructure(s["S"], s["V"])
                else:
                    return structure.PredStructure(s["S"], s["D"], s["I"], s["V"])
            else:
                if propositional:
                    return structure.PropModalStructure(s["S"], s["W"], s["R"], s["V"])
                else:
                    if not vardomains:
                        return structure.ConstModalStructure(s["S"], s["W"], s["R"], s["D"], s["I"], s["V"])
                    else:
                        return structure.VarModalStructure(s["S"], s["W"], s["R"], s["D"], s["I"], s["V"])
        else:
            if propositional:
                return structure.KripkePropStructure(s["S"], s["K"], s["R"], s["V"])
            else:
                return structure.KripkePredStructure(s["S"], s["K"], s["R"], s["D"], s["I"], s["V"])

if __name__ == "__main__":
    parse_f = FmlParser().parse
    parse_s = StructParser.parse
