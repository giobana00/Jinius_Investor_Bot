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

# 🚀 4. 미국 2년, 10년, 20년물 채권 종가 가져오기
def get_bond_prices():
    tickers = ["^IRX", "^TNX", "TLT"]  # 2년물, 10년물, 20년물 (TLT는 이미 있음)
    bond_data = yf.download(tickers, period="5d", interval="1d")["Close"].dropna()
    latest_bond_prices = bond_data.iloc[-1]  # 최신 종가 가져오기
    return latest_bond_prices

# 🚀 5. 채권 종가 가져오기
latest_bond_prices = get_bond_prices()

# 🚀 6. 채권 종가 표 정리
bond_table = f"""
📊 [미국 국채 종가]
━━━━━━━━━━━━━━━━━
📅 날짜: {latest_date}
🔹 미국 2년물: {latest_bond_prices["^IRX"]:.2f}
🔹 미국 10년물: {latest_bond_prices["^TNX"]:.2f}
🔹 미국 20년물 (TLT): {latest_close:.2f}
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

# 🚀 8. RSI 그래프에서 값이 있는 곳부터 시작
tlt_1m_nonzero = tlt_1m[tlt_1m["RSI"].notna()]  # 값이 있는 부분만 가져오기
tlt_3m_nonzero = tlt_3m[tlt_3m["RSI"].notna()]

# 🚀 9. RSI 그래프 생성
plt.figure(figsize=(10, 5))
plt.plot(tlt_1m_nonzero.index, tlt_1m_nonzero["RSI"], label="RSI (1개월)", marker="o")
plt.plot(tlt_3m_nonzero.index, tlt_3m_nonzero["RSI"], label="RSI (3개월)", linestyle="dashed")
plt.axhline(y=70, color="r", linestyle="--", label="과매수 (70)")
plt.axhline(y=30, color="g", linestyle="--", label="과매도 (30)")
plt.legend()
plt.title("📊 TLT RSI 추이 (1개월 & 3개월)")
plt.xlabel("날짜")
plt.ylabel("RSI")
plt.grid()

# 🚀 10. 이미지 저장 경로 변경
image_path = "/tmp/tlt_rsi_chart.png"
plt.savefig(image_path)
plt.close()

# 🚀 11. 텔레그램 설정
TELEGRAM_BOT_TOKEN = "7756935846:AAGbwXzNvkjliKDeOhYLJjoE_c45P26cBSM"
TELEGRAM_CHAT_ID = "6594623274"

# 🚀 12. 텔레그램 메시지 전송 함수
def send_telegram_text(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print("✅ Telegram 메시지 전송 성공!")
    else:
        print(f"❌ Telegram 메시지 전송 실패! 오류 메시지: {response.text}")

# 🚀 13. 텔레그램 이미지 전송 함수
def send_telegram_image(image_path, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    
    if not os.path.exists(image_path):
        print(f"❌ 오류: 이미지 파일이 존재하지 않습니다! ({image_path})")
        return

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

# 🚀 14. 텔레그램으로 데이터 전송 실행
send_telegram_text(message)
send_telegram_image(image_path, "📊 TLT RSI + 채권 종가 업데이트")
