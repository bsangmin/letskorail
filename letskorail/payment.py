# coding=utf-8

import re
from typing import Union

class CreditCard:
    """Set credit card or check card information for payment.

   card_type: 개인(0), 법인(1)

   card_no: 1234-1234-1234-1234 or 1234123412341234

   card_pw: Two digits in front of the password.

   card_date: Valid thru. format: `yymm` ex) 2021.01 => 2101

   reg_num: First digit of registration number.
            (개인: 주민번호 앞자리, 법인: 사업자번호 10자리)

   monthly_plan: monthly installment plan. (할부)
            (0, 2, 3, 4, 5, 6, 12, 24) 
    """

    card_type = None
    card_no = None
    card_pw = None
    card_date = None
    reg_num = None
    monthly_plan = None

    def __init__(self, card_type: Union[str, int], card_no: str, card_pw: str, card_date: str, reg_num: str, monthly_plan: str="0"):
        if int(card_type) in (0, 1):
            self.card_type = "J" if int(card_type) == 0 else "S"
        else:
            raise ValueError("Invalid card type")
        
        tmp = re.findall(r"\d", card_no)
        if len(tmp) == 16:
            self.card_no = "".join(tmp)
        else:
            raise ValueError("Invalid card number")

        tmp = re.findall(r"\d", card_pw)
        if len(tmp) == 2:
            self.card_pw = card_pw
        else:
            raise ValueError("Two digits in front of the password")
        
        tmp = re.findall(r"\d", card_date)
        if len(tmp) == 4:
            self.card_date = card_date
        else:
            raise ValueError("Invalid valid thru number")
        
        tmp = re.findall(r"\d", reg_num)
        if card_type == 0 and len(tmp) == 6:
            self.reg_num = reg_num
        elif card_type == 1 and len(tmp) == 10:
            self.reg_num = reg_num
        else:
            raise ValueError("Invalid registration number")

        if monthly_plan in ("0", "2", "3", "4", "5", "6", "12", "24"):
            self.monthly_plan = monthly_plan
        else:
            raise ValueError("Invalid value in monthly_plan")

        