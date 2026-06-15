import duckdb

DB_PATH = 'ssak.duckdb'

def get_connection():
    return duckdb.connect(DB_PATH)

def create_tables():
    con = get_connection()

    # ── 시퀀스 (자동 증가 ID) ─────────────────────────────────────────────────
    con.execute("CREATE SEQUENCE IF NOT EXISTS seq_user        START 1")
    con.execute("CREATE SEQUENCE IF NOT EXISTS seq_schedule    START 1")
    con.execute("CREATE SEQUENCE IF NOT EXISTS seq_plant       START 1")
    con.execute("CREATE SEQUENCE IF NOT EXISTS seq_interaction START 1")
    con.execute("CREATE SEQUENCE IF NOT EXISTS seq_item        START 1")

    # ── user ─────────────────────────────────────────────────────────────────
    con.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id            INTEGER     PRIMARY KEY,
            nickname      VARCHAR(50) NOT NULL UNIQUE,
            password_hash VARCHAR(64) NOT NULL,
            is_public     BOOLEAN     DEFAULT TRUE,
            created_at    TIMESTAMP   DEFAULT NOW()
        )
    """)

    # ── schedule ──────────────────────────────────────────────────────────────
    con.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id         INTEGER      PRIMARY KEY,
            user_id    INTEGER      NOT NULL,
            title      VARCHAR(100) NOT NULL,
            sched_date DATE         NOT NULL,
            color      VARCHAR(10)  DEFAULT 'blue'
                       CHECK (color IN ('blue', 'green', 'red', 'yellow')),
            is_done    BOOLEAN      DEFAULT FALSE,
            memo       TEXT,
            icon       VARCHAR(20)  DEFAULT 'task'
                       CHECK (icon IN ('task', 'health', 'book', 'meeting')),
            FOREIGN KEY (user_id) REFERENCES user(id)
        )
    """)

    # ── plant (plant_img 제거: stage에서 도출 → 3NF 준수) ────────────────────
    con.execute("""
        CREATE TABLE IF NOT EXISTS plant (
            id           INTEGER    PRIMARY KEY,
            user_id      INTEGER    UNIQUE NOT NULL,
            stage        VARCHAR(20) DEFAULT 'seed'
                         CHECK (stage IN ('seed', 'leaf', 'flower', 'tree')),
            total_points INTEGER    DEFAULT 0 CHECK (total_points >= 0),
            streak_days  INTEGER    DEFAULT 0 CHECK (streak_days >= 0),
            last_updated TIMESTAMP  DEFAULT NOW(),
            FOREIGN KEY (user_id) REFERENCES user(id)
        )
    """)

    # ── friend (복합 PK — 대리키 id 불필요) ──────────────────────────────────
    con.execute("""
        CREATE TABLE IF NOT EXISTS friend (
            from_user_id INTEGER    NOT NULL,
            to_user_id   INTEGER    NOT NULL,
            status       VARCHAR(20) DEFAULT 'pending'
                         CHECK (status IN ('pending', 'accepted')),
            created_at   TIMESTAMP   DEFAULT NOW(),
            PRIMARY KEY (from_user_id, to_user_id),
            FOREIGN KEY (from_user_id) REFERENCES user(id),
            FOREIGN KEY (to_user_id)   REFERENCES user(id),
            CHECK (from_user_id <> to_user_id)
        )
    """)

    # ── interaction ───────────────────────────────────────────────────────────
    con.execute("""
        CREATE TABLE IF NOT EXISTS interaction (
            id           INTEGER    PRIMARY KEY,
            from_user_id INTEGER    NOT NULL,
            to_user_id   INTEGER    NOT NULL,
            type         VARCHAR(20) NOT NULL
                         CHECK (type IN ('water', 'cheer', 'like')),
            sent_at      TIMESTAMP   DEFAULT NOW(),
            FOREIGN KEY (from_user_id) REFERENCES user(id),
            FOREIGN KEY (to_user_id)   REFERENCES user(id),
            CHECK (from_user_id <> to_user_id)
        )
    """)

    # ── item ──────────────────────────────────────────────────────────────────
    con.execute("""
        CREATE TABLE IF NOT EXISTS item (
            id          INTEGER     PRIMARY KEY,
            name        VARCHAR(50) NOT NULL,
            description TEXT,
            price       INTEGER     NOT NULL CHECK (price > 0),
            emoji       VARCHAR(10),
            category    VARCHAR(20) DEFAULT 'deco'
                        CHECK (category IN ('skin', 'deco', 'tool', 'rare'))
        )
    """)

    # ── user_item (복합 PK — 대리키 id 불필요) ───────────────────────────────
    con.execute("""
        CREATE TABLE IF NOT EXISTS user_item (
            user_id      INTEGER   NOT NULL,
            item_id      INTEGER   NOT NULL,
            purchased_at TIMESTAMP DEFAULT NOW(),
            PRIMARY KEY (user_id, item_id),
            FOREIGN KEY (user_id) REFERENCES user(id),
            FOREIGN KEY (item_id) REFERENCES item(id)
        )
    """)

    # ── 인덱스 ────────────────────────────────────────────────────────────────
    # 캘린더: 월별 일정 조회 (user_id + sched_date 복합 범위 스캔)
    con.execute("CREATE INDEX IF NOT EXISTS idx_sched_user_date    ON schedule(user_id, sched_date)")
    # 완료 여부 필터 조회
    con.execute("CREATE INDEX IF NOT EXISTS idx_sched_user_done    ON schedule(user_id, is_done)")
    # 친구 목록: 받은 요청 조회
    con.execute("CREATE INDEX IF NOT EXISTS idx_friend_to_status   ON friend(to_user_id, status)")
    # 친구 목록: 보낸 요청 + accepted 필터
    con.execute("CREATE INDEX IF NOT EXISTS idx_friend_from_status ON friend(from_user_id, status)")
    # 상호작용 이력 검색
    con.execute("CREATE INDEX IF NOT EXISTS idx_interact_pair      ON interaction(from_user_id, to_user_id)")
    # 보유 아이템 조회
    con.execute("CREATE INDEX IF NOT EXISTS idx_user_item_user     ON user_item(user_id)")

    con.close()


