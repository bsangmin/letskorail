# coding=utf-8

import json

from letskorail import Korail
from letskorail.options import AdultPsg, ChildPsg
from letskorail.options import TrainType
from letskorail.options import SeatOption
from letskorail.options import YouthDisc

with open("secret/info.json", "r") as f:
    info = json.load(f)

korail = Korail(info)

###########################
# 디바이스의 uuid를 알고 있을 떄
###########################
korail.set_uuid(info["uuid"])

###########################
# 로그인
###########################
profile = korail.login(info["id"], info["pw"])

###########################
# 승객 설정
###########################
psgrs = [AdultPsg(), ChildPsg(2)]

###########################
# 열차 조회
###########################
trains = korail.search_train(
    "청량리",
    "안동",
    date="20220101",
    time="060000",
    passengers=psgrs,
    train_type=TrainType.KTX_EUM,
)

###########################
# 할인 상품 열차 조회
###########################
trains = korail.search_train(
    "청량리",
    "안동",
    discnt_type=YouthDisc(),  # 힘내라 청춘 상품
    passengers=[AdultPsg()]
    # 힘내라 청춘은 성인 1명 대상임
    # 인원을 초과하면 DiscountError exception 발생
    # 자세한 조건은 코레일 app이나 discount.py 참고
)
print(trains[0])

###########################
# 열차 예약
###########################
rsv = korail.reserve(trains[0], seat_opt=SeatOption.SPECIAL_FIRST)

###########################
# 선호 좌석 예약
###########################
seats = (
    trains[0].cars[3].select_seats(location="출입문", position="내측"),
)  # 3호차 좌석 예약

rsv = korail.reserve(trains[0], seat_opt=seats)  # Iterable 형태로 넘겨줘야 함
print(rsv.info)

###########################
# 예약 취소
###########################
korail.cancel(rsv)

###########################
# 정기권 조회 및 예약
###########################
ticket = korail.pass_ticket("내일로")
trains = korail.pass_search(ticket, "서울", "부산", "20220207", "000000")
rsv = korail.pass_reserve(ticket, trains[0])
print(rsv.info)