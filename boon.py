import random
from enum import Enum

from pydantic import BaseModel


class BoonRecord(BaseModel):
    owed: int
    debter: int
    type: str
    num: int = 1


class BoonType(str, Enum):
    Life = "life"
    Major = "major"
    Standard = "standard"
    Minor = "minor"
    Trivial = "trivial"


class Boon(BaseModel):
    type: BoonType
    weight: int


def get_weighted_boons(boon_values: list[Boon]) -> tuple[int, dict[str, int]]:
    weight = 0
    weighted_boons = {}
    for boon in boon_values:
        weight += boon.weight
        weighted_boons[boon.type] = weight
    return weight, weighted_boons


def pick_boon(boon_values: list[Boon]) -> str:
    (max_weight, weights) = get_weighted_boons(boon_values)
    val = random.randrange(0, max_weight)
    for k in weights:
        if val < weights[k]:
            return k

