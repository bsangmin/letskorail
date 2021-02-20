# coding=utf-8

from six import with_metaclass


def result_checker(rst):
    h_msg_cd = rst.get("h_msg_cd", "")
    h_msg_txt = rst.get("h_msg_txt", "")

    error = list(
        filter(
            lambda x: h_msg_cd in x,
            (NoResultsError, NeedToLoginError, SoldOutError, LoginError),
        )
    )

    if error:
        raise error[0](h_msg_txt, h_msg_cd)

    if rst.get("strResult", "") == "FAIL":
        raise KorailError(h_msg_txt, h_msg_cd)
    else:
        return True


class _exceptionForm(type):
    codes = set()

    def __contains__(cls, item):
        return item in cls.codes


class KorailError(with_metaclass(_exceptionForm, Exception)):
    """Korail Base Error Class"""

    def __init__(self, msg, code=None):
        self.msg = msg
        self.code = code

    def __str__(self):
        return "%s (%s)" % (self.msg, self.code)


class LoginError(KorailError):
    codes = {"WRC000391"}

    def __init__(self, msg="Wrong id or password", code=None):
        KorailError.__init__(self, msg, code)


class NeedToLoginError(KorailError):
    """Korail NeedToLogin Error Class"""

    codes = {"P058"}

    def __init__(self, msg="Need to Login", code=None):
        KorailError.__init__(self, msg, code)


class NoResultsError(KorailError):
    """Korail NoResults Error Class"""

    codes = {
        "P100",  # 예약된 열차가 없음
        "WRG000000",
        "WRD000061",  # 직통열차는 없지만, 환승으로 조회 가능합니다.
        "WRT300005",
    }

    def __init__(self, msg="No Results", code=None):
        KorailError.__init__(self, msg, code)


class SoldOutError(KorailError):
    codes = {"ERR211161"}

    def __init__(self, msg="Sold out", code=None):
        KorailError.__init__(self, msg, code)


class DiscountError(Exception):
    pass