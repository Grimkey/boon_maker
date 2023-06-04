from __future__ import annotations

import json
import random
from typing import Tuple, Optional

from pydantic import BaseModel

from boon import Boon, BoonRecord, pick_boon
from kindred import Kindred, find_kindred_from_name, get_weighted_vampires, pick_kindred

# Easy to update and print version
BoonLog = dict[int, dict[int, dict[str, int]]]


class City(BaseModel):
    kindred: dict[int, Kindred]
    boon_log: list[BoonRecord]
    boon_values: list[Boon]

    @staticmethod
    def ctor(vampire_file: str, boon_file: Optional[str], boon_values: list[Boon]) -> City:
        kindred = Kindred.read_from_file(vampire_file)
        boon_log = _read_boon_file(boon_file, kindred) if boon_file else []
        return City(kindred=kindred, boon_log=boon_log, boon_values=boon_values)

    def print_log(self):
        print_log = _aggregated_log(self.boon_log)
        for k in print_log:
            print(f"{self.kindred[k].name} is owned the following:")
            for debter in print_log[k]:
                for t in print_log[k][debter]:
                    print(f"\tFrom {self.kindred[debter].name} {print_log[k][debter][t]} {t} boons")
        print(f"Total boons {len(self.boon_log)}")

    def print_records(self, records: list[BoonRecord]):
        for k in records:
            owed = self.kindred[k.owed].name
            debter = self.kindred[k.debter].name
            print(f"{owed} is owned a {k.type} boon from {debter}")

    def print_resolved_records(self, records: list[BoonRecord]):
        for k in records:
            owed = self.kindred[k.owed].name
            debter = self.kindred[k.debter].name
            print(f"{owed} has paid off a {k.type} boon from {debter}")

    def to_record(self) -> list[dict]:
        record: list[dict] = []
        for k in self.boon_log:
            owed = self.kindred[k.owed].name
            debter = self.kindred[k.debter].name
            record.append({
                "owed": owed,
                "debter": debter,
                "num": k.num,
                "type": k.type,
            })
        return record

    def remove_boons(self, num: int) -> list[BoonRecord]:
        removed: list[BoonRecord] = []
        for _ in range(0, num):
            popped = self.boon_log.pop(random.randrange(len(self.boon_log)))
            removed.append(popped)
        return removed

    def add_boons(self, num_to_add: int) -> list[BoonRecord]:
        boon_list: list[BoonRecord] = []
        (max_weight, weights) = get_weighted_vampires(self.kindred)
        for i in range(0, num_to_add):
            owed = pick_kindred(max_weight, weights)
            (owing_max_weight, owing_weights) = get_weighted_vampires(self.kindred, True, owed)
            owing = pick_kindred(owing_max_weight, owing_weights)
            boon = pick_boon(self.boon_values)
            boon_list.append(BoonRecord(
                owed=owed,
                debter=owing,
                type=boon,
                num=1,
            ))
        return boon_list


def _aggregated_log(boon_log: list[BoonRecord]) -> BoonLog:
    aggregated_log: BoonLog = {}
    for boon in boon_log:
        _add_boon_to_list(aggregated_log, boon.owed, boon.debter, boon.type)
    return aggregated_log


class BoonFileRecord(BaseModel):
    owed: str
    debter: str
    type: str


def _read_boon_file(name: str, kindred: dict[int, Kindred]) -> list[BoonRecord]:
    records: list[BoonRecord] = []
    with open(name) as f:
        data: list[dict] = json.load(f)
        for entry in data:
            records.append(_lookup_kindred(BoonFileRecord(**entry), kindred))
        return records


def _lookup_kindred(record: BoonFileRecord, kindred: dict[int, Kindred]) -> BoonRecord:
    owed_id = find_kindred_from_name(record.owed, kindred)
    if owed_id == -1:
        raise Exception(f"Cannot find vampire named {record.owed}")
    debter_id = find_kindred_from_name(record.debter, kindred)
    if debter_id == -1:
        raise Exception(f"Cannot find vampire named {record.debter}")

    return BoonRecord(owed=owed_id, debter=debter_id, type=record.type)


def _add_boon_to_list(boon_log: BoonLog, owed: int, debter: int, new_boon: str, adding: int = 1):
    if boon_log.get(owed) is None:
        boon_log[owed] = {}
    if boon_log[owed].get(debter) is None:
        boon_log[owed][debter] = {}
    if boon_log[owed][debter].get(new_boon) is None:
        boon_log[owed][debter][new_boon] = 0
    boon_log[owed][debter][new_boon] += adding
