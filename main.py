import flet as _flet
import random
import threading
import time
from abc import ABC, abstractmethod


class ft:
    """Compatibility wrapper around flet with concrete implementations for abstract-style hooks."""

    Page = _flet.Page
    ThemeMode = _flet.ThemeMode
    CrossAxisAlignment = _flet.CrossAxisAlignment
    MainAxisAlignment = _flet.MainAxisAlignment
    TextAlign = _flet.TextAlign
    FontWeight = _flet.FontWeight
    AlertDialog = _flet.AlertDialog
    IconButton = _flet.IconButton
    icons = _flet.icons
    Row = _flet.Row
    Column = _flet.Column
    GridView = _flet.GridView
    Container = _flet.Container
    Text = _flet.Text
    VerticalDivider = _flet.VerticalDivider
    Divider = _flet.Divider
    AppView = _flet.AppView
    border = _flet.border
    alignment = _flet.alignment
    app = staticmethod(_flet.app)

    class ElevatedButton(_flet.ElevatedButton, AbstractControl):
        """Concrete Flet button implementation that fulfills the abstract control API."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def render(self):
            return self

        def update(self):
            super().update()
            return self

    class AbstractControl(ABC):
        @abstractmethod
        def render(self):
            raise NotImplementedError("render() must be implemented by subclasses.")

        @abstractmethod
        def update(self):
            raise NotImplementedError("update() must be implemented by subclasses.")

    class Panel(AbstractControl):
        def __init__(self, *children, **kwargs):
            self.children = list(children)
            self.kwargs = kwargs

        def render(self):
            rendered = []
            for child in self.children:
                if hasattr(child, "render") and callable(child.render):
                    rendered.append(child.render())
                else:
                    rendered.append(child)
            return {"type": "panel", "children": rendered, **self.kwargs}

        def update(self):
            for child in self.children:
                if hasattr(child, "update") and callable(child.update):
                    child.update()
            return self

    class Label(Panel):
        def __init__(self, text="", **kwargs):
            super().__init__(**kwargs)
            self.text = str(text)

        def render(self):
            payload = {"type": "label", "text": self.text}
            payload.update(self.kwargs)
            return payload

    @staticmethod
    def build_panel(*children, **kwargs):
        return ft.Panel(*children, **kwargs)

TETRIS_SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[1, 1, 1], [0, 1, 0]],
]
TETRIS_COLORS = ["#00f0f0", "#f0f000", "#a000f0", "#f0a000", "#0000f0", "#00f000", "#f00000"]


def main(page: ft.Page):
    page.title = "Game Center Mobile"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    show_menu(page)


def show_menu(page: ft.Page):
    page.controls.clear()
    page.add(
        ft.Text("GAME CENTER", size=28, weight=ft.FontWeight.BOLD, color="#2c3e50"),
        ft.VerticalDivider(height=20),
        ft.ElevatedButton(
            "🔢 Chơi Sudoku Classic",
            on_click=lambda _: start_sudoku(page),
            width=250,
            height=50,
            bgcolor="#3498db",
            color="white",
        ),
        ft.VerticalDivider(height=10),
        ft.ElevatedButton(
            "🧱 Chơi Tetris Classic",
            on_click=lambda _: start_tetris(page),
            width=250,
            height=50,
            bgcolor="#2ecc71",
            color="white",
        ),
    )
    page.update()


### ==================== GAME 1: SUDOKU CLASSIC ====================

def start_sudoku(page: ft.Page):
    page.controls.clear()

    board = [[0] * 9 for _ in range(9)]
    original_board = [[0] * 9 for _ in range(9)]
    selected = None

    lbl_title = ft.Text("SUDOKU CLASSIC", size=20, weight=ft.FontWeight.BOLD, color="#2c3e50")

    grid = ft.GridView(runs_count=9, max_extent=38, spacing=2, run_spacing=2, width=360, height=360)
    cells = []

    def cell_click(r, c):
        nonlocal selected
        if original_board[r][c] != 0:
            return
        if selected is not None:
            sr, sc = selected
            cells[sr * 9 + sc].bgcolor = "white"
        selected = (r, c)
        cells[r * 9 + c].bgcolor = "#dff9fb"
        page.update()

    for r in range(9):
        for c in range(9):
            btn_cell = ft.Container(
                content=ft.Text("", size=16, weight=ft.FontWeight.BOLD, color="#2c3e50", text_align=ft.TextAlign.CENTER),
                bgcolor="white",
                border=ft.border.all(1, "#bdc3c7"),
                border_radius=4,
                on_click=lambda e, row=r, col=c: cell_click(row, col),
                alignment=ft.alignment.center,
            )
            cells.append(btn_cell)
            grid.controls.append(btn_cell)

    def set_number(num):
        nonlocal selected
        if selected is None:
            return
        r, c = selected
        board[r][c] = num
        cells[r * 9 + c].content.value = str(num) if num != 0 else ""
        cells[r * 9 + c].content.color = "#2980b9"
        page.update()

    num_row = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=5)
    for i in range(1, 10):
        num_row.controls.append(
            ft.ElevatedButton(
                str(i),
                on_click=lambda e, n=i: set_number(n),
                width=35,
                padding=0,
                bgcolor="#3498db",
                color="white",
            )
        )
    num_row.controls.append(
        ft.ElevatedButton("Xóa", on_click=lambda _: set_number(0), width=50, padding=0, bgcolor="#e67e22", color="white")
    )

    def generate_puzzle():
        nonlocal selected
        sample = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9],
        ]
        for r in range(9):
            for c in range(9):
                board[r][c] = sample[r][c]
                original_board[r][c] = sample[r][c]
                val = sample[r][c]
                cells[r * 9 + c].content.value = str(val) if val != 0 else ""
                cells[r * 9 + c].bgcolor = "#ecf0f1" if val != 0 else "white"
                cells[r * 9 + c].content.color = "#2c3e50"
        selected = None
        page.update()

    def is_valid(r, c, val):
        for i in range(9):
            if i != c and board[r][i] == val:
                return False
            if i != r and board[i][c] == val:
                return False
        sr, sc = 3 * (r // 3), 3 * (c // 3)
        for i in range(3):
            for j in range(3):
                if (sr + i != r or sc + j != c) and board[sr + i][sc + j] == val:
                    return False
        return True

    def check_solution():
        for r in range(9):
            for c in range(9):
                val = board[r][c]
                if val == 0 or not is_valid(r, c, val):
                    page.open(ft.AlertDialog(title=ft.Text("Có ô chưa đúng hoặc còn trống!")))
                    return
        page.open(ft.AlertDialog(title=ft.Text("Chúc mừng! Bạn đã hoàn thành!")))

    action_row = ft.Row(
        [
            ft.ElevatedButton("Kiểm tra", on_click=lambda _: check_solution(), bgcolor="#2ecc71", color="white"),
            ft.ElevatedButton("Game mới", on_click=lambda _: generate_puzzle(), bgcolor="#9b59b6", color="white"),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    page.add(
        ft.Row([ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: show_menu(page)), lbl_title], alignment=ft.MainAxisAlignment.START),
        grid,
        num_row,
        ft.Divider(),
        action_row,
    )
    generate_puzzle()


### ==================== GAME 2: TETRIS MOBILE ====================

def start_tetris(page: ft.Page):
    page.controls.clear()

    COLS, ROWS = 10, 20
    game_state = {
        "board": [["#2c3e50"] * COLS for _ in range(ROWS)],
        "score": 0,
        "level": 1,
        "game_over": False,
        "curr_piece": None,
        "curr_color": None,
        "r": 0,
        "c": 0,
    }

    lbl_score = ft.Text("SCORE: 0  |  LEVEL: 1", size=18, weight=ft.FontWeight.BOLD, color="#e67e22")

    tetris_grid = ft.GridView(runs_count=COLS, max_extent=25, spacing=1, run_spacing=1, width=270, height=520)
    blocks = []
    for _ in range(ROWS * COLS):
        b = ft.Container(bgcolor="#2c3e50", border=ft.border.all(0.5, "#34495e"), border_radius=2)
        blocks.append(b)
        tetris_grid.controls.append(b)

    def valid_move(piece, dr, dc):
        for pr in range(len(piece)):
            for pc in range(len(piece[pr])):
                if piece[pr][pc]:
                    nr, nc = dr + pr, dc + pc
                    if nc < 0 or nc >= COLS or nr >= ROWS:
                        return False
                    if nr >= 0 and game_state["board"][nr][nc] != "#2c3e50":
                        return False
        return True

    def draw_board():
        display = [row[:] for row in game_state["board"]]
        if game_state["curr_piece"] and not game_state["game_over"]:
            p = game_state["curr_piece"]
            for pr in range(len(p)):
                for pc in range(len(p[pr])):
                    if p[pr][pc]:
                        nr, nc = game_state["r"] + pr, game_state["c"] + pc
                        if 0 <= nr < ROWS and 0 <= nc < COLS:
                            display[nr][nc] = game_state["curr_color"]

        for r in range(ROWS):
            for c in range(COLS):
                blocks[r * COLS + c].bgcolor = display[r][c]
        lbl_score.value = f"SCORE: {game_state['score']}  |  LEVEL: {game_state['level']}"
        page.update()

    def new_piece():
        idx = random.randint(0, len(TETRIS_SHAPES) - 1)
        game_state["curr_piece"] = [row[:] for row in TETRIS_SHAPES[idx]]
        game_state["curr_color"] = TETRIS_COLORS[idx]
        game_state["r"] = 0
        game_state["c"] = COLS // 2 - len(game_state["curr_piece"][0]) // 2
        if not valid_move(game_state["curr_piece"], game_state["r"], game_state["c"]):
            game_state["game_over"] = True

    def merge_piece():
        p = game_state["curr_piece"]
        for pr in range(len(p)):
            for pc in range(len(p[pr])):
                if p[pr][pc]:
                    rr = game_state["r"] + pr
                    cc = game_state["c"] + pc
                    if 0 <= rr < ROWS and 0 <= cc < COLS:
                        game_state["board"][rr][cc] = game_state["curr_color"]

        n_rows = []
        for r in range(ROWS):
            if all(cell != "#2c3e50" for cell in game_state["board"][r]):
                n_rows.append(r)
        if n_rows:
            for r in sorted(n_rows, reverse=True):
                game_state["board"].pop(r)
                game_state["board"].insert(0, ["#2c3e50"] * COLS)
            game_state["score"] += len(n_rows) * 100
            game_state["level"] = (game_state["score"] // 500) + 1

    def move(dc, dr):
        if game_state["game_over"]:
            return
        if valid_move(game_state["curr_piece"], game_state["r"] + dr, game_state["c"] + dc):
            game_state["r"] += dr
            game_state["c"] += dc
            draw_board()
        elif dr == 1:
            merge_piece()
            new_piece()
            draw_board()

    def rotate():
        if game_state["game_over"]:
            return
        p = game_state["curr_piece"]
        rotated = [[p[y][x] for y in range(len(p) - 1, -1, -1)] for x in range(len(p[0]))]
        if valid_move(rotated, game_state["r"], game_state["c"]):
            game_state["curr_piece"] = rotated
            draw_board()

    def game_loop():
        new_piece()
        while not game_state["game_over"] and page.controls:
            time.sleep(max(0.1, 0.6 - (game_state["level"] * 0.05)))
            move(0, 1)
        if game_state["game_over"] and page.controls:
            page.open(ft.AlertDialog(title=ft.Text("GAME OVER!")))
            page.update()

    dpad = ft.Row(
        [
            ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: move(-1, 0), width=60, height=60, icon_size=35, bgcolor="#bdc3c7"),
            ft.Column(
                [
                    ft.IconButton(ft.icons.ROTATE_RIGHT, on_click=lambda _: rotate(), width=60, height=60, icon_size=35, bgcolor="#bdc3c7"),
                    ft.IconButton(ft.icons.ARROW_DOWNWARD, on_click=lambda _: move(0, 1), width=60, height=60, icon_size=35, bgcolor="#bdc3c7"),
                ],
                spacing=5,
            ),
            ft.IconButton(ft.icons.ARROW_FORWARD, on_click=lambda _: move(1, 0), width=60, height=60, icon_size=35, bgcolor="#bdc3c7"),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
    )

    def exit_tetris():
        game_state["game_over"] = True
        show_menu(page)

    page.add(
        ft.Row([ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: exit_tetris()), lbl_score], alignment=ft.MainAxisAlignment.START),
        tetris_grid,
        ft.Divider(),
        dpad,
    )
    draw_board()
    threading.Thread(target=game_loop, daemon=True).start()

ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550, host="0.0.0.0", web_renderer="html")
