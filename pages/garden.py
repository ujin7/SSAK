import session
import flet as ft
from repository.plant import get_plant
from theme import (SCREEN, CARD, BORDER, ACCENT, TEXT, SUB, FAINT,
                   STAGE_EMOJI, STAGE_LABELS, STAGE_COLORS, border, stage_progress)


def build_garden_page(page: ft.Page) -> ft.Control:
    plant_img      = ft.Text('🌱', size=80)
    stage_text     = ft.Text('씨앗 단계', size=22, weight=ft.FontWeight.W_800, color=ACCENT)
    points_text    = ft.Text('0 포인트', size=15, color=SUB)
    streak_text    = ft.Text('연속 0일', size=13, color=FAINT)
    progress_bar   = ft.ProgressBar(value=0, bgcolor='#202819', color=ACCENT)
    progress_label = ft.Text('', size=11, color=SUB)

    def refresh():
        plant = get_plant(session.state['user_id'])
        if plant is None:
            return
        stage  = plant['stage']
        points = plant['total_points']
        streak = plant['streak_days']

        plant_img.value       = STAGE_EMOJI.get(stage, '🌱')
        stage_text.value      = STAGE_LABELS.get(stage, stage)
        stage_text.color      = STAGE_COLORS.get(stage, ACCENT)
        points_text.value     = f'{points} 포인트'
        streak_text.value     = f'연속 {streak}일'

        ratio, label = stage_progress(stage, points)
        progress_bar.value   = ratio
        progress_label.value = label

        page.update()

    refresh()

    return ft.Container(
        bgcolor=SCREEN,
        expand=True,
        content=ft.Column([
            ft.Container(
                padding=ft.Padding(left=22, top=4, right=22, bottom=12),
                content=ft.Text('나의 정원', size=22, weight=ft.FontWeight.W_800, color=TEXT),
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
                        content=plant_img,
                    ),
                    ft.Container(height=20),
                    ft.Container(alignment=ft.Alignment(0, 0), content=stage_text),
                    ft.Container(alignment=ft.Alignment(0, 0), content=points_text),
                    ft.Container(alignment=ft.Alignment(0, 0), content=streak_text),
                    ft.Container(height=16),
                    ft.Container(
                        bgcolor=CARD,
                        border_radius=16,
                        border=border(1, BORDER),
                        padding=ft.Padding(left=20, top=16, right=20, bottom=16),
                        content=ft.Column([
                            progress_bar,
                            ft.Container(height=6),
                            progress_label,
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    ),
                    ft.Container(height=16),
                    ft.Container(
                        bgcolor=CARD,
                        border_radius=12,
                        padding=ft.Padding(left=16, top=12, right=16, bottom=12),
                        content=ft.Text(
                            '일정을 완료하면 10포인트를 받아요!\n식물이 나무로 성장해요 🌳',
                            size=12, color=SUB, text_align=ft.TextAlign.CENTER,
                        ),
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
            ),
        ], spacing=0, expand=True),
    )
