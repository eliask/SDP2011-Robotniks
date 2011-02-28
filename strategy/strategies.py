import null
import kicktest

try:
    from main2 import Main2
    from main3 import Main3
    from mlbridge import MLBridge
except ImportError:
    MLBridge = None

"A list of strategies that can be used"

strategies = { 'main2' : Main2,
               'kicktest' : kicktest.KickTest,
               'main3' : Main3,
               'null' : null.Null,
               'ML'   : MLBridge,
             }

def list_strategies():
    for strat in strategies:
        print strat

