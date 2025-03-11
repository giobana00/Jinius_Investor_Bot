import matplotlib.pyplot as plt
import subprocess
import matplotlib.font_manager as fm
import os
import yfinance as yf
import pandas as pd
import requests

# 🚀 GitHub Actions에서 한글 폰트 설치 및 캐시 업데이트
def install_nanum_font():
    print("🚀 한글 폰트 설치 중...")
    subprocess.run(["sudo", "apt-get", "install", "-y", "fonts-nanum"], check=True)
    subprocess.run(["fc-cache", "-fv"], check=True)  # 🚀 폰트 캐시 업데이트
    print("✅ 한글 폰트 설치 완료!")

    # 🚀 폰트 경로 확인 후 적용
    font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"

    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)  # 폰트 추가
        plt.rc("font", family="NanumGothic")
        print(f"✅ 한글 폰트 적용 완료! ({font_path})")
    else:
        print("❌ 한글 폰트 적용 실패! 기본 폰트 사용")
    
    # 🚀 `matplotlib` 폰트 캐시 강제 업데이트
    fm._load_fontmanager()
    print("✅ `matplotlib` 폰트 캐시 업데이트 완료!")

# 🚀 한글 폰트 설치 실행
install_nanum_font()
plt.rcParams["axes.unicode_minus"] = False  # 마이너스 기호 깨짐 방지

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

# 🚀 3. 최신 데이터 정리 (Series 문제 해결)
latest = tlt_1m.iloc[-1]
latest_date = str(latest.name)[:10]
latest_close = float(latest["Close"])  # 🚀 Series → float 변환
latest_rsi = float(latest["RSI"])  # 🚀 Series → float 변환
avg_rsi_1m = float(tlt_1m["RSI"].mean())  # 🚀 평균도 float 변환
avg_rsi_3m = float(tlt_3m["RSI"].mean())

# 🚀 4. 미국 2년, 10년, 20년물 채권 종가 + 변동폭 가져오기
def get_bond_prices():
    tickers = ["^IRX", "^TNX", "TLT"]  # 2년물, 10년물, 20년물 (TLT는 이미 있음)
    bond_data = yf.download(tickers, period="5d", interval="1d")["Close"].dropna()

    latest_prices = bond_data.iloc[-1]  # 최신 종가
    prev_prices = bond_data.iloc[-2]  # 전일 종가

    # 🚀 전일 대비 변동폭 계산
    price_changes = latest_prices - prev_prices

    # 🚀 2년, 10년물 금리를 100으로 나눠 실제 금리와 맞춤
    latest_prices["^IRX"] /= 100.0
    latest_prices["^TNX"] /= 100.0
    price_changes["^IRX"] /= 100.0
    price_changes["^TNX"] /= 100.0

    return latest_prices, price_changes

# 🚀 5. 채권 종가 & 변동폭 가져오기
latest_bond_prices, bond_changes = get_bond_prices()

# 🚀 6. 채권 종가 & 변동폭 표 정리
bond_table = f"""
📊 [미국 국채 종가]
━━━━━━━━━━━━━━━━━
📅 날짜: {latest_date}
🔹 미국 2년물: {latest_bond_prices["^IRX"]:.2f}% ({bond_changes["^IRX"]:+.2f}%)
🔹 미국 10년물: {latest_bond_prices["^TNX"]:.2f}% ({bond_changes["^TNX"]:+.2f}%)
🔹 미국 20년물 (TLT): {latest_close:.2f} ({bond_changes["TLT"]:+.2f})
━━━━━━━━━━━━━━━━━
"""

# 🚀 7. 텔레그램 메시지 생성 (RSI + 채권 종가 추가)
message = f"""
📊 [미국 20년물 국채 (TLT) RSI 업데이트]
📅 날짜: {latest_date}
💰 종가: {latest_close:.2f}
📈 RSI: {latest_rsi:.2f}

📊 최근 1개월 평균 RSI: {avg_rsi_1m:.2f}
📊 최근 3개월 평균 RSI: {avg_rsi_3m:.2f}

🔹 RSI > 70 → 과매수 (매도 신호 가능)
🔹 RSI < 30 → 과매도 (매수 신호 가능)

{bond_table}  # 채권 종가 정보 추가
"""

print(message)

# 🚀 8. 텔레그램으로 데이터 전송 실행
TELEGRAM_BOT_TOKEN = "7756935846:AAGbwXzNvkjliKDeOhYLJjoE_c45P26cBSM"
TELEGRAM_CHAT_ID = "6594623274"

def send_telegram_text(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print("✅ Telegram 메시지 전송 성공!")
    else:
        print(f"❌ Telegram 메시지 전송 실패! 오류 메시지: {response.text}")

send_telegram_text(message)
