/usr/bin/python3.8 /home/natalie/Dropbox/Code/pyPL/PL.py

This is pyPL, a naive model checker for classical first-order logic.

Usage notes:
------------
This tool is not equipped with an interactive user interface; input has to be specified in the source code.
A number of examples are already set up.
- Models and formulas to compute denotations for are defined in the function 'compute' (near bottom of source code).
  Formulas, unforunately, have to be entered in prenex form.
  Follow the existing examples and the documentations of the classes and methods to get an idea.
- You can select which models to include in the output by editing the variable 'active' (near top of source code).
- You can select whether or not to print out intermediate steps by editing the variable 'verbose' (same place).

If you would like to understand what's going on under the hood:
The interesting part for you are the 'denot' methods in each of the expression classes.
Inspect the code and compare how the formal definitions can be translated into working code almost 1:1,
and try to follow how the implementation behaves, especially in the loop logic for the quantifiers.
A recommendation is to set breakpoints and step through an evaluation process symbol by symbol
to see how a denotation is computed recursively in line with the inductive definitions.
The '__repr__' methods are what makes the expressions formatted human-redable in the output.
Simply ignore anything that looks completely unfamiliar to you (such as 'w'/modal stuff, function symbols, etc.).

Notes on notation:
- 'M' = model/structure (aka 'A')
- 'D' = domain of discourse (aka 'M')
- 'I' = interpretation function (aka 'F')
- 'v' = variable assignment function (aka 'g')

After specifying your input in the source code, execute this script in a terminal to view the output.


---------------------------------

Example 1: tupperware boxes, lids and a bunny (lecture 09)

Model M = (D,I) with
D = {'rectbox', 'rectlid', 'roundlid', 'bunny', 'roundbox'}
I = {
     'b1' ↦ 'roundbox', 
     'b2' ↦ 'rectbox', 
     'f' ↦ 'bunny', 
     'box' ↦ {('rectbox'), ('roundbox')}, 
     'lid' ↦ {('rectlid'), ('roundlid')}, 
     'fit' ↦ {('rectlid', 'rectbox'), ('roundlid', 'roundbox')}
    }
v1 = {'x': 'roundbox', 'y': 'bunny'}
v'1 = {'x': 'bunny', 'y': 'rectbox'}

[[x]]^M1,v1 =
roundbox

[[x]]^M1,v'1 =
bunny

[[f]]^M1,v1 =
bunny

[[f]]^M1,v'1 =
bunny

[[box(x)]]^M1,v1 =
True

[[box(x)]]^M1,v'1 =
False

[[∀x(box(x) → ∃y(lid(y) ∧ fit(y,x)))]]^M1 =
  Let v'(x) := 'rectbox'.
    [[(box(x) → ∃y(lid(y) ∧ fit(y,x)))]]^M,v' =
    Let v''(y) := 'rectbox'.
      [[(lid(y) ∧ fit(y,x))]]^M,v'' =
      0
    Let v''(y) := 'rectlid'.
      [[(lid(y) ∧ fit(y,x))]]^M,v'' =
      1
    Since with v''(y) := 'rectlid' ex. g'': [[(lid(y) ∧ fit(y,x))]]^M,v'' = 1,
    [[∃y(lid(y) ∧ fit(y,x))]]^M,v' = 1.
    1
  Let v'(x) := 'rectlid'.
    [[(box(x) → ∃y(lid(y) ∧ fit(y,x)))]]^M,v' =
    1
  Let v'(x) := 'roundlid'.
    [[(box(x) → ∃y(lid(y) ∧ fit(y,x)))]]^M,v' =
    1
  Let v'(x) := 'bunny'.
    [[(box(x) → ∃y(lid(y) ∧ fit(y,x)))]]^M,v' =
    1
  Let v'(x) := 'roundbox'.
    [[(box(x) → ∃y(lid(y) ∧ fit(y,x)))]]^M,v' =
    Let v''(y) := 'rectbox'.
      [[(lid(y) ∧ fit(y,x))]]^M,v'' =
      0
    Let v''(y) := 'rectlid'.
      [[(lid(y) ∧ fit(y,x))]]^M,v'' =
      0
    Let v''(y) := 'roundlid'.
      [[(lid(y) ∧ fit(y,x))]]^M,v'' =
      1
    Since with v''(y) := 'roundlid' ex. g'': [[(lid(y) ∧ fit(y,x))]]^M,v'' = 1,
    [[∃y(lid(y) ∧ fit(y,x))]]^M,v' = 1.
    1
  Since f.a. v': [[(box(x) → ∃y(lid(y) ∧ fit(y,x)))]]^M,v' = 1,
  [[∀x(box(x) → ∃y(lid(y) ∧ fit(y,x)))]]^M,v = 1.
