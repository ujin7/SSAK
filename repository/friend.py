from database import get_connection

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
        """SELECT u.id, u.nickname, u.profile_img,
                  p.stage, p.total_points
           FROM friend f
           JOIN user u ON f.to_user_id = u.id
           LEFT JOIN plant p ON u.id = p.user_id
           WHERE f.from_user_id = ? AND f.status = 'accepted'""",
        [user_id]
    ).fetchall()
    con.close()
    return [
        {'id': r[0], 'nickname': r[1], 'profile_img': r[2],
         'stage': r[3], 'total_points': r[4]}
        for r in rows
    ]

def add_interaction(from_user_id: int, to_user_id: int, type_: str = 'water'):
    con = get_connection()
    con.execute(
        "INSERT INTO interaction (id, from_user_id, to_user_id, type) VALUES (nextval('seq_interaction'), ?, ?, ?)",
        [from_user_id, to_user_id, type_]
    )
    con.close()
