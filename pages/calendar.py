import session
import flet as ft
import calendar as cal_lib
from datetime import date
from repository.schedule import get_monthly, get_by_date, complete_schedule, delete_schedule
from repository.plant import add_points, get_plant
from theme import (SCREEN, CARD, CARD_ALT, BORDER, ACCENT, TEXT, SUB, FAINT,
                   FIRE, WATER, DAY_RED, HEAT, STAGE_EMOJI, border)


_DEMO_STAGES = {
    2: 'leaf', 5: 'flower', 8: 'tree', 10: 'leaf',
    14: 'flower', 15: 'tree', 19: 'leaf', 21: 'flower',
    28: 'flower', 29: 'leaf',
}
_DEMO_HEAT = {
    1: 1, 2: 2, 4: 1, 5: 3, 6: 1, 8: 4, 9: 2, 10: 1, 11: 2,
    13: 1, 14: 3, 15: 4, 16: 2, 18: 1, 19: 2, 20: 1, 21: 3,
    23: 2, 24: 1, 25: 2, 27: 1, 28: 3, 29: 2, 30: 2,
}


def build_calendar_page(page: ft.Page) -> ft.Control:
    today      = date.today()
    sel_year   = [today.year]
    sel_month  = [today.month]
    sel_date   = [str(today)]

    month_lbl   = ft.Text('', size=22, weight=ft.FontWeight.W_800, color=TEXT, no_wrap=True)
    streak_lbl  = ft.Text('🔥 0일', size=13, color=FIRE, weight=ft.FontWeight.W_700)
    growth_pct  = ft.Text('', size=18, weight=ft.FontWeight.W_900, color=ACCENT)
    growth_bar  = ft.ProgressBar(value=0, bgcolor='#202819', color=ACCENT)
    stat_streak = ft.Text('', size=17, weight=ft.FontWeight.W_800, color=TEXT)
    stat_days   = ft.Text('', size=17, weight=ft.FontWeight.W_800, color=TEXT)
    stat_rate   = ft.Text('', size=17, weight=ft.FontWeight.W_800, color=ACCENT)

    grid_col = ft.Column(spacing=5)

    detail_date_lbl = ft.Text('', size=16, weight=ft.FontWeight.W_800, color=TEXT)
    detail_list     = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)

    def refresh_detail():
        detail_list.controls.clear()
        items = get_by_date(session.state['user_id'], sel_date[0])
        if not items:
            detail_list.controls.append(
                ft.Container(
                    alignment=ft.Alignment(0, 0),
                    padding=ft.Padding(top=28, bottom=28, left=0, right=0),
                    content=ft.Text('일정이 없어요', color=FAINT, size=13),
                )
            )
            return
        for item in items:
            done = item['is_done']
            def mk_done(sid):
                def h(e):
                    complete_schedule(sid)
                    add_points(session.state['user_id'], 10)
                    refresh_detail()
                    build_grid()
                    page.update()
                return h
            def mk_del(sid):
                def h(e):
                    delete_schedule(sid)
                    refresh_detail()
                    build_grid()
                    page.update()
                return h
            detail_list.controls.append(
                ft.Container(
                    bgcolor=CARD_ALT,
                    border=border(1, BORDER),
                    border_radius=12,
                    padding=ft.Padding(left=14, top=10, right=14, bottom=10),
                    content=ft.Row([
                        ft.Container(
                            width=3, height=36, border_radius=2,
                            bgcolor=ACCENT if done else FAINT,
                        ),
                        ft.Column([
                            ft.Text(
                                item['title'], size=14, weight=ft.FontWeight.W_600,
                                color=FAINT if done else TEXT,
                                style=ft.TextStyle(
                                    decoration=ft.TextDecoration.LINE_THROUGH
                                ) if done else None,
                            ),
                            ft.Text(item['memo'] or '', size=11, color=FAINT),
                        ], spacing=2, expand=True),
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.CHECK_CIRCLE if done
                                     else ft.Icons.RADIO_BUTTON_UNCHECKED,
                                icon_color=ACCENT if done else FAINT,
                                icon_size=20,
                                on_click=mk_done(item['id']),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=DAY_RED,
                                icon_size=20,
                                on_click=mk_del(item['id']),
                            ),
                        ], spacing=0),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                )
            )

    def open_detail(d_str: str):
        sel_date[0] = d_str
        y, m, d = d_str.split('-')
        detail_date_lbl.value = f"{int(m)}월 {int(d)}일"
        refresh_detail()
        detail_dlg.open = True
        page.update()

    def close_detail(e=None):
        detail_dlg.open = False
        build_grid()
        page.update()

    def open_add(e=None):
        from pages.schedule_form import build_schedule_form
        def on_saved():
            refresh_detail()
            build_grid()
            page.update()
        dlg = build_schedule_form(page, sel_date[0], on_saved=on_saved)
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    detail_dlg = ft.AlertDialog(
        bgcolor=CARD,
        shape=ft.RoundedRectangleBorder(radius=22),
        title=ft.Row([
            detail_date_lbl,
            ft.IconButton(
                ft.Icons.ADD_CIRCLE,
                icon_color=ACCENT, icon_size=24,
                on_click=open_add, tooltip='일정 추가',
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        content=ft.Container(
            width=320, height=280,
            content=detail_list,
        ),
        actions=[
            ft.TextButton(
                '닫기', on_click=close_detail,
                style=ft.ButtonStyle(color=SUB),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(detail_dlg)

    def build_grid():
        grid_col.controls.clear()
        y, m = sel_year[0], sel_month[0]
        month_lbl.value = f"{y}년 {m}월"

        schedules = get_monthly(session.state['user_id'], y, m)
        done_cnt: dict[str, int] = {}
        for s in schedules:
            if s['is_done']:
                done_cnt[s['sched_date']] = done_cnt.get(s['sched_date'], 0) + 1

        total         = len(schedules)
        done          = sum(1 for s in schedules if s['is_done'])
        rate          = done / total if total > 0 else 0
        days_recorded = len(set(str(s['sched_date']) for s in schedules))
        plant         = get_plant(session.state['user_id'])
        streak        = plant['streak_days'] if plant else 0

        growth_pct.value  = f"{int(rate * 100)}%"
        growth_bar.value  = rate
        stat_streak.value = f"{streak}일"
        stat_days.value   = f"{days_recorded}일"
        stat_rate.value   = f"{int(rate * 100)}%"
        streak_lbl.value  = f"🔥 {streak}일"

        first_wd, days = cal_lib.monthrange(y, m)
        offset    = (first_wd + 1) % 7
        today_str = str(date.today())
        use_demo  = (y == 2026 and m == 5)

        row_cells = [ft.Container(expand=True, height=52) for _ in range(offset)]

        for day in range(1, days + 1):
            d_str = f"{y}-{m:02d}-{day:02d}"

            db_heat  = min(done_cnt.get(d_str, 0), 4)
            heat     = db_heat if db_heat > 0 else (_DEMO_HEAT.get(day, 0) if use_demo else 0)
            stage    = _DEMO_STAGES.get(day) if use_demo else None
            is_today = (d_str == today_str)
            light    = heat >= 3

            num = ft.Text(
                str(day), size=11,
                weight=ft.FontWeight.W_800 if is_today else ft.FontWeight.W_500,
                color='#0E160A' if light else TEXT,
                text_align=ft.TextAlign.CENTER,
            )
            stack_kids = [
                ft.Container(
                    alignment=ft.Alignment(0, -1),
                    padding=ft.Padding(top=4, bottom=0, left=0, right=0),
                    content=num,
                    expand=True,
                )
            ]
            if stage:
                stack_kids.append(
                    ft.Container(
                        alignment=ft.Alignment(0, 1),
                        padding=ft.Padding(bottom=2, top=0, left=0, right=0),
                        content=ft.Text(STAGE_EMOJI.get(stage, '🌱'), size=13),
                    )
                )

            cell = ft.Container(
                content=ft.Stack(stack_kids, expand=True),
                bgcolor=HEAT[heat],
                border=border(2 if is_today else 1, ACCENT if is_today else BORDER),
                border_radius=9,
                expand=True,
                height=52,
                on_click=lambda e, d=d_str: open_detail(d),
            )
            row_cells.append(cell)

            if len(row_cells) == 7:
                grid_col.controls.append(
                    ft.Row(row_cells, spacing=5, expand=True)
                )
                row_cells = []

        if row_cells:
            while len(row_cells) < 7:
                row_cells.append(ft.Container(expand=True, height=52))
            grid_col.controls.append(
                ft.Row(row_cells, spacing=5, expand=True)
            )

    def on_prev(e):
        if sel_month[0] == 1: sel_month[0] = 12; sel_year[0] -= 1
        else: sel_month[0] -= 1
        build_grid()
        page.update()

    def on_next(e):
        if sel_month[0] == 12: sel_month[0] = 1; sel_year[0] += 1
        else: sel_month[0] += 1
        build_grid()
        page.update()

    build_grid()

    legend = ft.Row([
        ft.Text('적음', size=11, color=SUB),
        *[
            ft.Container(
                width=11, height=11, border_radius=3, bgcolor=c,
                border=border(1, BORDER) if i == 0 else None,
            )
            for i, c in enumerate(HEAT)
        ],
        ft.Text('많음', size=11, color=SUB),
    ], spacing=6, alignment=ft.MainAxisAlignment.END)

    wd_colors = [DAY_RED] + [SUB] * 5 + [WATER]
    wd_row = ft.Row([
        ft.Container(
            expand=True,
            content=ft.Text(
                w, size=12, weight=ft.FontWeight.W_600,
                color=c, text_align=ft.TextAlign.CENTER,
            ),
        )
        for w, c in zip(['일', '월', '화', '수', '목', '금', '토'], wd_colors)
    ])

    growth_card = ft.Container(
        margin=ft.Margin(left=16, top=8, right=16, bottom=18),
        bgcolor=CARD,
        border=border(1, BORDER),
        border_radius=18,
        padding=14,
        content=ft.Column([
            ft.Row([
                ft.Row([
                    ft.Text('🌿', size=20),
                    ft.Text('이번 달 성장률', size=14,
                            weight=ft.FontWeight.W_700, color=TEXT),
                ], spacing=6),
                growth_pct,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(margin=ft.Margin(top=8, bottom=8, left=0, right=0), content=growth_bar),
            ft.Row([
                ft.Column([
                    ft.Text('연속 기록', size=11, color=SUB),
                    stat_streak,
                ], spacing=2),
                ft.Column([
                    ft.Text('기록한 날', size=11, color=SUB),
                    stat_days,
                ], spacing=2),
                ft.Column([
                    ft.Text('완료율', size=11, color=SUB),
                    stat_rate,
                ], spacing=2),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ], spacing=0),
    )

    return ft.Container(
        bgcolor=SCREEN,
        expand=True,
        content=ft.Column([
            ft.Container(
                padding=ft.Padding(left=22, top=4, right=22, bottom=12),
                content=ft.Row([
                    ft.Row([
                        ft.Row([
                            month_lbl,
                            ft.Text('▾', size=16, color=SUB),
                        ], spacing=4),
                        ft.Row([
                            ft.IconButton(
                                ft.Icons.CHEVRON_LEFT,
                                icon_color=SUB, icon_size=18,
                                on_click=on_prev,
                            ),
                            ft.IconButton(
                                ft.Icons.CHEVRON_RIGHT,
                                icon_color=SUB, icon_size=18,
                                on_click=on_next,
                            ),
                        ], spacing=0),
                    ], spacing=8),
                    ft.Row([
                        streak_lbl,
                        ft.Text('⋯', size=20, color=SUB),
                    ], spacing=14),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ),
            ft.Container(
                padding=ft.Padding(left=22, right=22, bottom=10, top=0),
                content=legend,
            ),
            ft.Container(
                padding=ft.Padding(left=16, right=16, top=0, bottom=0),
                content=wd_row,
            ),
            ft.Container(height=4),
            ft.Container(
                padding=ft.Padding(left=16, right=16, top=0, bottom=0),
                content=grid_col,
            ),
            growth_card,
        ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True),
    )
