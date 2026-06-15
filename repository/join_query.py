import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database import get_connection  # noqa: E402

def query1_user_schedule_plant(user_id: int = 1) -> list[dict]:
    """쿼리1: user + schedule + plant 3개 LEFT JOIN"""
    con = get_connection()
    rows = con.execute(
        """SELECT u.nickname, s.title, s.sched_date, s.is_done, p.stage, p.total_points
           FROM user u
           LEFT JOIN schedule s ON u.id = s.user_id
           LEFT JOIN plant p ON u.id = p.user_id
           WHERE u.id = ?""",
        [user_id]
    ).fetchall()
    con.close()
    return [
        {'nickname': r[0], 'title': r[1], 'sched_date': str(r[2]),
         'is_done': r[3], 'stage': r[4], 'total_points': r[5]}
        for r in rows
    ]

def query2_friend_list_with_plant(user_id: int = 1) -> list[dict]:
    """쿼리2: user + friend + plant 3개 LEFT JOIN (친구 목록)"""
    con = get_connection()
    rows = con.execute(
        """SELECT u.nickname, fu.nickname AS friend_name, fp.stage, fp.total_points
           FROM friend f
           LEFT JOIN user u ON f.from_user_id = u.id
           LEFT JOIN user fu ON f.to_user_id = fu.id
           LEFT JOIN plant fp ON fu.id = fp.user_id
           WHERE f.from_user_id = ? AND f.status = 'accepted'""",
        [user_id]
    ).fetchall()
    con.close()
    return [
        {'nickname': r[0], 'friend_name': r[1], 'stage': r[2], 'total_points': r[3]}
        for r in rows
    ]

def query3_friend_public_schedule(user_id: int = 1) -> list[dict]:
    """쿼리3: user + friend + schedule 3개 LEFT JOIN (친구 공개 일정)"""
    con = get_connection()
    rows = con.execute(
        """SELECT fu.nickname, s.title, s.sched_date, s.icon
           FROM friend f
           LEFT JOIN user fu ON f.to_user_id = fu.id
           LEFT JOIN schedule s ON fu.id = s.user_id AND s.color = 'green'
           WHERE f.from_user_id = ? AND f.status = 'accepted'""",
        [user_id]
    ).fetchall()
    con.close()
    return [
        {'nickname': r[0], 'title': r[1], 'sched_date': str(r[2]) if r[2] else None, 'icon': r[3]}
        for r in rows
    ]

if __name__ == "__main__":
    print("=== 쿼리1: user + schedule + plant ===")
    for row in query1_user_schedule_plant(1):
        print(row)

    print("\n=== 쿼리2: user + friend + plant ===")
    for row in query2_friend_list_with_plant(1):
        print(row)

    print("\n=== 쿼리3: user + friend + schedule (공개일정) ===")
    for row in query3_friend_public_schedule(1):
        print(row)
