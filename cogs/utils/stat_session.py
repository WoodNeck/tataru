import discord
import urllib

class StatSession:
    '''
    페이지별 포맷이 다른 Session
    '''
    def __init__(self, stat):
        self.index = 0
        self.pages = [self.overall, self.playtime, self.classinfo]
        self.stat = stat

    def makeEmbed(self):
        nickname = self.stat["nickname"]
        encodedNickname = urllib.parse.quote(nickname.encode("utf-8"))
        em = discord.Embed(colour=0xDEADBF)
        em.set_author(name="{}{}의 스텟 정보에용".format(self.stat["clan"], nickname),
        url="http://gg2statsapp.appspot.com/profile?id={}".format(encodedNickname),
        icon_url="http://gg2statsapp.appspot.com/avatar?nickname={}".format(encodedNickname))
        em.set_footer(text="{}({}/{})".format(self.pages[self.index].__doc__, self.index + 1, len(self.pages)))
        return em

    def prev(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.pages) - 1
        prevPage = self.pages[self.index]
        return prevPage()

    def next(self):
        self.index += 1
        if self.index >= len(self.pages):
            self.index = 0
        nextPage = self.pages[self.index]
        return nextPage()

    def overall(self):
        """종합정보"""
        nickname = self.stat["nickname"]
        encodedNickname = urllib.parse.quote(nickname.encode("utf-8"))
        region = self.stat["region"][:2].lower()
        kda = (self.stat["kill"] + self.stat["assist"]) / max(self.stat["death"], 1)
        h, m , d = self.parseTime("time_total")

        em = self.makeEmbed()
        em.set_thumbnail(url="http://gg2statsapp.appspot.com/avatar?nickname={}".format(encodedNickname))

        desc = []
        desc.append(":flag_{}:".format(region))
        if self.stat["title"]:
            desc.append("\"{}\"".format(self.stat["title"]))
        desc.append("`LEVEL` **{}** `EXP` **{}** / **{}** `COIN` **{}**".format(self.stat["level"], self.stat["exp"], self.maxExp(), self.stat["coin"]))
        desc.append("**{}**시간 **{}**분 **{}**초동안 **{}**판 플레이".format(h, m , d, self.stat["playcount"]))
        desc.append("🔫: **{}**, 💀: **{}**, 🤝: **{}**, `KDA`: **{:.2f}**".format(self.stat["kill"], self.stat["death"], self.stat["assist"], kda))
        desc.append("🚩: **{}**, 🛡️: **{}**, 💥: **{}**".format(self.stat["capture"], self.stat["defense"], self.stat["destruction"]))
        desc.append("🗡️: **{}**, ♥️: **{}**, 🌟: **{}**".format(self.stat["stab"], self.strlize(self.stat["healing"]), self.stat["invuln"]))
        desc.append("**{}**`승` **{}**`패` **{}**`비김` **{}**`탈주`".format(self.stat["win"], self.stat["lose"], self.stat["draw"], self.stat["disconnect"]))
        desc = "\n".join(desc)
        desc = "{}".format(desc)
        em.description = desc
        return em

    def playtime(self):
        """플레이타임"""
        red = int(self.stat["time_red"] * 100 / self.stat["time_total"])
        blue = int(self.stat["time_blue"] * 100 / self.stat["time_total"])
        spec = int(self.stat["time_spectate"] * 100 / self.stat["time_total"])

        redStr = self.timeToString(self.parseTime("time_red"))
        blueStr = self.timeToString(self.parseTime("time_blue"))
        specStr = self.timeToString(self.parseTime("time_spectate"))

        chartUrl = ["https://image-charts.com/chart?cht=p"]
        chartUrl.append("chtt={}'s+Playtime".format(self.stat["nickname"]))
        chartUrl.append("chs=300x300")
        chartUrl.append("chd=t:{},{},{}".format(red, blue, spec))
        chartUrl.append("chl={}|{}|{}".format(redStr, blueStr, specStr))
        chartUrl.append("chds=a")
        chartUrl.append("chdl=Red|Blue|Spectate")
        chartUrl.append("chco=FF6347,4169E1,757575")
        chartUrl = "&".join(chartUrl)
        em = self.makeEmbed()
        em.set_image(url=chartUrl)
        return em

    def classinfo(self):
        """클래스별 정보"""
        classes = ["runner", "firebug", "rocketman", "overweight", "detonator", "healer", "constructor", "infiltrator", "rifleman", "quote"]

        killData = []
        for cls in classes:
            killData.append(str(self.stat["{}_kill".format(cls)]))
        killData = ",".join(killData)

        deathData = []
        for cls in classes:
            deathData.append(str(self.stat["{}_death".format(cls)]))
        deathData = ",".join(deathData)

        assistData = []
        for cls in classes:
            assistData.append(str(self.stat["{}_assist".format(cls)]))
        assistData = ",".join(assistData)

        classData = [killData, deathData, assistData]
        classData = "|".join(classData)

        chartUrl = ["https://image-charts.com/chart?cht=bhs"]
        chartUrl.append("chs=600x300")
        chartUrl.append("chd=t:{}".format(classData))
        chartUrl.append("chdl=Kill|Death|Assist")
        chartUrl = "&".join(chartUrl)
        em = self.makeEmbed()
        em.set_image(url=chartUrl)
        return em

    def parseTime(self, time_key):
        user_time = self.stat[time_key]
        time_h = 0
        time_m = 0
        time_s = 0
        if user_time // 108000:
            time_h = user_time // 108000
            user_time -= 108000*time_h
        if user_time // 1800 and time_h < 100:
            time_m = user_time // 1800
            user_time -= 1800*time_m
        if not time_h:
            time_s = user_time // 30
        return (time_h, time_m, time_s)

    def timeToString(self, timeInfo):
        result = []
        h, m ,s = timeInfo
        if h > 0:
            result.append("{}h".format(h))
        if h < 100:
            result.append("{}m".format(m))
        if h <= 0:
            result.append("{}s".format(s))
        return "+".join(result)

    def maxExp(self):
    	return 1500 * self.stat["level"]

    def strlize(self, num):
        if (num >= 1000):
            return "{:.1f}K".format(num / 1000)
        elif (num >= 1000000):
            return "{:.1f}M".format(num / 1000000)
        else:
            return "{:.1f}".format(num)
