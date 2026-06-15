from database import get_connection

MOOD_EMOJI = {
    'great':   '😄',
    'good':    '😊',
    'neutral': '😐',
    'bad':     '😟',
    'terrible': '😢',
}
MOOD_LABEL = {
    'great': '최고', 'good': '좋음', 'neutral': '보통',
    'bad': '나쁨', 'terrible': '힘듦',
}

def get_log(user_id: int, log_date: str) -> dict | None:
    con = get_connection()
    row = con.execute(
        "SELECT mood, diary FROM daily_log WHERE user_id = ? AND log_date = ?",
        [user_id, log_date]
    ).fetchone()
    con.close()
    if row is None:
        return None
    return {'mood': row[0], 'diary': row[1]}

def upsert_log(user_id: int, log_date: str, mood: str | None, diary: str | None):
    con = get_connection()
    con.execute(
        """INSERT INTO daily_log (user_id, log_date, mood, diary, updated_at)
           VALUES (?, ?, ?, ?, NOW())
           ON CONFLICT (user_id, log_date) DO UPDATE SET
               mood       = excluded.mood,
               diary      = excluded.diary,
               updated_at = excluded.updated_at""",
        [user_id, log_date, mood or None, diary or None]
    )
    con.close()

def get_mood_stats(user_id: int, year: int, month: int) -> dict[str, int]:
    """월별 기분 집계 — 통계 차트용"""
    con = get_connection()
    rows = con.execute(
        """SELECT mood, COUNT(*) FROM daily_log
           WHERE user_id = ? AND YEAR(log_date) = ? AND MONTH(log_date) = ?
             AND mood IS NOT NULL
           GROUP BY mood""",
        [user_id, year, month]
    ).fetchall()
    con.close()
    return {r[0]: r[1] for r in rows}
