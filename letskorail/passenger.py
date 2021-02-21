# coding=utf-8

# pylint: disable=relative-beyond-top-level

from functools import reduce
from itertools import groupby


class Passenger:
    count = 1
    key = ""
    p_type = ""
    discount_type = ""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("%s is abstarct class" % type(self).__name__)

    def __init_internal__(self, count):
        self.count = count

    def __add__(self, other):
        assert isinstance(other, self.__class__)
        if self.key == other.key:
            return self.__class__(count=self.count + other.count)
        else:
            raise TypeError(
                "other's key({}) is not equal to self's key({}).".format(
                    other.key, self.key
                )
            )

    @staticmethod
    def reduce(psg_list):
        if tuple(filter(lambda x: not isinstance(x, Passenger), psg_list)):
            raise TypeError("Passengers must be based on Passenger")

        groups = groupby(
            sorted(psg_list, key=(lambda x: x.key)),
            lambda x: x.key,
        )

        return tuple(
            filter(
                lambda x: x.count > 0,
                [reduce(lambda a, b: a + b, g) for k, g in groups],
            )
        )

    @staticmethod
    def psg_count(psg_list):
        count = {}
        total = 0
        for ins in _psg_instances:
            count[ins.key] = reduce(
                lambda a, b: a + b.count,
                tuple(filter(lambda x: isinstance(x, ins), psg_list)),
                0,
            )
            total += count[ins.key]

        count["total"] = total

        return count


# "AdultPsg": {"disc": "000", "type": "1"},
# "__nothing1": {"disc": "P11", "type": "1"},
# "ChildPsg": {"disc": "000", "type": "3"},
# "BabyPsg": {"disc": "321", "type": "3"},
# "SeniorPsg": {"disc": "131", "type": "1"},
# "DisabilityAPsg": {"disc": "111", "type": "1"},
# "DisabilityBPsg": {"disc": "112", "type": "1"},
# "__nothing2": {"disc": "173", "type": "1"},


class AdultPsg(Passenger):
    """성인"""

    key = "adult"
    discount_type = "000"
    p_type = "1"

    def __init__(self, count=1):
        Passenger.__init_internal__(self, count)


class TeenPsg(Passenger):
    """청소년 (할인 열차에만 가능)"""

    key = "teenager"
    discount_type = "P11"
    p_type = "1"

    def __init__(self, count=1):
        Passenger.__init_internal__(self, count)


class ChildPsg(Passenger):
    """만6세 이상 13세 미만 아동"""

    key = "child"
    discount_type = "000"
    p_type = "3"

    def __init__(self, count=1):
        Passenger.__init_internal__(self, count)


class BabyPsg(Passenger):
    """만6세 미만 아동 좌석 필요시"""

    key = "baby"
    discount_type = "321"
    p_type = "3"

    def __init__(self, count=1):
        Passenger.__init_internal__(self, count)


class SeniorPsg(Passenger):
    """만65세 이상"""

    key = "senior"
    discount_type = "131"
    p_type = "1"

    def __init__(self, count=1):
        Passenger.__init_internal__(self, count)


class DisabilityAPsg(Passenger):
    """1급 - 3급 중증 장애인"""

    key = "dis_a"
    discount_type = "111"
    p_type = "1"

    def __init__(self, count=1):
        Passenger.__init_internal__(self, count)


class DisabilityBPsg(Passenger):
    """4급 - 6급 경증 장애인"""

    key = "dis_b"
    discount_type = "112"
    p_type = "1"

    def __init__(self, count=1):
        Passenger.__init_internal__(self, count)


_psg_instances = (
    AdultPsg,
    TeenPsg,
    ChildPsg,
    BabyPsg,
    SeniorPsg,
    DisabilityAPsg,
    DisabilityBPsg,
)

# _psg_instances_dict = {ins.key: ins for ins in _psg_instances}

# def psg_instance_name(iterable):
#     names = tuple(_psg_instances_dict[k].__name__ for k in iterable)
#     return ", ".join(names)