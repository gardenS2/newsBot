import requests
import os
import urllib.parse
from datetime import datetime

# 1. 환경 정보 가져오기
NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

SEARCH_KEYWORD = "부동산"
DB_FILE = "sent_urls.txt"  # 발송 완료된 링크를 저장할 파일명
MAX_MESSAGE_LENGTH = 3500  # 텔레그램 제한(4096자)보다 여유를 둔 안전선 설정

def load_sent_urls():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_sent_urls(new_urls):
    # 1. 기존에 저장되어 있던 모든 링크를 순서대로 읽어옵니다.
    existing_urls = []
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            existing_urls = [line.strip() for line in f if line.strip()]

    # 2. 이번에 새로 발송 성공한 링크들을 뒤에 추가합니다.
    total_urls = existing_urls + new_urls

    # 3. 전체 개수가 1000개를 넘어가면, 오래된 앞부분을 잘라내고 최신 1000개만 남깁니다.
    if len(total_urls) > 1000:
        print(f"데이터 최적화 진행: 총 {len(total_urls)}개 중 오래된 {len(total_urls) - 1000}개의 기록을 삭제합니다.")
        total_urls = total_urls[-1000:]

    # 4. 'w' 모드로 파일을 새로 열어 정제된 1000개 데이터만 덮어씁니다.
    with open(DB_FILE, "w", encoding="utf-8") as f:
        for url in total_urls:
            f.write(f"{url}\n")

def fetch_and_filter_news():
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        print("에러: 네이버 API 클라이언트 ID 또는 Secret이 설정되지 않았습니다.")
        return

    encText = urllib.parse.quote(SEARCH_KEYWORD)
    url = f"https://openapi.naver.com/v1/search/news.json?query={encText}&display=30&sort=date"
    
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        news_data = response.json()
    except Exception as e:
        print(f"네이버 API 호출 중 오류 발생: {e}")
        return

    items = news_data.get("items", [])
    print(f"가져온 검색 뉴스 개수: {len(items)}개")

    sent_urls = load_sent_urls()
    matched_articles = []
    new_sent_list = []

    now = datetime.now()
    today_str = now.strftime("%d %b %Y")

    for item in items:
        title = item["title"].replace("<b>", "").replace("</b>", "").replace("&quot;", "\"")
        link = item["originallink"] or item["link"]
        pub_date_str = item.get("pubDate", "")

        if today_str not in pub_date_str:
            continue

        if link in sent_urls:
            continue

        try:
            # 네이버 날짜 규격: "Sat, 18 Jul 2026 14:20:00 +0900"
            clean_date_str = pub_date_str.rsplit(" ", 1)[0]
            dt = datetime.strptime(clean_date_str, "%a, %d %b %Y %H:%M:%S")
            # 💡 [yy.mm.dd] 형식으로 포맷 축소 (예: 26.07.18)
            formatted_date = dt.strftime("%y.%m.%d")
        except Exception:
            # 예외 발생 시 현재 시간 기준 포맷팅
            formatted_date = now.strftime("%y.%m.%d")

        # 💡 요 청 사 항 : 제목 뒤에 [yy.mm.dd] 구조로 배치 변경
        matched_articles.append(f"📌 {title} [{formatted_date}]\n🔗 {link}")
        new_sent_list.append(link)

    if matched_articles:
        current_message = "<b>🏠 [오늘의 부동산 뉴스 알림]</b>\n\n"
        send_count = 0

        for article in matched_articles:
            if len(current_message) + len(article) + 2 > MAX_MESSAGE_LENGTH:
                send_telegram_message(current_message)
                send_count += 1
                current_message = "<b>🏠 [오늘의 부동산 뉴스 알림 - 계속]</b>\n\n"

            current_message += article + "\n\n"

        if current_message.strip() and current_message != "<b>🏠 [오늘의 부동산 뉴스 알림 - 계속]</b>\n\n":
            send_telegram_message(current_message)
            send_count += 1

        save_sent_urls(new_sent_list)
        print(f"새로운 {len(matched_articles)}개의 뉴스를 총 {send_count}개의 메시지로 분할 발송 완료했습니다.")
    else:
        print("오늘 작성된 새로운 부동산 뉴스가 없거나 이미 모두 발송되었습니다.")

def send_telegram_message(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("에러: 텔레그램 토큰 또는 채팅 ID가 환경변수에 설정되지 않았습니다.")
        return

    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True #링크밑 미리보기 강제 비활성화
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"텔레그램 전송 실패! 응답 코드: {response.status_code}, 메시지: {response.text}")

if __name__ == "__main__":
    fetch_and_filter_news()