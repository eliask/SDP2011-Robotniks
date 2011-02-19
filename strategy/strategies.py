import main
import main2
import null
import kicktest

try:
    from mlbridge import MLBridge
except ImportError:
    MLBridge = None

"A list of strategies that can be used"

strategies = { 'main' : main.Main,
               'main2' : main2.Main,
               'kicktest'   : KickTest.kicktest,
               'null' : null.Null,
               'ML'   : MLBridge,
             }

def list_strategies():
    for strat in strategies:
        print strat

