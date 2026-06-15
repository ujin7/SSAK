import flet as ft

# ── 색상 토큰 ──────────────────────────────────────────────
SCREEN   = '#12160F'
CARD     = '#1A2014'
CARD_ALT = '#1F2618'
BORDER   = '#2C3622'
ACCENT   = '#84CC4E'
TEXT     = '#EAF0E2'
SUB      = '#94A085'
FAINT    = '#5E6B52'
FIRE     = '#E8893B'
WATER    = '#5AA7D6'
DAY_RED  = '#e2706a'
HEAT     = ['#1A2014', '#274A22', '#386E2C', '#52993B', '#84CC4E']

# ── 식물 상수 ──────────────────────────────────────────────
STAGE_EMOJI = {'seed': '🌱', 'leaf': '🌿', 'flower': '🌸', 'tree': '🌳'}
STAGE_LABELS = {'seed': '씨앗 단계', 'leaf': '새싹 단계', 'flower': '꽃 단계', 'tree': '나무 단계'}
STAGE_COLORS = {'seed': '#94A085', 'leaf': '#84CC4E', 'flower': '#EC407A', 'tree': '#52993B'}
STAGE_START  = {'seed': 0, 'leaf': 50, 'flower': 100, 'tree': 200}
NEXT_STAGE   = {'seed': 50, 'leaf': 100, 'flower': 200, 'tree': None}

# ── 공통 헬퍼 ─────────────────────────────────────────────
def border(width: int, color: str) -> ft.Border:
    s = ft.BorderSide(width, color)
    return ft.Border(left=s, right=s, top=s, bottom=s)

def stage_progress(stage: str, points: int) -> tuple[float, str]:
    next_pts = NEXT_STAGE.get(stage)
    if next_pts is None:
        return 1.0, '최고 단계 달성! 🎉'
    start = STAGE_START.get(stage, 0)
    ratio = max(0.0, min(1.0, (points - start) / (next_pts - start)))
    return ratio, f'다음 단계까지 {next_pts - points} 포인트'
