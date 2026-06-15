from database import get_connection
from repository.plant import calc_stage

def get_items() -> list[dict]:
    con = get_connection()
    rows = con.execute(
        "SELECT id, name, description, price, emoji, category FROM item ORDER BY category, price"
    ).fetchall()
    con.close()
    return [{'id': r[0], 'name': r[1], 'description': r[2],
             'price': r[3], 'emoji': r[4], 'category': r[5]}
            for r in rows]

def get_user_items(user_id: int) -> set[int]:
    con = get_connection()
    rows = con.execute(
        "SELECT item_id FROM user_item WHERE user_id = ?", [user_id]
    ).fetchall()
    con.close()
    return {r[0] for r in rows}

def buy_item(user_id: int, item_id: int, price: int) -> bool:
    """포인트 차감 + 아이템 지급을 트랜잭션으로 처리 (원자성 보장)"""
    con = get_connection()
    try:
        con.begin()

        row = con.execute(
            "SELECT total_points FROM plant WHERE user_id = ?", [user_id]
        ).fetchone()
        if row is None or row[0] < price:
            con.rollback()
            return False

        exists = con.execute(
            "SELECT 1 FROM user_item WHERE user_id = ? AND item_id = ?", [user_id, item_id]
        ).fetchone()
        if exists:
            con.rollback()
            return False

        new_points = row[0] - price
        new_stage  = calc_stage(new_points)

        con.execute(
            "UPDATE plant SET total_points = ?, stage = ?, last_updated = NOW() WHERE user_id = ?",
            [new_points, new_stage, user_id]
        )
        # 복합 PK → id 없이 INSERT
        con.execute(
            "INSERT INTO user_item (user_id, item_id) VALUES (?, ?)",
            [user_id, item_id]
        )
        con.commit()
        return True
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()
