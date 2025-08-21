#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Parse a formula given as string into an Expr object.
"""

import re

debug = False


class ExprParser:
    """
    Parse a formula given as string into an Expr object.
    """

    def __init__(self):
        self.stack_out = []
        self.stack_oper = []

    def parse(self, inp):
        outp = ""
        tokens, mode = self.tokenize(inp)
        expr = __import__("expr")

        def eval_expr(token):
            return getattr(expr, token[0])(token[1])

        def push_oper(token):
            stack_oper.append(eval_expr(token))
        
        def push_iden(token):
            stack_out.append(eval_expr(token))

        for token in tokens:
            match token:
                case "Lbrack":  # left bracket
                    pass
                case "Rbrack":  # right bracket
                    pass
                case "Comma" | "Semic" | "Dsemic" | "Period":  # auxiliary symbols
                    pass
                case "Inf" | "Noninf":  # meta symbols
                    pass
                case "Prop":  # atom symbols
                    pass
                case "Var" | "Const":  # term symbols
                    push_iden(token)
                case "Func":  # term symbols
                    push_oper(token)
                case "Pred":  # atom symbols
                    push_oper(token)
                case "Eq":  # binary opertors
                    pass
                case "Verum" | "Falsum":  # nullary connectives
                    pass
                case "Neg":  # unary conectives
                    pass
                case "Conj" | "Disj" | "Imp" | "Biimp" | "Xor":  # binary connectives
                    pass
                case "Exists" | "Forall":  # unary quantifiers
                    pass
                case "Most":  # binary quantifiers
                    pass
                case "More":  # ternary quantifiers
                    pass
                case "Poss" | "Nec" | "Int" | "Ext":  # unary modal operators
                    pass
                case "Abstr":  # lambda operator
                    pass
                case _:
                    raise Exception("Token not recognized")

        return outp

    def parse_(self, inp):
        tokens, mode = self.tokenize(inp)
        expr = self.parse(tokens)
        return expr, mode

    def tokenize(self, inp):
        """
        Split an input string into a list of tokens.
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
            "Var": r"(x|y|z|u)(_?\d+)?",
            "Const": r"(([a-z][a-z]+)|(([a-e]|[i-o])(_?\d+)?))",
            "Func": r"(f|g|h)(_?\d+)?",
            # atom symbols
            "Prop": r"[p-t](_?\d+)?",
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
                    return structure.PredStructure(s["S"], s["D"], s["I"])
            else:
                if propositional:
                    return structure.PropModalStructure(s["S"], s["W"], s["R"], s["V"])
                else:
                    if not vardomains:
                        return structure.ConstModalStructure(s["S"], s["W"], s["R"], s["D"], s["I"])
                    else:
                        return structure.VarModalStructure(s["S"], s["W"], s["R"], s["D"], s["I"])
        else:
            if propositional:
                return structure.KripkePropStructure(s["S"], s["K"], s["R"], s["V"])
            else:
                return structure.KripkePredStructure(s["S"], s["K"], s["R"], s["D"], s["I"])

if __name__ == "__main__":
    parse_e = ExprParser.parse
    parse_s = StructParser.parse
