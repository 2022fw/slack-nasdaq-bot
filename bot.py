import os
import requests
import yfinance as yf
from datetime import datetime
import logging

logging.basicConfig(level=logging.DEBUG)

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#나스닥")  # 채널을 #나스닥으로 설정

def get_stock_price(ticker="^IXIC", name="나스닥"):  # 나스닥 지수의 티커는 ^IXIC
    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period="2d")  # 2일치 데이터 가져오기
        logging.debug(f"{ticker} 데이터: {history}")
        
        if len(history) < 2:
            logging.error(f"{name} 지수 데이터가 부족합니다: {history}")
            return f"{name} 지수 데이터를 가져올 수 없습니다."
        
        prev_close = history["Close"].iloc[-2]  # 전날 종가
        current_close = history["Close"].iloc[-1]  # 오늘 종가
        
        change_percent = ((current_close - prev_close) / prev_close) * 100  # 변동률 계산
        change_sign = f"+{change_percent:.2f}" if change_percent > 0 else f"{change_percent:.2f}"  # 양수일 때 + 추가
        
        return f"{name} 지수 참고하렴 *{current_close:.2f}* ({change_sign}%)  :rocket:"
    except Exception as e:
        logging.error(f"get_stock_price 오류: {e}")
        return f"{name} 지수 정보를 가져오는 중 오류 발생"

def send_slack_message(text):
    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}", "Content-Type": "application/json"}
    data = {"channel": SLACK_CHANNEL, "text": text}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        logging.debug(f"Slack 응답: {response.text}")
        
        if response.status_code != 200:
            logging.error(f"Slack API error: {response.status_code} - {response.text}")
            return {"ok": False, "error": response.text}
        
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Slack 메시지 전송 실패: {e}")
        return {"ok": False, "error": "Slack 요청 실패"}
    except requests.exceptions.JSONDecodeError:
        logging.error("Slack 응답을 JSON으로 변환할 수 없음")
        return {"ok": False, "error": "Invalid JSON response"}

def is_market_open():
    now = datetime.now()
    logging.debug(f"현재 시간: {now}, 시장 열림 여부: {now.weekday() < 5 and 9 <= now.hour < 16}")
    
    if now.weekday() >= 5:  # 토요일(5)이나 일요일(6)은 시장이 열리지 않음
        return False
    # 미국 시장은 오전 9시 30분부터 오후 4시까지 운영됨
    if now.hour >= 9 and now.hour < 16:
        return True
    return False

if __name__ == "__main__":
    try:
        logging.debug(f"시장 상태 확인: {is_market_open()}")
        if is_market_open():
            print('market open')
            message1 = get_stock_price("^IXIC", "NASDAQ")  # 나스닥 지수 가격 가져오기
            message2 = get_stock_price("^GSPC", "S&P500")  # S&P500 지수 가격 가져오기
            
            result1 = send_slack_message(message1)
            result2 = send_slack_message(message2)
            
            logging.debug(f"Slack 메시지 1 결과: {result1}")
            logging.debug(f"Slack 메시지 2 결과: {result2}")
        else:
            send_slack_message("미국 시장은 현재 열려 있지 않습니다.")
    except Exception as e:
        logging.error(f"메인 실행 중 오류 발생: {e}")
