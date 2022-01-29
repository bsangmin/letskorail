# Letskorail on Python

[korail2](https://github.com/carpedm20/korail2)에 영감을 받아 작성한 코드입니다.

주요 코드는 [korail2](https://github.com/carpedm20/korail2)에서 참조 했습니다.

## 주의
예약 확정을 해주지 않습니다.

코레일 발권 시스템은 자리배정 -> 예약 -> 결제 -> 발권 순으로 흘러갑니다.

이 프로젝트는 자리배정 -> 예약 단계만 지원합니다.

이후는 직접 코레일 앱에서 해야됩니다.

예약 후 20분내로 결제를 완료해야 발권되고 이후엔 자동으로 취소됩니다.

예약 -> 결제 단계에서 디바이스의 [고유번호(uuid)](https://github.com/bsangmin/letskorail/blob/master/letskorail/korail.py#L664)를 요구합니다.

고유번호를 생성하여 발권 할 수 있지만 앱에서 확인하면 `다른 기기에서 발권한 승차권`으로 표시되고 티켓이 비활성화 됩니다.

자신의 uuid는 코레일 앱에서 승차권 확인 메뉴를 터치하면 https로 txtDeviceId 파라미터로 전송됩니다. 이 값을 확인하는 방법은 여러가지 있으나 저는 [ROOT 인증서를 사용한 프록시](https://github.com/bsangmin/ssl_unpinning_mobile_app)로 확인했습니다.





## korail2에서 바뀐점

- 중앙선(청량리 - 안동) KTX-이음 추가
- 장애인 승객 추가 (코레일앱에서 별도 인증 필요)
- 21년 12월 파라미터 반영

## Requirement

- python 3.6+

## Installation

```bash
$ git clone https://github.com/bsangmin/letskorail.git
$ cd letskorail
$ pip install -r requirements.txt
```

## Usage

### 로그인

```python
# korail.py

from letskorail import Korail

korail = Korail()
# email
profile = korail.login("email@mail.com", PW)
# or cell phone number
profile = korail.login("010-0000-0000", PW)
# or korail membership number
profile = korail.login("12345678", PW)

print(profile)
# <korail.Profile object>

print(vars(profile))
# {"name": ..., "email": ..., ...}
```

### 열차 검색

#### korail.search_train()

##### rtype: train.Trains

| param           | type                              | comment                         | default  |
| --------------- | --------------------------------- | ------------------------------- | -------- |
| dpt             | string                            | 출발지                          |          |
| arv             | string                            | 목적지                          |          |
| date            | string                            | (optional) 출발날짜(`yyyymmdd`) | now.date |
| time            | string                            | (optional) 출발시간(`hhmmss`)   | now.time |
| passengers      | Iterable[[Passenger](#Passenger)] | (optional) 승객                 | AdultPsg |
| discnt_type     | [Discount](#Discount)             | (optional) 할인상품             | None     |
| train_type      | [TrainType](#TrainType)           | (optional) 열차종류             | ALL      |
| include_soldout | bool                              | (optional) 매진포함             | False    |

#### 기본 검색

```python
trains = korail.search_train("부산", "동대구")
# 당일, 현재시간, 성인 1명  열차 검색
```

#### 날짜, 시간 조건

```python
trains = korail.search_train("부산", "동대구", "20210301", "060000")
# 21년 3월 1일 06시 이후 열차 검색
```

#### 승객 추가 [Passenger Class](#Passenger)

```python
from letskorail.options import AdultPsg, BabyPsg, DisabilityAPsg

psgrs = [AdultPsg(), BabyPsg(1), DisabilityAPsg(2)]

trains = korail.search_train("부산", "동대구", passengers=psgrs)
```

#### 열차 종류 [TrainType Class](#TrainType)

```python
from letskorail.options import TrainType

trains = korail.search_train("부산", "동대구",
         train_type=TrainType.ITX_SAEMAEUL)
```

#### 할인 상품 [Discount Class](#Discount)

```python
from letskorail.options import YouthDisc

trains = korail.search_train(..., discnt_type=YouthDisc()) # 힘내라 청춘
```

#### 매진된 열차 포함

```python
trains = korail.search_train("부산", "동대구", include_soldout=True)
```

#### OUTPUT

```python
print(trains)
# <train.Trains object>

print(trains[0])
# <train.Train object>

print(vars(trains[0]))
# {'train_type': '00', 'train_group': '100', 'train_name': 'KTX' ... }

print(trains[0].info)
# [KTX]
# 출발: 부산 03월 01일 06:10
# 도착: 동대구 03월 01일 07:01
# 소요: 00시간 51분
# 잔여: 일반실 O | 특실 O
```

#### More information about train

```python
print(train.cars[1]) # 1호차 정보
# <train.Car object>

print(train.cars[1].seats) # 1호차 좌석 정보
# <train.Seats object>

print(train.cars[1].seats.seat_info)
# {"1A": <train.Seat object>, ... }
```

### 예약

#### korail.reserve()

##### rtype: reservation.Reservation

| param          | type                                             | comment              | default      |
| -------------- | ------------------------------------------------ | -------------------- | ------------ |
| train          | train.Train                                      | Train Object         |              |
| seat_opt       | Union[[SeatOption](#SeatOption), Iterable[Dict]] | (optional) 좌석 옵션 | GENERAL_ONLY |
| ignore_soldout | bool                                             | (optional) 매진 포함 | False        |

#### 기본

```python
reservation = korail.reserve(train)
```

#### 좌석 옵션

```python
from letskorail.options import SeatOption

reservation = korail.reserve(train, seat_opt=SeatOption.SPECIAL_ONLY)
```

#### 선호 좌석

[select_seats()](<#select_seats()>)

```python
seats = train.cars[5].select_seats()
# [{'car_no': ..., 'seat': '6A', 'seat_no': ...}]
reservation = korail.reserve(train, seat_opt=seats)
```

#### OUTPUT

```python
print(reservation)
# <Reservation object>

print(vars(reservation))
# {'rsv_no': 'xxxxxxxxxxx', 'journey_no': '0001', 'rsv_chg_no': '000' ... }

print(reservation.info)
# [직통] KTX(008)
# 기한: 02월 15일 22:00:00 까지
# 여정1: 부산(06:10) - 동대구(07:01)
# 좌석1: 5호차 10D (어른)
# 가격: 17,100원
```

### 예약 조회

| param  | type   | comment             | default |
| ------ | ------ | ------------------- | ------- |
| rsv_no | string | (optional) 예약번호 | None    |

```python
reservations = korail.reservations()
# List[<Reservation object>, ...]
```

### 예약 취소

| param | type        | comment            | default |
| ----- | ----------- | ------------------ | ------- |
| rsv   | Reservation | Reservation Object |         |

```python
rst = korail.cancel(reservation)
# True
```

### 티켓 구매

법적 문제의 소지가 있어 비공개

### 티켓 조회

```python
tickets = korail.tickets()
# List[<Ticket object>, ...]
```

### 티켓 환불

| param  | type   | comment       | default |
| ------ | ------ | ------------- | ------- |
| ticket | Ticket | Ticket Object |         |

```python
rst = korail.refund(ticket)
# True
```

## Class

### letskorail.train.Car

#### select_seats()

| param     | type   | comment              | values          | default |
| --------- | ------ | -------------------- | --------------- | ------- |
| count     | int    | (optional) 인원      | Integer         | 1       |
| location  | string | (optional) 선호 위치 | 중앙, 출입문    | 중앙    |
| direction | string | (optional) 선호 방향 | 순방향, 역방향  | 순방향  |
| position  | string | (optional) 선호 좌석 | 창측, 내측, 1인 | 창측    |
| seat_type | string | (optional) 좌석 종류 | 일반석, 2층석   | 일반석  |

```python
print(train.cars[1].select_seats()) # 1호차 좌석 선택
# [{"car_no": "0001", "seat": "9A", ...}]

print(train.cars[3].select_seats(position="1인")) # KTX 특실에만 적용
# [{"car_no": "0003", "seat": "6A", ...}]
```

##### :exclamation: 참고사항

- Passenger > 1 이면 모든 승객은 코레일 좌석배정 시스템상 같은 호차에 배정됨.

  따라서 아래와 같은 시나리오는 불가능.

  ```python
  psgrs = [AdultPsg(2)]
  ...
  seats = train.cars[5].select_seats()
  seats2 = train.cars[6].select_seats()
  ################## ^^^ 차량이 다르면 코레일에서 임의로 배정하거나 오류발생
  seats.extend(seats2)
  korail.reserve(train, seat_opt=seats) # diffrent result what you expect

  #################

  seats = train.cars[5].select_seats(count=2)
  korail.reserve(train, seat_opt=seats) # It's okay
  ```

- 다수 예약시 특수좌석(유아동반, 휠체어석 등 인증이 필요한 좌석)이 필요한 경우

  ```python
  psgrs = [AdultPsg(), AdultPsg(), AdultPsg()]
  ...
  seats = train.cars[8].select_seats(count=2)
  seats2 = train.cars[8].select_seats(seat_type="유아동반석")

  seats.extend(seats2)
  korail.reserve(train, seat_opt=seats)
  ```

## Options

### Passenger

```python
from letskorail.options import AdultPsg, ChildPsg, ...
```

`AdultPsg`: 성인(만 13세 이상)

`TeenPsg`: 청소년(만 24세 이하)

`ChildPsg`: 어린이(만 6세 - 12세)

`BabyPsg`: 좌석이 필요한 아기(만 6세 미만)

`SeniorPsg`: 경로(만 65세 이상)

`DisabilityAPsg`: 중증 장애인(1급 - 3급)

`DisabilityBPsg`: 경증 장애인(4급 - 6급)

> 청소년은 "청소년 드림" 상품에만 적용되고 나머지 상품에는 성인으로 적용됨

### Discount

```python
from letskorail.options import YouthDisc, TeenDisc, ...
```

`YouthDisc`: 힘내라 청춘

`TeenDisc`: 청소년 드림

`MomDisc`: 맘편한 KTX

`BasicLive`: 기차누리

`FamilyDisc`: 다자녀행복

`StoGDisc`: KTX 5000 특가

### TrainType

```python
from letskorail.options import TrainType
```

`ALL`

`KTX_ALL`
`KTX_SANCHEON`
`KTX_EUM`

`ITX_CHEONGCHUN`

`ITX_SAEMAEUL`
`SAEMAEUL`

`MUGUNGHWA`
`NURIRO`

`TONGGUEN`

`AIRPORT`

### SeatOption

```python
from letskorail.options import SeatOption
```

`GENERAL_FIRST`: 일반실 우선

`GENERAL_ONLY`: 일반실만

`SPECIAL_FIRST`: 특실 우선

`SPECIAL_ONLY`: 특실만

## License

Source codes are distributed under BSD license.
