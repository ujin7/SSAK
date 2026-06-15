import flet as ft
import session
from repository.user import get_users_with_plant, create_user_with_plant
from theme import SCREEN, CARD, CARD_ALT, BORDER, ACCENT, TEXT, SUB, FAINT, STAGE_EMOJI, border


def build_login_page(page: ft.Page, on_login) -> ft.Control:
    users      = get_users_with_plant()
    user_list  = ft.Column(spacing=10)
    error_text = ft.Text('', color='#E8504A', size=12)

    for u in users:
        emoji = STAGE_EMOJI.get(u['stage'], '🌱')

        def make_login(uid):
            def h(e):
                session.state['user_id'] = uid
                on_login()
            return h

        user_list.controls.append(
            ft.Container(
                bgcolor=CARD,
                border_radius=16,
                border=border(1, BORDER),
                padding=ft.Padding(left=16, top=14, right=16, bottom=14),
                on_click=make_login(u['id']),
                content=ft.Row([
                    ft.Container(
                        width=48, height=48, border_radius=24,
                        bgcolor=CARD_ALT,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text(emoji, size=24),
                    ),
                    ft.Container(width=12),
                    ft.Column([
                        ft.Text(u['nickname'], size=16,
                                weight=ft.FontWeight.W_700, color=TEXT),
                        ft.Text(f"{u['stage']} · {u['points']}p",
                                size=12, color=SUB),
                    ], spacing=3, expand=True),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, color=FAINT, size=20),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            )
        )

    nick_field = ft.TextField(
        hint_text='닉네임 입력',
        color=TEXT, border_color=BORDER,
        focused_border_color=ACCENT,
        hint_style=ft.TextStyle(color=FAINT),
        border_radius=12,
        content_padding=ft.Padding(left=14, top=12, right=14, bottom=12),
    )

    def create_account(e):
        name = nick_field.value.strip()
        if not name:
            error_text.value = '닉네임을 입력해주세요'
            page.update()
            return
        if len(name) > 12:
            error_text.value = '12자 이내로 입력해주세요'
            page.update()
            return
        new_id = create_user_with_plant(name)
        session.state['user_id'] = new_id
        on_login()

    return ft.Container(
        bgcolor=SCREEN,
        expand=True,
        content=ft.Column([
            ft.Container(height=60),
            ft.Container(
                alignment=ft.Alignment(0, 0),
                content=ft.Column([
                    ft.Text('🌱', size=64, text_align=ft.TextAlign.CENTER),
                    ft.Text('싹', size=36, weight=ft.FontWeight.W_900,
                            color=ACCENT, text_align=ft.TextAlign.CENTER),
                    ft.Text('나만의 습관 정원', size=14, color=SUB,
                            text_align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
            ),
            ft.Container(height=40),
            ft.Container(
                padding=ft.Padding(left=24, top=0, right=24, bottom=0),
                content=ft.Column([
                    ft.Text('계정을 선택하세요', size=13, color=SUB),
                    ft.Container(height=8),
                    user_list,
                    ft.Container(height=20),
                    ft.Divider(color=BORDER, height=1),
                    ft.Container(height=16),
                    ft.Text('새 계정 만들기', size=13, color=SUB),
                    ft.Container(height=8),
                    nick_field,
                    ft.Container(height=4),
                    error_text,
                    ft.Container(height=8),
                    ft.ElevatedButton(
                        '시작하기',
                        bgcolor=ACCENT, color='#0E120C',
                        width=999,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                        on_click=create_account,
                    ),
                ], spacing=0),
            ),
        ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True),
    )
