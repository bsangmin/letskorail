# Letskorail on Python

개인 프로젝트 목적입니다.

[korail2](https://github.com/carpedm20/korail2)에 영감을 받아 작성한 코드입니다.

주요 코드는 [korail2](https://github.com/carpedm20/korail2)에서 참조 했습니다.

## korail2에서 바뀐점

- 중앙선(청량리 - 안동) KTX-이음 추가
- 장애인 승객 추가 (코레일앱에서 별도 인증 필요)
- 20년 12월 파라미터 반영

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
# out: <korail.Profile> object

print(vars(profile))
# out: {"name": ..., "email": ..., ...}
```

### 열차 검색

| param           | type                          | comment                         | default  |
| --------------- | ----------------------------- | ------------------------------- | -------- |
| dpt             | string                        | 출발지                          |          |
| arv             | string                        | 목적지                          |          |
| date            | string                        | (optional) 출발날짜(`yyyymmdd`) | now.date |
| time            | string                        | (optional) 출발시간(`hhmmss`)   | now.time |
| passengers      | List[[Passenger](#Passenger)] | (optional) 승객                 | AdultPsg |
| train_type      | [TrainType](#TrainType)       | (optional) 열차종류             | ALL      |
| include_soldout | bool                          | (optional) 매진포함             | False    |

#### 1. 기본 검색

```python
trains = korail.search_train("부산", "동대구")
# 당일, 현재시간, 성인 1명  열차 검색
```

#### 2. 날짜 검색

```python
trains = korail.search_train("부산", "동대구", "20210301", "060000")
# 21년 3월 1일 06시 이후 열차 검색
```

#### 3. 승객 추가

```python
from letskorail.options import AdultPsg, BabyPsg, DisabilityAPsg

psgrs = [AdultPsg(), BabyPsg(1), DisabilityAPsg(2)]

trains = korail.search_train("부산", "동대구", passengers=psgrs)
```

#### 4. 열차 종류

```python
from letskorail.options import TrainType

trains = korail.search_train("부산", "동대구",
         train_type=TrainType.ITX_SAEMAEUL)
```

#### 5. 매진된 열차 포함

```python
trains = korail.search_train("부산", "동대구", include_soldout=True)
```

#### OUTPUT

```python
print(trains)
# List[<Train object>, ...]

print(trains[0])
# <Train object>

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
print(train.cars[0]) # 1호차 정보
# <letskorail.train.Car object>

print(train.cars[0].seats) # 1호차 좌석 정보
# {'15D': {'near_wind': '창측', 'seat_type': '일반석', ... }

print(train.cars[1].seats["1A"]) # 2호차 1A 좌석 정보
# {'sale_psb': False, 'near_door': True, 'near_wind': '창측', ... }
```

### 예약

| param          | type                          | comment              | default      |
| -------------- | ----------------------------- | -------------------- | ------------ |
| train          | train.Train                   | 열차 Object          |              |
| passengers     | List[[Passenger](#Passenger)] | (optional) 승객      | AdultPsg     |
| option         | [SeatOption](#SeatOption)     | (optional) 좌석 옵션 | GENERAL_ONLY |
| ignore_soldout | bool                          | (optional) 매진 포함 | False        |

#### 1. 기본

```python
reservation = korail.reserve(train)
```

#### 2. 좌석 옵션

```python
from letskorail.options import SeatOption

reservation = korail.reserve(train, option=SeatOption.SPECIAL_ONLY)
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

## Options

### Passenger

```python
from letskorail.options import AdultPsg, ChildPsg ...
```

`AdultPsg`: 성인(만 13세 이상)

`ChildPsg`: 어린이(만 6세 - 12세)

`BabyPsg`: 좌석이 필요한 아기(만 6세 미만)

`SeniorPsg`: 경로(만 65세 이상)

`DisabilityAPsg`: 중증 장애인(1급 - 3급)

`DisabilityBPsg`: 경증 장애인(4급 - 6급)

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
