import session
import flet as ft
from itertools import groupby
from operator import itemgetter
from repository.item import get_items, get_user_items, buy_item
from repository.plant import get_plant
from theme import SCREEN, CARD, CARD_ALT, BORDER, ACCENT, TEXT, SUB, FAINT, FIRE, border


CATEGORY_LABEL = {
    'skin': '식물 스킨',
    'deco': '정원 장식',
    'tool': '도구',
    'rare': '희귀 아이템',
}
CATEGORY_EMOJI = {
    'skin': '🌿', 'deco': '🏡', 'tool': '🛠️', 'rare': '✨',
}


def build_shop_page(page: ft.Page, go_back) -> ft.Control:
    points_lbl = ft.Text('', size=14, color=ACCENT, weight=ft.FontWeight.W_700)
    item_grid  = ft.Column(spacing=10)

    def refresh():
        plant     = get_plant(session.state['user_id'])
        my_points = plant['total_points'] if plant else 0
        owned     = get_user_items(session.state['user_id'])
        items     = get_items()
        points_lbl.value = f'⭐ {my_points}p 보유'

        item_grid.controls.clear()

        for cat, group in groupby(items, key=itemgetter('category')):
            group = list(group)
            item_grid.controls.append(
                ft.Container(
                    padding=ft.Padding(left=0, top=8, right=0, bottom=4),
                    content=ft.Text(
                        f"{CATEGORY_EMOJI.get(cat, '')} {CATEGORY_LABEL.get(cat, cat)}",
                        size=13, weight=ft.FontWeight.W_700, color=SUB,
                    ),
                )
            )
            for i in range(0, len(group), 2):
                row_items    = group[i:i+2]
                row_controls = []
                for it in row_items:
                    is_owned   = it['id'] in owned
                    can_afford = my_points >= it['price']

                    def make_buy(iid, iprice, iname):
                        def h(e):
                            ok = buy_item(session.state['user_id'], iid, iprice)
                            if ok:
                                page.snack_bar = ft.SnackBar(
                                    ft.Text(f"{iname} 구매 완료! 🎉"), bgcolor=CARD,
                                )
                            else:
                                page.snack_bar = ft.SnackBar(
                                    ft.Text("포인트가 부족해요"), bgcolor='#3A1A1A',
                                )
                            page.snack_bar.open = True
                            refresh()
                            page.update()
                        return h

                    if is_owned:
                        btn = ft.Container(
                            bgcolor=CARD_ALT,
                            border_radius=8,
                            padding=ft.Padding(left=12, top=6, right=12, bottom=6),
                            content=ft.Text('보유 중', size=11, color=FAINT),
                        )
                    elif can_afford:
                        btn = ft.ElevatedButton(
                            f'{it["price"]}p',
                            bgcolor=ACCENT, color='#0E120C',
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=make_buy(it['id'], it['price'], it['name']),
                        )
                    else:
                        btn = ft.Container(
                            bgcolor=CARD_ALT,
                            border_radius=8,
                            padding=ft.Padding(left=12, top=6, right=12, bottom=6),
                            content=ft.Text(f'{it["price"]}p', size=11, color=FAINT),
                        )

                    row_controls.append(
                        ft.Container(
                            expand=True,
                            bgcolor=CARD,
                            border_radius=14,
                            border=border(1, ACCENT if is_owned else BORDER),
                            padding=ft.Padding(left=14, top=14, right=14, bottom=14),
                            content=ft.Column([
                                ft.Text(it['emoji'], size=32,
                                        text_align=ft.TextAlign.CENTER),
                                ft.Text(it['name'], size=13,
                                        weight=ft.FontWeight.W_700, color=TEXT),
                                ft.Text(it['description'], size=10,
                                        color=SUB, max_lines=2),
                                ft.Container(height=6),
                                btn,
                            ], spacing=4,
                               horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        )
                    )

                if len(row_controls) == 1:
                    row_controls.append(ft.Container(expand=True))

                item_grid.controls.append(
                    ft.Row(row_controls, spacing=10)
                )

        page.update()

    refresh()

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
                    ft.Text('아이템 상점', size=20,
                            weight=ft.FontWeight.W_800, color=TEXT),
                    points_lbl,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ),
            ft.Container(
                expand=True,
                padding=ft.Padding(left=16, top=0, right=16, bottom=20),
                content=ft.Column(
                    [item_grid],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
            ),
        ], spacing=0, expand=True),
    )
