import os
import requests
import yfinance as yf

# 슬랙 봇 토큰과 채널 이름을 환경 변수에서 가져옴
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#나스닥")

# NASDAQ 지수 가격을 가져오는 함수
def get_nasdaq_price(ticker="^IXIC"):
    stock = yf.Ticker(ticker)
    price = stock.history(period="1d")["Close"].iloc[-1]
    return f"NASDAQ 지수 현재 가격: ${price:.2f}"

# 슬랙에 메시지를 보내는 함수
def send_slack_message(text):
    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}", "Content-Type": "application/json"}
    data = {"channel": SLACK_CHANNEL, "text": text}
    response = requests.post(url, headers=headers, json=data)
    return response.json()

if __name__ == "__main__":
    # NASDAQ 지수의 현재 가격을 가져오고, 슬랙에 메시지를 보냄
    message = get_nasdaq_price("^IXIC")
    send_slack_message(message)
