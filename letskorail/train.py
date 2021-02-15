# coding=utf-8


class TrainType:
    """type of train
    > ex) TrainType.KTX

    > ex) TrainType.ITX_CHEONGCHUN

    KTX_ALL == KTX, KTX_SANCHEON and KTX_EUM

    SAEMAEUL == SAEMAEUL and ITX_SAEMAEUL

    MUGUNGHWA == MUGUNGHWA and NURIRO
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
        # 특실 예약 가능 00: 특실칸 없음 11: 가능 13: 매진 h_spe_rsv_cd
        self.special_seat = data.get("h_spe_rsv_cd")
        # 일반 예약 가능 00: 일반칸 없음 11: 가능 13: 매진 h_gen_rsv_cd
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

    def has_special_seat(self):
        return self.special_seat == "11"

    def has_general_seat(self):
        return self.general_seat == "11"

    def has_seat(self):
        return self.has_general_seat() or self.has_special_seat()

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
    def info(self):
        return "[{}]\n{}\n{}\n{}\n{}".format(
            self.train_name,
            self._str_dpt(),
            self._str_arv(),
            self._str_run(),
            self._str_emtyseat(),
        )


class _seat(object):
    # h_srcar_no
    car_no = None
    # h_seat_no
    seat_no = None
    # h_psg_tp_dv_nm
    psg_type = None
    # h_dcnt_knd_cd1_nm
    psg_sub_type = None
    # h_rcvd_amt
    price = None
    # h_mlg_apl_flg
    h_mlg_apl_flg = None

    def __init__(self, data):
        self.car_no = data.get("h_srcar_no")
        self.seat_no = data.get("h_seat_no")
        self.psg_type = data.get("h_psg_tp_dv_nm", data.get("h_psg_tp_nm"))
        self.psg_sub_type = data.get("h_dcnt_knd_cd1_nm")
        self.price = int(data.get("h_rcvd_amt", 0))
        self.h_mlg_apl_flg = data.get("h_mlg_apl_flg")