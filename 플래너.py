import streamlit as st
from datetime import datetime, timedelta
import json
import base64

st.set_page_config(page_title="📘 문제집 공부 플래너", layout="wide")
st.title("📘 문제집 공부 플래너")

# --- 상태 관리 ---
if 'books' not in st.session_state:
    st.session_state.books = []
if 'book_count' not in st.session_state:
    st.session_state.book_count = 0

# --- 요일 매핑 ---
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
weekday_map = {day: i for i, day in enumerate(days)}
index_to_weekday = {i: day for day, i in enumerate(weekday_map)}

# --- 문제집 추가 모달 ---
with st.expander("➕ 문제집 추가 (펼쳐서 입력)", expanded=False):
    if 'new_title' not in st.session_state:
        st.session_state['new_title'] = ""
    if 'new_pages' not in st.session_state:
        st.session_state['new_pages'] = 100
    if 'new_start' not in st.session_state:
        st.session_state['new_start'] = datetime.today()
    if 'new_days' not in st.session_state:
        st.session_state['new_days'] = ["Monday", "Wednesday", "Friday"]
    for day in days:
        if f"new_dist_{day}" not in st.session_state:
            st.session_state[f"new_dist_{day}"] = 10

    st.session_state.new_title = st.text_input("문제집 이름", st.session_state.new_title, key="new_title")
    st.session_state.new_pages = st.number_input("총 페이지 수", min_value=1, value=st.session_state.new_pages, key="new_pages")
    st.session_state.new_start = st.date_input("시작일", value=st.session_state.new_start, key="new_start")
    st.session_state.new_days = st.multiselect("공부할 요일", days, default=st.session_state.new_days, key="new_days")

    page_distribution = {}
    for day in st.session_state.new_days:
        st.session_state[f"new_dist_{day}"] = st.number_input(
            f"{day}에 풀 페이지 수", min_value=1, max_value=100, value=st.session_state[f"new_dist_{day}"],
            key=f"new_dist_{day}"
        )
        page_distribution[day] = st.session_state[f"new_dist_{day}"]

    if st.button("📥 문제집 추가", key="add_book"):
        st.session_state.books.append({
            'id': st.session_state.book_count,
            'title': st.session_state.new_title,
            'total_pages': st.session_state.new_pages,
            'start_date': st.session_state.new_start,
            'days_selected': st.session_state.new_days,
            'page_distribution': page_distribution,
            'plan': []
        })
        st.session_state.book_count += 1
        # 상태 초기화
        del st.session_state['new_title']
        del st.session_state['new_pages']
        del st.session_state['new_start']
        del st.session_state['new_days']
        for day in days:
            key = f"new_dist_{day}"
            if key in st.session_state:
                del st.session_state[key]

# --- 문제집 리스트와 계획 생성 ---
st.subheader("📚 등록된 문제집")
all_events = []

for book in st.session_state.books:
    with st.expander(f"📘 {book['title']}", expanded=False):
        if st.button(f"📅 {book['title']} 계획 생성", key=f"plan_{book['id']}"):
            current_page = 1
            current_date = datetime.combine(book['start_date'], datetime.min.time())
            plan = []
            while current_page <= book['total_pages']:
                weekday = current_date.weekday()
                weekday_name = index_to_weekday[weekday]
                if weekday_name in book['page_distribution']:
                    pages_today = book['page_distribution'][weekday_name]
                    end_page = min(current_page + pages_today - 1, book['total_pages'])
                    plan.append({
                        "title": f"{book['title']} {current_page}~{end_page}p",
                        "start": current_date.strftime("%Y-%m-%d")
                    })
                    current_page = end_page + 1
                current_date += timedelta(days=1)
            book['plan'] = plan

    all_events.extend(book['plan'])

# --- 오늘 할 일 보여주기 ---
st.subheader("📌 오늘 할 공부")
today = datetime.today().strftime("%Y-%m-%d")
today_tasks = [event for event in all_events if event['start'] == today]

if today_tasks:
    for task in today_tasks:
        st.success(f"✅ {task['title']}")
else:
    st.info("오늘은 할 공부가 없습니다. 😊")

# --- 달력 표시 ---
if all_events:
    st.subheader("📅 통합 공부 캘린더")
    events_json = json.dumps(all_events)
    default_april = datetime(datetime.today().year, 4, 1).strftime("%Y-%m-%d")

    calendar_html = f'''
    <!DOCTYPE html>
    <html>
    <head>
      <link href='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/main.min.css' rel='stylesheet'>
      <script src='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/main.min.js'></script>
      <style>
        html, body {{ margin: 0; padding: 0; }}
        #calendar {{ max-width: 95%; margin: 40px auto; }}
      </style>
    </head>
    <body>
      <div id='calendar'></div>
      <script>
        document.addEventListener('DOMContentLoaded', function() {{
          var calendar = new FullCalendar.Calendar(document.getElementById('calendar'), {{
            initialView: 'dayGridWeek',
            height: 'auto',
            initialDate: '{default_april}',
            events: {events_json}
          }});
          calendar.render();
        }});
      </script>
    </body>
    </html>
    '''

    encoded_html = base64.b64encode(calendar_html.encode()).decode()
    src = f"data:text/html;base64,{encoded_html}"
    st.components.v1.html(f'<iframe src="{src}" width="100%" height="720" style="border:none;"></iframe>', height=740)
else:
    st.info("왼쪽 상단의 '문제집 추가' 버튼을 눌러 계획을 세워보세요!")

