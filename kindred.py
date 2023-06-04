from __future__ import annotations
import json
import random
from enum import Enum
from typing import Optional

from pydantic import BaseModel

# Vampire ids
vid = int


class Clan(str, Enum):
    Gangrel = "Gangrel"
    Daeva = "Daeva"
    Ventrue = "Ventrue"
    Mekhet = "Mekhet"
    Nosferatu = "Nosferatu"


class Faction(str, Enum):
    Invictus = 'Invictus'
    Carthian = "Carthian"
    Lanca = "Lanca Sanctum"
    Circle = "Circle of the Crone"
    Ordo = "Ordo Dracul"


class Alliance(str, Enum):
    North = "North"
    South = "South"
    Middle = "Middle"


class Kindred(BaseModel):
    name: str
    status: int
    bp: int
    clan: Clan
    faction: Faction
    alliance: Alliance
    title: str
    pc: bool = False

    @staticmethod
    def read_from_file(name: str) -> dict[vid, Kindred]:
        index = 0
        result: dict[vid, Kindred] = {}
        with open(name) as f:
            data: list[dict] = json.load(f)
            for k in data:
                kindred = Kindred(**k)
                result[index] = kindred
                index += 1
        return result


def get_weighted_vampires(kindreds: dict[vid, Kindred], invert: bool = False, ignore: Optional[vid] = None) -> tuple[
    int, dict[vid, int]]:
    weight = 0
    weighted_kindred: dict[vid, int] = {}
    for kindred_id in kindreds:
        if ignore is not None and kindred_id == ignore:
            continue
        kindred = kindreds[kindred_id]
        if kindred.pc:
            continue
        weight += (kindred.bp + kindred.status) * 5
        if invert:
            weight = 100 - weight
        weighted_kindred[kindred_id] = weight
    return weight, weighted_kindred


def pick_kindred(max_weight, weights: dict[vid, int]) -> vid:
    val = random.randrange(0, max_weight)
    for k in weights:
        if val < weights[k]:
            return k


def find_kindred_from_name(name: str, kindred: dict[int, Kindred]) -> int:
    for id in kindred:
        if name == kindred[id].name:
            return id
    return -1
