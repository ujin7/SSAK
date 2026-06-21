# 싹 (SSAK) 🌱

> 나만의 습관 정원 — 습관을 기록하고 식물을 키우는 데스크톱 앱

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flet](https://img.shields.io/badge/Flet-GUI-green)
![DuckDB](https://img.shields.io/badge/DuckDB-Database-yellow)

---

## 소개

**싹(SSAK)**은 일상적인 습관 기록과 식물 성장 시뮬레이션을 결합한 모바일형 데스크톱 애플리케이션입니다.  
매일 일정을 완료하면 포인트를 획득하고, 포인트로 식물을 씨앗부터 나무까지 성장시킬 수 있습니다.  
친구와 서로의 식물에 물·햇빛·비료를 주는 소셜 기능과 날짜별 감정 일기 기능도 제공합니다.

---

## 주요 기능

- **로그인 / 회원가입** — SHA-256 비밀번호 해시 인증
- **캘린더** — 날짜별 일정 등록·완료·삭제, 감정 일기 기록
- **정원** — 포인트 기반 식물 4단계 성장 (씨앗 → 새싹 → 꽃 → 나무)
- **친구** — 친구 추가/수락, 물주기·햇빛·비료 상호작용 (24시간 쿨다운), 피드
- **통계** — 월별 완료 현황 바 차트, 감정 분포 차트
- **상점** — 포인트로 아이템 구매 (트랜잭션 원자성 보장)

---

## 기술 스택

| 분류 | 기술 |
|------|------|
| Language | Python 3.10+ |
| GUI | Flet |
| Database | DuckDB |
| Auth | SHA-256 (hashlib) |

---

## 데이터베이스 구조

- **테이블 8개**: user, schedule, plant, friend, interaction, item, daily_log, user_item
- **뷰 3개**: v_user_plant, v_friend_plant, v_friend_public_schedule
- **인덱스 7개**: 월별 일정 조회, 친구 목록, 상호작용 이력 등 성능 최적화

---

## 실행 방법

```bash
# 의존성 설치
pip install flet duckdb

# 실행
python main.py
```

---

## 프로젝트 구조

```
SSAK/
├── main.py               # 앱 진입점
├── database.py           # DB 스키마 생성 및 샘플 데이터
├── session.py            # 로그인 세션 관리
├── theme.py              # 색상 및 공통 스타일
├── pages/                # 화면별 UI
│   ├── login.py
│   ├── calendar.py
│   ├── garden.py
│   ├── friends.py
│   ├── friend_garden.py
│   ├── profile.py
│   ├── stats.py
│   └── shop.py
├── repository/           # DB 접근 계층
│   ├── user.py
│   ├── plant.py
│   ├── schedule.py
│   ├── friend.py
│   ├── item.py
│   └── daily_log.py
└── assets/               # 식물 이미지
    ├── seed.png
    ├── leaf.png
    ├── flower.png
    └── tree.png
```

---

## 스크린샷

| 로그인 | 정원 | 친구 |
|--------|------|------|
| ![login](assets/seed.png) | ![garden](assets/flower.png) | ![friends](assets/leaf.png) |
