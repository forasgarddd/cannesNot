import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# === CONFIGURATION ===
LOGIN_URL = "https://ticketonline3.festival-cannes.com/welcome?key=aPoHynQw0nmEDQjCmzuJobQSHx8KMxzQUQFHF8Shnww%3d"
SCREENING_URL = "https://ticketonline3.festival-cannes.com/fiche?idproj=hXo8YIhgMIk%3D"
CHECK_INTERVAL = 60  # seconds

TELEGRAM_BOT_TOKEN = "7805063902:AAEmbUy8kCBENQ1TiwbiMnBouvrY1r5jfK0"
TELEGRAM_CHAT_ID = "369699433"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"[!] Error sending Telegram message: {e}")

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/chromium"
    return webdriver.Chrome(executable_path="/usr/bin/chromedriver", options=chrome_options)

def check_ticket_availability(driver):
    try:
        driver.get(LOGIN_URL)
        time.sleep(2)
        driver.get(SCREENING_URL)
        time.sleep(3)
        page_text = driver.page_source
        if "Full for now" in page_text:
            print("[-] Still full...")
            return False
        elif "BOOK" in page_text or "Book your ticket" in page_text or "Book" in page_text:
            print("[+] TICKETS MAY BE AVAILABLE!")
            send_telegram_message(f"🎟️ Tickets may be available!\n\n{SCREENING_URL}")
            return True
        else:
            print("[?] Couldn't determine status clearly.")
            return False
    except Exception as e:
        print(f"[!] Error: {e}")
        return False

if __name__ == "__main__":
    print("Starting Cannes ticket notifier with Selenium...")
    driver = get_driver()
    try:
        while True:
            is_available = check_ticket_availability(driver)
            if is_available:
                print("[!] Notification sent. Waiting 10 minutes before checking again.")
                time.sleep(600)
            else:
                time.sleep(CHECK_INTERVAL)
    finally:
        driver.quit()