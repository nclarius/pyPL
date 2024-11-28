use_module(library(assoc)).

:- [writeproof].

% rules
prf(C, v(X), T) :-
    get_assoc(X, C, T).
prf(C, abs(v(X), A, M), imp(A, B)) :-
	put_assoc(X, C, A, C1),
    prf(C1, M, B).
prf(C, app(M, N), B) :-
    prf(C, M, imp(A, B)),
    prf(C, N, A).
prf(C, pair(M, N), conj(A, B)) :-
    prf(C, M, A),
    prf(C, N, B).
prf(C, fst(M), A) :-
    prf(C, M, conj(A, _)).
prf(C, snd(M), A) :-
    prf(C, M, conj(_, A)).
prf(C, inl(M), disj(A, _)) :-
    prf(C, M, T).
prf(C, inr(M), disj(_, A)) :-
    prf(C, M, T).
prf(C, case(M, v(X), N, v(Y), O), A) :-
    prf(C, M, disj(A, B)),
    put_assoc(X, C, A, C1),
    put_assoc(Z, C, B, C2),
    prf(C1, N, A),
    prf(C2, B, A).
prf(_, true(), bool).
prf(_, false(), bool).
prf(_, unit(), unit).

% wrapper predicates
typeinf(E) :- % find possible types with empty context
    typeinf([], E).
typeinf(C, E) :- % find possible prfs with given context
    findall(T, prfcheck(C, E, T), Ts),
    (length(Ts, 0) -> write("untypable"), fail; write_prop(Ts), !).
prfcheck(E, T) :- % check provability with given type with empty context
    prfcheck([], E, T).
prfcheck(CL, E, T) :- % check provability with given prf with given context
    list_to_assoc(CL, CA),
    prf(CA, E, T).
write_props([]):-
    !.
write_props([T|Ts]) :-
    write_prop(T), nl, write_props(Ts).

% example queries
% typeinf(app(abs(v(x), bool, v(x)), unit())).
% typeinf(app(abs(v(x), bool, v(x)), false())).
% typeinf([f-imp(bool, bool)], app(v(f), cond(false(), true(), false()))).
% typeinf([f-imp(bool, bool)], abs(v(x), bool, app(v(f), cond(v(x), true(), v(x))))).
% typeinf(unit()).
% typeinf(seq(unit(), false())).
% typeinf(let(v(x), true(), cond(true(), v(x), false()))).
% typeinf(abs(v(x), conj(a, a), inl(fst(v(x))))).
