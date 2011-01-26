import main

"A list of strategies that can be used"

strategies = { 'main' : main.Main,
             }

def list_strategies():
    for strat in strategies:
        print strat

