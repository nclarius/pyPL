A naive model checker for classical propositional and first-order logic with an extension to modal logic.  
© Natalie Clarius <natalie.clarius@student.uni-tuebingen.de>  
Licensed under CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/).

Usage notes:
------------
see `main.py`.

Disclaimer:
-----------
This implementation is intended for didactical purposes. It is not efficient or designed for real-life applications.
I am happy to learn about any bugs or improvement suggestions.

Features:
---------
 - specification of expressions in a language of PL
 - specification of expressions in a language of FOL
   - accepts languages with with zero-place predicates, function symbols, term equality and modal operators ◻, ◇
 - specification of models of FOL with domain, interpretation function and variable assignments
   - accepts models without possible worlds, modal models with constant domains and modal models with varying domains
 - evaluation of expressions (non-log. symbols, terms, open formulas, closed formulas)
   relative to models, variable assignments and possible worlds

Restrictions:
-------------
 - works only on models with finite domains and languages with a finite set of propositional or individual variables
 - can't infer universal validity, logical inference etc., only truth in a given model

Known issues:
-------------
 - name of model, domain, interpr. func., variable assignment and world is not systematically recognized,
   instead always 'M', 'D', 'I', 'v', 'w' used in printout
 - efficiency: assignment functions have to be specified on all variables of the language;
   the domain is not restricted expression-wise to those variables that actually occur in the expression
 - depth has to be reset manually after each call of denot
 - global variables are bad

Wish list:
----------
 - print out detailed derivation rather than just final result of evaluation, possibly with LaTeX mode
 - more user-friendly input:
   - expression parser instead of the cumbersome PNF specification
   - a better way of dealing with singleton tuples
   - interactive mode/API instead of need to edit source code in order to set up input
 - model generation?
