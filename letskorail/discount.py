# coding=utf-8

from typing import Tuple

from .passenger import (
    Passenger,
    AdultPsg,
    TeenPsg,
    ChildPsg,
    BabyPsg,
    SeniorPsg,
    DisabilityAPsg,
    DisabilityBPsg,
)


class Discount:
    title = ""
    disc_code = ""

    max_cnt = 0
    min_cnt = 0

    allow_psg = dict()

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("%s is abstarct class" % type(self).__name__)

    def __repr__(self):
        return self.title

    def _vaild(self, psgrs) -> Tuple[bool, str]:
        def name(objs):
            def _name(o):
                return o.__name__ if isinstance(o, type) else type(o).__name__

            if not isinstance(objs, (list, tuple, set)):
                return _name(objs)

            return ", ".join(tuple(_name(o) for o in objs))

        insts = set(type(ins) for ins in psgrs)
        essential_psgr = set(
            filter(lambda x: self.allow_psg[x]["min"] > 0, self.allow_psg)
        )

        if not (insts & essential_psgr):
            return False, f"{name(self)}에 {name(essential_psgr)} 승객이 포함되야 합니다."

        total = 0
        for p in psgrs:
            total += p.count

            allow = self.allow_psg.get(type(p))
            if not allow:
                return False, f"{name(p)}은(는) {name(self)}에 적용할 수 없습니다."

            if not (allow["min"] <= p.count <= allow["max"]):
                return False, f"{name(p)}은(는) {allow['max']}명을 초과할 수 없습니다."

        if not (self.min_cnt <= total <= self.max_cnt):
            return False, f"{self.title} 최대 적용 인원은 {self.max_cnt}명 입니다."

        return True, ""


class TeenDisc(Discount):
    """청소년 드림"""

    def __init__(self):
        self.title = "청소년 드림"
        self.disc_code = "B121410002GY"
        self.max_cnt = 9
        self.min_cnt = 1

        self.allow_psg = {
            AdultPsg: {"min": 0, "max": 9},
            TeenPsg: {"min": 1, "max": 1},
            ChildPsg: {"min": 0, "max": 9},
            SeniorPsg: {"min": 0, "max": 9},
            DisabilityAPsg: {"min": 0, "max": 9},
            DisabilityBPsg: {"min": 0, "max": 9},
        }


class YouthDisc(Discount):
    """힘내라 청춘"""

    def __init__(self):
        self.title = "힘내라 청춘"
        self.disc_code = "Y20150924001"
        self.max_cnt = 1
        self.min_cnt = 1

        self.allow_psg = {
            AdultPsg: {"min": 1, "max": 1},
        }


class MomDisc(Discount):
    """맘편한 KTX"""

    def __init__(self):
        self.title = "맘편한 KTX"
        self.disc_code = "Y20150924002"
        self.max_cnt = 2
        self.min_cnt = 1

        self.allow_psg = {
            AdultPsg: {"min": 1, "max": 2},
            ChildPsg: {"min": 0, "max": 1},
            BabyPsg: {"min": 0, "max": 1},
            SeniorPsg: {"min": 0, "max": 1},
            DisabilityAPsg: {"min": 0, "max": 1},
            DisabilityBPsg: {"min": 0, "max": 1},
        }


class FamilyDisc(Discount):
    """다자녀행복"""

    def __init__(self):
        self.title = "다자녀행복"
        self.disc_code = "Y20151104001"
        self.max_cnt = 9
        self.min_cnt = 1

        self.allow_psg = {
            AdultPsg: {"min": 1, "max": 9},
            ChildPsg: {"min": 0, "max": 8},
            BabyPsg: {"min": 0, "max": 8},
        }


class StoGDisc(Discount):
    """서울광명 특가"""

    def __init__(self):
        self.title = "서울광명 특가"
        self.disc_code = "Y20190313001"
        self.max_cnt = 9
        self.min_cnt = 1

        self.allow_psg = {
            AdultPsg: {"min": 1, "max": 9},
        }


class BasicLive(Discount):
    """기차누리(기초생활수급자)"""

    def __init__(self):
        self.title = "기차누리(기초)"
        self.disc_code = "Y20180208001"
        self.max_cnt = 1
        self.min_cnt = 1

        self.allow_psg = {
            AdultPsg: {"min": 1, "max": 1},
        }