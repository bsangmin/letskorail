import json,time,random
from letskorail import Korail
from letskorail.options import AdultPsg
from letskorail.options import TrainType
from letskorail.options import SeatOption
from sendTelegram import sendTelegram
import asyncio

reservation_success = False

with open("secret/info.json", "r") as f:
    info = json.load(f)

def sendMessage(message):
    reservation_success_message = "[예매알림]\n" + message
    asyncio.run(sendTelegram(reservation_success_message))

korail = Korail()

# 로그인
###########################
profile = korail.login(info["id"], info["pw"])

# 승객 설정
###########################
psgrs = [AdultPsg()]

# 열차 조회
###########################
time_table = ["100000","110000","120000","140000","150000","160000","180000"]
while True:
    for _time in time_table:
        try:
            trains = korail.search_train(
                "광천",
                "용산",
                date="20240211",
                time=_time,
                passengers=psgrs,
                train_type=TrainType.ALL,
                include_soldout=True
            )
            print(trains[0].info)
            
            # 열차 예약
            ###########################
            rsv = korail.reserve(trains[0], seat_opt=SeatOption.GENERAL_FIRST)
            print("예매완료")
            print(rsv.info)
            reservation_success = True
            break       
        except:
            time.sleep(random.uniform(0.1685,0.2872))
            pass
    if reservation_success:
        print("텔레그램 전송")
        sendMessage(rsv.info)
        break
