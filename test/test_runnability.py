import sys
sys.path.append('.')
import tataru.main


def test_load_cog():
    bot = tataru.main.initialize()
    failed_cogs = tataru.main.load_cogs(bot)
    assert(len(failed_cogs) == 0)