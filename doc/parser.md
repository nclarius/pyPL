Here is how to enter formulas, structures and input files.

# Entering formulas

## Auxiliary symbols

- All symbols except parentheses and commas must be separated by whitespace.  
 Example: `- (p ^ q)`; not: `-(p^q)`.
- All formulas use round brackets.  
  Example: `\exi x (P(x) ^ Q(x))`; not: `\exi x [P(x) ^ Q(x)]`.
- Terms inside function expressions and atomic predications are enclosed by brackets and separated by commas.  
  Example: `P(a,b)`; not: `Pab`.
- Bracketing conventions:

  - Binary connectives go with outer brackets, unary operators do not.
     Example: `(p ∧ (q → r))`,  `(p → ¬q)`, `∃x(P(x) ∧ Q(x))`; not: `(p → (¬q))`, `(∃x(P(x) ∧ Q(x)))`.
  - Outer brackets may be omitted.  
  Example: `p ∧ q` = `(p ∧ q)`.
  - Occurrences of the same operator are left-associative.  
   Example: `p ∧ q ∧ r` = `((p ∧ q) ∧ r)`.
  - Operator precedence: `∃`,`∀`, `¬` > `∧` > `∨` > `→` > `↔` > `⊕`.  
    Example:  `¬ p ∨ q ∧ r` = `((¬p) ∨ (q ∧ r))`, `∃x P(x) ∧ Q(x)` = `(∃x P(x)) ∧ Q(x)` (brackets around `¬` and `∃` only for clarity here).

## Term symbols

### Individual variables

Lowercase letters `x` - `z`, optionally followed by a number, optionally separated by an underscore.  
Examples: `x`, `y`, `z5`, `x_23`.

### Individual constants
Lowercase letters `a` - `e` and `i` - `o`, optionally followed by a number, optionally separated by an underscore; <br/>or: a sequence of letters, numbers and underscore, with the first symbol a lowercase letter.      
Examples: `a`, `m`, `c12`, `peter`; not: `p` , `Mary`.

### Functions

Lowercase letters `f` - `h`, optionally followed by a number, optionally separated by an underscore.  
Examples: `f`, `g2`.

## Atomic symbols

### Propositional variables
Lowercase letters `p` - `u`, optionally followed by a number, optionally separated by an underscore.  
Examples: `p`, `q`, `p_1`, `u_23`.

### Predicates
A sequence of letters, numbers and underscore, with the first symbol an uppercase letter.  
Examples: `P`, `Loves`, `P_123`; not: `p`, `loves`.

### Term equality
`=`, `\eq`.

## Connectives

### Verum
`⊤`, `\top`, `\verum`, `\ltrue`

### Falsum
`⊥`, `\bot`, `\falsum`, `\lfalse`

### Negation
`¬`, `-`, `~`, `\neg`, `\lnot`

### Conjunction
`∧`, `^`, `&`, `\wedge`, `\land`

### Disjunction
`∨`, `v`, `|`, `\vee`, `\lor`  

### Implication
`→`, `⇒`, `⊃`, `->`, `=>`, `\rightarrow`, `\Rightarrow`, `\to`, `\limp`

### Biimplication
`↔`, `⇔`, `≡`, `<->`, `<=>`, `\leftrightarrow`, `\Leftrightarrow`, `\oto`, `\lbiimp`

### Exclusive disjunction
`⊕`, `⊻`, `\oplus`, `\lxor`


## Quantifiers

### There exists
`∃`, `\exists`, `\exi`, `\ex`

### For all
`∀`, `\forall`, `\all`, `\fa`

### Most
`\most`  
Example: `\most x(Child(x), Sleep(x))`.

### More than
`\more`  
Example: `\more x(Boy(x), Girl(x), Sleep(x))`.


## Intensional operators

### Possibility
`◇`, `*`, `\Diamond`, `\poss`

### Necessity
`◻`, `#`, `\Box`, `\nec`

### Intension
`\int`

### Extension
`\ext`

## Formulas
Examples:

`p ^ q -> (- r v p)`  
`P(a)`  
`\all x (Woman(x) -> \exi y (- (x = y) ^ Man(y) ^ Love(x,y)))`  
`# p -> \falsum`  
`Believe(john, \int Bald(theking))`  


# Entering structures

