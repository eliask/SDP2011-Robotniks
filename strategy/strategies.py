import main
import null
import goThenKick

"A list of strategies that can be used"

strategies = { 'main' : main.Main,
               'null' : null.Null,
               'go' : goThenKick.GoThenKick,
             }

def list_strategies():
    for strat in strategies:
        print strat

