import os
import requests
import yfinance as yf
from datetime import datetime
import logging

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#나스닥")  # 채널을 #나스닥으로 설정

def get_stock_price(ticker="^IXIC", name="나스닥"):  # 나스닥 지수의 티커는 ^IXIC
    stock = yf.Ticker(ticker)
    history = stock.history(period="2d")  # 2일치 데이터 가져오기
    
    if len(history) < 2:
        return f"{name} 지수 데이터를 가져올 수 없습니다."
    
    prev_close = history["Close"].iloc[0]  # 전날 종가
    current_close = history["Close"].iloc[1]  # 오늘 종가
    
    change_percent = ((current_close - prev_close) / prev_close) * 100  # 변동률 계산
    change_sign = f"+{change_percent:.2f}" if change_percent > 0 else f"{change_percent:.2f}"  # 양수일 때 + 추가
    
    return f"{name} 지수 참고하렴 *{current_close:.2f}* ({change_sign}%)  :rocket:"

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
        print('market open')
        message1 = get_stock_price("^IXIC", "NASDAQ")  # 나스닥 지수 가격 가져오기
        message2 = get_stock_price("^GSPC", "S&P500")  # S&P500 지수 가격 가져오기
        
        result = send_slack_message(message1)
        send_slack_message(message2)
        
        print(result)
    else:
        send_slack_message("미국 시장은 현재 열려 있지 않습니다.")
