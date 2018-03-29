from discord import Embed

class SessionEmoji:
    PREV = 0
    NEXT = 1
    DELETE = 2

class Session:
    """
    공용 세션 클래스
    """
    def __init__(self, bot, msg, pages=None, max_time=30, color=0xDEADBF, show_footer=False):
        self._index = 0
        self._bot = bot # TODO: Make this Singleton
        self._cmdMsg = msg
        self._author = msg.author
        self._pages = pages
        self._maxTime = max_time
        self._embedColor = color
        self._emojiMenu = ["⬅", "➡", "❌"]
        self._callbacks = [self._prev, self._next, self._delete]
        self._embedMsg = None
        self._footer = show_footer
        self._shouldEnd = False

    def addEmoji(self, emoji, callback, pos=None):
        if pos:
            self._emojiMenu.insert(pos, emoji)
            self._callbacks.insert(pos, callback)
        else:
            self._emojiMenu.append(emoji)
            self._callbacks.append(callback)

    async def start(self):
        em = self.makeEmbed()
        self._embedMsg = await self._bot.send_message(self._cmdMsg.channel, embed=em)
        for emoji in self._emojiMenu:
            await self.bot.add_reaction(self._embedMsg, emoji)
        await self._waitForAuthorReaction()

    def end(self):
        self._shouldEnd = True

    async def _waitForAuthorReaction(self):
        res = await self._bot.wait_for_reaction(self._emojiMenu, timeout=self._maxTime, user=self._author, message=self._embedMsg)
        if not res:
            await self._finishSession()
        else:
            await self._handleMsg(res)
        if not self._shouldEnd:
            await self._waitForAuthorReaction()

    async def _makeEmbed(self):
        em = Embed(colour=self._embedColor)
        page = self._pages[self._index]
        if page.title: em.title = page.title
        if page.desc: em.description = page.desc
        if page.image: em.set_image(page.image)
        if page.thumb: em.set_thumbnail = page.thumb
        if self._footer: em.set_footer("{}/{}".format(self._index + 1, len(self._pages)))

    async def _handleMsg(self, res):
        emoji = res.reaction.emoji
        emojiIndex = self._emojiMenu.index(emoji)
        callback = self._callbacks[emojiIndex]
        await callback()

    async def _finishSession(self):
        for emoji in self._emojiMenu:
            await self._bot.remove_reaction(self._embedMsg, emoji, self._bot.user)
            await self._bot.remove_reaction(self._embedMsg, emoji, self._author)
        self.end()

    async def _prev(self):
        if self._index > 0:
            self._index -= 1
        else:
            self._index = len(self._pages) - 1
        emoji = self._emojiMenu[SessionEmoji.PREV]
        em = await self.makeEmbed()
        await self._bot.edit_message(self._embedMsg, embed=em)
        await self._bot.remove_reaction(self._embedMsg, emoji, self._author)

    async def _next(self):
        if self._index < len(self._page) -1:
            self._index += 1
        else:
            self._index = 0
        return self._pages[self._index]

    async def _delete(self):
        await self._bot.delete_message(self._cmdMsg)
        await self._bot.delete_message(self._embedMsg)
        self.end()

class Page:
    def __init__(self, title=None, desc=None, image=None, thumb=None):
        self.title = title
        self.desc = desc
        self.image = image
        self.thumb = thumb