True

[[∃y(lid(y) ∧ ∀x(box(x) → fit(y,x)))]]^M1 =
  Let v'(y) := 'rectbox'.
    [[(lid(y) ∧ ∀x(box(x) → fit(y,x)))]]^M,v' =
    0
  Let v'(y) := 'rectlid'.
    [[(lid(y) ∧ ∀x(box(x) → fit(y,x)))]]^M,v' =
    Let v''(x) := 'rectbox'.
      [[(box(x) → fit(y,x))]]^M,v'' =
      1
    Let v''(x) := 'rectlid'.
      [[(box(x) → fit(y,x))]]^M,v'' =
      1
    Let v''(x) := 'roundlid'.
      [[(box(x) → fit(y,x))]]^M,v'' =
      1
    Let v''(x) := 'bunny'.
      [[(box(x) → fit(y,x))]]^M,v'' =
      1
    Let v''(x) := 'roundbox'.
      [[(box(x) → fit(y,x))]]^M,v'' =
      0
  Since with v'(x) := 'roundbox' ex. v': [[(box(x) → fit(y,x))]]^M,v' = 0,
  [[∀x(box(x) → fit(y,x))]]^M,v = 0.
    0
  Let v'(y) := 'roundlid'.
    [[(lid(y) ∧ ∀x(box(x) → fit(y,x)))]]^M,v' =
    Let v''(x) := 'rectbox'.
      [[(box(x) → fit(y,x))]]^M,v'' =
      0
  Since with v'(x) := 'rectbox' ex. v': [[(box(x) → fit(y,x))]]^M,v' = 0,
  [[∀x(box(x) → fit(y,x))]]^M,v = 0.
    0
  Let v'(y) := 'bunny'.
    [[(lid(y) ∧ ∀x(box(x) → fit(y,x)))]]^M,v' =
    0
  Let v'(y) := 'roundbox'.
    [[(lid(y) ∧ ∀x(box(x) → fit(y,x)))]]^M,v' =
    0
  Since ex. no v': [[(lid(y) ∧ ∀x(box(x) → fit(y,x)))]]^M,v' = 1,
  [[∃y(lid(y) ∧ ∀x(box(x) → fit(y,x)))]]^M,v = 0.
False

---------------------------------

Example 2: MMiL (example from the book)
Model M = (D,I) with
D = {'Mary', 'Jane', 'MMiL'}
I = {
     'm' ↦ 'Mary', 
     'student' ↦ {('Jane'), ('Mary')}, 
     'book' ↦ {('MMiL')}, 
     'read' ↦ {('Mary', 'MMiL')}
    }
v = {'x': 'Jane', 'y': 'Mary', 'z': 'MMiL'}

[[x]]^M2,v2 =
Jane

[[m]]^M2,v2 =
Mary

[[read]]^M2,v2 =
{('Mary', 'MMiL')}

[[book(x)]]^M2,v2 =
False

[[∃x(book(x) ∧ read(m,x))]]^M2,v2 =
  Let v'(x) := 'Mary'.
    [[(book(x) ∧ read(m,x))]]^M,v' =
    0
  Let v'(x) := 'Jane'.
    [[(book(x) ∧ read(m,x))]]^M,v' =
    0
  Let v'(x) := 'MMiL'.
    [[(book(x) ∧ read(m,x))]]^M,v' =
    1
  Since with v'(x) := 'MMiL' ex. g': [[(book(x) ∧ read(m,x))]]^M,v' = 1,
  [[∃x(book(x) ∧ read(m,x))]]^M,v = 1.
True

