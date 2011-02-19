import main
import main2
import null
import mlbridge

"A list of strategies that can be used"

strategies = { 'main' : main.Main,
               'main2' : main2.Main,
               'null' : null.Null,
               'ML'   : mlbridge.MLBridge,
             }

def list_strategies():
    for strat in strategies:
        print strat

