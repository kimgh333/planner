import streamlit as st
from datetime import datetime, timedelta
import json

st.set_page_config(page_title="문제집 공부 플래너", layout="centered")
st.title("📘 문제집 공부 플래너")

# --- 상태 초기화 ---
if 'page_distribution' not in st.session_state:
    st.session_state.page_distribution = {}
if 'days_selected' not in st.session_state:
    st.session_state.days_selected = ["Monday", "Wednesday", "Friday"]

# --- 입력 UI ---
book_title = st.text_input("문제집 이름", "수학의 정석")
total_pages = st.number_input("총 페이지 수", min_value=1, value=300)
start_date = st.date_input("시작일", datetime.today())

st.markdown("### 📅 요일별 계획 설정")
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
days_selected = st.multiselect("공부할 요일을 선택하세요", days, default=st.session_state.days_selected)
st.session_state.days_selected = days_selected

# 상태 동기화
for day in list(st.session_state.page_distribution.keys()):
    if day not in days_selected:
        del st.session_state.page_distribution[day]

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

if st.button("📅 계획 생성하기"):
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

    # iframe-safe FullCalendar HTML (작동률 향상)
    iframe_html = f'''
    <iframe srcdoc="""
    <!DOCTYPE html>
    <html>
    <head>
      <link href='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/main.min.css' rel='stylesheet'>
      <script src='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/main.min.js'></script>
      <style>
        body {{ margin: 0; padding: 0; }}
        #calendar {{ max-width: 900px; margin: 40px auto; }}
      </style>
    </head>
    <body>
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
    </body>
    </html>
    """ width="100%" height="600" style="border:none;"></iframe>
    '''

    st.components.v1.html(iframe_html, height=650, scrolling=False)
