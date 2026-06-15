import session
import flet as ft
from repository.plant import get_plant, add_water_points
from repository.user import get_user
from repository.friend import add_interaction, interaction_cooldown_label
from theme import (SCREEN, CARD, BORDER, ACCENT, TEXT, SUB, FAINT,
                   WATER, STAGE_LABELS, border, stage_progress)

# 상호작용 버튼 설정: (label, icon, type_, points, active_color)
ACTIONS = [
    ('햇빛 주기', ft.Icons.WB_SUNNY,    'like',  10, '#F5C840'),
    ('물 주기',   ft.Icons.WATER_DROP,  'water', 10, WATER),
    ('비료 주기', ft.Icons.GRASS,       'cheer', 20, ACCENT),
]


def build_friend_garden_page(page: ft.Page, friend_id: int, go_back) -> ft.Control:
    user  = get_user(friend_id)
    plant = [get_plant(friend_id)]   # list로 감싸 refresh 시 교체 가능

    nickname = user['nickname'] if user else '친구'

    # ── 식물 정보 컨트롤 ──────────────────────────────────────────────────────
    plant_img    = ft.Image(src='seed.png', width=160, height=160)
    stage_text   = ft.Text('', size=22, weight=ft.FontWeight.W_800, color=ACCENT)
    points_text  = ft.Text('', size=15, color=SUB)
    streak_text  = ft.Text('', size=13, color=FAINT)
    progress_bar = ft.ProgressBar(value=0, bgcolor='#202819', color=ACCENT)
    prog_label   = ft.Text('', size=11, color=SUB, text_align=ft.TextAlign.CENTER)

    def refresh_plant():
        p = plant[0]
        if p is None:
            return
        plant_img.src       = p['image_path']
        stage_text.value    = STAGE_LABELS.get(p['stage'], p['stage'])
        points_text.value   = f"{p['total_points']} 포인트"
        streak_text.value   = f"연속 {p['streak_days']}일"
        ratio, lbl          = stage_progress(p['stage'], p['total_points'])
        progress_bar.value  = ratio
        prog_label.value    = lbl

    refresh_plant()

    # ── 액션 버튼 ─────────────────────────────────────────────────────────────
    def make_action(label, icon, type_, pts, color):
        cooldown = interaction_cooldown_label(session.state['user_id'], friend_id, type_)

        def active_content():
            return ft.Column([
                ft.Icon(icon, color='#0E120C', size=22),
                ft.Text(label, size=12, color='#0E120C',
                        weight=ft.FontWeight.W_700, text_align=ft.TextAlign.CENTER),
                ft.Text(f'+{pts}p', size=11, color='#0E120C',
                        text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
               alignment=ft.MainAxisAlignment.CENTER, spacing=3)

        def cooldown_content(cd_text):
            return ft.Column([
                ft.Icon(ft.Icons.ACCESS_TIME, color=SUB, size=20),
                ft.Text(cd_text, size=12, color=SUB,
                        text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
               alignment=ft.MainAxisAlignment.CENTER, spacing=4)

        container = ft.Container(
            expand=True, height=80, border_radius=20,
            bgcolor=CARD if cooldown else color,
            border=border(1, BORDER) if cooldown else None,
            content=cooldown_content(cooldown) if cooldown else active_content(),
        )

        def on_click(e):
            if container.bgcolor != color:
                return
            add_interaction(session.state['user_id'], friend_id, type_)
            add_water_points(friend_id, pts)
            plant[0] = get_plant(friend_id)
            refresh_plant()
            container.bgcolor = CARD
            container.border  = border(1, BORDER)
            container.content = cooldown_content('24시간 후')
            page.snack_bar = ft.SnackBar(
                ft.Text(f"{nickname}의 식물에 {label}! (+{pts}p)"), bgcolor=CARD,
            )
            page.snack_bar.open = True
            page.update()

        container.on_click = on_click
        return container

    action_row = ft.Row(
        [make_action(l, i, t, p, c) for l, i, t, p, c in ACTIONS],
        spacing=8,
    )

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
                    ft.Text(f'{nickname}의 정원', size=20,
                            weight=ft.FontWeight.W_800, color=TEXT),
                    ft.Container(width=40),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ),
            ft.Container(
                expand=True,
                padding=ft.Padding(left=20, top=8, right=20, bottom=8),
                content=ft.Column([
                    ft.Container(
                        alignment=ft.Alignment(0, 0),
                        bgcolor=CARD,
                        border_radius=24,
                        border=border(1, BORDER),
                        padding=32,
                        content=plant_img,
                    ),
                    ft.Container(height=16),
                    ft.Container(alignment=ft.Alignment(0, 0), content=stage_text),
                    ft.Container(alignment=ft.Alignment(0, 0), content=points_text),
                    ft.Container(alignment=ft.Alignment(0, 0), content=streak_text),
                    ft.Container(height=12),
                    ft.Container(
                        bgcolor=CARD,
                        border_radius=16,
                        border=border(1, BORDER),
                        padding=ft.Padding(left=20, top=14, right=20, bottom=14),
                        content=ft.Column([
                            progress_bar,
                            ft.Container(height=6),
                            prog_label,
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
            ),
            ft.Container(
                padding=ft.Padding(left=16, top=8, right=16, bottom=20),
                content=action_row,
            ),
        ], spacing=0, expand=True),
    )
