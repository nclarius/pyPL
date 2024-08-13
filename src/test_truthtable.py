import unittest

from expr import *
from truthtable import *


class TestTruthtable(unittest.TestCase):
    def test_sentence(self):
        fml = Disj(Conj(Prop("p"), Prop("q")), Neg(Prop("r")))
        tt = Truthtable(fml, silent=True)
        assert not tt.valid() and tt.satisfiable()
    
    def test_inference(self):
        fml1 = Imp(Prop("p"), Prop("q"))
        fml2 = Imp(Prop("q"), Prop("r"))
        fml = Imp(Prop("p"), Prop("r"))
        tt = Truthtable(fml, premises=[fml1, fml2], silent=True)
        assert tt.valid()

        fml1 = Disj(Prop("p"), Prop("q"))
        fml2 = Neg(Prop("p"))
        fml = Neg(Prop("q"))
        tt = Truthtable(fml, premises=[fml1, fml2], silent=True)
        assert not tt.valid()
    
    def test_theory(self):
        fml1 = Disj(Prop("p"), Prop("q"))
        fml2 = Neg(Conj(Prop("p"), Prop("q")))
        tt = Truthtable(None, premises=[fml1, fml2], silent=True)
        assert tt.satisfiable()

    def test_edgecase(self):
        fml = Verum()
        tt = Truthtable(fml, silent=True)
        assert tt.valid()
    
if __name__ == '__main__':
    unittest.main()
