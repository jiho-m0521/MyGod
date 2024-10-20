import datetime
import flet as ft
import json
import requests

API_KEY = "6d66c4f0983447aa8bf0df3f7ef043e5"
BASE_URL = "https://open.neis.go.kr/hub/SchoolSchedule"  # Replace with actual OpenAPI URL

def get_academic_schedule():
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    url = f"{BASE_URL}/schedule"  # Replace with actual endpoint
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Assuming it returns JSON data
    else:
        return None

def get_timetable():
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    url = f"{BASE_URL}/timetable"  # Replace with actual endpoint
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Assuming it returns JSON data
    else:
        return None

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
    
    def save_school(school):
        school_data = load_data("user_data.json")
        school_data["school"] = school
        save_data(school_data, "user_data.json")
    
    def load_username():
        user_data = load_data("user_data.json")
        return user_data.get("username", "")
    
    def load_school():
        school_data = load_data("user_data.json")
        return school_data.get("school", "")

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
        if page.route == "/":
            username = load_username()
            global school
            school = load_school()
            if not username:
                username_dialog()  # 사용자 이름 입력 대화상자 열기
            else:
                page.go("/main")  # 사용자 이름이 있으면 메인 페이지로 이동
        elif page.route == "/main":
            show_main_page(load_username())
        elif page.route == "/todo":
            try:
                show_todo()  # Show the todo app when the route is /todo
            except Exception as e:
                pass
        page.update()
        
    dd = ft.Dropdown(
        label="학교 종류",
        hint_text="중/고등",
        width=100,
        options=[
            ft.dropdown.Option("중학교"),
            ft.dropdown.Option("고등학교"),          
        ],
        autofocus=True,
    )
    
    def username_dialog():
        username_field = ft.TextField(label="이름을 입력하세요")
        school_field = ft.TextField(label="학교 이름을 입력하세요")
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("환영합니다!", size=24, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text("학생 도우미 앱에 오신 것을 환영합니다!", size=16),
                ft.Text("이름과 현재 재학 중인 학교를 입력하고 시작해보세요.", size=14, color="grey"),
                username_field,
                school_field,
                dd,
                ft.Text("학교 란에는 학교 이름만 입력해주세요!\n ex. 중학교 이름이 서초중학교라면: '서초'만 입력해주세요", size=14, color="blue", weight=ft.FontWeight.BOLD),
                
            ], tight=True, spacing=20),
            
            actions=[
                ft.TextButton(
                    "확인",
                    on_click=lambda e: (
                        save_username(username_field.value),
                        save_school(school_field.value + dd.value),
                        page.go("/main"),
                        
                    )
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def show_calendar(_):
        schedule_data = get_academic_schedule()

        if schedule_data:
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
                            ft.Text("학사 일정", size=20, weight=ft.FontWeight.BOLD),
                            ft.ListView(
                                controls=[
                                    ft.Text(f"날짜: {event['date']}, 일정: {event['event']}", size=16)
                                    for event in schedule_data
                                ]
                            ),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
                    ]
                )
            )
            page.go("/calendar")
        else:
            show_snack_bar("학사 일정을 불러올 수 없습니다.")

    # Define the TodoApp class as specified in your todo.txt
    class TodoApp(ft.Column):
        def __init__(self):
            super().__init__()
            

            self.new_task = ft.TextField(
                hint_text="할 일을 입력하세요", on_submit=self.add_clicked, expand=True
            )
            self.tasks = ft.Column()
            self.filter = ft.Tabs(
                scrollable=False,
                selected_index=0,
                on_change=self.tabs_changed,
                tabs=[ft.Tab(text="모두"), ft.Tab(text="완료"), ft.Tab(text="미완료")]
            )
            self.items_left = ft.Text("0 개의 항목 남음")
            self.width = 600
            self.controls = [
                ft.Row(
                    [ft.Text("할 일 목록", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    controls=[
                        self.new_task,
                        ft.FloatingActionButton(icon=ft.icons.ADD, on_click=self.add_clicked)
                    ],
                ),
                ft.Column(
                    spacing=25,
                    controls=[
                        self.filter,
                        self.tasks,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                self.items_left,
                                ft.OutlinedButton(
                                    text="완료된 항목 지우기", on_click=self.clear_clicked
                                ),
                                
                                ft.OutlinedButton(
                                    text="모두 지우기", on_click=self.clear_all
                                ),
                            ],
                        ),
                    ],
                ),
            ]

        def add_clicked(self, e):
            if self.new_task.value:
                task = Task(self.new_task.value, self.task_status_change, self.task_delete)
                self.tasks.controls.append(task)
                user_data = load_data("user_data.json")
                user_data["todo"] = self.new_task.value
                save_data(user_data, "user_data.json")
                self.new_task.value = ""
                self.new_task.focus()
                self.update()

        def task_status_change(self, task):
            self.update()

        def task_delete(self, task):
            self.tasks.controls.remove(task)
            self.update()

        def tabs_changed(self, e):
            self.update()

        def clear_clicked(self, e):
            for task in self.tasks.controls[:]:
                if task.completed:
                    self.task_delete(task)

        def clear_all(self, e):
            for task in self.tasks.controls[:]:
                self.task_delete(task)

        def before_update(self):
            status = self.filter.tabs[self.filter.selected_index].text
            count = 0
            for task in self.tasks.controls:
                task.visible = (
                    status == "모두"
                    or (status == "미완료" and not task.completed)
                    or (status == "완료" and task.completed)
                )
                if not task.completed:
                    count += 1
            self.items_left.value = f"{count} 개의 항목 남음"

    class Task(ft.Row):
        def __init__(self, task_name, task_status_change, task_delete):
            super().__init__()
            self.completed = False
            self.task_name = task_name
            self.task_status_change = task_status_change
            self.task_delete = task_delete

            self.display_task = ft.Checkbox(
                value=False, label=self.task_name, on_change=self.status_changed
            )
            self.edit_name = ft.TextField(expand=1)

            self.display_view = ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.display_task,
                    ft.Row(
                        spacing=0,
                        controls=[
                            ft.IconButton(
                                icon=ft.icons.CREATE_OUTLINED,
                                tooltip="할 일 수정",
                                on_click=self.edit_clicked,
                            ),
                            ft.IconButton(
                                ft.icons.DELETE_OUTLINE,
                                tooltip="할 일 삭제",
                                on_click=self.delete_clicked,
                            ),
                        ],
                    ),
                ],
            )

            self.edit_view = ft.Row(
                visible=False,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.edit_name,
                    ft.IconButton(
                        icon=ft.icons.DONE_OUTLINE_OUTLINED,
                        icon_color=ft.colors.GREEN,
                        tooltip="할 일 수정 완료",
                        on_click=self.save_clicked,
                    ),
                ],
            )

            self.controls = [self.display_view, self.edit_view]

        def edit_clicked(self, e):
            self.edit_name.value = self.display_task.label
            self.display_view.visible = False
            self.edit_view.visible = True
            self.update()

        def save_clicked(self, e):
            self.display_task.label = self.edit_name.value
            self.display_view.visible = True
            self.edit_view.visible = False
            self.update()

        def status_changed(self, e):
            self.completed = self.display_task.value
            self.task_status_change(self)

        def delete_clicked(self, e):
            self.task_delete(self)


    def show_todo(_):
        try:
            todo_app = TodoApp()  # Create an instance of the TodoApp
            page.views.append(
                ft.View(
                    "/todo",
                    controls=[
                        ft.AppBar(
                            leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/")),
                            title=ft.Text("할 일 목록"),
                            bgcolor=primary_color
                        ),
                        todo_app,
                    ],
                )
            )
            page.go("/todo")
        except Exception as e:
            pass



    def show_timetable(_):
        timetable_data = get_timetable()

        if timetable_data:
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
                        *[ft.DataCell(ft.Text(subject, size=12)) for subject in day['subjects']]
                    ]
                ) for i, day in enumerate(timetable_data)
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
        else:
            show_snack_bar("시간표를 불러올 수 없습니다.")


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
                                        ft.Text(f"재학 중인 학교: {school}", size=18),
                                        ft.Divider(height=10),
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
                            ft.ElevatedButton(
                                content=ft.Row([
                                    ft.Icon(ft.icons.CHECK_CIRCLE),
                                    ft.Text("할 일 트래커", size=16)
                                ]),
                                on_click=show_todo,
                                style=ft.ButtonStyle(
                                    color=ft.colors.GREEN,
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
