A naive model generator, model checker and theorem prover   
for some combinations of classical and intuitionistic, non-modal and modal, propositional and first-order logic.  

This tool can compute  
- the denotation (truth value) of a given logical expression in a given structure,  
- an analytic tableau with associated (counter) models for a given inference or set of formulas.   

![pyPL GUI -- start](doc/img/pyPL_1_MG.png)
![pyPL GUI -- input](doc/img/pyPL_2_MG.png)
![pyPL GUI -- output](doc/img/pyPL_5_MG.png)

© Natalie Clarius <natalie.clarius@student.uni-tuebingen.de>  
License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/).

Disclaimer
----------
- This implementation is intended for didactical purposes. It is not efficient or designed for real-life applications.  
- Although the program has been extensively tested, I do not guarantee soundness. Use at your own risk.

I am happy to learn about any bugs or improvement suggestions.

Features
--------

```
 |                 classical                 |               intutionistic               |
 |    propositional    |    predicational    |    propositional    |    predicational    |
 | non-modal |  modal  | non-modal |  modal  | non-modal |  modal  | non-modal |  modal  |  
 |           |         |           | CD | VD |           |         |           | CD | VD |
 | TT | MC |  MG  | MC | MG | MC |  MG  | MC | MG | MC |  MG  | MC | MG | MC |  MG  | MC | MG |
 |-------------------------------------------|-------------------------------------------|
 | 🗸  | 🗸  |  🗸  |  🗸 | 🗸  | 🗸  |  🗸  | 🗸  | 🗸  |  🗸 |  ✗  |  ✗ | ✗  |  🗸 |  ✗   | ✗  | ✗  |
TT = truth table generation, MC = model checking, MG = model generation + tableau calculus;
CD = with constant domains, VD = with varying domains;  
modal MG only for K frames.
```
 - accepts languages
   - of propositional logic
   - of first-order logic with zero-place predicates, function symbols and term equality
   - with modal operators ◻, ◇, ^, ⱽ 
 - specification of structures (aka models, interpretations)
    - of classical logic
        - of PL with valuation function
          - with and without possible worlds
        - of FOL with domain, interpretation function and variable assignments
          - without possible worlds, with possible worlds with constant domains and possible worlds with varying domains
    - of intuitionistic logic (Kripke structures with sets of states)
        - of PL with valuation function
        - of FOL with domain, interpretation function and variable assignments
 - model checking: evaluation of expressions (non-log. symbols, terms, open formulas, closed formulas)
   relative to structures, variable assignments and possible worlds
 - analytic tableau proofs -- currently under construction
 - model generation -- currently under construction
 - output in plain text or LaTeX-generated PDF format

Restrictions
------------
 - works only on structures with finite domains and languages with a finite set of propositional or individual variables
 - no model generation and modal logic available for intuitionistic logic

Known issues
------------
 - global variables are bad
 - search strategy for tableaus is sometimes inefficient
 - tableaus and model generation for non-K frames not working properly

Wish list
---------
 - more user-friendly input and output:
   - expression parser instead of the cumbersome prefix notation
   - interactive mode/file input instead of need to edit source code in order to set up input
   - GUI
- in model checking, print out detailed derivation rather than just final result of evaluation
- broader coverage:
  - tableaus with free variables
  - more frames for modal logic
  - model generation for intuitionistic logic
  - modal logic for intuitionistic logic

Usage notes
-----------

### Try it out
**You can try the model checking feature of this tool out [here](https://trinket.io/python3/757871dd18).**  
If you want to dive in deeper, I recommend downloading pyPL to your own computer.

### Installation and execution
To run this tool locally on your machine:
1. Install dependencies: `Python` (version >= 3.9), `tkinter`, `pdflatex` (if you want nicely formatted output).
2. Clone this repository.
3. Execute `gui.py`.

How to 'clone github repository', 'install python', 'edit .py file' and 'execute .py script' is all easily googleable for your respective operating system.

### Specifying input
Documentation on how to enter formulas, structures and input files can be found in `doc/Parser.md`.

### Have fun!