- A structure is specified by listing its components, with components separated by linebreaks (without commas), and the component name and its specification separated by ` = `.
- Whitespace and linebreaks within component specificaions are ignored.

Component names:

- `V`: valuation function for propositional logics
- `D`: domain of discourse for predicate logics
- `I`: interpretation function for predicate logics
- `W`: set of possible worlds for modal logics
- `K`: set of states for intensional logics (instead of W)
- `R`: accessibility relation for modal and intensional logics
- `V`: set of designated assignment functions for predicate logics (optional)

Component specifications:
- Names (formal symbols and real-world objects) are entered as bare srings. Names can not contain whitespace.  
  Example: `a`, `John`; not: `Santa Claus`.
- Sets are enclosed by `{`, `}`, with the elements separated by `,`.
- Tuples are enclosed by `(`, `)`, with the elements separated by `,`.
- Functions are enclosed by `[`, `]`, with the elements separated by `,` and argument - value pairs separated by `:`.
- Elements of interpretations of one-place predicates and one-place function domains have to be entered as singleton tuples enclosed in brackets `(a)` rather than as bare elements `a`.  

Examples:

Non-modal propositional structure: 
```
V = [p: True, q: False, r: True]
```

Non-modal predicational structure:
```
D = {Mary, Susan, Paula, John, Peter}
I = [m: Mary,
     j: John,
     f: [(Mary): Susan, (John): Peter],
     Woman: {(Mary), (Susan), (Paula)},
     Man: {(John), (Peter)},
     Happy: {(Mary), (Susan), (John), (Peter)},
     Love: {(Mary, John), (Susan, John), (Paula, Peter), (Peter, John)}]
V = [v1: [x: Mary, y: Paula, z: Peter],
     v2: [x: Paula, y: Paula, z: Peter]]
```
Modal propositional structure:
```
W = {w1, w2}
R = {(w1, w1), (w1, w2)}
V = [p: [w1: True, w2: False],
     q: [w1: False, w2: True]]
```

Modal predicational structure with constant domains:  

```
W = {w1, w2}
R = {(w1, w1), (w1, w2)}
D = {Mary, John}
I = [m: [w1: Mary, w2: Mary],
     Love: [w1: {(Mary, Peter)}, 
            w2: {(Mary, Peter), (Peter, Mary)}]]
```

Modal predicational structure with varying domains:  

```
W = {w1, w2}
R = {(w1, w1), (w1, w2)}
D = [w1: {Mary, John},
     w2: {Mary, Susan}]
I = [m: [w1: Mary, w2: Mary],
     Love: [w1: {(Mary, Peter)}, 
            w2: {(Mary, Susan), (Mary, Mary)}]]
```

Kripke (intuitionistic) structures:  
like modal propositional structure and modal varying predicational structure, except with the set of worlds named `K` instead of `W`.


# Entering file input
- Input files are plain text files.
- Each formulas is written on one line.
- The first formula in the list is interpreted as the conclusion and the others as the premises (if applicable).
- If a structure and formulas are specified, they are separated by a blank line.  
- If expressions are to be evaluated against assignment functions and/or possible worlds in a structure, they are specified by prepending their names to the formula prefixed with `v:` and `w:` respectively and suffixed with ` `.  
  Examples: `v:v1 Love(m,x)`, `w:w2 \exi x Unicorn(x)`, `v:v1 w:w2 Unicorn(x)`.

Examples: see the exemplary files in `pyPL/input`.

# Issues

- If the program hung itself up or crashed (especially after adding/removing formulas), usually simply restarting it resolves the issue. In case the program doesn’t seem to respond, please note that tableaus for largish (sets of) formulas may take some time to compute. If problems persist, you can check if there is useful information in the log file `pyPL/pyPL.log`. 
- If the formula or structure you entered won't update, you probably made a typo. Unfortunately there are no error messages telling you what exactly went wrong; you will have to check back with this documentation to see where the problem might be.  
- If no output file opens and a `.tex` file but no `.pdf` file was generated, compiling the `.tex` file via `pdflatex` probably went wrong. Try to compile the `.tex` file manually to see what the error is (perhaps a missing package). If LaTeX causes problems, select plain text instead of LaTeX PDF output in the settings. 
- If no output file opens, the automatic file opening via `xdg-open` probably isn't working on your machine. You can find all your output files in `pyPL/output`.  
