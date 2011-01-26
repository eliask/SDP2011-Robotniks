import main
import null

"A list of strategies that can be used"

strategies = { 'main' : main.Main,
               'null' : null.Null,
             }

def list_strategies():
    for strat in strategies:
        print strat

