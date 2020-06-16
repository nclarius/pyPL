A naive model checker for classical propositional and first-order logic with an extension to modal logic.  
© Natalie Clarius <natalie.clarius@student.uni-tuebingen.de>  
Licensed under CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/).  

Disclaimer
----------
This implementation is intended for didactical purposes. It is not efficient or designed for real-life applications.  
I am happy to learn about any bugs or improvement suggestions.

Features
--------
 - specification of expressions in a language of PL
 - specification of expressions in a language of FOL
   - accepts languages with with zero-place predicates, function symbols, term equality and modal operators ◻, ◇
 - specification of models of FOL with domain, interpretation function and variable assignments
   - accepts models without possible worlds, modal models with constant domains and modal models with varying domains
 - evaluation of expressions (non-log. symbols, terms, open formulas, closed formulas)
   relative to models, variable assignments and possible worlds

Restrictions
------------
 - works only on models with finite domains and languages with a finite set of propositional or individual variables
 - can't infer universal validity, logical inference etc., only truth in a given model

Known issues
------------
 - name of model, domain, interpr. func., variable assignment and world is not systematically recognized,
   instead always 'M', 'D', 'I', 'v', 'w' used in printout
 - efficiency: assignment functions have to be specified on all variables of the language;
   the domain is not restricted expression-wise to those variables that actually occur in the expression
 - depth has to be reset manually after each call of `denot`
 - global variables are bad

Wish list
---------
 - print out detailed derivation rather than just final result of evaluation, possibly with LaTeX mode
 - more user-friendly input:
   - expression parser instead of the cumbersome PNF specification
   - a better way of dealing with singleton tuples
   - interactive mode/API instead of need to edit source code in order to set up input
 - model generation?

Usage notes
-----------

### Installation
To run this tool on your machine:
1. Clone this repository.
3. If you want, edit the file `CPL/main.py` in a text editor of your choice to specify custom input (see next section).
4. Execute `CPL/main.py`.

Running this program requires Python (version >= 3.8) to be installed on your machine.  
How to 'install python', 'edit .py file', 'execute .py script' and 'clone github repository'
is all easily googleable for your respective operating system.

### Defining input
**This tool is not equipped with an interactive user interface; input has to be specified in the source code.**  
A number of examples are already set up.
- Models and formulas to compute denotations for are **defined in the function `compute` in `main.py`.**
  Formulas, unfortunately, have to be entered in prenex form.
  Follow the existing examples and the documentations of the classes and methods to get an idea.
- You can select which models to include in the output by editing the variable `active` (near top of source code).
- You can select whether or not to print out intermediate steps by editing the variable `verbose` (same place).
After specifying your input in the source code, **execute `main.py` in a terminal to view the output.**  

### If you would like to understand what's going on under the hood
- The directory `CPL` contains the program files for classical logic, `IPL` the ones for intuitionistic logic.  
  The structure in these two versions is the same:
  `main.py` is the main module in which input is specified and from which the computations are run.  
  `expr.py` defines the language, and `model.py` the models, of the logic.
- The interesting part for you are the `denot` methods in each of the expression classes in `expr.py`.  
  Compare how the formal definitions can be translated into code almost 1:1,
  and try to follow why the implementation works the way it does, especially the loop logic for the quantifiers.  
- A recommendation is to set breakpoints and step through an evaluation process symbol by symbol
  to see how a denotation is computed recursively in line with the inductive definitions,
  or trace the variables `v` and `v_` to keep track of what the current variable assignment looks like during 
  quantifier evaluation.  
- The `__str__` methods are what makes the expressions formatted human-readable in the output.  
- Simply ignore all the print statements and anything that looks completely unfamiliar to you (such as `w`/modal stuff).  

### Notes on notation
- 'M' = model/structure (aka 'A')
- 'D' = domain of discourse (aka 'M')
- 'I' = interpretation function for non-logical symbols (aka 'F')
- 'v' = variable assignment function for individual variables (aka 'g')
- 'V' = valuation function for propositional variables

Have fun!