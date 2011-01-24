import strategy

"A list of strategies that can be specified"

strategies = { 'main' : strategy.Strategy }

def list_strategies():
    for strat in strategies:
        print strat

