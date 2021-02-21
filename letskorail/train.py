# coding=utf-8

from typing import Generator, Tuple, Dict, List
from .constants import window_side, seat_type
from .exceptions import KorailError


class TrainType:
    """type of train
    > ex) TrainType.KTX

    > ex) TrainType.ITX_CHEONGCHUN

    KTX_ALL == KTX == KTX_SANCHEON == KTX_EUM

    ITX_SAEMAEUL == SAEMAEUL

    MUGUNGHWA == NURIRO
    """

    KTX_ALL = KTX_SANCHEON = KTX_EUM = "100"
    SAEMAEUL = ITX_SAEMAEUL = "101"
    MUGUNGHWA = NURIRO = "102"
    TONGGUEN = "103"
    ITX_CHEONGCHUN = "104"
    AIRPORT = "105"
    ALL = "109"

    def __init__(self):
        raise NotImplementedError("%s is abstarct class" % type(self).__name__)


class Seat(object):
    sale_psb = None
    near_door = None
    near_wind = None
    seat_type = None

    seat_no = None
    seat_no2 = None
    direction = None
    raw = None

    def __init__(self, data):
        if data["h_for_rev_dir_dv"] == "009":
            direction = "순방향"
        elif data["h_for_rev_dir_dv"] == "010":
            direction = "역방향"
        else:
            direction = data["h_for_rev_dir_dv"]

        self.sale_psb = data.get("h_sale_psb_flg", "N") == "Y"
        self.near_door = data.get("h_door_nbor_flg", "N") == "Y"
        self.near_wind = window_side[data.get("h_sigl_win_in_dv", "012")]
        self.seat_type = seat_type[data.get("h_dmd_seat_att", "015")]
        self.seat_no = data.get("h_con_seat_no", "0A")
        self.seat_no2 = data.get("h_seat_no", "0")
        self.direction = direction
        self.raw = data


class Seats(object):
    car_no = None
    reverse_car = None
    max_seat = None
    psb_seat = None
    arr_seat = None
    seat_info = dict()

    def __init__(self, data):
        self.reverse_car = data.get("h_seat_dir_cd", "1") == "2"
        self.max_seat = int(data.get("h_max_seat_no", 0))
        self.psb_seat = int(data.get("h_psb_seat_cnt", 0))
        self.arr_seat = int(data.get("h_seat_arr_info", 0))
        self.car_no = data.get("h_srcar_no")

        for s in data["seat_infos"]["seat_info"]:
            s_no = s["h_con_seat_no"]
            if s_no == "0A":
                continue

            self.seat_info[s_no] = Seat(s)

    def _select_seat(
        self,
        location,
        direction,
        position,
        seat_type,
    ) -> Dict:

        si = self.seat_info

        def _filter(o):
            return (
                o.sale_psb
                and o.near_wind == position
                and o.direction == direction
                and o.seat_type == seat_type
            )

        condition = set(filter(lambda x: _filter(si[x]), si))

        if not condition:
            raise KorailError(f"조건에 맞는 좌석이 없습니다.")

        if location == "중앙":
            pos = 0
        elif location == "출입문":
            pos = -1

        def _sort(o):
            new_no = int(int(self.max_seat) / 2) - int(o.seat_no2)
            return abs(new_no)

        seat = sorted(condition, key=(lambda x: _sort(si[x])))[pos]

        return {
            "car_no": self.car_no,
            "seat_no": si[seat].seat_no2,
            "seat": seat,
        }


class Car(object):
    h_seat_cnt = None
    h_rest_seat_cnt = None
    h_srcar_no = None
    h_psrm_cl_cd = None
    h_psrm_cl_nm = None
    special_seats = None

    _gen: Generator = None
    _seats: Seats = None

    def __init__(self, data):
        self.h_srcar_no = data.get("h_srcar_no")
        self.h_seat_cnt = data.get("h_seat_cnt")
        self.h_rest_seat_cnt = data.get("h_rest_seat_cnt")
        self.h_psrm_cl_cd = data.get("h_psrm_cl_cd")
        self.h_psrm_cl_nm = data.get("h_psrm_cl_nm")

        ci = data.get("seatAttInfos")
        if ci:
            self.special_seats = tuple(c.get("seatAttCd", "015") for c in ci)

    def _set_seats(self, gen: Generator):
        assert isinstance(gen, Generator)
        self._gen = gen

    @property
    def seats(self) -> Seats:
        try:
            rst = next(self._gen)
            self._seats = Seats(rst)

        except StopIteration:
            pass

        return self._seats

    def select_seat(
        self,
        location="중앙",
        direction="순방향",
        position="창측",
        seat_type="일반석",
    ) -> Dict:

        data = self.seats._select_seat(location, direction, position, seat_type)
        data.update({"psrm_cl_cd": self.h_psrm_cl_cd})

        return data