[[∀y(student(y) → ∃x(book(x) ∧ read(y,z)))]]^M2,v2 =
  Let v'(y) := 'Mary'.
    [[(student(y) → ∃x(book(x) ∧ read(y,z)))]]^M,v' =
    Let v''(x) := 'Mary'.
      [[(book(x) ∧ read(y,z))]]^M,v'' =
      0
    Let v''(x) := 'Jane'.
      [[(book(x) ∧ read(y,z))]]^M,v'' =
      0
    Let v''(x) := 'MMiL'.
      [[(book(x) ∧ read(y,z))]]^M,v'' =
      1
    Since with v''(x) := 'MMiL' ex. g'': [[(book(x) ∧ read(y,z))]]^M,v'' = 1,
    [[∃x(book(x) ∧ read(y,z))]]^M,v' = 1.
    1
  Let v'(y) := 'Jane'.
    [[(student(y) → ∃x(book(x) ∧ read(y,z)))]]^M,v' =
    Let v''(x) := 'Mary'.
      [[(book(x) ∧ read(y,z))]]^M,v'' =
      0
    Let v''(x) := 'Jane'.
      [[(book(x) ∧ read(y,z))]]^M,v'' =
      0
    Let v''(x) := 'MMiL'.
      [[(book(x) ∧ read(y,z))]]^M,v'' =
      0
    Since ex. no v'': [[(book(x) ∧ read(y,z))]]^M,v'' = 1,
    [[∃x(book(x) ∧ read(y,z))]]^M,v' = 0.
    0
Since with v(y) := 'Jane' ex. v: [[(student(y) → ∃x(book(x) ∧ read(y,z)))]]^M,v = 0,
[[∀y(student(y) → ∃x(book(x) ∧ read(y,z)))]]^M,v = 0.
False

[[¬∃y(student(y) ∧ ∃x(book(x) ∧ read(y,z)))]]^M2,v2 =
  Let v'(y) := 'Mary'.
    [[(student(y) ∧ ∃x(book(x) ∧ read(y,z)))]]^M,v' =
    Let v''(x) := 'Mary'.
      [[(book(x) ∧ read(y,z))]]^M,v'' =
      0
    Let v''(x) := 'Jane'.
      [[(book(x) ∧ read(y,z))]]^M,v'' =
      0
    Let v''(x) := 'MMiL'.
      [[(book(x) ∧ read(y,z))]]^M,v'' =
      1
    Since with v''(x) := 'MMiL' ex. g'': [[(book(x) ∧ read(y,z))]]^M,v'' = 1,
    [[∃x(book(x) ∧ read(y,z))]]^M,v' = 1.
    1
  Since with v'(y) := 'Mary' ex. g': [[(student(y) ∧ ∃x(book(x) ∧ read(y,z)))]]^M,v' = 1,
  [[∃y(student(y) ∧ ∃x(book(x) ∧ read(y,z)))]]^M,v = 1.
False

---------------------------------

Example 3: love #1 (ExSh 9 Ex. 1)
Model M = (D,I) with
D = {'Peter', 'John', 'Mary'}
I = {
     'j' ↦ 'Peter', 
     'p' ↦ 'John', 
     'woman' ↦ {('Mary')}, 
     'man' ↦ {('Peter'), ('John')}, 
     'love' ↦ {('John', 'Mary'), ('Peter', 'Mary'), ('Peter', 'John'), ('Mary', 'John'), ('John', 'John')}, 
     'jealous' ↦ {('Peter', 'Mary', 'John'), ('Peter', 'John', 'Mary')}
    }
v = {'x': 'Mary', 'y': 'Mary', 'z': 'Peter'}
v' = {'x': 'John', 'y': 'Peter', 'z': 'John'}

[[p]]^M3,v3 =
John

[[y]]^M3,v3 =
Mary

[[y]]^M3,v'3 =
Peter

[[love(p,j)]]^M3,v3 =
False

[[love(y,z)]]^M3,v3 =
False

[[love(y,z)]]^M3,v'3 =
True

[[∃x¬love(j,x)]]^M3,v3 =
  Let v'(x) := 'Peter'.
    [[¬love(j,x)]]^M,v' =
    1
  Since with v'(x) := 'Peter' ex. g': [[¬love(j,x)]]^M,v' = 1,
  [[∃x¬love(j,x)]]^M,v = 1.
True

