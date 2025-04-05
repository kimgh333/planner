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

# --- 문제집 추가 버튼 ---
if st.button("➕ 문제집 추가"):
    new_book = {
        'id': st.session_state.book_count,
        'title': f"문제집 {st.session_state.book_count+1}",
        'total_pages': 100,
        'start_date': datetime.today(),
        'days_selected': ["Monday", "Wednesday", "Friday"],
        'page_distribution': {"Monday": 10, "Wednesday": 10, "Friday": 10},
        'plan': []
    }
    st.session_state.books.append(new_book)
    st.session_state.book_count += 1

# --- 요일 매핑 ---
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
weekday_map = {day: i for i, day in enumerate(days)}
index_to_weekday = {i: day for day, i in weekday_map.items()}

# --- 각 문제집 UI 및 계획 생성 ---
all_events = []

for book in st.session_state.books:
    with st.expander(f"📘 {book['title']} 설정", expanded=True):
        book['title'] = st.text_input("문제집 이름", book['title'], key=f"title_{book['id']}")
        book['total_pages'] = st.number_input("총 페이지 수", min_value=1, value=book['total_pages'], key=f"pages_{book['id']}")
        book['start_date'] = st.date_input("시작일", value=book['start_date'], key=f"start_{book['id']}")

        book['days_selected'] = st.multiselect("공부할 요일", days, default=book['days_selected'], key=f"days_{book['id']}")

        # 동기화된 페이지 수 입력
        for day in list(book['page_distribution'].keys()):
            if day not in book['days_selected']:
                del book['page_distribution'][day]
        for day in book['days_selected']:
            if day not in book['page_distribution']:
                book['page_distribution'][day] = 10

        for day in book['days_selected']:
            book['page_distribution'][day] = st.number_input(
                f"{day}에 풀 페이지 수",
                min_value=1,
                max_value=100,
                value=book['page_distribution'][day],
                key=f"dist_{book['id']}_{day}"
            )

        # 계획 생성 버튼
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

# --- 모든 계획 모아서 달력으로 출력 ---
for book in st.session_state.books:
    all_events.extend(book['plan'])

if all_events:
    st.subheader("📅 통합 공부 캘린더")
    events_json = json.dumps(all_events)

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
            initialView: 'dayGridMonth',
            height: 'auto',
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
    st.components.v1.html(f'<iframe src="{src}" width="100%" height="700" style="border:none;"></iframe>', height=720)