class Cars:
    def __init__(self, cars: Tuple[Car]):
        self._cars = {c.h_srcar_no: c for c in cars}

    def __getitem__(self, idx) -> Car:
        if not isinstance(idx, int):
            raise KeyError(f"key '{idx}' is not int type")

        v = self._cars.get(f"{idx:04d}")
        if not v:
            raise KorailError(f"조회가능한 칸: {self.car_list()}")

        return v

    def car_list(self) -> List:
        return sorted([int(k) for k in self._cars.keys()])


class Train(object):
    # 열차 타입 h_trn_clsf_cd
    train_type = None
    # 열차 그룹 h_trn_gp_cd
    train_group = None
    # 열차 이름 h_trn_clsf_nm
    train_name = None
    # 열차 번호 h_trn_no
    train_no = None
    # 출발역 이름 h_dpt_rs_stn_nm
    dpt_name = None
    # 출발역 코드 h_dpt_rs_stn_cd
    dpt_code = None
    # 출발 날짜 h_dpt_dt (yyyyMMDD)
    dpt_date = None
    # 출발 시간 h_dpt_tm (hhmmss)
    dpt_time = None
    # 도착역 이름 h_arv_rs_stn_nm
    arv_name = None
    # 도착역 코드 h_arv_rs_stn_cd
    arv_code = None
    # 도착 날짜 h_arv_dt (yyyyMMDD)
    arv_date = None
    # 도착 시간 h_arv_tm (hhmmss)
    arv_time = None
    # 운행 날짜 h_run_dt (yyyyMMDD)
    run_date = None
    # 지연(hhmm) h_expct_dlay_hr
    delay_time = None
    # 예약 가능 h_rsv_psb_flg ('Y' or 'N')
    reserve_possible = False
    # 예약 가능 msg h_rsv_psb_nm
    reserve_possible_name = None
    # 특실 예약 가능 00: 특실칸 없음 11: 가능 13: 매진 h_spe_rsv_cd
    special_seat = None
    # 일반 예약 가능 00: 일반칸 없음 11: 가능 13: 매진 h_gen_rsv_cd
    general_seat = None
    # 일반실 가격(할인 적용) h_rcvd_amt
    general_price = None
    # 특실 가격(할인 적용) h_rcvd_fare
    special_price = None
    # 할인 비율 h_train_disc_gen_rt
    sale_percent = None
    # 예약시 필요 정보
    h_dpt_stn_cons_ordr = None
    # 예약시 필요 정보
    h_arv_stn_cons_ordr = None
    # 예약시 필요 정보
    h_dpt_stn_run_ordr = None
    # 예약시 필요 정보
    h_arv_stn_run_ordr = None

    ### 예약 조회시 set
    # 1개의 예약에 있는 기차 시퀀스 h_jrny_sqno
    journey_no = None
    # 예약 번호 h_pnr_no
    rsv_no = None
    #########

    # 예약 타입 enum
    h_rsv_tp_cd = None
    # enum_h_jrny_tp_cd
    h_jrny_tp_cd = None

    psgr_count = dict()
    discount_no = ""
    menu_id = ""

    _gen: Generator = None
    _cars: Cars = None

    def __init__(self, data):
        # 열차 타입 h_trn_clsf_cd
        self.train_type = data.get("h_trn_clsf_cd")
        # 열차 그룹 h_trn_gp_cd
        self.train_group = data.get("h_trn_gp_cd")
        # 열차 이름 h_trn_clsf_nm
        self.train_name = data.get("h_trn_clsf_nm")
        # 열차 번호 h_trn_no
        self.train_no = data.get("h_trn_no")
        # 출발역 이름 h_dpt_rs_stn_nm
        self.dpt_name = data.get("h_dpt_rs_stn_nm")
        # 출발역 코드 h_dpt_rs_stn_cd
        self.dpt_code = data.get("h_dpt_rs_stn_cd")
        # 출발 날짜 h_dpt_dt (yyyyMMDD)
        self.dpt_date = data.get("h_dpt_dt")
        # 출발 시간 h_dpt_tm (hhmmss)
        self.dpt_time = data.get("h_dpt_tm")
        # 도착역 이름 h_arv_rs_stn_nm
        self.arv_name = data.get("h_arv_rs_stn_nm")
        # 도착역 코드 h_arv_rs_stn_cd
        self.arv_code = data.get("h_arv_rs_stn_cd")
        # 도착 날짜 h_arv_dt (yyyyMMDD)
        self.arv_date = data.get("h_arv_dt")
        # 도착 시간 h_arv_tm (hhmmss)
        self.arv_time = data.get("h_arv_tm")
        # 운행 날짜 h_run_dt (yyyyMMDD)
        self.run_date = data.get("h_run_dt")
        # 소요시간 h_run_tm (hhmm)
        self.run_time = data.get("h_run_tm")
        # 지연(hhmm) h_expct_dlay_hr
        self.delay_time = data.get("h_expct_dlay_hr")
        # 예약 가능 h_rsv_psb_flg ('Y' or 'N')
        self.reserve_possible = (
            True if data.get("h_rsv_psb_flg") == "Y" else False
        )
        # 예약 가능 msg h_rsv_psb_nm
        self.reserve_possible_name = data.get("h_rsv_psb_nm", "").replace(
            "\n", " "
        )
        # 특실 예약 가능 00: 특실칸 없음, 11,21: 가능, 13,23: 매진 h_spe_rsv_cd
        self.special_seat = data.get("h_spe_rsv_cd")
        # 일반 예약 가능 00: 일반칸 없음, 11,21: 가능, 13,23: 매진 h_gen_rsv_cd
        self.general_seat = data.get("h_gen_rsv_cd")
        # 일반실 가격(할인 적용) h_rcvd_amt
        self.general_price = int(data.get("h_rcvd_amt", 0))
        # 특실 가격(할인 적용) h_rcvd_fare
        self.special_price = (
            (self.general_price + int(data.get("h_rcvd_fare", 0)))
            if data.get("h_rcvd_fare")
            else 0
        )
        # 할인 비율 h_train_disc_gen_rt
        self.sale_percent = float(data.get("h_train_disc_gen_rt", 0.0))
        # 예약시 필요 정보
        self.h_dpt_stn_cons_ordr = data.get("h_dpt_stn_cons_ordr")
        # 예약시 필요 정보
        self.h_arv_stn_cons_ordr = data.get("h_arv_stn_cons_ordr")
        # 예약시 필요 정보
        self.h_dpt_stn_run_ordr = data.get("h_dpt_stn_run_ordr")
        # 예약시 필요 정보
        self.h_arv_stn_run_ordr = data.get("h_arv_stn_run_ordr")

        # 1개의 예약에 있는 열차 시퀀스 h_jrny_sqno
        self.journey_no = data.get("h_jrny_sqno")
        # 예약 번호 h_pnr_no
        self.rsv_no = data.get("h_pnr_no")

        # enum_h_rsv_tp_cd
        self.h_rsv_tp_cd = data.get("h_rsv_tp_cd")
        # enum_h_jrny_tp_cd
        self.h_jrny_tp_cd = data.get("h_jrny_tp_cd")

    def has_special_seat(self):
        return self.special_seat in ["11", "21"]

    def has_general_seat(self):
        return self.general_seat in ["11", "21"]

    def has_seat(self):
        return self.has_general_seat() or self.has_special_seat()

    def _set_cars(self, gen: Generator):
        assert isinstance(gen, Generator)
        self._gen = gen

    @property
    def cars(self) -> Cars:
        try:
            self._cars = next(self._gen)
        except StopIteration:
            pass

        return self._cars

    def __add__(self, other):
        assert isinstance(other, dict)
        return self.__class__(other)

    def _str_dpt(self):
        return "출발: {} {} {}".format(
            self.dpt_name,
            "{}월 {}일".format(self.dpt_date[4:6], self.dpt_date[6:]),
            "{}:{}".format(self.dpt_time[:2], self.dpt_time[2:4]),
        )

    def _str_arv(self):
        return "도착: {} {} {}".format(
            self.arv_name,
            "{}월 {}일".format(self.arv_date[4:6], self.arv_date[6:]),
            "{}:{}".format(self.arv_time[:2], self.arv_time[2:4]),
        )

    def _str_run(self):
        return "소요: {}".format(
            "{}시간 {}분".format(self.run_time[:2], self.run_time[2:])
        )

    def _str_emtyseat(self):
        return "잔여: 일반실 {} | 특실 {}".format(
            "O" if self.has_general_seat() else "X",
            "O" if self.has_special_seat() else "X",
        )

    @property
    def info(self) -> str:
        return "[{}]({})\n{}\n{}\n{}\n{}".format(
            self.train_name,
            self.train_no,
            self._str_dpt(),
            self._str_arv(),
            self._str_run(),
            self._str_emtyseat(),
        )


class Trains(tuple):
    def __getitem__(self, key) -> Train:
        return super(Trains, self).__getitem__(key)