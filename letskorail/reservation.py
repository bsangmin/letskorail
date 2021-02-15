# coding=utf-8

from .train import Train, _seat

class Reservation(object):
    # h_pnr_no
    rsv_no = None
    # h_jrny_sqno
    journey_no = None
    # h_jrny_cnt
    journey_cnt = "1"
    # h_rsv_chg_no
    rsv_chg_no = None
    # h_ntisu_lmt_dt
    buy_limit_date = None
    # h_ntisu_lmt_tm
    buy_limit_time = None
    # h_rsv_amt
    total_price = None
    # h_wct_no
    h_wct_no = None

    train_info = {}
    # trains = None

    def __init__(self, data):
        trs = data["train_infos"]["train_info"]
        tr = trs[0]

        self.rsv_no = tr.get("h_pnr_no")
        self.journey_no = tr.get("h_jrny_sqno", "0001")
        self.rsv_chg_no = tr.get("h_rsv_chg_no", "000")
        self.buy_limit_date = tr.get("h_ntisu_lmt_dt")
        self.buy_limit_time = tr.get("h_ntisu_lmt_tm")
        self.total_price = int(tr.get("h_rsv_amt", 0))

        # self.trains = {t["h_jrny_sqno"]: {"train": dict(t)} for t in trs}
        self.train_info = {t["h_jrny_sqno"]: {"train": dict(t)} for t in trs}

    def _set_seats(self, data):
        self.journey_cnt = data.get("h_jrny_cnt")
        self.h_wct_no = data.get("h_wct_no")
        
        rsv_infos = data["jrny_infos"]["jrny_info"]
        for r in rsv_infos:
            sq = r["h_jrny_sqno"]
            seats = r["seat_infos"]["seat_info"]

            train = self.train_info[sq]["train"]
            train.update(dict(r))

            self.train_info[sq] = {
                "train": Train(train),
                "seats": [_seat(s) for s in seats],
            }

            # self.train_info[sq]["train"] = Train(train)
            # self.train_info[sq]["seats"] = [_seat(s) for s in seats]

    def _str_price(self):
        return "가격: {:,}원".format(self.total_price)

    def _str_deadline(self):
        return "기한: {}월 {}일 {}:{}:{} 까지".format(
            self.buy_limit_date[4:6],
            self.buy_limit_date[6:],
            self.buy_limit_time[:2],
            self.buy_limit_time[2:4],
            self.buy_limit_time[4:],
        )

    def _str_train_info(self):
        trains = []
        details = []

        srtd_sqce = sorted(self.train_info.keys(), key=(lambda x: int(x)))
        for idx, sq in enumerate(srtd_sqce):
            tr = self.train_info[sq]["train"]
            trains.append("{}({})".format(tr.train_name, tr.train_no))

            seats = [
                "{}호차 {} ({})".format(
                    s.car_no,
                    s.seat_no,
                    s.psg_sub_type if s.psg_sub_type else s.psg_type,
                )
                for s in self.train_info[sq]["seats"]
            ]

            v = {
                "idx": idx + 1,
                "d_name": tr.dpt_name,
                "d_time": "{}:{}".format(tr.dpt_time[:2], tr.dpt_time[2:4]),
                "a_name": tr.arv_name,
                "a_time": "{}:{}".format(tr.arv_time[:2], tr.arv_time[2:4]),
                "seats": " | ".join(seats),
            }

            details.append(
                "여정{idx}: {d_name}({d_time}) - {a_name}({a_time})\n좌석{idx}: {seats}".format(
                    **v
                )
            )

        return "[{}] {}\n{}\n{}\n{}".format(
            "직통" if len(srtd_sqce) == 1 else "환승",
            " -> ".join(trains),
            self._str_deadline(),
            "\n".join(details),
            self._str_price()
        )

    @property
    def info(self):
        return self._str_train_info()
