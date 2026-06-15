import flet as ft
from database import create_tables, insert_sample_data
from pages.calendar import build_calendar_page
from pages.garden import build_garden_page
from pages.friends import build_friends_page
from pages.profile import build_profile_page
from pages.friend_garden import build_friend_garden_page
from pages.stats import build_stats_page
from pages.shop import build_shop_page
from pages.login import build_login_page


def main(page: ft.Page):
    page.title = "싹 (SSAK)"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0E120C"
    page.padding = 0
    page.window.width = 393
    page.window.height = 852
    page.window.resizable = False

    content = ft.Container(expand=True)
    nav = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
                                        selected_icon=ft.Icons.CALENDAR_MONTH, label="캘린더"),
            ft.NavigationBarDestination(icon=ft.Icons.FOREST_OUTLINED,
                                        selected_icon=ft.Icons.FOREST, label="정원"),
            ft.NavigationBarDestination(icon=ft.Icons.PEOPLE_OUTLINE,
                                        selected_icon=ft.Icons.PEOPLE, label="친구"),
            ft.NavigationBarDestination(icon=ft.Icons.PERSON_OUTLINE,
                                        selected_icon=ft.Icons.PERSON, label="프로필"),
        ],
        bgcolor='#1A2014',
        indicator_color='rgba(132,204,78,0.18)',
        shadow_color='#0E120C',
        visible=False,
        on_change=lambda e: switch_tab(e.control.selected_index),
    )

    def navigate(route: str, **kwargs):
        page.overlay.clear()
        if route == 'friend_garden':
            content.content = build_friend_garden_page(
                page, friend_id=kwargs['friend_id'],
                go_back=lambda: switch_tab(nav.selected_index),
            )
        elif route == 'stats':
            content.content = build_stats_page(
                page, go_back=lambda: switch_tab(nav.selected_index),
            )
        elif route == 'shop':
            content.content = build_shop_page(
                page, go_back=lambda: switch_tab(nav.selected_index),
            )
        page.update()

    def switch_tab(index: int):
        page.overlay.clear()
        nav.visible = True
        if index == 0:
            content.content = build_calendar_page(page)
        elif index == 1:
            content.content = build_garden_page(page)
        elif index == 2:
            content.content = build_friends_page(page, navigate=navigate)
        elif index == 3:
            content.content = build_profile_page(page, navigate=navigate)
        page.update()

    def on_login():
        nav.selected_index = 0
        switch_tab(0)

    # 로그인 화면으로 시작
    content.content = build_login_page(page, on_login=on_login)
    page.add(content, nav)
    page.update()


create_tables()
insert_sample_data()
ft.run(main)
