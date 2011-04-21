from null import Null
from kicktest import KickTest
from main2 import Main2
from main3 import Main3
from penalty_a import PenaltyA
from penalty_d import PenaltyD
from friendly1 import Friendly1
from final import Final

# A list of strategies that can be used:
strategies = { 'main2'     : Main2,
               'main3'     : Main3,
               'kicktest'  : KickTest,
	       'penalty_a' : PenaltyA,
	       'penalty_d' : PenaltyD,
               'null'      : Null,
               'friendly1' : Friendly1,
               'final'     : Final,
             }

def list_strategies():
    for strat in strategies:
        print strat

