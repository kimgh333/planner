import streamlit as st
from datetime import datetime, timedelta
import json

st.set_page_config(page_title="문제집 공부 플래너", layout="centered")
st.title("📘 문제집 공부 플래너")

with st.form("study_form"):
    book_title = st.text_input("문제집 이름", "수학의 정석")
    total_pages = st.number_input("총 페이지 수", min_value=1, value=300)
    start_date = st.date_input("시작일", datetime.today())

    st.markdown("### 📅 요일별 계획 설정")
    days_selected = st.multiselect("공부할 요일을 선택하세요", 
                                   ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                   default=["Monday", "Wednesday", "Friday"])

    page_distribution = {}
    for day in days_selected:
        pages = st.number_input(f"{day}에 풀 페이지 수", min_value=1, max_value=100, value=10, key=day)
        page_distribution[day] = pages

    submitted = st.form_submit_button("📅 계획 생성하기")

if submitted:
    # 내부 요일 매핑
    weekday_map = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6
    }
    index_to_weekday = {v: k for k, v in weekday_map.items()}

    current_page = 1
    current_date = datetime.combine(start_date, datetime.min.time())
    plan = []

    while current_page <= total_pages:
        weekday = current_date.weekday()
        weekday_name = index_to_weekday[weekday]

        if weekday_name in page_distribution:
            pages_today = page_distribution[weekday_name]
            end_page = min(current_page + pages_today - 1, total_pages)
            plan.append({
                "title": f"{book_title} {current_page}~{end_page}p",
                "start": current_date.strftime("%Y-%m-%d")
            })
            current_page = end_page + 1

        current_date += timedelta(days=1)

    st.success(f"총 {len(plan)}일치 계획이 생성되었습니다!")

    # 캘린더 출력용 HTML 코드 생성 (FullCalendar 사용)
    st.markdown("### 🗓️ 공부 계획 캘린더")
    calendar_events = json.dumps(plan)
    
    fullcalendar_html = f'''
    <link href='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/main.min.css' rel='stylesheet' />
    <script src='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/main.min.js'></script>
    <div id='calendar'></div>
    <script>
      document.addEventListener('DOMContentLoaded', function() {{
        var calendarEl = document.getElementById('calendar');
        var calendar = new FullCalendar.Calendar(calendarEl, {{
          initialView: 'dayGridMonth',
          events: {calendar_events}
        }});
        calendar.render();
      }});
    </script>
    <style>
      #calendar {{ max-width: 800px; margin: 20px auto; }}
    </style>
    '''

    # Streamlit에서 HTML+JS 임베딩
    st.components.v1.html(fullcalendar_html, height=600, scrolling=True)
