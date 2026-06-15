from database import get_connection
from datetime import date, timedelta

STAGE_MAP = [
    (0,   49,  'seed'),
    (50,  99,  'leaf'),
    (100, 199, 'flower'),
    (200, 9999,'tree'),
]

def calc_stage(points: int) -> str:
    for low, high, stage in STAGE_MAP:
        if low <= points <= high:
            return stage
    return 'tree'

STAGE_IMAGE = {
    'seed':   'seed.png',
    'leaf':   'leaf.png',
    'flower': 'flower.png',
    'tree':   'tree.png',
}

def get_plant(user_id: int) -> dict | None:
    con = get_connection()
    row = con.execute(
        "SELECT id, user_id, stage, total_points, streak_days, image_path FROM plant WHERE user_id = ?",
        [user_id]
    ).fetchone()
    con.close()
    if row is None:
        return None
    return {'id': row[0], 'user_id': row[1], 'stage': row[2],
            'total_points': row[3], 'streak_days': row[4], 'image_path': row[5]}

def add_points(user_id: int, points: int = 10):
    """일정 완료 시 포인트 추가 · stage 업데이트 · streak 재계산을 트랜잭션으로 처리"""
    con = get_connection()
    try:
        con.begin()

        row = con.execute(
            "SELECT total_points FROM plant WHERE user_id = ?", [user_id]
        ).fetchone()
        if row is None:
            con.rollback()
            return

        new_points = row[0] + points
        new_stage  = calc_stage(new_points)

        # 완료된 날짜 기반 streak 계산
        rows = con.execute(
            "SELECT DISTINCT sched_date FROM schedule WHERE user_id = ? AND is_done = TRUE ORDER BY sched_date DESC",
            [user_id]
        ).fetchall()
        done_dates = set()
        for r in rows:
            d = r[0]
            done_dates.add(d.date() if hasattr(d, 'date') else date.fromisoformat(str(d)))

        streak = 0
        check  = date.today()
        while check in done_dates:
            streak += 1
            check -= timedelta(days=1)
        if streak == 0:
            check = date.today() - timedelta(days=1)
            while check in done_dates:
                streak += 1
                check -= timedelta(days=1)

        con.execute(
            "UPDATE plant SET total_points = ?, stage = ?, streak_days = ?, image_path = ?, last_updated = NOW() WHERE user_id = ?",
            [new_points, new_stage, streak, STAGE_IMAGE[new_stage], user_id]
        )
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

def add_water_points(user_id: int, points: int = 5):
    """친구가 물을 줄 때 포인트 추가 (streak는 변경하지 않음)"""
    con = get_connection()
    try:
        con.begin()
        row = con.execute(
            "SELECT total_points FROM plant WHERE user_id = ?", [user_id]
        ).fetchone()
        if row is None:
            con.rollback()
            return
        new_points = row[0] + points
        new_stage  = calc_stage(new_points)
        con.execute(
            "UPDATE plant SET total_points = ?, stage = ?, image_path = ?, last_updated = NOW() WHERE user_id = ?",
            [new_points, new_stage, STAGE_IMAGE[new_stage], user_id]
        )
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

def recalc_streak(user_id: int) -> int:
    """streak만 단독으로 재계산이 필요할 때 사용"""
    con = get_connection()
    rows = con.execute(
        "SELECT DISTINCT sched_date FROM schedule WHERE user_id = ? AND is_done = TRUE ORDER BY sched_date DESC",
        [user_id]
    ).fetchall()
    done_dates = set()
    for r in rows:
        d = r[0]
        done_dates.add(d.date() if hasattr(d, 'date') else date.fromisoformat(str(d)))

    streak = 0
    check  = date.today()
    while check in done_dates:
        streak += 1
        check -= timedelta(days=1)
    if streak == 0:
        check = date.today() - timedelta(days=1)
        while check in done_dates:
            streak += 1
            check -= timedelta(days=1)

    con.execute("UPDATE plant SET streak_days = ? WHERE user_id = ?", [streak, user_id])
    con.close()
    return streak

def update_stage(user_id: int):
    """현재 포인트 기준으로 stage 재계산"""
    con = get_connection()
    row = con.execute("SELECT total_points FROM plant WHERE user_id = ?", [user_id]).fetchone()
    if row is None:
        con.close()
        return
    con.execute(
        "UPDATE plant SET stage = ?, last_updated = NOW() WHERE user_id = ?",
        [calc_stage(row[0]), user_id]
    )
    con.close()
