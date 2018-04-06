import sys
sys.path.append('.')
import main


def test_load_cog():
    bot = main.initialize()
    failed_cogs = main.load_cogs(bot)
    assert(len(failed_cogs) == 0)