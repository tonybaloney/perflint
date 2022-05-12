import abc
import curses
from Engine import Game, Level, MapPoint, MapTileTypeHelper, UnitVector
from Keyboard import Keyboard


class Renderer(abc.ABC):
    def render(self, game: Game):
        ...


class CursesRenderer(Renderer, Keyboard):
    def __init__(self):
        self.console = curses.initscr()
        curses.curs_set(0)
        self.console.keypad(True)
        self.console.refresh()

    def render(self, game: Game):
        self._drawLevel(game.level)
        self.console.refresh()

    def readKey(self) -> str:
        return self.console.getch()

    def tryGetUnitVector(self, key: str) -> UnitVector | None:
        match key:
            case "7":
                return UnitVector.NW
            case curses.KEY_UP | "8":
                return UnitVector.N
            case "9":
                return UnitVector.NE
            case curses.KEY_RIGHT | "6":
                return UnitVector.E
            case "3":
                return UnitVector.SE
            case curses.KEY_DOWN | "2":
                return UnitVector.S
            case "1":
                return UnitVector.SW
            case curses.KEY_LEFT | "4":
                return UnitVector.W
            case _:
                return None

    def _drawLevel(self, level: Level):
        for pointAndTile in level.map.tiles:
            self._drawAt(
                MapTileTypeHelper.getGlyph(pointAndTile[1].type)
                if pointAndTile[1].isExplored
                else " ",
                pointAndTile[0],
            )

        for obj in level.knownObjects:
            self._drawAt(obj.glyph, obj.position)

    def _drawAt(self, glyph: str, point: MapPoint):
        self.console.addch(point.y, point.x, glyph)

    def _drawLogString(self, logEntry: str):
        for i in range(0, self.console.width):
            charToRender = logEntry[i] if i < len(logEntry) else " "
            self._drawAt(charToRender, MapPoint(i, self.console.height - 1))
