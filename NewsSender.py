import feedparser
import requests
import os

# 1. 환경변수에서 텔레그램 정보 가져오기 (GitHub Secrets 연동용)
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# 2. 부동산 관련 RSS 피드 URL (네이버 뉴스 - 부동산 섹션 예시)
# 실제 활용 시 언론사나 국토부 등 다양한 RSS 주소로 확장 가능합니다.
RSS_URL = "https://news.naver.com/breakingnews/section/101/260" 

def fetch_and_filter_news():
    feed = feedparser.parse(RSS_URL)
    keywords = ["대출","신도시", "집값", "정책", "부동산", "분양","교산","하남","덕풍","풍산"]
    matched_articles = []

    for entry in feed.entries:
        title = entry.title
        link = entry.link
        
        # 제목에 키워드가 포함되어 있는지 검사
        if any(keyword in title for keyword in keywords):
            matched_articles.append(f"📌 {title}\n🔗 {link}")

    if matched_articles:
        message = "🏠 [오늘의 부동산 뉴스 알림]\n\n" + "\n\n".join(matched_articles)
        send_telegram_message(message)
    else:
        print("조건에 맞는 새로운 부동산 뉴스가 없습니다.")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    fetch_and_filter_news()