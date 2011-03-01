import null
import kicktest

try:
    from main2 import Main2
    from main3 import Main3
    from penalty_a import PenaltyA
    from penalty_d import PenaltyD
    from mlbridge import MLBridge
except ImportError:
    MLBridge = None

"A list of strategies that can be used"

strategies = { 'main2' : Main2,
               'main3' : Main3,
               'kicktest' : kicktest.KickTest,
               'main3' : Main3,
	       'penalty_a' : PenaltyA,
	       'penalty_d' : PenaltyD,
               'null' : null.Null,
               'ML'   : MLBridge,
             }

def list_strategies():
    for strat in strategies:
        print strat

