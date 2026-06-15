import session
import flet as ft
from repository.user import get_user, update_user
from repository.plant import get_plant
from repository.schedule import get_monthly
from datetime import date
from theme import SCREEN, CARD, BORDER, ACCENT, TEXT, SUB, FAINT, border


def build_profile_page(page: ft.Page, navigate=None, on_logout=None) -> ft.Control:
    nickname_text = ft.Text('', size=22, weight=ft.FontWeight.W_800, color=TEXT)
    avatar_emoji  = ft.Text('🌿', size=40)
    stats_row     = ft.Row(
        wrap=True,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10, run_spacing=10,
    )

    def refresh():
        user  = get_user(session.state['user_id'])
        plant = get_plant(session.state['user_id'])
        if user is None:
            return

        nickname_text.value = user['nickname']

        today      = date.today()
        schedules  = get_monthly(session.state['user_id'], today.year, today.month)
        done_count = sum(1 for s in schedules if s['is_done'])
        total      = len(schedules)
        rate       = int(done_count / total * 100) if total > 0 else 0

        stats_row.controls.clear()
        for label, value in [
            ('이번달 완료', f"{done_count}개"),
            ('총 포인트',   f"{plant['total_points'] if plant else 0}p"),
            ('연속일수',    f"{plant['streak_days'] if plant else 0}일"),
            ('완료율',      f"{rate}%"),
        ]:
            stats_row.controls.append(
                ft.Container(
                    bgcolor=CARD,
                    border_radius=14,
                    border=border(1, BORDER),
                    padding=ft.Padding(left=14, top=12, right=14, bottom=12),
                    content=ft.Column([
                        ft.Text(value, size=17, weight=ft.FontWeight.W_800, color=ACCENT),
                        ft.Text(label, size=11, color=SUB),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                )
            )
        page.update()

    def open_edit_dialog(e):
        tf = ft.TextField(
            label='닉네임', value=nickname_text.value, autofocus=True,
            color=TEXT, border_color=BORDER, focused_border_color=ACCENT,
            label_style=ft.TextStyle(color=SUB),
        )

        def save(ev):
            if tf.value.strip():
                update_user(session.state['user_id'], nickname=tf.value.strip())
                dlg.open = False
                page.update()
                refresh()

        def cancel(ev):
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            bgcolor=CARD,
            shape=ft.RoundedRectangleBorder(radius=22),
            title=ft.Text('프로필 설정', color=TEXT, weight=ft.FontWeight.W_700),
            content=tf,
            actions=[
                ft.TextButton('취소', on_click=cancel, style=ft.ButtonStyle(color=SUB)),
                ft.ElevatedButton('저장', bgcolor=ACCENT, color='#0E120C', on_click=save),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    refresh()

    return ft.Container(
        bgcolor=SCREEN,
        expand=True,
        content=ft.Column([
            ft.Container(
                padding=ft.Padding(left=22, top=4, right=22, bottom=12),
                content=ft.Text('프로필', size=22, weight=ft.FontWeight.W_800, color=TEXT),
            ),
            ft.Container(
                expand=True,
                padding=ft.Padding(left=20, top=16, right=20, bottom=20),
                content=ft.Column([
                    ft.Container(
                        alignment=ft.Alignment(0, 0),
                        content=ft.Container(
                            width=90, height=90,
                            border_radius=45,
                            bgcolor=CARD,
                            border=border(2, ACCENT),
                            alignment=ft.Alignment(0, 0),
                            content=avatar_emoji,
                        ),
                    ),
                    ft.Container(height=14),
                    ft.Container(alignment=ft.Alignment(0, 0), content=nickname_text),
                    ft.Container(
                        alignment=ft.Alignment(0, 0),
                        content=ft.Row([
                            ft.TextButton(
                                '프로필 설정',
                                icon=ft.Icons.EDIT,
                                on_click=open_edit_dialog,
                                style=ft.ButtonStyle(color=SUB),
                            ),
                            ft.TextButton(
                                '통계',
                                icon=ft.Icons.BAR_CHART,
                                on_click=lambda e: navigate('stats') if navigate else None,
                                style=ft.ButtonStyle(color=ACCENT),
                            ),
                            ft.TextButton(
                                '상점',
                                icon=ft.Icons.STORE,
                                on_click=lambda e: navigate('shop') if navigate else None,
                                style=ft.ButtonStyle(color=ACCENT),
                            ),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=0),
                    ),
                    ft.Container(height=20),
                    stats_row,
                    ft.Container(height=16),
                    ft.TextButton(
                        '로그아웃',
                        icon=ft.Icons.LOGOUT,
                        on_click=lambda e: on_logout() if on_logout else None,
                        style=ft.ButtonStyle(color='#E05C5C'),
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
            ),
        ], spacing=0, expand=True),
    )
