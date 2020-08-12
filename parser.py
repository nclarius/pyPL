#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Parse a formula given as string into an Expr object.
CURRENTLY UNDER CONSTRUCTION.
"""

from expr import *
import re

def lex(inp):
    """
    Lex an input string into a list of tokens.
    """
    token2regex = {
        # auxiliary symbols
        "Lbrack": r"\(",
        "Rbrack": r"\)",
        "Comma":  r",",
        "Semic":  r";",
        "Dsemic": r";;",
        # meta symbols
        "Inf":    r"(\|=||\\vDash|\\models|\\linf)",
        "Noninf": r"(\|/=||\\nvDash|\\nmodels|\\lninf)",
        # term symbols
        "Var":    r"(x|y|z)(_?\d+)?",
        "Const":  r"([a-o](_?\d+)?)",
        "Func":   r"(f|g|h)(_?\d+)?",
        "Pred":   r"[A-Z]\w*",
        # atom symbols
        "Prop":   r"[p-u](_?\d+)?",
        "Eq":     r"(=|\\eq)",
        # connectives
        "Verum":  r"(⊤|\\top|\\ltrue)",
        "Falsum": r"(⊥|\\bot|\\lfalse)",
        "Neg":    r"(¬|-|~|\\neg|\\lnot)",
        "Conj":   r"(∧|\^|&|\\wedge|\\land)",
        "Disj":   r"(∨|v|\||\\vee|\\lnot)",
        "Imp":    r"(→|⇒|⊃|(-|=)+>|\\rightarrow|\\Rightarrow|\\to|\\limp)",
        "Biimp":  r"(↔|⇔|≡|<(-|=)+>|\\leftrightarrow|\\Leftrightarrow|\\oto|\\lbiimp)",
        "Xor":    r"(⊕|⊻|\\oplus|\\lxor)",
        # quantifiers
        "Exists": r"(∃|\\exists|\\exi|\\ex)",
        "Forall": r"(∀|\\forall|\\all|\\fa)",
        # modal operators
        "Poss":   r"(◇|\\Diamond|\\poss)",
        "Nec":    r"(◻|\\Box||\\nec)"
    }
    regex2token = {v: k for k, v in token2regex.items()}

    # preprocces the input string
    inp = re.sub("([^\s])(\(|\)|,|;)", r"\1 \2", inp)  # insert whitespace left to aux. symbols
    inp = re.sub("(\(|\)|,|;)([^\s;])", r"\1 \2", inp)  # insert whitespace right to aux. symbols
    inp = re.sub(";\s;", ";;", inp)  # restore split up double semicolons
    inp = re.sub("\s+", " ", inp)  # remove redundant whitespace

    # process the input string split by whitespace
    tokens = []
    for symbol in inp.split(" "):
        found = 0
        # find a matching regex and append the respective token
        for regex in regex2token:
            pattern = re.compile("^" + regex + "$")
            if pattern.match(symbol):
                found += 1
                token = regex2token[regex]
                tokens.append((token, symbol))
        if found < 1:
            print(symbol, "no matches found")
        elif found > 1:
            print(symbol, "multiple matches found")

    # detect mode
    # todo process
    mode = dict()
    mode["validity"] = True if "noninf" not in [t[0] for t in tokens] else False
    mode["propositional"] = True if any([t[0] in ["prop"] for t in tokens]) else False
    mode["modal"] = True if any([t[0] in ["poss", "nec"] for t in tokens]) else False

    return tokens, mode

def parse(tokens):
    """
    Parse a list of tokens into an Expr object.
    """
    # todo parse meta symbols

    def add_symbol(stacks, t, s):
        print(t, s)
        if stacks:
            stack = stacks[-1]

        # opening bracket: start new stack
        if t in ["Lbrack"]:
            stack_ = []
            stacks.append(stack_)
            return stacks

        # closing bracket: add closure symbol to current stack
        if t in ["Rbrack"]:
            stack.append("#")
            return stacks

        # comma: continue
        if t in [","]:
            return stacks

        # atomic expression: add to current stack
        if t in ["Var", "Const", "Prop"]:
            c = getattr(expr, t)
            e = c(s)
            stack.append(e)
            return stacks

        # function symbol: start new stack with functerm
        if t in ["Func"]:
            c = getattr(expr, t)
            e = c(s)
            stack_ = ["Functerm", e]
            stacks.append(stack_)
            return stacks

        # predicate symbol: start new stack with atm
        if t in ["Pred"]:
            c = getattr(expr, t)
            e = c(s)
            stack_ = ["Atm", e]
            stacks.append(stack_)
            return stacks

        # prefix operator: start new stack
        if t in ["Verum", "Falsum", "Neg", "Exists", "Forall", "Poss", "Nec"]:
            c = getattr(expr, t)
            e = c(s)
            stack_ = [e]
            stacks.append(stack_)

        # infix operator: prepend to current stack
        if t in ["Eq", "Conj", "Disj", "Imp", "Biimp", "Xor"]:
            stack.insert(0, t)
            return stacks

    def check_stacks(stacks):
        print(stacks)
        if stacks:
            stack = stacks[-1]
        if not stacks or not stack:   # skip newly created, empty stacks
            return
        bot = stack[0]   # bottommost symbol
        top = stack[-1]  # topmost symbol

        # add the current symbol to the previous stack and remove the current stack
        def close(stacks, e):
            stack_ = stacks[-2]
            stack_.append(e)
            stacks = stacks[:-1]
            return stacks

        # function or predicate term: close if closure symbol is on top
        if bot in ["Functerm", "Atm"] and top == "#":
            o = stack[1]
            c = getattr(expr, bot)
            e = c(o, *stack[2:-1])
            return close(stacks, e)

        # operator: close if appropriate number of args is given

        # nullary operator
        if bot in ["Verum", "Falsum"] and len(stack) == 1:
            c = getattr(expr, bot)
            e = c()
            return close(stacks, e)

        # unary operator
        if bot in ["Neg", "Poss", "Nec"] and len(stack) == 2:
            c = getattr(expr, bot)
            e = c(stack[1])
            return close(stacks, e)

        # binary operator
        if bot in ["Eq", "Conj", "Disj", "Imp", "Biimp", "Xor", "Exists", "Forall"] and len(stack) == 3:
            c = getattr(expr, bot)
            e = c(stack[1], stack[2])
            return close(stacks, e)

    stacks = []  # initial stack
    # process tokens
    for t, s in tokens:
        stacks_ = add_symbol(stacks, s, t)
        stacks = check_stacks(stacks_)
    return stacks[0][0]

if __name__ == "__main__":
    expr = r"(\exi x P(x) ^ \forall x (P(x) \to Q(x)))"
    tokens = lex(expr)[0]
    tree = parse(tokens)
    print(tree)
