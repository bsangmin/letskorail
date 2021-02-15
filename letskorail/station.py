# coding=utf-8

from typing import List

class Station(object):
    code = None
    name = None
    longitude = None
    latitude = None
    group = None
    major = None
    popup_msg = None
    popup_type = None
    area = None
    stop = None

    def __init__(self, data):
        self.code = data.get("stn_cd")
        self.name = data.get("stn_nm")
        self.longitude = data.get("longitude")
        self.latitude = data.get("latitude")
        self.group = data.get("group")
        self.major = data.get("major")
        self.popup_msg = data.get("popupMessage")
        self.popup_type = data.get("popupType")
        self.area = data.get("area")
        self.stop = data.get("stop")

class Stations(object):
    map_version = None # type str
    count = 0 # type int
    stations = list() # type List[Station]

    def __init__(self, data):
        self.map_version = data.get("map_version")
        self.count = int(data.get("count", 0))
        self.stations = list(data.get("stations"))