# coding=utf-8

import json

from letskorail import Korail
from letskorail.options import AdultPsg, ChildPsg
from letskorail.options import TrainType
from letskorail.options import SeatOption

with open("secret/info.json", "r") as f:
    info = json.load(f)

korail = Korail()

profile = korail.login(info["id"], info["pw"])

psgrs = [AdultPsg(), ChildPsg(2)]

###########################
trains = korail.search_train(
    "청량리",
    "안동",
    date="20210301",
    time="060000",
    passengers=psgrs,
    train_type=TrainType.KTX_EUM,
)

print(trains[0])

###########################
rsv = korail.reserve(
    trains[0], passengers=psgrs, option=SeatOption.SPECIAL_FIRST
)

print(rsv.info)

###########################
korail.cancel(rsv)