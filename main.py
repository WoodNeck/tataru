# -*- coding: utf-8 -*-
import os
import discord
import logging
from tataru import Tataru
from cogs.utils.botconfig import BotConfig

des = "타타루에용"
prefix = "타타루 "


if __name__ == '__main__':
    # Changing current working directory to use relative directories
    current_file_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(current_file_dir)

    bot = Tataru.instance(prefix, des)
    bot.load_cogs()

    config = BotConfig()
    token = config.request("BotUser", "Token")
    config.save()

    logging.basicConfig(filename='./tataru.log', level=logging.ERROR, format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p')

    bot.run(token)