[[∀x∃y love(x,y)]]^M3,v3 =
  Let v'(x) := 'Peter'.
    [[∃y love(x,y)]]^M,v' =
    Let v''(y) := 'Peter'.
      [[love(x,y)]]^M,v'' =
      0
    Let v''(y) := 'John'.
      [[love(x,y)]]^M,v'' =
      1
    Since with v''(y) := 'John' ex. g'': [[love(x,y)]]^M,v'' = 1,
    [[∃y love(x,y)]]^M,v' = 1.
    1
  Let v'(x) := 'John'.
    [[∃y love(x,y)]]^M,v' =
    Let v''(y) := 'Peter'.
      [[love(x,y)]]^M,v'' =
      0
    Let v''(y) := 'John'.
      [[love(x,y)]]^M,v'' =
      1
    Since with v''(y) := 'John' ex. g'': [[love(x,y)]]^M,v'' = 1,
    [[∃y love(x,y)]]^M,v' = 1.
    1
  Let v'(x) := 'Mary'.
    [[∃y love(x,y)]]^M,v' =
    Let v''(y) := 'Peter'.
      [[love(x,y)]]^M,v'' =
      0
    Let v''(y) := 'John'.
      [[love(x,y)]]^M,v'' =
      1
    Since with v''(y) := 'John' ex. g'': [[love(x,y)]]^M,v'' = 1,
    [[∃y love(x,y)]]^M,v' = 1.
    1
  Since f.a. v': [[∃y love(x,y)]]^M,v' = 1,
  [[∀x∃y love(x,y)]]^M,v = 1.
True

[[¬∀x(woman(x) → ∃y(man(y) ∧ love(x,y)))]]^M3,v3 =
  Let v'(x) := 'Peter'.
    [[(woman(x) → ∃y(man(y) ∧ love(x,y)))]]^M,v' =
    1
  Let v'(x) := 'John'.
    [[(woman(x) → ∃y(man(y) ∧ love(x,y)))]]^M,v' =
    1
  Let v'(x) := 'Mary'.
    [[(woman(x) → ∃y(man(y) ∧ love(x,y)))]]^M,v' =
    Let v''(y) := 'Peter'.
      [[(man(y) ∧ love(x,y))]]^M,v'' =
      0
    Let v''(y) := 'John'.
      [[(man(y) ∧ love(x,y))]]^M,v'' =
      1
    Since with v''(y) := 'John' ex. g'': [[(man(y) ∧ love(x,y))]]^M,v'' = 1,
    [[∃y(man(y) ∧ love(x,y))]]^M,v' = 1.
    1
  Since f.a. v': [[(woman(x) → ∃y(man(y) ∧ love(x,y)))]]^M,v' = 1,
  [[∀x(woman(x) → ∃y(man(y) ∧ love(x,y)))]]^M,v = 1.
False

[[¬∃y∃z jealous(j,y,z)]]^M3,v'3 =
  Let v'(y) := 'Peter'.
    [[∃z jealous(j,y,z)]]^M,v' =
    Let v''(z) := 'Peter'.
      [[jealous(j,y,z)]]^M,v'' =
      0
    Let v''(z) := 'John'.
      [[jealous(j,y,z)]]^M,v'' =
      0
    Let v''(z) := 'Mary'.
      [[jealous(j,y,z)]]^M,v'' =
      0
    Since ex. no v'': [[jealous(j,y,z)]]^M,v'' = 1,
    [[∃z jealous(j,y,z)]]^M,v' = 0.
    0
  Let v'(y) := 'John'.
    [[∃z jealous(j,y,z)]]^M,v' =
    Let v''(z) := 'Peter'.
      [[jealous(j,y,z)]]^M,v'' =
      0
    Let v''(z) := 'John'.
      [[jealous(j,y,z)]]^M,v'' =
      0
    Let v''(z) := 'Mary'.
      [[jealous(j,y,z)]]^M,v'' =
      1
    Since with v''(z) := 'Mary' ex. g'': [[jealous(j,y,z)]]^M,v'' = 1,
    [[∃z jealous(j,y,z)]]^M,v' = 1.
    1
  Since with v'(y) := 'John' ex. g': [[∃z jealous(j,y,z)]]^M,v' = 1,
  [[∃y∃z jealous(j,y,z)]]^M,v = 1.
False

---------------------------------

