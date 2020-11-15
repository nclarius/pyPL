# Entering formulas

## Auxiliary symbols
- All symbols except parentheses and commas must be separated by whitespace.  
 Example: `- (p ^ q)`, not: `-(p^q)`.
 
- All formulas use round brackets.  
  Example: `\exi x (P(x) ^ Q(x))`, not: `\exi x [P(x) ^ Q(x)]`.

- Terms inside function expressions and atomic predications are enclosed by brackets and separated by commas.  
  Example: `P(a,b)`, not: `Pab`.
  
- Bracketing conventions:

  - Outer brackets may be omitted.  
  Example: `p ^ q` = `(p ^ q)`.

  - Occurrences of the same operator are left-associative.  
   Example: `p ^ q ^ r` = `(p ^ q) ^ r`.

  - Operator precedence: `∃`,`∀`, `¬` < `∧` < `∨` < `→` < `↔` < `⊕`.  
  Examples:  `¬ p ∨ q ∧ r` = `(¬p ∨ (q ∧ r))`, `∃x P(x) ^ Q(x)` = `((∃x P(x)) ^ Q(x))`.

## Term symbols

### Individual variables
Lowrecase letters `x` - `z`, optionally followed by a (optionally separatd by `_`) number.  
Examples: `x`, `y`, `x_23`, `z5`.

### Individual constants
Lowercase letters `a` - `e` and `i` - `o`, optionally followed by a (optionally separatd by `_`) number.  
Examples: `a`, `m`, `c12`, `zc_345`.

### Functions
Lowercase letters `f` - `h`, optionally followed by a (optionally separatd by `_`) number.  
Examples: `f`, `g2`.

## Atomic symbols

### Propositional variables
Lowercase letters `p` - `u`, optionally followed by a (optionally separatd by `_`) number.  
Examples: `p`, `q`, `p_1`, `u_23`.

### Predicates
A sequence of letters, numbers and underscore, with the first symbol an uppercase letter.  
Examples: `P`, `Loves`, `P_123`, not: `p`, `loves`.

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
`∨`, `v`, `\`, ``, `\vee`, `\lor`  

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

```
p ^ q -> (- r v p)  
P(a)  
\all x (Woman(x) -> \exi y (- (x = y) ^ Man(y) ^ Love(x,y)))
# p -> \falsum
Believe(j, \int Bald(k))
```


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
  Example: `a`, `John`, not: `Santa Claus`.
- Sets are enclosed by `{`, `}`, with the elements separated by `,`.
- Tuples are enclosed by `(`, `)`, with the elements separated by `,`.
- Functions are enclosed by `[`, `]`, with the elements separated by `,` and argument - value pairs separated by `:`.
- Elements of interpretations of one-place predicates and the domain of one-place functions have to be entered as singleton tuples enclosed in brackets `(a)` rather than as bare elements `a`.

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
     Love: {(Mary, John), (Susan, John), (Paula, Peter), (Peter, John)},
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
- Each formulas is written on one line.
- The first formula in the list is interpreted as the conclusion (if applicable).
- If a structure and formulas are specified, they are separated by a blank line.  
- Assignment functions and possible worlds to evaluate formulas against can be specified by prepending their names to the formula prefixed with `v:` and `w:` respectively and suffixed with ` `.  

Examples: see the examplary files in `pyPL/input`.