from datetime import datetime
from database import get_connection

FEED_TYPE = {
    'water': ('💧', '물을 줬어요'),
    'like':  ('☀️', '햇빛을 줬어요'),
    'cheer': ('🌿', '비료를 줬어요'),
}

def _time_ago(sent_at) -> str:
    if hasattr(sent_at, 'replace'):
        sent_at = sent_at.replace(tzinfo=None)
    diff = (datetime.now() - sent_at).total_seconds()
    if diff < 60:    return '방금 전'
    if diff < 3600:  return f'{int(diff // 60)}분 전'
    if diff < 86400: return f'{int(diff // 3600)}시간 전'
    return f'{int(diff // 86400)}일 전'

def get_feed(user_id: int, limit: int = 20) -> list[dict]:
    """나와 관련된 상호작용 피드 (보내거나 받은 것)"""
    con = get_connection()
    rows = con.execute(
        """SELECT i.type, i.sent_at,
                  u_from.id, u_from.nickname,
                  u_to.id,   u_to.nickname
           FROM interaction i
           JOIN user u_from ON i.from_user_id = u_from.id
           JOIN user u_to   ON i.to_user_id   = u_to.id
           WHERE i.from_user_id = ? OR i.to_user_id = ?
           ORDER BY i.sent_at DESC
           LIMIT ?""",
        [user_id, user_id, limit]
    ).fetchall()
    con.close()
    return [
        {'type': r[0], 'sent_at': r[1],
         'from_id': r[2], 'from_name': r[3],
         'to_id': r[4], 'to_name': r[5],
         'time_ago': _time_ago(r[1])}
        for r in rows
    ]

def send_request(from_user_id: int, to_user_id: int):
    con = get_connection()
    # ON CONFLICT DO NOTHING: 이미 요청이 있으면 무시 (복합 PK 중복 방지)
    con.execute(
        "INSERT INTO friend (from_user_id, to_user_id, status) VALUES (?, ?, 'pending') ON CONFLICT DO NOTHING",
        [from_user_id, to_user_id]
    )
    con.close()

def accept(from_user_id: int, to_user_id: int):
    con = get_connection()
    con.execute(
        "UPDATE friend SET status = 'accepted' WHERE from_user_id = ? AND to_user_id = ?",
        [from_user_id, to_user_id]
    )
    con.close()

def search_users(query: str, exclude_user_id: int) -> list[dict]:
    con = get_connection()
    rows = con.execute(
        "SELECT id, nickname FROM user WHERE nickname LIKE ? AND id != ? AND is_public = TRUE LIMIT 10",
        [f'%{query}%', exclude_user_id]
    ).fetchall()
    con.close()
    return [{'id': r[0], 'nickname': r[1]} for r in rows]

def get_pending_requests(user_id: int) -> list[dict]:
    con = get_connection()
    rows = con.execute(
        """SELECT u.id, u.nickname FROM friend f
           JOIN user u ON f.from_user_id = u.id
           WHERE f.to_user_id = ? AND f.status = 'pending'""",
        [user_id]
    ).fetchall()
    con.close()
    return [{'id': r[0], 'nickname': r[1]} for r in rows]

def get_friends_with_plant(user_id: int) -> list[dict]:
    con = get_connection()
    rows = con.execute(
        """SELECT u.id, u.nickname, p.stage, p.total_points, p.image_path
           FROM friend f
           JOIN user u ON f.to_user_id = u.id
           LEFT JOIN plant p ON u.id = p.user_id
           WHERE f.from_user_id = ? AND f.status = 'accepted'""",
        [user_id]
    ).fetchall()
    con.close()
    return [
        {'id': r[0], 'nickname': r[1], 'stage': r[2], 'total_points': r[3], 'image_path': r[4]}
        for r in rows
    ]

def interaction_cooldown_label(from_user_id: int, to_user_id: int, type_: str) -> str | None:
    """해당 type 상호작용을 오늘 이미 했으면 남은 시간 문자열 반환, 아니면 None"""
    con = get_connection()
    row = con.execute(
        """SELECT sent_at FROM interaction
           WHERE from_user_id = ? AND to_user_id = ? AND type = ?
             AND DATE(sent_at) = CURRENT_DATE
           ORDER BY sent_at DESC LIMIT 1""",
        [from_user_id, to_user_id, type_]
    ).fetchone()
    con.close()
    if row is None:
        return None
    sent_at = row[0]
    if hasattr(sent_at, 'replace'):
        sent_at = sent_at.replace(tzinfo=None)
    remaining = max(0, 86400 - (datetime.now() - sent_at).total_seconds())
    h = int(remaining // 3600)
    m = int((remaining % 3600) // 60)
    return f'{h}시간 후' if h > 0 else f'{m}분 후'

def water_cooldown_label(from_user_id: int, to_user_id: int) -> str | None:
    return interaction_cooldown_label(from_user_id, to_user_id, 'water')

def has_watered_today(from_user_id: int, to_user_id: int) -> bool:
    con = get_connection()
    count = con.execute(
        """SELECT COUNT(*) FROM interaction
           WHERE from_user_id = ? AND to_user_id = ? AND type = 'water'
             AND DATE(sent_at) = CURRENT_DATE""",
        [from_user_id, to_user_id]
    ).fetchone()[0]
    con.close()
    return count > 0

def add_interaction(from_user_id: int, to_user_id: int, type_: str = 'water'):
    con = get_connection()
    con.execute(
        "INSERT INTO interaction (id, from_user_id, to_user_id, type) VALUES (nextval('seq_interaction'), ?, ?, ?)",
        [from_user_id, to_user_id, type_]
    )
    con.close()