(Example 4: love #2 (modification of example 3)
Model M = (D,I) with
D = {'John', 'Mary', 'Susan'}
I = {
     'm' ↦ 'Mary', 
     'j' ↦ 'John', 
     's' ↦ 'Susan', 
     'rain' ↦ , 
     'sun' ↦ {()}, 
     'woman' ↦ {('Susan'), ('Mary')}, 
     'man' ↦ {('John')}, 
     'love' ↦ {('Susan', 'Mary'), ('Mary', 'Susan'), ('Susan', 'Susan'), ('John', 'Mary')}, 
     'jealous' ↦ {('John', 'Susan', 'Mary')}
    }
v = {'x': 'John', 'y': 'Mary', 'z': 'Susan'}

[[x]]^M4,v4 =
John

[[j]]^M4,v4 =
John

[[love]]^M4,v4 =
{('Susan', 'Mary'), ('Mary', 'Susan'), ('Susan', 'Susan'), ('John', 'Mary')}

[[love(x,m)]]^M4,v4 =
True

[[love(x,m)]]^M4 =
 checking v := {'x': 'Mary'} ...
  ✗
 counter assignment: v := {'x': 'Mary'}
False

[[love(j,m)]]^M4 =
True

[[∃x love(j,x)]]^M4 =
  Let v'(x) := 'John'.
    [[love(j,x)]]^M,v' =
    0
  Let v'(x) := 'Mary'.
    [[love(j,x)]]^M,v' =
    1
  Since with v'(x) := 'Mary' ex. g': [[love(j,x)]]^M,v' = 1,
  [[∃x love(j,x)]]^M,v = 1.
True

[[∀x love(j,x)]]^M4 =
  Let v'(x) := 'John'.
    [[love(j,x)]]^M,v' =
    0
Since with v(x) := 'John' ex. v: [[love(j,x)]]^M,v = 0,
[[∀x love(j,x)]]^M,v = 0.
False

[[(love(m,s) ∧ love(s,m))]]^M4 =
True

[[∀x(love(s,x) → woman(x))]]^M4 =
  Let v'(x) := 'John'.
    [[(love(s,x) → woman(x))]]^M,v' =
    1
  Let v'(x) := 'Mary'.
    [[(love(s,x) → woman(x))]]^M,v' =
    1
  Let v'(x) := 'Susan'.
    [[(love(s,x) → woman(x))]]^M,v' =
    1
  Since f.a. v': [[(love(s,x) → woman(x))]]^M,v' = 1,
  [[∀x(love(s,x) → woman(x))]]^M,v = 1.
True

[[¬∃x love(x,x)]]^M4 =
  Let v'(x) := 'John'.
    [[love(x,x)]]^M,v' =
    0
  Let v'(x) := 'Mary'.
    [[love(x,x)]]^M,v' =
    0
  Let v'(x) := 'Susan'.
    [[love(x,x)]]^M,v' =
    1
  Since with v'(x) := 'Susan' ex. g': [[love(x,x)]]^M,v' = 1,
  [[∃x love(x,x)]]^M,v = 1.
False

[[¬∀x love(x,x)]]^M4 =
  Let v'(x) := 'John'.
    [[love(x,x)]]^M,v' =
    0
Since with v(x) := 'John' ex. v: [[love(x,x)]]^M,v = 0,
[[∀x love(x,x)]]^M,v = 0.
True

[[∀x(woman(x) → ∃y(man(y) ∧ love(x,y)))]]^M4 =
  Let v'(x) := 'John'.
    [[(woman(x) → ∃y(man(y) ∧ love(x,y)))]]^M,v' =
    1
  Let v'(x) := 'Mary'.
    [[(woman(x) → ∃y(man(y) ∧ love(x,y)))]]^M,v' =
    Let v''(y) := 'John'.
      [[(man(y) ∧ love(x,y))]]^M,v'' =
      0
    Let v''(y) := 'Mary'.
      [[(man(y) ∧ love(x,y))]]^M,v'' =
      0
    Let v''(y) := 'Susan'.
      [[(man(y) ∧ love(x,y))]]^M,v'' =
      0
    Since ex. no v'': [[(man(y) ∧ love(x,y))]]^M,v'' = 1,
    [[∃y(man(y) ∧ love(x,y))]]^M,v' = 0.
    0
Since with v(x) := 'Mary' ex. v: [[(woman(x) → ∃y(man(y) ∧ love(x,y)))]]^M,v = 0,
[[∀x(woman(x) → ∃y(man(y) ∧ love(x,y)))]]^M,v = 0.
False

[[(((love(x,y) ∧ love(y,z)) ∧ ¬love(y,x)) → jealous(x,z,y))]]^M4 =
 checking v := {'x': 'Mary', 'y': 'Susan', 'z': 'Susan'} ...
  ✓
 checking v := {'x': 'John', 'y': 'Susan', 'z': 'John'} ...
  ✓
 checking v := {'x': 'Susan', 'y': 'John', 'z': 'Susan'} ...
  ✓
 checking v := {'x': 'Susan', 'y': 'John', 'z': 'John'} ...
  ✓
 checking v := {'x': 'Susan', 'y': 'Susan', 'z': 'Mary'} ...
  ✓
 checking v := {'x': 'Mary', 'y': 'Mary', 'z': 'Mary'} ...
  ✓
 checking v := {'x': 'Mary', 'y': 'Susan', 'z': 'John'} ...
  ✓
 checking v := {'x': 'John', 'y': 'Mary', 'z': 'Mary'} ...
  ✓
 checking v := {'x': 'Mary', 'y': 'John', 'z': 'Mary'} ...
  ✓
 checking v := {'x': 'John', 'y': 'John', 'z': 'Mary'} ...
  ✓
 checking v := {'x': 'Susan', 'y': 'Susan', 'z': 'Susan'} ...
  ✓
 checking v := {'x': 'Mary', 'y': 'Mary', 'z': 'Susan'} ...
  ✓
 checking v := {'x': 'Susan', 'y': 'Susan', 'z': 'John'} ...
  ✓
 checking v := {'x': 'Mary', 'y': 'Mary', 'z': 'John'} ...
  ✓
 checking v := {'x': 'John', 'y': 'Mary', 'z': 'Susan'} ...
  ✓
 checking v := {'x': 'Mary', 'y': 'John', 'z': 'Susan'} ...
  ✓
 checking v := {'x': 'John', 'y': 'Mary', 'z': 'John'} ...
  ✓
 checking v := {'x': 'Susan', 'y': 'Mary', 'z': 'Mary'} ...
  ✓
 checking v := {'x': 'Mary', 'y': 'John', 'z': 'John'} ...
  ✓
 checking v := {'x': 'John', 'y': 'John', 'z': 'Susan'} ...
  ✓
 checking v := {'x': 'John', 'y': 'Susan', 'z': 'Mary'} ...
  ✓
 checking v := {'x': 'Mary', 'y': 'Susan', 'z': 'Mary'} ...
  ✓
 checking v := {'x': 'John', 'y': 'John', 'z': 'John'} ...
  ✓
 checking v := {'x': 'Susan', 'y': 'John', 'z': 'Mary'} ...
  ✓
 checking v := {'x': 'Susan', 'y': 'Mary', 'z': 'Susan'} ...
  ✓
 checking v := {'x': 'Susan', 'y': 'Mary', 'z': 'John'} ...
  ✓
 checking v := {'x': 'John', 'y': 'Susan', 'z': 'Susan'} ...
  ✓
True

[[(∃x love(x,x) ∧ woman(x))]]^M4 =
 checking v := {'x': 'Mary'} ...
    Let v''(x) := 'John'.
      [[love(x,x)]]^M,v'' =
      0
    Let v''(x) := 'Mary'.
      [[love(x,x)]]^M,v'' =
      0
    Let v''(x) := 'Susan'.
      [[love(x,x)]]^M,v'' =
      1
    Since with v''(x) := 'Susan' ex. g'': [[love(x,x)]]^M,v'' = 1,
    [[∃x love(x,x)]]^M,v' = 1.
  ✓
 checking v := {'x': 'John'} ...
    Let v''(x) := 'John'.
      [[love(x,x)]]^M,v'' =
      0
    Let v''(x) := 'Mary'.
      [[love(x,x)]]^M,v'' =
      0
    Let v''(x) := 'Susan'.
      [[love(x,x)]]^M,v'' =
      1
    Since with v''(x) := 'Susan' ex. g'': [[love(x,x)]]^M,v'' = 1,
    [[∃x love(x,x)]]^M,v' = 1.
  ✗
 counter assignment: v := {'x': 'John'}
False

[[rain()]]^M4 =
False

[[sun()]]^M4 =
True

---------------------------------

Example 5: term equality and function symbols
Model M = (D,I) with
D = {'Peter', 'Mary', 'Susan', 'Jane'}
I = {
     'm' ↦ 'Mary', 
     's' ↦ 'Susan', 
     'j' ↦ 'Jane', 
     'mother' ↦ (('Mary',) ↦ 'Susan'), (('Peter',) ↦ 'Susan'), (('Susan',) ↦ 'Jane')
    }
v = {'x': 'Susan', 'y': 'Mary', 'z': 'Peter'}

[[mother(m)]]^M5,v5 =
Susan

[[mother(mother(m))]]^M5,v5 =
Jane

[[mother(m) = s]]^M5,v5 =
True

[[x≠m]]^M5,v5 =
True

---------------------------------

Example 6: modal logic with constant domain
Model M = (W,R,D,I) with
W = {'w1', 'w2'}
R = {('w2', 'w2'), ('w1', 'w2'), ('w1', 'w1')}
D = {'a'}
I = {
    'w1' ↦ 
           'P' ↦ {()}
     
    'w2' ↦ 
           'P' ↦ {}
    }
{'x': 'a', 'y': 'a', 'z': 'a'}
[[◇◻x = x]]^M6,v6 =
  checking w := 'w1' ...
    checking w'' := 'w1' ...
      checking w''' := 'w1' ...
      ✓
      checking w''' := 'w2' ...
      ✓
  ✓
  neighbor: w' := 'w1'
✓
checking w := 'w2' ...
  checking w' := 'w2' ...
    checking w'' := 'w2' ...
    ✓
✓
neighbor: w := 'w2'
✓
True
[[◻(P() ∨ ¬P())]]^M6,v6 =
  checking w := 'w1' ...
    checking w'' := 'w1' ...
    ✓
    checking w'' := 'w2' ...
    ✓
✓
checking w := 'w2' ...
  checking w' := 'w2' ...
  ✓
✓
True
[[(◻P() ∨ ◻¬P())]]^M6,v6 =
  checking w := 'w1' ...
    checking w'' := 'w1' ...
    ✓
    checking w'' := 'w2' ...
    ✗
    counter neighbor: w'' := 'w2'
    checking w'' := 'w1' ...
    ✗
    counter neighbor: w'' := 'w1'
  ✗
 counter world: w := 'w1'
False

---------------------------------

Example 7: modal logic with varying domain
Model M = (W,R,D,F) with
W = {'w1', 'w2'}
R = {('w2', 'w2'), ('w1', 'w2'), ('w1', 'w1')}
D = {
'w1' ↦ 'a'}, 
'w2' ↦ 'b', 'a'}}
I = {
    'w1' ↦          'P' ↦ {('a')}
    }, 
    'w2' ↦          'P' ↦ {('b')}
    }}
{'w1': [{'x': 'a', 'y': 'a', 'z': 'a'}], 'w2': [{'x': 'b', 'y': 'b', 'z': 'b'}, {'x': 'b', 'y': 'b', 'z': 'a'}, {'x': 'b', 'y': 'a', 'z': 'b'}, {'x': 'b', 'y': 'a', 'z': 'a'}, {'x': 'a', 'y': 'b', 'z': 'b'}, {'x': 'a', 'y': 'b', 'z': 'a'}, {'x': 'a', 'y': 'a', 'z': 'b'}, {'x': 'a', 'y': 'a', 'z': 'a'}]}

[[∃x∃yx≠y]]^M7,w1 =
  Let v'(x) := 'a'.
    [[∃yx≠y]]^M,v' =
    Let v''(y) := 'a'.
      [[x≠y]]^M,v'' =
      0
    Since ex. no v'': [[x≠y]]^M,v'' = 1,
    [[∃yx≠y]]^M,v' = 0.
    0
  Since ex. no v': [[∃yx≠y]]^M,v' = 1,
  [[∃x∃yx≠y]]^M,v = 0.
False

[[∃x∃yx≠y]]^M7,w2 =
  Let v'(x) := 'b'.
    [[∃yx≠y]]^M,v' =
    Let v''(y) := 'b'.
      [[x≠y]]^M,v'' =
      0
    Let v''(y) := 'a'.
      [[x≠y]]^M,v'' =
      1
    Since with v''(y) := 'a' ex. g'': [[x≠y]]^M,v'' = 1,
    [[∃yx≠y]]^M,v' = 1.
    1
  Since with v'(x) := 'b' ex. g': [[∃yx≠y]]^M,v' = 1,
  [[∃x∃yx≠y]]^M,v = 1.
True

---------------------------------


Scroll up for help information.

Process finished with exit code 0
