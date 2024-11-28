% pretty printing

write_prop(X) :- var(X),
    write("_").
write_prop(imp(T1, T2)) :-
    write("("), write_prop(T1), write(" → "), write_prop(T2), write(")").
write_prop(conj(T1, T2)) :-
    write("("), write_prop(T1), write(" ∧ "), write_prop(T2), write(")").
write_prop(disj(T1, T2)) :-
    write("("), write_prop(T1), write(" ∨ "), write_prop(T2), write(")").
write_prop(bool) :-
    write("Bool").
write_prop(unit) :-
    write("Unit").
write_prop(X) :-
    write(X).

write_constr(X) :- var(X),
    write("_").
write_constr(abs(v(X), A, M)) :-
    write("λ"), write(X), write(" : "), write_prop(A), write(". "), write_constr(M).
write_constr(app(M, N)) :-
    write_constr(M), write(" "), write_constr(N).
write_constr(pair(M, N)) :-
    write("〈"), write_constr(M), write(", "), write_constr(N), write("〉").
write_constr(fst(M)) :-
    write("π₁ "), write_constr(M).
write_constr(snd(M)) :-
    write("π₂ "), write_constr(M).
write_constr(inl(M)) :-
    write("ι₁ "), write_constr(M).
write_constr(inr(M)) :-
    write("ι₂ "), write_constr(M).
write_constr(case(M, v(X), N, v(Y), O)) :-
    write("case "), write_constr(M), write(" | ι₁ "), write(X), write(" ⇒ "), write_constr(N), write(" | ι₂ "), write(Y), write(" ⇒ "), write_constr(O).
