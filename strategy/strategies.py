import null
import kicktest

try:
    from main2 import Main2
    from main3 import Main3
    from penalty_a import PenaltyA
    from penalty_d import PenaltyD
    from friendly1 import Friendly1

    from mlbridge import MLBridge
except ImportError:
    MLBridge = None

"A list of strategies that can be used"

strategies = { 'main2' : Main2,
               'main3' : Main3,
               'kicktest' : kicktest.KickTest,
	       'penalty_a' : PenaltyA,
	       'penalty_d' : PenaltyD,
               'null' : null.Null,
               'ML'   : MLBridge,
               'friendly1'   : Friendly1,
             }

def list_strategies():
    for strat in strategies:
        print strat

