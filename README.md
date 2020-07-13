A naive model checker and -generator with analytic tableaux for classical non-modal and modal propositional and first-order logic and intuitionistic non-modal propositional and first-order logic.  
This tool can compute the denotation (truth value) of a given logical expression in a given structure, and an analytic tableau with associated (counter) models for a given inference.   
**Intuitionistic logic, tableau computation and model generation currently under construction.**  
© Natalie Clarius <natalie.clarius@student.uni-tuebingen.de>  
License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/). 

Disclaimer
----------
- This implementation is intended for didactical purposes. It is not efficient or designed for real-life applications.  
- Although the program has been extensively tested, I do not guarantee soundness. Use at your own risk.

I am happy to learn about any bugs or improvement suggestions.

Features
--------
 - evaluation of expressions (non-log. symbols, terms, open formulas, closed formulas)
   relative to structures, variable assignments and possible worlds
 - specification of expressions
    - in a language of propositional logic (aka statement logic)
    - in a language of first-order logic (aka predicate logic, quantifier logic)
    - accepts languages with with zero-place predicates, function symbols, term equality and modal operators ◻, ◇
 - specification of structures (aka models, interpretations)
    - of classical logic
        - of PL with valuation function
        - of FOL with domain, interpretation function and variable assignments
        - accepts non-modal structures, modal structures with constant domains and modal structures with varying domains
    - of intuitionistic logic (Kripke structures with sets of states)  -- currently under construction
        - of PL with valuation function
        - of FOL with domain, interpretation function and variable assignments
 - analytic tableau proofs -- currently under construction
 - model generation -- currently under construction

Restrictions
------------
 - works only on structures with finite domains and languages with a finite set of propositional or individual variables
 - search strategy for tableaus is sometimes inefficient
 - no modal logic available for intuitionistic logic

Known issues
------------
 - global variables are bad
 - depth has to be reset manually after each call of `denot`
 - efficiency: assignment functions have to be specified on all variables of the language;
   the domain is not restricted expression-wise to those variables that actually occur in the expression

Wish list
---------
 - print out detailed derivation rather than just final result of evaluation, possibly with LaTeX mode
 - more user-friendly input:
   - expression parser instead of the cumbersome prefix notation
   - interactive mode/API instead of need to edit source code in order to set up input
 - model generation?

Usage notes
-----------

(Usage instructions currently only apply to the model checking feature, as the tableau and model generation program is still under construction.)  

### Try it out
**You can try this tool out [here](https://trinket.io/python3/757871dd18).**  
If you want to dive in deeper, I recommend downloading pyPL to your own computer.

### Installation and execution
To run this tool locally on your machine:
1. Clone this repository.
2. *Optional:* To specify custom input (see next subsection), edit the file `main.py` in a text editor of your choice.
3. Execute `main.py` in a terminal.

Running this program requires Python (version >= 3.8) to be installed on your machine.  
How to 'install python', 'edit .py file', 'execute .py script in terminal' and 'clone github repository'
is all easily googleable for your respective operating system.

### Specifying input
**This tool is not equipped with an interactive user interface; input has to be specified in the source code.**  
A number of examples are already set up; this is the stuff you see when running the program.  
To specify your own input:  
- Structures and formulas to compute denotations for are defined in the function `compute_denot` in `main.py`.  
  Formulas, unfortunately, have to be entered in prefix notation.  
  Follow the existing examples and the documentations of the classes and methods to get an idea.  
- You can select which structures to include in the output by editing the variable `active` (near top of source code).
- You can select whether or not to print out intermediate steps by editing the variable `verbose` (same place).

After specifying your input in the source code, execute `main.py` in a terminal to view the output.

### If you would like to understand what's going on under the hood
- `main.py` is the main module in which input is specified and from which the computations are run.  
  `expr.py` defines the language and semantics, and `structure.py` the form of structures, of the logics.
  `tableau.py` computes tableau proofs and extracts models from them.
- The interesting part for you are the `denot` (denotation) methods in each of the expression classes in `expr.py`.  
  Compare how the formal definitions can be translated into code almost 1:1,
  and try to follow why the implementation works the way it does, especially the loop logic for the quantifiers 
  (classes `Exists` and `Forall` in `expr.py`).  
- To follow an evaluation process, I recommend to
  - set breakpoints at each of the `denot` method instances and step through an evaluation process symbol by symbol
    to see how a denotation is computed recursively in line with the inductive definitions.
  - trace (watch or simply print) the variables `v` and `v_` in the `denot` methods 
    to keep track of what the current variable assignment looks like during quantifier evaluation.  
- The `__str__` methods are what makes the expressions formatted human-readable in the output.  
- Simply ignore all the print statements and anything that looks completely unfamiliar to you (such as `w`/modal stuff).  

### Notes on notation
- 'M' = structure/model (aka 'A')
- 'D' = domain of discourse (aka 'M')
- 'I' = interpretation function for non-logical symbols (aka 'F')
- 'g' = variable assignment function for individual variables (aka 'v')
- 'V' = valuation function for propositional variables

### Have fun!