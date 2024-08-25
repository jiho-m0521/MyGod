import datetime
import flet as ft
import json

def main(page: ft.Page):
    page.title = "학생 도우미"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window.width = 360
    page.window.height = 640
    page.window.resizable = False

    # 색상 테마 설정
    primary_color = ft.colors.BLUE
    secondary_color = ft.colors.ORANGE_700
    background_color = ft.colors.BLUE_GREY_900

    page.bgcolor = background_color

    def save_data(data, filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_username(username):
        user_data = load_data("user_data.json")
        user_data["username"] = username
        save_data(user_data, "user_data.json")

    def load_username():
        user_data = load_data("user_data.json")
        return user_data.get("username", "")

    def get_latest_exam_result():
        exam_data = load_data("exam_records.json")
        if exam_data:
            latest_exam = max(exam_data.items(), key=lambda x: datetime.datetime.strptime(x[0], "%Y.%m.%d"))
            date, exam_info = latest_exam
            return f"{date} {exam_info['type']}고사\n평균: {exam_info['average']:.2f}점"
        return "아직 기록이 없습니다."

    def validate_score(score):
        try:
            score = int(score)
            return 0 <= score <= 100
        except ValueError:
            return False

    def view_history(_=None):
        exam_data = load_data("exam_records.json")
        history_list = ft.ListView(expand=1, spacing=10, padding=20)
        
        if exam_data:
            for date, exam_info in sorted(exam_data.items(), reverse=True):
                history_list.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.ListTile(
                                    leading=ft.Icon(ft.icons.CALENDAR_TODAY, color=secondary_color),
                                    title=ft.Text(f"{date} {exam_info['type']}고사", weight=ft.FontWeight.BOLD),
                                    subtitle=ft.Text(f"평균: {exam_info['average']:.2f}점"),
                                ),
                                ft.Divider(),
                                ft.Column([
                                    ft.Text(f"{subject}: {score}점") 
                                    for subject, score in exam_info['scores'].items()
                                ], spacing=5)
                            ]),
                            padding=10
                        ),
                        elevation=3
                    )
                )
        else:
            history_list.controls.append(ft.Text("기록이 없습니다.", size=16))
        
        page.views.append(
            ft.View(
                "/history",
                controls=[
                    ft.AppBar(
                        leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/")),
                        title=ft.Text("나의 성적 기록"),
                        bgcolor=primary_color
                    ),
                    history_list,
                ]
            )
        )
        page.go("/history")

    def home(_=None):
        content = ft.ListView(
            expand=1,
            controls=[
                ft.Text("시험 종류 선택", size=18, weight=ft.FontWeight.BOLD),
                cg,
                ft.Divider(height=1, color="white54"),
                ft.Text("과목별 점수 입력", size=18, weight=ft.FontWeight.BOLD),
                math,
                korean,
                english,
                science,
                social,
                ft.ElevatedButton(
                    content=ft.Text("계산하기"),
                    on_click=calc,
                    style=ft.ButtonStyle(
                        color=ft.colors.WHITE,
                        bgcolor=secondary_color,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    )
                ),
            ],
            spacing=20,
            padding=20,
        )
        
        page.views.append(
            ft.View(
                "/home",
                controls=[
                    ft.AppBar(
                        leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/")),
                        title=ft.Text("새 시험 입력"),
                        bgcolor=primary_color
                    ),
                    content,
                ],
            )
        )
        page.go("/home")

    def calc(e):
        if not cg.value:
            show_snack_bar("시험 종류를 선택해주세요.")
            return

        scores = {
            "수학": math.value,
            "국어": korean.value,
            "영어": english.value,
            "과학": science.value,
            "사회": social.value
        }

        for subject, score in scores.items():
            if not validate_score(score):
                show_snack_bar(f"{subject} 점수를 0에서 100 사이의 정수로 입력해주세요.")
                return

        scores = {k: int(v) for k, v in scores.items()}
        avg = sum(scores.values()) / len(scores)

        def create_bar(label, score, color):
            return ft.Container(
                content=ft.Column([
                    ft.Text(f"{label}: {score}", color=ft.colors.WHITE),
                    ft.ProgressBar(value=score/100, bgcolor="#ffffff33", color=color)
                ]),
                margin=5
            )

        bars = [create_bar(subject, score, color) for (subject, score), color in 
                zip(scores.items(), [primary_color, secondary_color, ft.colors.GREEN, ft.colors.PINK, ft.colors.PURPLE])]

        def save(e):
            now = datetime.datetime.now()
            date = now.strftime("%Y.%m.%d")
            exam_data = load_data("exam_records.json")
            exam_data[date] = {
                "type": cg.value,
                "average": avg,
                "scores": scores
            }
            save_data(exam_data, "exam_records.json")
            page.go("/")

        page.views.append(
            ft.View(
                "/result",
                controls=[
                    ft.AppBar(
                        leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/home")),
                        title=ft.Text("시험 결과"),
                        bgcolor=primary_color
                    ),
                    ft.ListView(
                        expand=1,
                        controls=[
                            ft.Text(
                                f"{cg.value}고사 평균 점수",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                f"{avg:.2f}점",
                                size=36,
                                weight=ft.FontWeight.BOLD,
                                color=secondary_color
                            ),
                            ft.Container(height=20),
                            *bars,
                            ft.Container(height=20),
                            ft.Row([
                                ft.ElevatedButton(
                                    "저장",
                                    on_click=save,
                                    style=ft.ButtonStyle(
                                        color=ft.colors.WHITE,
                                        bgcolor=secondary_color,
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                    )
                                ),
                                ft.OutlinedButton(
                                    "다시 입력", 
                                    on_click=lambda _: page.go("/home"),
                                    style=ft.ButtonStyle(
                                        color=secondary_color,
                                        side=ft.BorderSide(width=2, color=secondary_color),
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                    )
                                ),
                            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                        ],
                        padding=20,
                    ),
                ],
            )
        )
        page.go("/result")

    def show_snack_bar(message):
        page.snack_bar = ft.SnackBar(content=ft.Text(message))
        page.snack_bar.open = True
        page.update()

    cg = ft.RadioGroup(
        content=ft.Row(
            [
                ft.Radio(value="중간", label="중간고사"),
                ft.Radio(value="기말", label="기말고사"),
            ]
        ),
    )

    math = ft.TextField(label="수학", suffix_text="/ 100", height=60, filled=True)
    korean = ft.TextField(label="국어", suffix_text="/ 100", height=60, filled=True)
    english = ft.TextField(label="영어", suffix_text="/ 100", height=60, filled=True)
    science = ft.TextField(label="과학", suffix_text="/ 100", height=60, filled=True)
    social = ft.TextField(label="사회", suffix_text="/ 100", height=60, filled=True)

    def route_change(route):
        #page.views.clear()
        if page.route == "/":
            username = load_username()
            if not username:
                username_dialog()
            else:
                page.go("/main")
        elif page.route == "/main":
            show_main_page(load_username())
        page.update()

    def username_dialog():
        def save_name(e):
            if not username_input.value:
                show_snack_bar("이름을 입력해주세요.")
                return
            save_username(username_input.value)
            dlg.open = False
            page.update()
            page.go("/main")  # 메인 페이지로 이동

        username_input = ft.TextField(
            label="이름을 입력해주세요",
            autofocus=True,
            on_submit=save_name,
            border_color=secondary_color,
            focused_border_color=primary_color,
        )

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("환영합니다!", size=24, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text("학생 도우미 앱에 오신 것을 환영합니다!", size=16),
                ft.Text("이름을 입력하고 시작해보세요.", size=14, color="grey"),
                username_input
            ], tight=True, spacing=20),
            actions=[
                ft.ElevatedButton(
                    text="시작하기",
                    on_click=save_name,
                    style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=secondary_color)
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def show_calendar(_):
        def handle_change(e):
            selected_date.value = e.control.value.strftime('%Y-%m-%d')
            page.update()

        def handle_dismissal(e):
            pass

        selected_date = ft.Text()

        page.views.append(
            ft.View(
                "/calendar",
                controls=[
                    ft.AppBar(
                        leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/")),
                        title=ft.Text("학사 일정"),
                        bgcolor=primary_color
                    ),
                    ft.Column([
                        ft.ElevatedButton(
                            "날짜 선택",
                            icon=ft.icons.CALENDAR_MONTH,
                            on_click=lambda _: page.open(
                                ft.DatePicker(
                                    first_date=datetime.datetime(year=2023, month=1, day=1),
                                    last_date=datetime.datetime(year=2024, month=12, day=31),
                                    on_change=handle_change,
                                    on_dismiss=handle_dismissal,
                                )
                            )
                        ),
                        selected_date,
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
                ]
            )
        )
        page.go("/calendar")

    def show_timetable(_):
        timetable_data = [
            ["국어", "수학", "영어", "과학", "체육"],
            ["사회", "영어", "수학", "음악", "국어"],
            ["과학", "국어", "체육", "영어", "수학"],
            ["음악", "사회", "국어", "수학", "영어"],
            ["체육", "과학", "사회", "국어", "수학"],
        ]

        columns = [
            ft.DataColumn(ft.Text("교시", size=12)),
            ft.DataColumn(ft.Text("월", size=12)),
            ft.DataColumn(ft.Text("화", size=12)),
            ft.DataColumn(ft.Text("수", size=12)),
            ft.DataColumn(ft.Text("목", size=12)),
            ft.DataColumn(ft.Text("금", size=12)),
        ]

        rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(f"{i+1}", size=12)),
                    *[ft.DataCell(ft.Text(subject, size=12)) for subject in row]
                ]
            ) for i, row in enumerate(timetable_data)
        ]

        timetable = ft.DataTable(
            columns=columns,
            rows=rows,
            column_spacing=10,
            horizontal_lines=ft.border.BorderSide(1, ft.colors.GREY_400),
            vertical_lines=ft.border.BorderSide(1, ft.colors.GREY_400),
        )

        page.views.append(
            ft.View(
                "/timetable",
                controls=[
                    ft.AppBar(
                        leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/")),
                        title=ft.Text("학급 시간표"),
                        bgcolor=primary_color
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("학급 시간표", size=20, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=timetable,
                                border=ft.border.all(1, ft.colors.GREY_400),
                                border_radius=5,
                                padding=10,
                            ),
                        ]),
                        padding=20,
                        alignment=ft.alignment.top_center,
                    ),
                ],
                scroll=ft.ScrollMode.AUTO
            )
        )
        page.go("/timetable")

    def show_main_page(username):
        latest_result = get_latest_exam_result()
        page.views.append(
            ft.View(
                "/main",
                controls=[
                    ft.AppBar(title=ft.Text("학생 도우미"), bgcolor=primary_color),
                    ft.ListView(
                        expand=1,
                        controls=[
                            ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Text(f"안녕하세요,", size=20),
                                        ft.Text(f"{username}님!", size=28, weight=ft.FontWeight.BOLD),
                                        ft.Container(height=10),
                                        ft.Text("최근 시험 결과", size=16, weight=ft.FontWeight.BOLD),
                                        ft.Text(latest_result, size=14)
                                    ]),
                                    padding=20
                                ),
                                elevation=5,
                                margin=10
                            ),
                            ft.Container(height=20),
                            ft.ElevatedButton(
                                content=ft.Row([
                                    ft.Icon(ft.icons.ADD),
                                    ft.Text("새 시험 입력", size=16)
                                ]),
                                on_click=home,
                                style=ft.ButtonStyle(
                                    color=ft.colors.WHITE,
                                    bgcolor=secondary_color,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                                width=250,
                                height=50
                            ),
                            ft.OutlinedButton(
                                content=ft.Row([
                                    ft.Icon(ft.icons.HISTORY),
                                    ft.Text("나의 성적 기록", size=16)
                                ]),
                                on_click=view_history,
                                style=ft.ButtonStyle(
                                    color=secondary_color,
                                    side=ft.BorderSide(width=2, color=secondary_color),
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                                width=250,
                                height=50
                            ),
                            ft.ElevatedButton(
                                content=ft.Row([
                                    ft.Icon(ft.icons.CALENDAR_TODAY),
                                    ft.Text("학사 일정", size=16)
                                ]),
                                on_click=show_calendar,
                                style=ft.ButtonStyle(
                                    color=ft.colors.WHITE,
                                    bgcolor=primary_color,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                                width=250,
                                height=50
                            ),
                            ft.ElevatedButton(
                                content=ft.Row([
                                    ft.Icon(ft.icons.SCHEDULE),
                                    ft.Text("학급 시간표", size=16)
                                ]),
                                on_click=show_timetable,
                                style=ft.ButtonStyle(
                                    color=ft.colors.WHITE,
                                    bgcolor=primary_color,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                                width=250,
                                height=50
                            ),
                        ],
                        spacing=20,
                        padding=20,
                    )
                ],
            )
        )

    page.on_route_change = route_change
    page.go("/")

ft.app(target=main)