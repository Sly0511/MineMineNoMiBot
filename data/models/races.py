from enum import Enum


class Races(Enum):
    Human = "human"
    Cyborg = "cyborg"
    Mink = "mink"
    Fishman = "fishman"


class SubRaces(Enum):
    Bunny = "mink_bunny"
    Dog = "mink_dog"
    Lion = "mink_lion"