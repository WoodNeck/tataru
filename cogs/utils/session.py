from discord import Embed

class SessionEmoji:
    PREV = "⬅"
    NEXT = "➡"
    DELETE = "❌"

class Session:
    """
    공용 세션 클래스
    """
    def __init__(self, bot, msg, pages=None, max_time=30, color=0xDEADBF, show_footer=False, is_embed=True, footer_format=None):
        self._index = 0
        self._bot = bot
        self._cmdMsg = msg
        self._author = msg.author
        self._pages = pages
        self._maxTime = max_time
        self._embedColor = color
        self._emojiMenu = ["⬅", "➡", "❌"]
        self._callbacks = [self._prev, self._next, self.deleteMsg]
        self._is_embed = is_embed
        self._sessionMsg = None
        self._footer = show_footer
        self._footerFormat = footer_format
        self._shouldEnd = False

    def addEmoji(self, emoji, callback, pos=None):
        if pos:
            self._emojiMenu.insert(pos, emoji)
            self._callbacks.insert(pos, callback)
        else:
            self._emojiMenu.append(emoji)
            self._callbacks.append(callback)

    async def start(self):
        msg = await self._makeMsgContent()
        if self._is_embed:
            self._sessionMsg = await self._bot.send_message(self._cmdMsg.channel, embed=msg)
        else:
            self._sessionMsg = await self._bot.send_message(self._cmdMsg.channel, msg)
        for emoji in self._emojiMenu:
            await self._bot.add_reaction(self._sessionMsg, emoji)
        await self._waitForAuthorReaction()

    async def deleteMsg(self):
        await self._bot.delete_message(self._cmdMsg)
        await self._bot.delete_message(self._sessionMsg)
        self.end()

    def end(self):
        self._shouldEnd = True

    def current(self):
        return self._pages[self._index]

    async def _waitForAuthorReaction(self):
        res = await self._bot.wait_for_reaction(self._emojiMenu, timeout=self._maxTime, user=self._author, message=self._sessionMsg)
        if not res:
            await self._finishSession()
        else:
            await self._handleMsg(res)
        if not self._shouldEnd:
            await self._waitForAuthorReaction()

    async def _makeMsgContent(self):
        page = self._pages[self._index]
        if self._is_embed:
            em = Embed(colour=self._embedColor)
            if page.title: em.title = page.title
            if page.desc: em.description = page.desc
            if page.url: em.url = page.url
            if page.image: em.set_image(url=page.image)
            if page.thumb: em.set_thumbnail(url=page.thumb)
            if self._footer:
                if page.footer:
                    footer = page.footer
                    footer = footer.replace("%index", str(self._index + 1))
                    footer = footer.replace("%total", str(len(self._pages)))
                    em.set_footer(text=footer)
                else:
                    em.set_footer(text="{}/{}".format(self._index + 1, len(self._pages)))
            return em
        else:
            return page.desc

    async def _handleMsg(self, res):
        emoji = res.reaction.emoji
        emojiIndex = self._emojiMenu.index(emoji)
        callback = self._callbacks[emojiIndex]
        await callback()

    async def _finishSession(self):
        for emoji in self._emojiMenu:
            await self._bot.remove_reaction(self._sessionMsg, emoji, self._bot.user)
            await self._bot.remove_reaction(self._sessionMsg, emoji, self._author)
        self.end()

    async def _prev(self):
        if self._index > 0:
            self._index -= 1
        else:
            self._index = len(self._pages) - 1
        emojiIndex = self._emojiMenu.index(SessionEmoji.PREV)
        emoji = self._emojiMenu[emojiIndex]
        msg = await self._makeMsgContent()
        if self._is_embed:
            await self._bot.edit_message(self._sessionMsg, embed=msg)
        else:
            await self._bot.edit_message(self._sessionMsg, new_content=msg)
        await self._bot.remove_reaction(self._sessionMsg, emoji, self._author)

    async def _next(self):
        if self._index < len(self._pages) - 1:
            self._index += 1
        else:
            self._index = 0
        emojiIndex = self._emojiMenu.index(SessionEmoji.NEXT)
        emoji = self._emojiMenu[emojiIndex]
        msg = await self._makeMsgContent()
        if self._is_embed:
            await self._bot.edit_message(self._sessionMsg, embed=msg)
        else:
            await self._bot.edit_message(self._sessionMsg, new_content=msg)
        await self._bot.remove_reaction(self._sessionMsg, emoji, self._author)

class Page:
    def __init__(self, title=None, desc=None, url=None, image=None, thumb=None, footer_format=None):
        self.title = title
        self.desc = desc
        self.url = url
        self.image = image
        self.thumb = thumb
        self.footer = footer_format
