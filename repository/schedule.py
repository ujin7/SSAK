from database import get_connection

def add_schedule(user_id: int, title: str, sched_date: str,
                 color: str = 'blue', memo: str = '', icon: str = 'task'):
    con = get_connection()
    con.execute(
        """INSERT INTO schedule (id, user_id, title, sched_date, color, is_done, memo, icon)
           VALUES (nextval('seq_schedule'), ?, ?, ?, ?, FALSE, ?, ?)""",
        [user_id, title, sched_date, color, memo, icon]
    )
    con.close()

def get_by_date(user_id: int, sched_date: str) -> list[dict]:
    con = get_connection()
    rows = con.execute(
        "SELECT id, title, sched_date, color, is_done, memo, icon FROM schedule WHERE user_id = ? AND sched_date = ? ORDER BY id",
        [user_id, sched_date]
    ).fetchall()
    con.close()
    return [_row_to_dict(r) for r in rows]

def get_monthly(user_id: int, year: int, month: int) -> list[dict]:
    con = get_connection()
    rows = con.execute(
        """SELECT id, title, sched_date, color, is_done, memo, icon
           FROM schedule
           WHERE user_id = ?
             AND YEAR(sched_date) = ?
             AND MONTH(sched_date) = ?
           ORDER BY sched_date""",
        [user_id, year, month]
    ).fetchall()
    con.close()
    return [_row_to_dict(r) for r in rows]

def complete_schedule(schedule_id: int):
    con = get_connection()
    con.execute("UPDATE schedule SET is_done = TRUE WHERE id = ?", [schedule_id])
    con.close()

def delete_schedule(schedule_id: int):
    con = get_connection()
    con.execute("DELETE FROM schedule WHERE id = ?", [schedule_id])
    con.close()

def _row_to_dict(r) -> dict:
    return {'id': r[0], 'title': r[1], 'sched_date': str(r[2]),
            'color': r[3], 'is_done': r[4], 'memo': r[5], 'icon': r[6]}
