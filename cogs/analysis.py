import os
from discord.utils import find
from discord.ext import commands
from wordcloud import WordCloud

class Analysis:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def 세줘(self, ctx, word):
        """{} 세줘 `단어` @user1 @user2 @user3 ...
        """.format(self.bot.prefix)
        serverId = ctx.message.server.id
        users = ctx.message.mentions
        if not users:
            await self.bot.say("분석할 유저를 추가로 주세용!")
            return
        
        def makeProcessMsgStr(processed, limit):
            percentage = 10 * processed / limit
            visualization = "".join(["🏇" if i < percentage else "▫️" for i in range(10)])
            msg = "[분석중이에용]{}({}/{})".format(visualization, processed, limit)
            return msg

        processed = 0
        msgLimit = 100000

        processMsgStr = makeProcessMsgStr(processed, msgLimit)
        processMsg = await self.bot.say(processMsgStr)

        msgCounts = [0 for i in range(len(users))]
        wordCounts = [0 for i in range(len(users))]
        totalMsgCounts = [0 for i in range(len(users))]
        async for msg in self.bot.logs_from(ctx.message.channel, limit=msgLimit):
            userIdx = -1
            for idx, user in enumerate(users):
                if msg.author == user:
                    userIdx = idx
                    break
            if userIdx < 0:
                continue
            wordCount = msg.content.count(word)
            if wordCount > 0:
                wordCounts[userIdx] += wordCount
                msgCounts[userIdx] += 1
            totalMsgCounts[userIdx] += 1
            processed += 1
            if int(10 * (processed - 1) / msgLimit) != int(10 * processed / msgLimit):
                processMsgStr = makeProcessMsgStr(processed, msgLimit)
                processMsg = await self.bot.edit_message(processMsg, new_content=processMsgStr)

        await self.bot.delete_message(processMsg)

        outMsg = []
        for idx, user in enumerate(users):
            avgWords = 0 if msgCounts[idx] == 0 else wordCounts[idx] / msgCounts[idx]
            outMsg.append("[{}] {}개의 {}을(를) {}/{}개의 메시지에서 찾았어용 (평균 {:.2f}개)".format(
                user.display_name, wordCounts[idx], word, msgCounts[idx], totalMsgCounts[idx], avgWords
            ))
        await self.bot.say("```최근 {}개의 메시지 중에서...\n{}```".format(msgLimit, '\n'.join(outMsg)))
    
    @commands.command(pass_context=True)
    async def 단어구름(self, ctx):
        """{} 단어구름
        """.format(self.bot.prefix)
        serverId = ctx.message.server.id
        users = ctx.message.mentions

        def makeProcessMsgStr(processed, limit):
            percentage = 10 * processed / limit
            visualization = "".join(["🏇" if i < percentage else "▫️" for i in range(10)])
            msg = "[분석중이에용]{}({}/{})".format(visualization, processed, limit)
            return msg

        processed = 0
        msgLimit = 100000

        processMsgStr = makeProcessMsgStr(processed, msgLimit)
        processMsg = await self.bot.say(processMsgStr)

        total_frequencies = dict()
        font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data/font/NanumGothicExtraBold.ttf"))
        wordcloud = WordCloud(font_path=font_path, width=800, height=800)
        async for msg in self.bot.logs_from(ctx.message.channel, limit=msgLimit):
            processed += 1
            if users and msg.author not in users:
                continue
            frequencies = wordcloud.process_text(msg.content)
            for k, v in frequencies.items():
                if k not in total_frequencies:
                    total_frequencies[k] = v
                else:
                    total_frequencies[k] += v

            if int(10 * (processed - 1) / msgLimit) != int(10 * processed / msgLimit):
                processMsgStr = makeProcessMsgStr(processed, msgLimit)
                processMsg = await self.bot.edit_message(processMsg, new_content=processMsgStr)

        await self.bot.delete_message(processMsg)

        image_path = "temp/analysis_{}.png".format(serverId)
        cloud = wordcloud.generate_from_frequencies(total_frequencies)
        cloud.to_file(image_path)

        with open(image_path, "rb") as f:
            await self.bot.send_file(ctx.message.channel, f)

def setup(bot):
    cog = Analysis(bot)
    bot.add_cog(cog)