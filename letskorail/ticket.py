# coding=utf-8

from .train import Train
from .reservation import Seat


class Ticket(object):

    tk_no = None
    # h_tot_stl_amt
    h_tot_stl_amt = None
    # h_sale_dt 구매일자
    h_sale_dt = None
    # h_apv_dt 승인일자
    h_apv_dt = None
    # h_wct_no
    h_wct_no = None
    # h_sale_sqno
    h_sale_sqno = None
    # h_tk_ret_pwd
    h_tk_ret_pwd = None
    # h_wct_nm "스마트폰-안드로이드폰"
    h_wct_nm = None
    # h_pnr_no
    h_pnr_no = None

    h_ret_sale_dt = None

    # 정기권 관련
    seat_att_cd1 = None
    menu_id = None

    train_info = {}

    def __init__(self, data):
        # MyTicketList로 받을땐
        tk_info = data.get("tk_infos", {}).get("tk_info", [{}])[0]
        if not tk_info:
            tk_info = data["ticket_list"][0]["train_info"][0]

        self.h_wct_no = data.get("h_wct_no", tk_info.get("h_orgtk_wct_no"))
        self.h_sale_dt = tk_info.get(
            "h_sale_dt", tk_info.get("h_orgtk_sale_dt")
        )
        self.h_tk_ret_pwd = tk_info.get(
            "h_tk_ret_pwd", tk_info.get("h_orgtk_ret_pwd")
        )
        self.h_sale_sqno = tk_info.get(
            "h_sale_sqno", tk_info.get("h_orgtk_sale_sqno")
        )

        self.h_ret_sale_dt = tk_info.get(
            "h_ret_sale_dt", tk_info.get("h_orgtk_ret_sale_dt")
        )

        self.tk_no = "{}-{}-{}-{}".format(
            self.h_wct_no[-5:],
            self.h_sale_dt[-4:],
            self.h_sale_sqno[-5:],
            self.h_tk_ret_pwd[-2:],
        )

        self.h_tk_knd_nm = tk_info.get("h_tk_knd_nm", "")

    def _detail(self, data):
        tk_infos = data.get("ticket_infos", {}).get("ticket_info", [])

        self.h_wct_nm = data.get("h_wct_nm")
        self.h_pnr_no = data.get("h_pnr_no")

        self.seat_att_cd1 = data.get("seatAttCd1")
        self.menu_id = data.get("menuId")

        for t in tk_infos:
            sq = t["h_jrny_sqno"]
            self.train_info = {sq: {"train": Train(t)}}

            seats = t["tk_seat_info"]
            self.train_info[sq]["seats"] = tuple(Seat(s) for s in seats)
