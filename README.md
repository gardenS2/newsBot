# 🏠 Real Estate News Bot (부동산 뉴스 알림 봇)

> **GitHub Actions와 네이버 뉴스 API를 활용하여 매일 정해진 시간대에 최신 부동산 뉴스를 텔레그램으로 자동 전송해 주는 무인 수집 파이프라인입니다.**

<p align="left">
  <img src="https://img.shields.io/github/actions/workflow/status/gardenS2/newsBot/cron.yml?branch=main&style=flat-square&label=Actions%20Status" alt="GitHub Actions Status">
  <img src="https://img.shields.io/badge/Python-3.10-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/Telegram-Bot%20API-26A5E4?style=flat-square&logo=telegram&logoColor=white" alt="Telegram API">
</p>

---

## 📌 주요 기능
* **하루 3회 정기 스케줄링**: 매일 오전 7시, 오후 12시, 오후 6시 정각에 자동 구동 (GitHub Actions Cron 활용)
* **네이버 오픈 API 연동**: '부동산' 키워드를 기준으로 최신 뉴스 50개를 실시간 조회
* **안전한 중복 전송 방지**: 발송된 기사 링크를 `sent_urls.txt`에 누적 기록하여 동일 뉴스 중복 수신 차단
* **스토리지 최적화**: 누적 링크가 1,000개를 초과하면 오래된 기록을 자동으로 정제하여 최신 1,000개 데이터 유지
* **텔레그램 가독성 최적화**: 
  * 텔레그램 글자 수 제한(4,096자) 에러 방지를 위한 **메시지 자동 분할(Chunking) 기능** 탑재
  * 링크 하단에 크게 표시되는 웹페이지 미리보기 창을 제거하여 깔끔한 텍스트 뷰 제공
  * 날짜 표시 형식을 `[YY.MM.DD]`로 축소 및 제목 후미 배치

## 🛠️ 시스템 구조
```text
[GitHub Actions (Cron)] ──> [Python Script] ──> [네이버 뉴스 API]
                                    │
                                    ├───> [sent_urls.txt (기록 1,000개 최적화)]
                                    │
                                    └───> [텔레그램 API (분할 발송)] ──> 알림 수신

## ⚙️ Environment Variables (GitHub Secrets)
이 프로젝트를 구동하려면 아래의 환경 변수들이 GitHub Repository Secrets에 등록되어 있어야 합니다.

NAVER_CLIENT_ID: 네이버 오픈 API 애플리케이션 클라이언트 ID
NAVER_CLIENT_SECRET: 네이버 오픈 API 애플리케이션 클라이언트 Secret
TELEGRAM_BOT_TOKEN: 텔레그램 봇 API 토큰
TELEGRAM_CHAT_ID: 알림을 수신받을 텔레그램 채팅 ID