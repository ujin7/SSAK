import session
import flet as ft
from repository.schedule import get_monthly
from repository.plant import get_plant
from datetime import date
from theme import SCREEN, CARD, BORDER, ACCENT, TEXT, SUB, FAINT, HEAT, border


def build_stats_page(page: ft.Page, go_back) -> ft.Control:
    today = date.today()
    plant = get_plant(session.state['user_id'])

    # 최근 6개월 데이터
    month_bars = []
    for i in range(5, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12; y -= 1
        schedules = get_monthly(session.state['user_id'], y, m)
        total     = len(schedules)
        done      = sum(1 for s in schedules if s['is_done'])
        rate      = done / total if total > 0 else 0
        heat_idx  = min(int(rate * 4), 4)
        month_bars.append((f'{m}월', done, total, rate, heat_idx))

    this_month = get_monthly(session.state['user_id'], today.year, today.month)
    done_this  = sum(1 for s in this_month if s['is_done'])
    total_this = len(this_month)
    rate_this  = int(done_this / total_this * 100) if total_this > 0 else 0

    # 바 차트
    max_done = max((b[1] for b in month_bars), default=1) or 1
    bars = []
    for label, done, total, rate, heat_idx in month_bars:
        bar_h = max(4, int(120 * done / max_done)) if done > 0 else 4
        bars.append(
            ft.Column([
                ft.Text(f'{done}', size=10, color=SUB, text_align=ft.TextAlign.CENTER),
                ft.Container(
                    width=32, height=bar_h,
                    bgcolor=HEAT[heat_idx],
                    border_radius=ft.BorderRadius(4, 4, 0, 0),
                ),
                ft.Container(height=4),
                ft.Text(label, size=10, color=FAINT, text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
               spacing=4,
               alignment=ft.MainAxisAlignment.END,
            )
        )

    stat_cards = [
        ('🎯 완료율',  f'{rate_this}%',                              '이번 달'),
        ('✅ 완료',    f'{done_this}개',                              '이번 달'),
        ('📋 전체',    f'{total_this}개',                             '이번 달'),
        ('🔥 연속',    f"{plant['streak_days'] if plant else 0}일",   '현재'),
        ('⭐ 포인트',  f"{plant['total_points'] if plant else 0}p",   '누적'),
        ('🌱 단계',    plant['stage'] if plant else 'seed',           '현재'),
    ]

    def make_card_row(items):
        return ft.Row([
            ft.Container(
                expand=True,
                bgcolor=CARD,
                border_radius=14,
                border=border(1, BORDER),
                padding=ft.Padding(left=14, top=14, right=14, bottom=14),
                content=ft.Column([
                    ft.Text(label, size=11, color=SUB),
                    ft.Text(value, size=20, weight=ft.FontWeight.W_800, color=ACCENT),
                    ft.Text(period, size=10, color=FAINT),
                ], spacing=3),
            )
            for label, value, period in items
        ], spacing=10)

    return ft.Container(
        bgcolor=SCREEN,
        expand=True,
        content=ft.Column([
            ft.Container(
                padding=ft.Padding(left=8, top=4, right=22, bottom=12),
                content=ft.Row([
                    ft.IconButton(
                        ft.Icons.ARROW_BACK_IOS_NEW,
                        icon_color=SUB, icon_size=20,
                        on_click=lambda e: go_back(),
                    ),
                    ft.Text('통계', size=20, weight=ft.FontWeight.W_800, color=TEXT),
                    ft.Container(width=40),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ),
            ft.Container(
                expand=True,
                padding=ft.Padding(left=16, top=0, right=16, bottom=20),
                content=ft.Column([
                    ft.Container(
                        bgcolor=CARD,
                        border_radius=18,
                        border=border(1, BORDER),
                        padding=ft.Padding(left=16, top=16, right=16, bottom=16),
                        content=ft.Column([
                            ft.Text('월별 완료 현황', size=14,
                                    weight=ft.FontWeight.W_700, color=TEXT),
                            ft.Container(height=12),
                            ft.Row(
                                bars,
                                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                vertical_alignment=ft.CrossAxisAlignment.END,
                            ),
                        ]),
                    ),
                    ft.Container(height=12),
                    make_card_row(stat_cards[:3]),
                    ft.Container(height=10),
                    make_card_row(stat_cards[3:]),
                ], spacing=0, scroll=ft.ScrollMode.AUTO),
            ),
        ], spacing=0, expand=True),
    )
