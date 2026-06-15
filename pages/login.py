import flet as ft
import session
from repository.user import verify_login, create_user_with_plant
from theme import SCREEN, CARD, CARD_ALT, BORDER, ACCENT, TEXT, SUB, FAINT, border


def _logo():
    return ft.Column(
        [
            ft.Text('🌱', size=64, text_align=ft.TextAlign.CENTER),
            ft.Text('싹', size=36, weight=ft.FontWeight.W_900,
                    color=ACCENT, text_align=ft.TextAlign.CENTER),
            ft.Text('나만의 습관 정원', size=14, color=SUB,
                    text_align=ft.TextAlign.CENTER),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=4,
    )


def _field(hint: str, password: bool = False) -> ft.TextField:
    return ft.TextField(
        hint_text=hint,
        password=password,
        can_reveal_password=password,
        color=TEXT,
        border_color=BORDER,
        focused_border_color=ACCENT,
        hint_style=ft.TextStyle(color=FAINT),
        border_radius=12,
        content_padding=ft.Padding(left=14, top=14, right=14, bottom=14),
    )


def _btn(label: str, on_click, primary: bool = True):
    if primary:
        return ft.ElevatedButton(
            label,
            bgcolor=ACCENT, color='#0E120C',
            width=999,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
            on_click=on_click,
        )
    return ft.TextButton(
        label,
        style=ft.ButtonStyle(color=SUB),
        on_click=on_click,
    )


def build_login_page(page: ft.Page, on_login) -> ft.Control:
    error_text = ft.Text('', color='#E8504A', size=12, text_align=ft.TextAlign.CENTER)
    view_ref = ft.Ref[ft.Column]()

    # ── 로그인 폼 ─────────────────────────────────────────────────────────────
    nick_login = _field('닉네임')
    pw_login   = _field('비밀번호', password=True)

    def do_login(e):
        error_text.value = ''
        nick = nick_login.value.strip()
        pw   = pw_login.value
        if not nick or not pw:
            error_text.value = '닉네임과 비밀번호를 입력해주세요'
            page.update()
            return
        user = verify_login(nick, pw)
        if user is None:
            error_text.value = '닉네임 또는 비밀번호가 올바르지 않습니다'
            page.update()
            return
        session.state['user_id'] = user['id']
        on_login()

    login_form = ft.Column(
        [
            ft.Text('로그인', size=22, weight=ft.FontWeight.W_700, color=TEXT),
            ft.Container(height=4),
            nick_login,
            ft.Container(height=8),
            pw_login,
            ft.Container(height=4),
            error_text,
            ft.Container(height=12),
            _btn('로그인', do_login),
            ft.Container(height=8),
            ft.Row(
                [
                    ft.Text('계정이 없으신가요?', size=13, color=FAINT),
                    _btn('회원가입', lambda e: _switch(False), primary=False),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        spacing=0,
    )

    # ── 회원가입 폼 ───────────────────────────────────────────────────────────
    nick_sign = _field('닉네임 (12자 이내)')
    pw_sign   = _field('비밀번호', password=True)
    pw_conf   = _field('비밀번호 확인', password=True)

    def do_signup(e):
        error_text.value = ''
        nick = nick_sign.value.strip()
        pw   = pw_sign.value
        conf = pw_conf.value
        if not nick:
            error_text.value = '닉네임을 입력해주세요'
            page.update()
            return
        if len(nick) > 12:
            error_text.value = '닉네임은 12자 이내로 입력해주세요'
            page.update()
            return
        if len(pw) < 4:
            error_text.value = '비밀번호는 4자 이상이어야 합니다'
            page.update()
            return
        if pw != conf:
            error_text.value = '비밀번호가 일치하지 않습니다'
            page.update()
            return
        try:
            new_id = create_user_with_plant(nick, pw)
        except Exception:
            error_text.value = '이미 사용 중인 닉네임입니다'
            page.update()
            return
        session.state['user_id'] = new_id
        on_login()

    signup_form = ft.Column(
        [
            ft.Text('회원가입', size=22, weight=ft.FontWeight.W_700, color=TEXT),
            ft.Container(height=4),
            nick_sign,
            ft.Container(height=8),
            pw_sign,
            ft.Container(height=8),
            pw_conf,
            ft.Container(height=4),
            error_text,
            ft.Container(height=12),
            _btn('시작하기', do_signup),
            ft.Container(height=8),
            ft.Row(
                [
                    ft.Text('이미 계정이 있으신가요?', size=13, color=FAINT),
                    _btn('로그인', lambda e: _switch(True), primary=False),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        spacing=0,
        visible=False,
    )

    # ── 화면 전환 ─────────────────────────────────────────────────────────────
    def _switch(to_login: bool):
        error_text.value = ''
        login_form.visible  = to_login
        signup_form.visible = not to_login
        page.update()

    return ft.Container(
        bgcolor=SCREEN,
        expand=True,
        content=ft.Column(
            [
                ft.Container(height=72),
                ft.Container(
                    alignment=ft.Alignment(0, 0),
                    content=_logo(),
                ),
                ft.Container(height=48),
                ft.Container(
                    padding=ft.Padding(left=28, top=0, right=28, bottom=0),
                    content=ft.Column([login_form, signup_form], spacing=0),
                ),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
    )
