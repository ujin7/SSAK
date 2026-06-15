import session
import flet as ft
from repository.friend import (get_friends_with_plant, search_users,
                                send_request, accept, get_pending_requests,
                                add_interaction, has_watered_today,
                                water_cooldown_label, get_feed, FEED_TYPE)
from repository.plant import add_water_points
from theme import (SCREEN, CARD, CARD_ALT, BORDER, ACCENT, TEXT, SUB, FAINT,
                   WATER, FIRE, STAGE_LABELS, STAGE_EMOJI, border)


def build_friends_page(page: ft.Page, navigate=None) -> ft.Control:
    # ── 탭 상태 ───────────────────────────────────────────────────────────────
    sel_tab = ['feed']   # 'feed' | 'list'

    feed_col   = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    friend_col = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    friend_list = friend_col   # 기존 코드와 호환

    tab_feed_btn = ft.Container()
    tab_list_btn = ft.Container()

    def render_tabs():
        def make_tab(label, key):
            active = sel_tab[0] == key
            return ft.Container(
                expand=True,
                padding=ft.Padding(left=0, top=8, right=0, bottom=8),
                border=ft.Border(bottom=ft.BorderSide(2, ACCENT if active else 'transparent')),
                alignment=ft.Alignment(0, 0),
                on_click=lambda e, k=key: switch_tab(k),
                content=ft.Text(label, size=14,
                                weight=ft.FontWeight.W_700 if active else ft.FontWeight.W_500,
                                color=TEXT if active else SUB),
            )
        tab_row.controls = [make_tab('피드', 'feed'), make_tab('친구 목록', 'list')]

    def switch_tab(key):
        sel_tab[0] = key
        feed_col.visible   = (key == 'feed')
        friend_col.visible = (key == 'list')
        render_tabs()
        if key == 'feed':
            refresh_feed()
        page.update()

    tab_row = ft.Row(spacing=0, expand=True)
    render_tabs()

    # ── 피드 ─────────────────────────────────────────────────────────────────
    def refresh_feed():
        feed_col.controls.clear()
        items = get_feed(session.state['user_id'])
        if not items:
            feed_col.controls.append(
                ft.Container(
                    alignment=ft.Alignment(0, 0), padding=40,
                    content=ft.Text('아직 활동이 없어요', color=FAINT),
                )
            )
            return
        for item in items:
            me = session.state['user_id']
            is_received = item['to_id'] == me
            emoji, action = FEED_TYPE.get(item['type'], ('?', '?'))
            if is_received:
                msg = f"{item['from_name']}이(가) 내 식물에 {action}"
            else:
                msg = f"{item['to_name']}에게 {action}"
            feed_col.controls.append(
                ft.Container(
                    bgcolor=CARD,
                    border_radius=14,
                    border=border(1, BORDER),
                    padding=ft.Padding(left=16, top=12, right=16, bottom=12),
                    content=ft.Row([
                        ft.Text(emoji, size=28),
                        ft.Container(width=12),
                        ft.Column([
                            ft.Text(msg, size=13, color=TEXT,
                                    weight=ft.FontWeight.W_600),
                            ft.Text(item['time_ago'], size=11, color=FAINT),
                        ], spacing=3, expand=True),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                )
            )

    refresh_feed()

    water_buttons: dict[int, ft.ElevatedButton] = {}

    def water_plant(friend_id: int, friend_name: str):
        add_interaction(session.state['user_id'], friend_id)
        add_water_points(friend_id, 5)
        btn = water_buttons.get(friend_id)
        if btn:
            btn.text     = '24시간 후'
            btn.icon     = ft.Icons.ACCESS_TIME
            btn.bgcolor  = FAINT
            btn.color    = SUB
            btn.disabled = True
        page.snack_bar = ft.SnackBar(
            ft.Text(f"{friend_name}의 식물에 물을 줬어요 💧 (+5p)"), bgcolor=CARD,
        )
        page.snack_bar.open = True
        page.update()

    def refresh():
        friend_list.controls.clear()

        pending = get_pending_requests(session.state['user_id'])
        for p in pending:
            def make_accept(uid, uname):
                def h(e):
                    accept(uid, session.state['user_id'])
                    refresh()
                return h
            friend_list.controls.append(
                ft.Container(
                    bgcolor=CARD_ALT,
                    border_radius=14,
                    border=border(1, FIRE),
                    padding=ft.Padding(left=14, top=10, right=14, bottom=10),
                    content=ft.Row([
                        ft.Text('📩', size=22),
                        ft.Container(width=8),
                        ft.Column([
                            ft.Text(p['nickname'], size=14, weight=ft.FontWeight.W_700, color=TEXT),
                            ft.Text('친구 요청을 보냈어요', size=11, color=SUB),
                        ], spacing=2, expand=True),
                        ft.ElevatedButton(
                            '수락',
                            bgcolor=ACCENT, color='#0E120C',
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=16)),
                            on_click=make_accept(p['id'], p['nickname']),
                        ),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                )
            )

        friends = get_friends_with_plant(session.state['user_id'])
        if not friends and not pending:
            friend_list.controls.append(
                ft.Container(
                    alignment=ft.Alignment(0, 0), padding=40,
                    content=ft.Text('아직 친구가 없어요', color=FAINT),
                )
            )
        for f in friends:
            stage       = f['stage'] or 'seed'
            stage_label = STAGE_LABELS.get(stage, '씨앗')
            image_path  = f['image_path'] or 'seed.png'
            pts         = f['total_points'] or 0

            def make_water(fid, fname):
                return lambda e: water_plant(fid, fname)

            def make_nav(fid):
                return lambda e: navigate('friend_garden', friend_id=fid) if navigate else None

            cooldown = water_cooldown_label(session.state['user_id'], f['id'])
            btn = ft.ElevatedButton(
                cooldown if cooldown else '물주기',
                icon=ft.Icons.ACCESS_TIME if cooldown else ft.Icons.WATER_DROP,
                bgcolor=FAINT if cooldown else WATER,
                color=SUB if cooldown else '#0E120C',
                disabled=bool(cooldown),
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                on_click=make_water(f['id'], f['nickname']),
            )
            water_buttons[f['id']] = btn

            friend_list.controls.append(
                ft.Container(
                    bgcolor=CARD,
                    border_radius=14,
                    border=border(1, BORDER),
                    padding=ft.Padding(left=14, top=12, right=14, bottom=12),
                    on_click=make_nav(f['id']),
                    content=ft.Row([
                        ft.Container(
                            width=44, height=44, border_radius=22,
                            bgcolor=CARD_ALT, alignment=ft.Alignment(0, 0),
                            content=ft.Image(src=image_path, width=36, height=36),
                        ),
                        ft.Container(width=10),
                        ft.Column([
                            ft.Text(f['nickname'], size=15, weight=ft.FontWeight.W_700, color=TEXT),
                            ft.Text(f"{stage_label} · {pts}p", size=12, color=SUB),
                        ], spacing=3, expand=True),
                        btn,
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                )
            )
        page.update()

    def open_add_dialog(e):
        search_field = ft.TextField(
            hint_text='닉네임 검색',
            color=TEXT, border_color=BORDER, focused_border_color=ACCENT,
            hint_style=ft.TextStyle(color=FAINT),
            autofocus=True,
        )
        result_list = ft.Column(spacing=8)

        def do_search(e):
            result_list.controls.clear()
            q = search_field.value.strip()
            if not q:
                page.update()
                return
            users = search_users(q, session.state['user_id'])
            if not users:
                result_list.controls.append(ft.Text('검색 결과 없음', color=FAINT, size=13))
            for u in users:
                def make_req(uid, uname):
                    def h(ev):
                        send_request(session.state['user_id'], uid)
                        page.snack_bar = ft.SnackBar(
                            ft.Text(f"{uname}에게 친구 요청을 보냈어요"), bgcolor=CARD,
                        )
                        page.snack_bar.open = True
                        dlg.open = False
                        page.update()
                        refresh()
                    return h
                result_list.controls.append(
                    ft.Container(
                        bgcolor=CARD_ALT,
                        border_radius=12,
                        border=border(1, BORDER),
                        padding=ft.Padding(left=14, top=10, right=14, bottom=10),
                        content=ft.Row([
                            ft.Text('🌱', size=20),
                            ft.Container(width=8),
                            ft.Text(u['nickname'], size=14, color=TEXT, expand=True),
                            ft.TextButton(
                                '요청',
                                style=ft.ButtonStyle(color=ACCENT),
                                on_click=make_req(u['id'], u['nickname']),
                            ),
                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    )
                )
            page.update()

        search_field.on_submit = do_search

        def close(ev):
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            bgcolor=CARD,
            shape=ft.RoundedRectangleBorder(radius=22),
            title=ft.Text('친구 추가', color=TEXT, weight=ft.FontWeight.W_700),
            content=ft.Container(
                width=300, height=280,
                content=ft.Column([
                    ft.Row([
                        ft.Container(content=search_field, expand=True),
                        ft.IconButton(
                            ft.Icons.SEARCH, icon_color=ACCENT,
                            on_click=do_search,
                        ),
                    ]),
                    result_list,
                ], spacing=10, scroll=ft.ScrollMode.AUTO),
            ),
            actions=[
                ft.TextButton('닫기', on_click=close, style=ft.ButtonStyle(color=SUB)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    refresh()

    friend_col.visible = False   # 기본 피드 탭

    return ft.Container(
        bgcolor=SCREEN,
        expand=True,
        content=ft.Column([
            ft.Container(
                padding=ft.Padding(left=22, top=4, right=22, bottom=4),
                content=ft.Row([
                    ft.Text('친구', size=22, weight=ft.FontWeight.W_800, color=TEXT),
                    ft.Row([
                        ft.IconButton(
                            ft.Icons.PERSON_ADD, icon_color=ACCENT,
                            on_click=open_add_dialog, tooltip='친구 추가',
                        ),
                        ft.IconButton(
                            ft.Icons.REFRESH, icon_color=SUB,
                            on_click=lambda e: refresh() if sel_tab[0] == 'list' else refresh_feed(),
                            tooltip='새로고침',
                        ),
                    ], spacing=0),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ),
            ft.Container(
                padding=ft.Padding(left=16, top=0, right=16, bottom=0),
                content=tab_row,
            ),
            ft.Container(
                expand=True,
                padding=ft.Padding(left=16, top=12, right=16, bottom=16),
                content=ft.Stack([feed_col, friend_col], expand=True),
            ),
        ], spacing=0, expand=True),
    )
