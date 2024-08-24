import flet as ft
import os as os
import datetime as datetime

def main(page: ft.Page):
    page.window_width = 350
    page.window_height = 700
    page.window_resizable = False


    # 라디오 그룹 변경 시 실행되는 함수
    def radiogroup_changed(e):
        t.value = f"선택된 시험: {e.control.value}고사"
        global avgval
        avgval = e.control.value
        page.update()

    def view_history(e):
        raise NotImplementedError
        page.views.append(
        ft.View("/history",
                controls=[
                        ft.Text("기록", size=30, weight=ft.FontWeight.BOLD),
                        
                        # 여기에다 자신의 기록을 저장한 record.txt 파일 내용을 표시하는 코드 작성하기
                        
                        ft.ElevatedButton("뒤로가기", on_click=lambda e: page.open(dlg_modal))
                    ]
                    
                )
        
        )
        page.update()

    def home(e):
        page.views.append(
                ft.View(
                    "/home",
                    controls=[
                        ft.Text("\n어떤 시험인지 선택해 주세요", size=20, weight=ft.FontWeight.BOLD), 
                        cg, t, 
                        ft.Divider(height=1, color="white"),
                        ft.Text("과목별 점수를 입력해주세요", size=20, weight=ft.FontWeight.BOLD),
                        math, science, korean, english, social,
                        ft.CupertinoFilledButton(
                            content=ft.Text("계산하기!"),
                            opacity_on_click=0.3,
                            on_click=calc,
                        )
                    ]
                )
            )
        page.update()
    
    # 점수 계산 후 결과 화면으로 이동하는 함수
    def calc(e):
        try:
            math_value = int(math.value)
            korean_value = int(korean.value)
            english_value = int(english.value)
            science_value = int(science.value)
            social_value = int(social.value)

            # 평균 계산
            avg = (math_value + korean_value + english_value + science_value + social_value) / 5

            # 막대그래프 컨테이너 생성
            def create_bar(label, score, color):
                return ft.Row([
                    ft.Container(
                        width=score * 2,  # 점수에 따라 길이 변경 (최대 100점 * 2 = 200px)
                        height=20,
                        bgcolor=color,
                        border_radius=5,
                        alignment=ft.alignment.center,
                        content=ft.Text(f"{score}", color="white"),
                    ),
                    ft.Text(label, width=50),
                ], alignment=ft.MainAxisAlignment.START)

            # 과목별 막대그래프 생성
            bars = [
                create_bar("수학", math_value, "blue"),
                create_bar("국어", korean_value, "green"),
                create_bar("영어", english_value, "red"),
                create_bar("과학", science_value, "purple"),
                create_bar("사회", social_value, "orange"),
            ]

            def handle_close(e):
                page.close(dlg_modal)
                page.go("/")


            now = datetime.datetime.now()
            def save(e):
                with open("record.txt", "a", encoding="utf8") as file:
                    file.write("\n" + now.strftime("%Y.%m.%d") + " {} \n # 평균 점수: {}\n영어: {}\n사회: {}\n수학: {}\n국어: {}\n과학: {}\n".format(t.value, avg, english_value, social_value, math_value, korean_value, science_value))
                    page.close(dlg_modal)
                    page.go("/")

            global dlg_modal
            dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("저장할까요?"),
        content=ft.Text("시험 기록을 저장할까요?"),
        actions=[
            ft.TextButton("네", on_click=save),
            ft.TextButton("아니오", on_click=handle_close),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

            # 결과 화면으로 이동
            page.views.append(
                ft.View(
                    "/result",
                    controls=[
                        ft.Text("\n\n당신의 {}고사 평균 점수는 {}점입니다.".format(avgval, int(avg)), size=15, weight=ft.FontWeight.BOLD),
                        
                        
                        ft.Column(bars, spacing=10),  # 막대그래프를 세로로 나열
                        ft.ElevatedButton("뒤로가기", on_click=lambda e: page.open(dlg_modal))
                    ]
                )
            )
            
            page.go("/result")

        except ValueError:
            dlg.content = ft.Text("올바른 점수를 입력해주세요.")
            page.dialog = dlg
            dlg.open = True
            page.update()

    # 라디오 그룹
    t = ft.Text(weight=ft.FontWeight.BOLD)
    cg = ft.RadioGroup(content=ft.Column([
        ft.Radio(value="중간", label="중간"),
        ft.Radio(value="기말", label="기말"),
    ]), on_change=radiogroup_changed)

    # 과목별 점수 입력 필드
    math = ft.TextField(label="수학 점수")
    korean = ft.TextField(label="국어 점수")
    english = ft.TextField(label="영어 점수")
    science = ft.TextField(label="과학 점수")
    social = ft.TextField(label="사회 점수")

    # 다이얼로그 정의
    dlg = ft.AlertDialog(title=ft.Text("오류"))

    # 라우트 변경 시 호출되는 함수
    def route_change(route):


        if page.route == "/":
            page.views.append(
                ft.View(
                    "/",
                    controls=[
                        ft.Text("\n", size=5, weight=ft.FontWeight.BOLD), 
                        ft.Image(
                            src=f"ExamApp.jpg",
                            width=700,
                            height=200,
                            fit=ft.ImageFit.CONTAIN,
                        ),
                        
                        
                        ft.CupertinoFilledButton(
                            content=ft.Text("계산하러 가기"),
                            opacity_on_click=0.3,
                            on_click=home,
                            width=500
                        ),
                        
                        ft.CupertinoFilledButton(
                            content=ft.Text("나의 기록"),
                            opacity_on_click=0.3,
                            on_click=view_history,
                            width=500
                            
                        ),
                        
    
                    ]
                )
            )

        page.update()

    # 페이지 라우팅 설정
    page.on_route_change = route_change

    # 시작 페이지 설정
    page.go("/")
ft.app(target=main)