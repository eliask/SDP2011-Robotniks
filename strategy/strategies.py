import main
import null
import mlbridge

"A list of strategies that can be used"

strategies = { 'main' : main.Main,
               'null' : null.Null,
               'ML'   : mlbridge.MLBridge,
             }

def list_strategies():
    for strat in strategies:
        print strat

