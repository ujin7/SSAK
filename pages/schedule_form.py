import session
import flet as ft
from repository.schedule import add_schedule
from theme import SCREEN, CARD, CARD_ALT, BORDER, ACCENT, TEXT, SUB, FAINT, border


COLOR_OPTIONS = [
    ('blue',   '#4A90D9', '파랑'),
    ('green',  '#5CB85C', '초록'),
    ('red',    '#D9534F', '빨강'),
    ('yellow', '#F0AD4E', '노랑'),
]

ICON_OPTIONS = [
    ('task',    ft.Icons.TASK_ALT,       '할일'),
    ('health',  ft.Icons.FITNESS_CENTER, '건강'),
    ('book',    ft.Icons.MENU_BOOK,      '독서'),
    ('meeting', ft.Icons.GROUPS,         '미팅'),
]


def build_schedule_form(page: ft.Page, default_date: str, on_saved=None) -> ft.AlertDialog:
    def _field(label, **kwargs):
        return ft.TextField(
            label=label,
            color=TEXT,
            border_color=BORDER,
            focused_border_color=ACCENT,
            label_style=ft.TextStyle(color=SUB),
            border_radius=10,
            **kwargs,
        )

    title_field = _field('제목', autofocus=True)
    memo_field  = _field('메모 (선택)', multiline=True, min_lines=2)
    date_field  = _field('날짜', value=default_date)

    selected_color = [COLOR_OPTIONS[0][0]]
    selected_icon  = [ICON_OPTIONS[0][0]]

    color_row = ft.Row(spacing=8, wrap=True)
    icon_row  = ft.Row(spacing=8, wrap=True)

    def rebuild_colors():
        color_row.controls.clear()
        for key, hex_color, label in COLOR_OPTIONS:
            is_sel = (key == selected_color[0])
            color_row.controls.append(
                ft.Container(
                    bgcolor=hex_color,
                    border_radius=20,
                    padding=ft.Padding(left=14, top=6, right=14, bottom=6),
                    border=border(2, '#FFFFFF') if is_sel else border(1, '#00000000'),
                    on_click=lambda e, k=key: (selected_color.__setitem__(0, k), rebuild_colors(), page.update()),
                    content=ft.Text(label, color='#FFFFFF', size=12, weight=ft.FontWeight.W_600),
                )
            )

    def rebuild_icons():
        icon_row.controls.clear()
        for key, icon, label in ICON_OPTIONS:
            is_sel = (key == selected_icon[0])
            icon_row.controls.append(
                ft.Container(
                    bgcolor=CARD_ALT,
                    border_radius=10,
                    padding=ft.Padding(left=10, top=6, right=10, bottom=6),
                    border=border(2, ACCENT) if is_sel else border(1, BORDER),
                    on_click=lambda e, k=key: (selected_icon.__setitem__(0, k), rebuild_icons(), page.update()),
                    content=ft.Row([
                        ft.Icon(icon, size=15,
                                color=ACCENT if is_sel else SUB),
                        ft.Text(label, size=12,
                                color=TEXT if is_sel else SUB,
                                weight=ft.FontWeight.W_600 if is_sel else ft.FontWeight.W_400),
                    ], spacing=4, tight=True),
                )
            )

    rebuild_colors()
    rebuild_icons()

    def save(e):
        if not title_field.value.strip():
            title_field.error_text = '제목을 입력해주세요'
            page.update()
            return
        add_schedule(
            user_id=session.state['user_id'],
            title=title_field.value.strip(),
            sched_date=date_field.value,
            color=selected_color[0],
            memo=memo_field.value or '',
            icon=selected_icon[0],
        )
        dlg.open = False
        page.update()
        if on_saved:
            on_saved()

    def cancel(e):
        dlg.open = False
        page.update()

    dlg = ft.AlertDialog(
        bgcolor=CARD,
        shape=ft.RoundedRectangleBorder(radius=22),
        title=ft.Text('일정 추가', weight=ft.FontWeight.W_800, color=TEXT),
        content=ft.Container(
            width=320,
            content=ft.Column([
                title_field,
                date_field,
                ft.Container(height=2),
                ft.Text('색상', size=11, color=SUB),
                color_row,
                ft.Text('아이콘', size=11, color=SUB),
                icon_row,
                memo_field,
            ], spacing=10, tight=True),
        ),
        actions=[
            ft.TextButton('취소', on_click=cancel, style=ft.ButtonStyle(color=SUB)),
            ft.ElevatedButton('저장', bgcolor=ACCENT, color='#0E120C', on_click=save),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    return dlg
