import warnings

from .environment import Environment
from .update import update_daily_before, update_daily_after
from .compute import compute
from .strategy import init, my_strategy


def backtest_structure():
    context = Environment()
    update_daily_before(context)
    init(context)
    my_strategy(context)     
    while not update_daily_after(context):
        update_daily_before(context)
        my_strategy(context)
    compute(context)
    return 



warnings.filterwarnings("ignore", category = FutureWarning)
backtest_structure()
