# coding=utf-8

# pylint: disable=relative-beyond-top-level,unsubscriptable-object
import re
import requests
import base64
import uuid
from datetime import datetime, timedelta
from typing import Tuple, Optional, Generator, Iterable, Dict, Union

from .exceptions import (
    result_checker,
    NoResultsError,
    SoldOutError,
    DiscountError,
)
from .train import Train, Trains, TrainType, Car, Cars
from .passenger import AdultPsg, Passenger
from .station import Station, Stations
from .reservation import Reservation
from .payment import CreditCard
from .ticket import Ticket
from .discount import Discount


class SeatOption:
    GENERAL_FIRST = "GENERAL_FIRST"  # 일반실 우선
    GENERAL_ONLY = "GENERAL_ONLY"  # 일반실만
    SPECIAL_FIRST = "SPECIAL_FIRST"  # 특실 우선
    SPECIAL_ONLY = "SPECIAL_ONLY"  # 특실만

    def __init__(self):
        raise NotImplementedError("%s is abstarct class" % type(self).__name__)


class URL:
    SCHEME = "https"
    HOST = "smart.letskorail.com"
    PORT = "443"

    DOMAIN = f"{SCHEME}://{HOST}:{PORT}"
    MOBILE = f"{DOMAIN}/classes/com.korail.mobile"

    LOGIN = f"{MOBILE}.login.Login"
    LOGOUT = f"{MOBILE}.login.Logout"

    STATION = f"{MOBILE}.common.stationdata"
    STATION_INFO = f"{MOBILE}.common.stationinfo"

    SCHEDULE = f"{MOBILE}.seatMovie.ScheduleView"

    CARS_INFO = f"{MOBILE}.research.TrainResearch"
    CAR_DETAIL = f"{MOBILE}.research.ResidualSeatsResearch.do"

    RESERVATION = f"{MOBILE}.certification.TicketReservation"
    MY_RESERVATIONS = f"{MOBILE}.reservation.ReservationView"
    MY_RESERVATION_DETAIL = f"{MOBILE}.certification.ReservationList"

    RESERVATION_CANCEL = f"{MOBILE}.reservationCancel.ReservationCancelChk"

    PAYMENT = f"{MOBILE}.payment.ReservationPayment"

    MY_TICKETS = f"{MOBILE}.myTicket.MyTicketList"
    MY_TICKET_DETAIL = f"{MOBILE}.refunds.SelTicketInfo"

    REFUND_INFO = f"{MOBILE}.refunds.CommissionView"
    REFUND_REQ = f"{MOBILE}.refunds.RefundsRequest"

    def __init__(self):
        raise NotImplementedError("%s is abstarct class" % type(self).__name__)


class Profile(object):
    name: str = ""  # strCustNm
    email: str = ""  # strEmailAdr
    sex: str = ""  # strSexDvCd
    member_num: str = ""  # strMbCrdNo
    phone_num: str = ""  # strCpNo
    birthday: str = ""  # strBtdt

    def __init__(self, data):
        self.name = data.get("strCustNm", "")
        self.email = data.get("strEmailAdr", "")
        self.sex = data.get("strSexDvCd", "")
        self.member_num = data.get("strMbCrdNo", "")
        self.phone_num = data.get("strCpNo", "")
        self.birthday = data.get("strBtdt", "")


