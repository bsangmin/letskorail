# coding=utf-8


"""
https://github.com/carpedm20/korail2/blob/master/korail2/constants.py
"""


class ConDict(dict):
    def __init__(self, d):
        assert isinstance(d, dict)
        super(ConDict, self).update(d)

    def get(self, k):
        return super(ConDict, self).get(k, f"{k}_unknown")

    def __getitem__(self, k):
        return self.get(k)


# h_jrny_tp_cd
journey_type = ConDict(
    {
        "10": "열차상품",
        "11": "편도",
        "12": "왕편",
        "13": "복편",
        "14": "환승편도",
        "15": "왕편환승",
        "16": "복편환승",
        "20": "병합",
        "21": "병합선행",
        "22": "병합후행",
        "50": "열차외상품",
        "51": "숙박",
        "52": "렌터카",
        "53": "선박",
        "54": "이벤트",
        "55": "항공",
    }
)

# h_psg_tp_cd
psgr_type = ConDict(
    {
        "1": "어른",
        "2": "unknown",
        "3": "어린이",
        "4": "유아",
        "5": "경로",
        "6": "중증장애인",
        "7": "경증장애인",
        "8": "unknown",
    }
)

# h_psrm_cl_cd
car_type = ConDict(
    {
        "1": "일반실",
        "2": "특실",
        "3": "침대실",
        "4": "가족실",
        "5": "별실",
        "6": "비승용",
        "7": "우등실",
    }
)

# h_rsv_tp_cd
reserve_type = ConDict(
    {
        "0": "unknown",
        "1": "특단",
        "2": "전세",
        "3": "일반",
        "4": "대납",
        "5": "Open",
        "6": "T-Less",
        "7": "OVER",
        "8": "대기",
        "9": "단체",
        "10": "열전",
        "11": "군수송",
        "12": "우편배송",
    }
)


# h_for_rev_dir_dv
# h_seat_att_cd_2
direction_type = ConDict(
    {
        "009": "순방",
        "010": "역방",
    }
)

# h_sigl_win_in_dv
# h_seat_att_cd_3
window_side = ConDict(
    {
        "011": "1인",
        "012": "창측",
        "013": "내측",
    }
)


# h_seat_att_cd_4
seat_type = ConDict(
    {
        "015": "일반석",
        "018": "2층석",
        "019": "유아동반석",
        "021": "휠체어석",
        "024": "???",
        "027": "4인석",
        "028": "전동휠체어석",
        "032": "자전거",
        "052": "대피도우미",
    }
)

# h_trn_clsf_cd
train_code = ConDict(
    {
        "00": "KTX",
        "01": "새마을호",
        "02": "무궁화호",
        "03": "통근열차",
        "04": "누리로",
        "05": "전체",
        "06": "공항직통",
        "07": "KTX-산천",
        "08": "ITX-새마을",
        "09": "ITX-청춘",
        "16": "KTX-이음",
        "17": "SRT",
    }
)
