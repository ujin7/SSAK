import hashlib
from database import get_connection

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(user_id: int) -> dict | None:
    con = get_connection()
    row = con.execute(
        "SELECT id, nickname, is_public, created_at FROM user WHERE id = ?",
        [user_id]
    ).fetchone()
    con.close()
    if row is None:
        return None
    return {'id': row[0], 'nickname': row[1], 'is_public': row[2], 'created_at': row[3]}

def get_all_users() -> list[dict]:
    con = get_connection()
    rows = con.execute("SELECT id, nickname, is_public, created_at FROM user").fetchall()
    con.close()
    return [{'id': r[0], 'nickname': r[1], 'is_public': r[2], 'created_at': r[3]} for r in rows]

def update_user(user_id: int, nickname: str = None, is_public: bool = None):
    con = get_connection()
    if nickname is not None:
        con.execute("UPDATE user SET nickname = ? WHERE id = ?", [nickname, user_id])
    if is_public is not None:
        con.execute("UPDATE user SET is_public = ? WHERE id = ?", [is_public, user_id])
    con.close()

def get_users_with_plant() -> list[dict]:
    con = get_connection()
    rows = con.execute("""
        SELECT u.id, u.nickname, p.stage, p.total_points
        FROM user u
        LEFT JOIN plant p ON u.id = p.user_id
        ORDER BY u.id
    """).fetchall()
    con.close()
    return [{'id': r[0], 'nickname': r[1], 'stage': r[2] or 'seed', 'points': r[3] or 0}
            for r in rows]

def verify_login(nickname: str, password: str) -> dict | None:
    con = get_connection()
    row = con.execute(
        "SELECT id, nickname, is_public FROM user WHERE nickname = ? AND password_hash = ?",
        [nickname, _hash(password)]
    ).fetchone()
    con.close()
    if row is None:
        return None
    return {'id': row[0], 'nickname': row[1], 'is_public': row[2]}

def create_user_with_plant(nickname: str, password: str) -> int:
    con = get_connection()
    try:
        con.begin()
        new_id = con.execute("SELECT nextval('seq_user')").fetchone()[0]
        con.execute(
            "INSERT INTO user (id, nickname, password_hash, is_public) VALUES (?, ?, ?, TRUE)",
            [new_id, nickname, _hash(password)]
        )
        plant_id = con.execute("SELECT nextval('seq_plant')").fetchone()[0]
        con.execute(
            "INSERT INTO plant (id, user_id, stage, total_points, streak_days) VALUES (?, ?, 'seed', 0, 0)",
            [plant_id, new_id]
        )
        con.commit()
        return new_id
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()
