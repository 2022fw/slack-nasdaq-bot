import os
import requests
import yfinance as yf
from datetime import datetime

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#나스닥")  # 채널을 #나스닥으로 설정

def get_stock_price(ticker="^IXIC"):  # 나스닥 지수의 티커는 ^IXIC
    stock = yf.Ticker(ticker)
    price = stock.history(period="1d")["Close"].iloc[-1]
    return f"나스닥 지수 현재 가격: {price:.2f} USD"

def send_slack_message(text):
    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}", "Content-Type": "application/json"}
    data = {"channel": SLACK_CHANNEL, "text": text}
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def is_market_open():
    now = datetime.now()
    if now.weekday() >= 5:  # 토요일(5)이나 일요일(6)은 시장이 열리지 않음
        return False
    # 미국 시장은 오전 9시 30분부터 오후 4시까지 운영됨
    if now.hour >= 9 and now.hour < 16:
        return True
    return False

if __name__ == "__main__":
    if is_market_open():
        message = get_stock_price("^IXIC")  # 나스닥 지수 가격 가져오기
        send_slack_message(message)
    else:
        send_slack_message("미국 시장은 현재 열려 있지 않습니다.")