class Korail(object):
    """Unoffical Korail api

    See details https://github.com/bsangmin/letskorail

    """

    _email_regx = re.compile(r"[^@]+@[^@]+\.[^@]+")
    _phone_regx = re.compile(r"(\d{3})-(\d{3,4})-(\d{4})")

    _device = "AD"
    _version = "201223001"
    _key = "korail1234567890"

    _k_id = None
    _k_pw = None
    _k_pw_b64 = None

    logined = False

    def __init__(self):
        uas = (
            "Dalvik/2.1.0 (Linux; U; Android 11; Pixel 4a (5G) Build/RQ1A.210105.003)",
            "Dalvik/2.1.0 (Linux; U; Android 7.1.2; SM-G965N Build/QP1A.190711.020)",
        )
        ua = uas[0]

        self._sess = requests.Session()
        self._sess.headers.update({"user-agent": ua})

    def _req_data_builder(self, data={}):
        d = {
            "Device": self._device,
            "Version": self._version,
            "Key": self._key,
        }
        d.update(data)
        return d

    def stations(self) -> Stations:
        """Get information for all stations"""
        res = self._sess.get(URL.STATION)
        rst = res.json()
        if result_checker(rst):
            stns = rst["stns"]["stn"]
            stations_ = tuple(Station(st) for st in stns)

        res = self._sess.get(URL.STATION_INFO)
        rst = res.json()
        if result_checker(rst):
            rst.update({"stations": stations_})

            return Stations(rst)

    def login(self, k_id: str, k_pw: str) -> Profile:
        """Login to korail server

        `email`, `cell phone number` or `membership number`

        :return Profile

        """
        self._k_id = k_id
        self._k_pw = k_pw
        self._k_pw_b64 = base64.b64encode(k_pw.encode()).decode()

        if self._email_regx.match(k_id):
            input_flag = "5"
        elif self._phone_regx.match(k_id):
            input_flag = "4"
        else:  # membership number
            input_flag = "2"

        data = self._req_data_builder(
            {
                "txtInputFlg": input_flag,
                "txtMemberNo": self._k_id,
                "txtPwd": self._k_pw_b64,
                "checkValidPw": "Y",
            }
        )

        res = self._sess.post(URL.LOGIN, data=data)
        rst = res.json()

        if result_checker(rst):
            self.logined = True
            return Profile(rst)

    def logout(self) -> None:
        """Logout"""
        self._sess.get(URL.LOGOUT)
        self.logined = False

    def search_train_allday(
        self,
        dpt: str,
        arv: str,
        date: Optional[str] = None,
        time: Optional[str] = None,
        passengers: Optional[Iterable[Passenger]] = None,
        discnt_type: Optional[Discount] = None,
        train_type: TrainType = TrainType.ALL,
        include_soldout: bool = False,
    ) -> Trains:
        """See search_train

        :return Trains
        """
        td = timedelta(minutes=1)
        trains = []

        for _ in range(20):
            try:
                tr = self.search_train(
                    dpt,
                    arv,
                    date,
                    time,
                    passengers,
                    discnt_type,
                    train_type,
                    include_soldout,
                )
                trains.extend(tr)

                next_time = datetime.strptime(tr[-1].dpt_time, "%H%M%S") + td
                time = next_time.strftime("%H%M%S")
            except NoResultsError:
                break
        return Trains(trains)

    def search_train(
        self,
        dpt: str,
        arv: str,
        date: Optional[str] = None,
        time: Optional[str] = None,
        passengers: Optional[Iterable[Passenger]] = None,
        discnt_type: Optional[Discount] = None,
        train_type: TrainType = TrainType.ALL,
        include_soldout: bool = False,
    ) -> Trains:
        """Search trains for specific time and date.

        :param dpt: A departure station

        :param arv: A arrival station

        :param date: (optional) A departure date (format: `yyyyMMDD`)

        :param time: (optional) A departure time (foramt: `hhmmss`)

        :param passengers: (optional) The passengers

        :parm discnt_type: (optional) Discount product

        :param train_type: (optional) A type of train

        :param include_soldout: (optional) includes trains which has no seats

        :return Trains
        """

        if not date:
            date = datetime.now().strftime("%Y%m%d")
        if not time:
            time = datetime.now().strftime("%H%M%S")
        if not passengers:
            passengers = [AdultPsg(1)]

        passengers = Passenger.reduce(passengers)
        count = Passenger.psg_count(passengers)

        if isinstance(discnt_type, Discount):
            rst, msg = discnt_type._vaild(passengers)
            if not rst:
                raise DiscountError(msg)
        else:
            discnt_type = None

        discnt_no = discnt_type.disc_code if discnt_type else ""
        menu_id = "41" if discnt_type else "11"

        data = self._req_data_builder(
            {
                # 1: 직통, 2: 환승
                "radJobId": "1",
                # 열차 종류
                "selGoTrain": train_type,
                # 할인 수단
                "txtGdNo": discnt_no,
                # 출발 날짜
                "txtGoAbrdDt": date,
                # 도착역
                "txtGoEnd": arv,
                # 출발 시간
                "txtGoHour": time,
                # 출발역
                "txtGoStart": dpt,
                # 할인 메뉴 (일반: 11, 청춘,다자녀: 41, 4인동반: 51)
                "txtMenuId": menu_id,
                # 성인 승객
                "txtPsgFlg_1": count["adult"] + count["teenager"],
                # 어린이 승객(유아 포함)
                "txtPsgFlg_2": count["child"] + count["baby"],
                # 시니어 승객
                "txtPsgFlg_3": count["senior"],
                # 중증장애 승객
                "txtPsgFlg_4": count["dis_a"],
                # 경증장애 승객
                "txtPsgFlg_5": count["dis_b"],
                # 순방향, 역방향
                "txtSeatAttCd_2": "000",
                # 창측, 내측
                "txtSeatAttCd_3": "000",
                # 015: 일반석 018: 2층석
                # 019: 유아동반석 021: 휠체어석 028: 전동휠체어석
                # 032: 자전거 052: 대피도우미
                "txtSeatAttCd_4": "015",
                # 열차 그룹
                "txtTrnGpCd": train_type,
                # 인접역 출력
                "adjStnScdlOfrFlg": "N",
                # srtCheckYn 값에 따라 감
                "ebizCrossCheck": "N",
                # 왕복
                "rtYn": "N",
                # SRT 출력
                "srtCheckYn": "N",
            }
        )

        res = self._sess.post(URL.SCHEDULE, data=data)
        rst = res.json()

        trains = tuple()
        if result_checker(rst):
            train_infos = rst["trn_infos"]["trn_info"]

            trains = tuple(Train(t) for t in train_infos)

            if not include_soldout:
                trains = tuple(filter(lambda x: x.has_seat(), trains))

            if len(trains) == 0:
                raise NoResultsError("조건에 맞는 열차가 없습니다.")

        # Generator
        def car_seats(data):
            res = self._sess.post(URL.CAR_DETAIL, data=data)
            rst = res.json()
            if result_checker(rst):
                yield rst

        # Generator
        def cars_info(payload):
            cars = list()

            for data in payload:
                res = self._sess.post(URL.CARS_INFO, data=data)
                rst = res.json()

                if result_checker(rst):
                    c_info = rst["srcar_infos"]["srcar_info"]
                    cars_ = tuple(Car(c) for c in c_info)

                    for c in cars_:
                        tmp = dict(data)
                        tmp.update({"txtSrcarNo": c.h_srcar_no})

                        c._set_seats(car_seats(tmp))

                    cars.extend(cars_)

            yield Cars(cars)

        for t in trains:
            t.psgr_count = count
            t.discount_no = discnt_no
            t.menu_id = menu_id

            tmp = self._req_data_builder(
                {
                    "txtArvRsStnCd": t.arv_code,
                    "txtArvStnRunOrdr": t.h_arv_stn_run_ordr,
                    "txtDptDt": t.dpt_date,
                    "txtDptRsStnCd": t.dpt_code,
                    "txtDptStnRunOrdr": t.h_dpt_stn_run_ordr,
                    "txtGdNo": data.get("txtGdNo", ""),
                    "txtMenuId": data.get("txtMenuId", "11"),
                    "txtPsrmClCd": "1",
                    "txtRunDt": t.run_date,
                    "txtSeatAttCd": data.get("txtSeatAttCd_4", "015"),
                    "txtTotPsgCnt": count["total"],
                    "txtTrnClsfCd": t.train_type,
                    "txtTrnGpCd": t.train_group,
                    "txtTrnNo": t.train_no,
                }
            )

            payload = []
            if not t.general_seat == "00":
                payload.append(tmp)

            if not t.special_seat == "00":
                tmp2 = dict(tmp)
                tmp2.update({"txtPsrmClCd": "2"})
                payload.append(tmp2)

            t._set_cars(cars_info(payload))

        return Trains(trains)

    def _seat_type(self, train, option, ignore_soldout):
        seat_type = "1"

        if ignore_soldout:
            if option == SeatOption.GENERAL_ONLY:
                seat_type = "1"
            elif option == SeatOption.SPECIAL_ONLY:
                seat_type = "2"
            else:
                raise TypeError(
                    "Just allowed GENERAL_ONLY or SPECIAL_ONLY when ignore_soldout is True"
                )
        elif not train.has_seat():
            raise SoldOutError("매진입니다.")
        elif option == SeatOption.GENERAL_ONLY:
            if train.has_general_seat():
                seat_type = "1"
            else:
                raise SoldOutError("일반석 매진입니다.")
        elif option == SeatOption.SPECIAL_ONLY:
            if train.has_special_seat():
                seat_type = "2"
            else:
                raise SoldOutError("특실 매진입니다.")
        elif option == SeatOption.GENERAL_FIRST:
            if train.has_general_seat():
                seat_type = "1"
            else:
                seat_type = "2"
        elif option == SeatOption.SPECIAL_FIRST:
            if train.has_special_seat():
                seat_type = "2"
            else:
                seat_type = "1"
        return seat_type

    def reserve(
        self,
        train: Train,
        seat_opt: Union[SeatOption, Iterable] = SeatOption.GENERAL_ONLY,
        ignore_soldout: bool = False,
    ) -> Reservation:
        """Reserve train.

        :return Reservation

        """
        iter_type = isinstance(seat_opt, (list, tuple, set))
        if iter_type:
            seat_type = seat_opt[0]["psrm_cl_cd"]
        else:
            seat_type = self._seat_type(train, seat_opt, ignore_soldout)

        count = train.psgr_count

        data = self._req_data_builder(
            {
                # ???
                "hidFreeFlg": "N",
                # 도착역 코드
                "txtArvRsStnCd1": train.arv_code,
                "txtArvStnConsOrdr1": train.h_arv_stn_cons_ordr,
                "txtArvStnRunOrdr1": train.h_arv_stn_run_ordr,
                # 출발역 코드
                "txtDptRsStnCd1": train.dpt_code,
                "txtDptStnConsOrdr1": train.h_dpt_stn_cons_ordr,
                "txtDptStnRunOrdr1": train.h_dpt_stn_run_ordr,
                # 시간 정보
                "txtDptDt1": train.dpt_date,
                "txtDptTm1": train.dpt_time,
                # 할인 정보
                "txtGdNo": train.discount_no,
                # ???
                "txtJobId": "1101",
                # 여정 중 열차 대수(환승일때 2)
                "txtJrnyCnt": "1",
                # txtJrnySqnoX X번째 열차 시퀀스
                "txtJrnySqno1": "001",
                # txtJrnyTpCdX X번째 열차 타입 코드
                "txtJrnyTpCd1": "11",  # 환승일때 14
                # 할인 타입
                "txtMenuId": train.menu_id,
                # 좌석 타입
                "txtPsrmClCd1": seat_type,
                # 출발 날짜
                "txtRunDt1": train.run_date,
                # 열차 타입
                "txtTrnClsfCd1": train.train_type,
                # 열차 그룹
                "txtTrnGpCd1": train.train_group,
                # 열차 번호
                "txtTrnNo1": train.train_no,
                # ???
                "txtStndFlg": "N",
                # ???
                "txtChgFlg1": "N",
                # ???
                "txtSeatAttCd1": "000",
                # 순방, 역방(000 고정)
                "txtSeatAttCd2": "000",
                # 창측, 내측(000 고정)
                "txtSeatAttCd3": "000",
                # 좌석 타입
                "txtSeatAttCd4": "015",
                # ???
                "txtSeatAttCd5": "000",
                # 승객별 정보
                "txtTotPsgCnt": count.get("total", 0),
                "txtCompaCnt1": count.get("adult", 0),
                "txtCompaCnt2": count.get("teenager", 0),
                "txtCompaCnt3": count.get("child", 0),
                "txtCompaCnt4": count.get("baby", 0),
                "txtCompaCnt5": count.get("senior", 0),
                "txtCompaCnt6": count.get("dis_a", 0),
                "txtCompaCnt7": count.get("dis_b", 0),
                "txtCompaCnt8": count.get("unknown", 0),
                "txtDiscKndCd1": "000",
                "txtDiscKndCd2": "P11",
                "txtDiscKndCd3": "000",
                "txtDiscKndCd4": "321",
                "txtDiscKndCd5": "131",
                "txtDiscKndCd6": "111",
                "txtDiscKndCd7": "112",
                "txtDiscKndCd8": "173",
                "txtPsgTpCd1": "1",
                "txtPsgTpCd2": "1",
                "txtPsgTpCd3": "3",
                "txtPsgTpCd4": "3",
                "txtPsgTpCd5": "1",
                "txtPsgTpCd6": "1",
                "txtPsgTpCd7": "1",
                "txtPsgTpCd8": "1",
            }
        )
        if iter_type:
            data.update({"txtSrcarCnt": len(seat_opt)})
            for idx, o in enumerate(seat_opt):
                data.update(
                    {
                        f"txtSeatNo{idx+1}": o["seat_no"],
                        f"txtSrcarNo{idx+1}": o["car_no"],
                    }
                )

        res = self._sess.post(URL.RESERVATION, data=data)
        rst = res.json()
        if result_checker(rst):
            return self.reservations(rst["h_pnr_no"])[0]

    # def seat_choice(self, train: Train, count: Dict):
    #     cars = train.cars

    def reservations(self, rsv_no: Optional[str] = None) -> Tuple[Reservation]:
        """Get my all reservations

        :return List[reservation.Reservation]

        If you want to see specific your reservation
        set `rsv_no` parameter

        """

        data = self._req_data_builder()

        res = self._sess.post(URL.MY_RESERVATIONS, data=data)
        rst = res.json()

        if result_checker(rst):
            my_rsv = []

            rsv_infos = rst["jrny_infos"]["jrny_info"]

            if rsv_no:
                for r in rsv_infos:
                    if rsv_no == r["train_infos"]["train_info"][0]["h_pnr_no"]:
                        my_rsv = [Reservation(r)]
                        break
            else:
                my_rsv = [Reservation(r) for r in rsv_infos]

            if len(my_rsv) == 0:
                raise NoResultsError("예약을 확인할 수 없습니다.")

            for r in my_rsv:
                data = self._req_data_builder({"hidPnrNo": r.rsv_no})
                res = self._sess.post(URL.MY_RESERVATION_DETAIL, data=data)
                rst = res.json()
                if result_checker(rst):
                    r._set_seats(rst)

            return tuple(my_rsv)

    def cancel(self, rsv: Reservation) -> bool:
        """Cancel your reservated journey

        return bool

        `reservation.Reservation` object

        """
        data = self._req_data_builder(
            {
                "hidRsvChgNo": rsv.rsv_chg_no,
                "txtJrnyCnt": rsv.journey_cnt,
                "txtJrnySqno": rsv.journey_no,
                "txtPnrNo": rsv.rsv_no,
            }
        )
        res = self._sess.post(URL.RESERVATION_CANCEL, data=data)
        rst = res.json()

        return result_checker(rst)

    def _ticket_detail(self, ticket):
        data = self._req_data_builder(
            {
                "h_orgtk_ret_pwd": ticket.h_tk_ret_pwd,
                "h_orgtk_ret_sale_dt": ticket.h_sale_dt[-4:],
                "h_orgtk_sale_sqno": ticket.h_sale_sqno[-5:],
                "h_orgtk_wct_no": ticket.h_wct_no[-5:],
                "h_purchase_history": "N",
            }
        )

        res = self._sess.post(URL.MY_TICKET_DETAIL, data=data)
        rst = res.json()

        if result_checker(rst):
            ticket._detail(rst)

    def buy_ticket(self, rsv: Reservation, cc: CreditCard) -> Ticket:
        """Buy ticket"""
        try:
            from .purchase import buy_ticket

            rst = buy_ticket(self, URL.PAYMENT, rsv, cc)

            if result_checker(rst):
                tk = Ticket(rst)
                self._ticket_detail(tk)

                return tk

        except ImportError:
            return None

    def tickets(self) -> Tuple[Ticket]:
        """Get your tickets"""
        data = self._req_data_builder(
            {
                "h_abrd_dt_from": "",
                "h_abrd_dt_to": "",
                "h_page_no": "1",
                "hiduserYn": "Y",
                "txtDeviceId": uuid.uuid4(),
                "txtIndex": "1",
            }
        )

        res = self._sess.post(URL.MY_TICKETS, data=data)
        rst = res.json()

        if result_checker(rst):
            tk_list = rst["reservation_list"]

            tickets = tuple(Ticket(t) for t in tk_list)

            for t in tickets:
                self._ticket_detail(t)

            # for tkl in tk_list:
            #     tk = Ticket(tkl)
            #     tk = self._ticket_detail(tk)
            #     tickets.append(tk)

            return tickets

    def refund(self, ticket: Ticket) -> bool:
        """Refund your a ticket"""
        data = self._req_data_builder(
            {
                "h_comp_cert_no": "",
                "h_comp_nm": "",
                "h_orgtk_ret_pwd": ticket.h_tk_ret_pwd[-2:],
                "h_orgtk_ret_sale_dt": ticket.h_sale_dt[-4:],
                "h_orgtk_sale_sqno": ticket.h_sale_sqno[-5:],
                "h_orgtk_wct_no": ticket.h_wct_no[-5:],
            }
        )

        res = self._sess.post(URL.REFUND_INFO, data=data)
        rst = res.json()

        if result_checker(rst):
            ti = ticket.train_info
            sq = sorted(ti.keys(), key=(lambda x: int(x)))[0]
            data = self._req_data_builder(
                {
                    "h_mlg_stl": ti[sq]["seats"][0].h_mlg_apl_flg,
                    "h_orgtk_ret_pwd": ticket.h_tk_ret_pwd[-2:],
                    "h_orgtk_sale_dt": ticket.h_sale_dt[-8:],
                    "h_orgtk_sale_sqno": ticket.h_sale_sqno[-5:],
                    "h_orgtk_sale_wct_no": ticket.h_wct_no[-5:],
                    "h_ret_amt": rst.get("ret_amt"),
                    "h_ret_fee": rst.get("ret_fee"),
                    "latitude": "",
                    "longitude": "",
                    "tk_ret_tms_dv_cd": rst.get("tk_ret_tms_dv_cd"),
                    "trnNo": ti[sq]["train"].train_no,
                    "txtPnrNo": rst.get("pnr_no"),
                }
            )

            res = self._sess.post(URL.REFUND_REQ, data=data)
            rst = res.json()

            return result_checker(rst)
