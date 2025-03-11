import requests
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import os

# 🚀 Telegram 설정 (환경 변수를 사용하지 않고 직접 입력)
TELEGRAM_BOT_TOKEN = "7756935846:AAGbwXzNvkjliKDeOhYLJjoE_c45P26cBSM"  # 🔹 직접 입력
TELEGRAM_CHAT_ID = "6594623274"  # 🔹 직접 입력

# 🚀 1. TLT 데이터 가져오기 & RSI 계산
def get_tlt_data(period="3mo"):
    data = yf.download("TLT", period=period, interval="1d")

    # RSI 계산 함수
    def calculate_rsi(data, period=14):
        delta = data["Close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=period, min_periods=1).mean()
        avg_loss = loss.rolling(window=period, min_periods=1).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    data["RSI"] = calculate_rsi(data)
    return data

# 🚀 2. 1개월 & 3개월 데이터 가져오기
tlt_1m = get_tlt_data("1mo")
tlt_3m = get_tlt_data("3mo")

# 🚀 3. 최신 데이터 정리
latest = tlt_1m.iloc[-1]
latest_date = str(latest.name)[:10]
latest_close = latest["Close"]
latest_rsi = latest["RSI"]
avg_rsi_1m = tlt_1m["RSI"].mean()
avg_rsi_3m = tlt_3m["RSI"].mean()

# 🚀 4. 텔레그램 메시지 생성
message = f"""
📊 [미국 20년물 국채 (TLT) RSI 업데이트]
📅 날짜: {latest_date}
💰 종가: {latest_close:.2f}
📈 RSI: {latest_rsi:.2f}

📊 최근 1개월 평균 RSI: {avg_rsi_1m:.2f}
📊 최근 3개월 평균 RSI: {avg_rsi_3m:.2f}

🔹 RSI > 70 → 과매수 (매도 신호 가능)
🔹 RSI < 30 → 과매도 (매수 신호 가능)
"""

print(message)  # 🚀 메시지 확인용 출력

# 🚀 5. RSI 그래프 생성
plt.figure(figsize=(10,5))
plt.plot(tlt_1m.index, tlt_1m["RSI"], label="RSI (1개월)", marker="o")
plt.plot(tlt_3m.index, tlt_3m["RSI"], label="RSI (3개월)", linestyle="dashed")
plt.axhline(y=70, color="r", linestyle="--", label="과매수 (70)")
plt.axhline(y=30, color="g", linestyle="--", label="과매도 (30)")
plt.legend()
plt.title("📊 TLT RSI 추이 (1개월 & 3개월)")
plt.xlabel("날짜")
plt.ylabel("RSI")
plt.grid()

# 🚀 6. 이미지 저장 경로 변경 (GitHub Actions에서 사용 가능하도록 수정)
image_path = "/tmp/tlt_rsi_chart.png"
plt.savefig(image_path)
plt.close()

# 🚀 7. 텔레그램 메시지 전송 함수
def send_telegram_text(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print("✅ Telegram 메시지 전송 성공!")
    else:
        print(f"❌ Telegram 메시지 전송 실패! 오류 메시지: {response.text}")

# 🚀 8. 텔레그램 이미지 전송 함수
def send_telegram_image(image_path, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    try:
        with open(image_path, "rb") as img:
            files = {"photo": img}
            data = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption}
            response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            print("✅ Telegram 그래프 이미지 전송 성공!")
        else:
            print(f"❌ Telegram 그래프 이미지 전송 실패! 오류 메시지: {response.text}")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

# 🚀 9. 텔레그램으로 데이터 전송 실행
send_telegram_text(message)
send_telegram_image(image_path, "📊 TLT RSI 그래프 업데이트")
