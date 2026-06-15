import flet as ft
from repository.plant import get_plant
from repository.user import get_user
from theme import (SCREEN, CARD, BORDER, ACCENT, TEXT, SUB, FAINT,
                   STAGE_LABELS, STAGE_EMOJI, border, stage_progress)


def build_friend_garden_page(page: ft.Page, friend_id: int, go_back) -> ft.Control:
    user  = get_user(friend_id)
    plant = get_plant(friend_id)

    nickname   = user['nickname'] if user else '친구'
    stage      = plant['stage']       if plant else 'seed'
    points     = plant['total_points'] if plant else 0
    streak     = plant['streak_days']  if plant else 0
    image_path = plant['image_path']   if plant else 'seed.png'

    progress, prog_label = stage_progress(stage, points)

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
                padding=ft.Padding(left=20, top=8, right=20, bottom=20),
                content=ft.Column([
                    ft.Container(
                        alignment=ft.Alignment(0, 0),
                        bgcolor=CARD,
                        border_radius=24,
                        border=border(1, BORDER),
                        padding=32,
                        content=ft.Image(src=image_path, width=160, height=160),
                    ),
                    ft.Container(height=20),
                    ft.Container(
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text(
                            STAGE_LABELS.get(stage, stage),
                            size=22, weight=ft.FontWeight.W_800, color=ACCENT,
                        ),
                    ),
                    ft.Container(
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text(f'{points} 포인트', size=15, color=SUB),
                    ),
                    ft.Container(
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text(f'연속 {streak}일', size=13, color=FAINT),
                    ),
                    ft.Container(height=16),
                    ft.Container(
                        bgcolor=CARD,
                        border_radius=16,
                        border=border(1, BORDER),
                        padding=ft.Padding(left=20, top=16, right=20, bottom=16),
                        content=ft.Column([
                            ft.ProgressBar(value=progress, bgcolor='#202819', color=ACCENT),
                            ft.Container(height=6),
                            ft.Text(prog_label, size=11, color=SUB,
                                    text_align=ft.TextAlign.CENTER),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
            ),
        ], spacing=0, expand=True),
    )
