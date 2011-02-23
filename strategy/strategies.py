import main
import null
import kicktest

try:
    from main2 import Main2
    from mlbridge import MLBridge
except ImportError:
    MLBridge = None

"A list of strategies that can be used"

strategies = { 'main2' : Main2,
               'kicktest' : kicktest.KickTest,
               'null' : null.Null,
               'ML'   : MLBridge,
             }

def list_strategies():
    for strat in strategies:
        print strat

