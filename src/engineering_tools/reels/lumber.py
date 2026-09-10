from enum import Enum


class Lumber(Enum):
    TWO_BY_FOUR = (1.5, 3.5)
    TWO_BY_SIX = (1.5, 5.5)
    TWO_BY_EIGHT = (1.5, 7.25)
    TWO_BY_TEN = (1.5, 9.25)
    TWO_BY_TWELVE = (1.5, 11.25)

    def __init__(self, thickness: float, width: float):
        self._thickness = thickness
        self._width = width

    @property
    def thickness(self) -> float:
        return self._thickness

    @property
    def width(self) -> float:
        return self._width

    @property
    def area(self) -> float:
        return self._width * self._thickness