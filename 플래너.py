import streamlit as st
from datetime import datetime, timedelta
import json

st.set_page_config(page_title="문제집 공부 플래너", layout="centered")
st.title("📘 문제집 공부 플래너")

if 'page_distribution' not in st.session_state:
    st.session_state.page_distribution = {}

with st.form("study_form"):
    book_title = st.text_input("문제집 이름", "수학의 정석")
    total_pages = st.number_input("총 페이지 수", min_value=1, value=300)
    start_date = st.date_input("시작일", datetime.today())

    st.markdown("### 📅 요일별 계획 설정")
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    days_selected = st.multiselect("공부할 요일을 선택하세요", days, default=list(st.session_state.page_distribution.keys()))

    # Remove unselected days from state
    for day in list(st.session_state.page_distribution.keys()):
        if day not in days_selected:
            del st.session_state.page_distribution[day]

    # Add newly selected days with default value
    for day in days_selected:
        if day not in st.session_state.page_distribution:
            st.session_state.page_distribution[day] = 10

    for day in days_selected:
        st.session_state.page_distribution[day] = st.number_input(
            f"{day}에 풀 페이지 수",
            min_value=1,
            max_value=100,
            value=st.session_state.page_distribution[day],
            key=f"input_{day}"
        )

    submitted = st.form_submit_button("📅 계획 생성하기")

if submitted:
    page_distribution = st.session_state.page_distribution

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

    st.markdown("### 🗓️ 공부 계획 캘린더")
    calendar_events = json.dumps(plan)

    fullcalendar_html = f'''
    <html>
    <head>
    <link href="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/main.min.css" rel="stylesheet" />
    <script src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/main.min.js"></script>
    </head>
    <body>
    <div id='calendar'></div>
    <script>
      document.addEventListener('DOMContentLoaded', function() {{
        var calendarEl = document.getElementById('calendar');
        var calendar = new FullCalendar.Calendar(calendarEl, {{
          initialView: 'dayGridMonth',
          height: 'auto',
          events: {calendar_events}
        }});
        calendar.render();
      }});
    </script>
    <style>
      #calendar {{ max-width: 900px; margin: 20px auto; }}
    </style>
    </body>
    </html>
    '''

    st.components.v1.html(fullcalendar_html, height=700, scrolling=True)