def insert_sample_data():
    con = get_connection()

    count = con.execute("SELECT COUNT(*) FROM user").fetchone()[0]
    if count > 0:
        con.close()
        return

    # ── 유저 5명 (비밀번호: 모두 "1234" → SHA-256) ──────────────────────────
    # sha256("1234") = 03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4
    PW = '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4'
    con.executemany(
        "INSERT INTO user (id, nickname, password_hash, is_public) VALUES (?, ?, ?, ?)",
        [
            (1, '노우진', PW, True),
            (2, '김민지', PW, True),
            (3, '이서준', PW, True),
            (4, '박하은', PW, False),
            (5, '최지호', PW, True),
        ]
    )

    # ── 일정 22개 ─────────────────────────────────────────────────────────────
    con.executemany(
        "INSERT INTO schedule (id, user_id, title, sched_date, color, is_done, memo, icon) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (1,  1, '알고리즘 과제',      '2026-06-01', 'blue',   True,  '정렬 문제',         'task'),
            (2,  1, 'DB 프로젝트 설계',   '2026-06-02', 'green',  True,  'ERD 작성',          'task'),
            (3,  1, '운동',               '2026-06-03', 'red',    True,  '헬스장 1시간',      'health'),
            (4,  1, '독서',               '2026-06-04', 'yellow', True,  '클린코드 50p',      'book'),
            (5,  1, '데이터베이스 공부',  '2026-06-05', 'blue',   True,  'JOIN 쿼리 복습',    'task'),
            (6,  1, '팀 미팅',            '2026-06-06', 'green',  True,  '프로젝트 진행상황', 'meeting'),
            (7,  1, '코딩 테스트 준비',   '2026-06-07', 'blue',   True,  'LeetCode 3문제',    'task'),
            (8,  1, '운동',               '2026-06-08', 'red',    True,  '러닝 5km',          'health'),
            (9,  1, 'DB 프로젝트 구현',   '2026-06-09', 'green',  True,  'DDL/DML 작성',      'task'),
            (10, 1, '독서',               '2026-06-10', 'yellow', True,  '클린코드 100p',     'book'),
            (11, 1, '운동',               '2026-06-11', 'red',    True,  '헬스장',            'health'),
            (12, 1, 'Flet 공부',          '2026-06-12', 'green',  True,  'UI 컴포넌트',       'task'),
            (13, 2, '영어 공부',          '2026-06-01', 'yellow', True,  '단어 100개',        'book'),
            (14, 2, '요리',               '2026-06-02', 'green',  True,  '파스타 만들기',     'task'),
            (15, 2, '자격증 공부',        '2026-06-03', 'blue',   True,  '정보처리기사',      'task'),
            (16, 2, '친구 만남',          '2026-06-04', 'red',    True,  '카페에서 수다',     'meeting'),
            (17, 2, '독서',               '2026-06-05', 'yellow', False, '소설 읽기',         'book'),
            (18, 3, '수학 공부',          '2026-06-01', 'blue',   True,  '미적분 복습',       'task'),
            (19, 3, '프로젝트 발표준비',  '2026-06-03', 'green',  True,  'PPT 제작',          'task'),
            (20, 3, '운동',               '2026-06-05', 'red',    False, '수영 1시간',        'health'),
            (21, 4, '그림 그리기',        '2026-06-02', 'yellow', True,  '수채화 연습',       'task'),
            (22, 5, '봉사활동',           '2026-06-01', 'green',  True,  '동물보호소',        'meeting'),
        ]
    )

    # ── 식물 (plant_img 컬럼 없음) ────────────────────────────────────────────
    con.executemany(
        "INSERT INTO plant (id, user_id, stage, total_points, streak_days) VALUES (?, ?, ?, ?, ?)",
        [
            (1, 1, 'flower', 120, 12),
            (2, 2, 'leaf',    60,  4),
            (3, 3, 'leaf',    45,  2),
            (4, 4, 'tree',   200, 14),
            (5, 5, 'seed',    10,  1),
        ]
    )

    # ── 친구 관계 (복합 PK — id 없음) ────────────────────────────────────────
    con.executemany(
        "INSERT INTO friend (from_user_id, to_user_id, status) VALUES (?, ?, ?)",
        [
            (1, 2, 'accepted'),
            (1, 3, 'accepted'),
            (1, 5, 'pending'),
            (2, 1, 'accepted'),
            (3, 1, 'accepted'),
        ]
    )

    # ── 아이템 ────────────────────────────────────────────────────────────────
    con.executemany(
        "INSERT INTO item (id, name, description, price, emoji, category) VALUES (?, ?, ?, ?, ?, ?)",
        [
            (1,  '선인장 스킨',     '정원에 선인장을 심어요',           50,  '🌵', 'skin'),
            (2,  '야자수 스킨',     '열대 분위기 야자수',               80,  '🌴', 'skin'),
            (3,  '네잎클로버',      '행운을 가져다줘요',                30,  '🍀', 'deco'),
            (4,  '나비 장식',       '정원에 나비가 날아와요',            40,  '🦋', 'deco'),
            (5,  '분수 장식',       '작은 분수로 정원을 꾸며요',         100, '⛲', 'deco'),
            (6,  '달빛 씨앗',       '희귀한 달빛 식물을 키워요',         150, '🌙', 'rare'),
            (7,  '무지개 물뿌리개', '물주기 효과가 2배!',               60,  '🌈', 'tool'),
            (8,  '돌 장식',         '아담한 돌로 정원 경계를 만들어요',  20,  '🪨', 'deco'),
            (9,  '버섯 장식',       '귀여운 버섯이 자라나요',            35,  '🍄', 'deco'),
            (10, '별빛 비료',       '포인트 획득량 +5 (하루)',           120, '⭐', 'tool'),
        ]
    )

    # ── 상호작용 ─────────────────────────────────────────────────────────────
    con.executemany(
        "INSERT INTO interaction (id, from_user_id, to_user_id, type, sent_at) VALUES (?, ?, ?, ?, ?)",
        [
            (1, 2, 1, 'water', '2026-06-10 10:00:00'),
            (2, 3, 1, 'water', '2026-06-11 11:00:00'),
            (3, 1, 2, 'cheer', '2026-06-12 09:00:00'),
        ]
    )

    # ── 시퀀스 전진 (샘플 데이터 이후 충돌 방지) ────────────────────────────
    # nextval을 n번 호출해 다음 발급값이 샘플 최대 ID + 1이 되도록 설정
    def _advance(seq: str, n: int):
        for _ in range(n):
            con.execute(f"SELECT nextval('{seq}')")
    _advance('seq_user',        5)   # 다음 = 6
    _advance('seq_schedule',   22)   # 다음 = 23
    _advance('seq_plant',       5)   # 다음 = 6
    _advance('seq_interaction', 3)   # 다음 = 4
    _advance('seq_item',       10)   # 다음 = 11

    con.close()


def reset_db():
    """DB 전체 초기화 (개발용)"""
    con = get_connection()
    for tbl in ['user_item', 'item', 'interaction', 'friend', 'plant', 'schedule', 'user']:
        con.execute(f"DROP TABLE IF EXISTS {tbl}")
    for seq in ['seq_user', 'seq_schedule', 'seq_plant', 'seq_interaction', 'seq_item']:
        con.execute(f"DROP SEQUENCE IF EXISTS {seq}")
    con.close()
    create_tables()
    insert_sample_data()


if __name__ == "__main__":
    reset_db()
    print("DB 초기화 완료")
