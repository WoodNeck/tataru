import json
from discord import Embed
from pathlib import Path


class ShipInfo:
    FILE_PATH = "ship_info.json"

    def __init__(self, serverId):
        self._serverId = serverId
        self._info = dict()
        self.load(serverId)

    def load(self, serverId):
        file = Path(ShipInfo.FILE_PATH)
        if not file.is_file():
            return
        with open(ShipInfo.FILE_PATH, "r") as data:
            totalInfo = json.load(data)
            info = totalInfo.get(serverId)
            if info:
                self._info = info

    def save(self):
        file = Path(ShipInfo.FILE_PATH)
        totalInfo = dict()
        if file.is_file():
            with open(ShipInfo.FILE_PATH, "r") as data:
                totalInfo = json.load(data)
        totalInfo[self._serverId] = self._info
        with open(ShipInfo.FILE_PATH, "w") as f:
            f.write(json.dumps(totalInfo))

    def addOrModifyShip(self, shipName, crewId, maxCrew=1, thumbUrl=None, embedColor=None):
        if self._info.get(shipName):
            ship = self._info[shipName]
            if not maxCrew:
                maxCrew = ship["max"]
            if not thumbUrl:
                thumbUrl = ship["thumb"]
            if not embedColor:
                embedColor = ship["color"]
            crews = set(ship["crews"])
            crews.add(crewId)
            crews = list(crews)
            self._info[shipName] = {"thumb": thumbUrl, "max": maxCrew, "crews": crews, "color": embedColor}
        else:
            self._info[shipName] = {"thumb": thumbUrl, "max": maxCrew, "crews": [crewId], "color": embedColor}
        self.save()

    def removeShip(self, shipName, crewId):
        if self._info.get(shipName):
            del self._info[shipName]
            self.save()
        else:
            raise ShipNotExistError("Ship does not exist!")

    def addCrew(self, shipName, crewId):
        if self._info.get(shipName):
            crews = set(self._info[shipName]["crews"])
            crews.add(crewId)
            self._info[shipName]["crews"] = list(crews)
            self.save()
        else:
            raise ShipNotExistError("Ship does not exist!")

    def removeCrew(self, shipName, crewId):
        if self._info.get(shipName):
            if crewId in self._info[shipName]["crews"]:
                self._info[shipName]["crews"].remove(crewId)
                self.save()
            else:
                raise CrewNotExistError("Commander is not associated with this ship!")
        else:
            raise ShipNotExistError("Ship does not exist!")

    def depart(self, shipName, crewId):
        if self._info.get(shipName):
            if crewId in self._info[shipName]["crews"]:
                crewNum = len(self._info[shipName]["crews"])
                self._info[shipName]["crews"] = []
                self.save()
                return crewNum
            else:
                raise CrewNotExistError("Commander is not associated with this ship!")
        else:
            raise ShipNotExistError("Ship does not exist!")

    async def shipInfo(self, shipName, bot):
        if not self._info.get(shipName):
            raise ShipNotExistError("Ship does not exist!")
        ship = self._info[shipName]
        em = Embed(title=shipName)
        if ship["color"]:
            em.colour = ship["color"]
        if ship["thumb"]:
            em.set_thumbnail(url=ship["thumb"])
        _crews = ship["crews"]
        crews = []
        for crewId in _crews:
            crew = await bot.get_user_info(crewId)
            crews.append(crew.display_name)
        crews = ", ".join(crews)
        if not crews:
            crews = "❌"
        em.add_field(name="선원", value=crews)
        em.set_footer(text="{}/{}".format(len(_crews), ship["max"]))
        return em

    def allShips(self):
        result = []
        for shipName in self._info:
            ship = self._info[shipName]
            result.append("🚢{} ({}/{})".format(shipName, len(ship["crews"]), ship["max"]))
        result = "\n".join(result)
        return "```{}```".format(result)


class ShipNotExistError(Exception):
    pass


class CrewNotExistError(Exception):
    pass
