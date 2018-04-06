import sys
import os
sys.path.append(os.path.abspath(os.curdir))
print(os.getcwd())
from .. import main


def test_load_cog():
    bot = main.initialize()
    failed_cogs = main.load_cogs(bot)
    assert(len(failed_cogs) == 0)