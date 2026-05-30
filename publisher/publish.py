import os
import sys
import json
import random
import requests
from datetime import datetime
import pytz

# أضف المجلد الرئيسي للـ path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from content.generator import generate_content, SPECIALTIES

PUBLISHER_TOKEN = os.environ.get("PUBLISHER_TOKEN")
TELEGRAM_CHANNEL = os.environ.get("TELEGRAM_CHANNEL")
LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "logs", "daily_log.json")

EGYPT_TZ = pytz.timezone("Africa/Cairo")


def send_to_channel(text: str) -> bool:
    """Send message to Telegram channel."""
    # تم إصلاح الرابط هنا ليكون في سطر واحد
    url = f"https://api.telegram.org/bot{PUBLISHER_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": TELEGRAM_CHANNEL,
        "text": text,
        "parse_mode": "HTML",
    }
    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        print("[Publisher] تم النشر بنجاح ✅")
        return True
    except Exception as e:
        print(f"[Publisher] فشل النشر: {e}")
        return False


def load_log() -> dict:
    """Load or create daily log."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    today = datetime.now(EGYPT_TZ).strftime("%Y-%m-%d")

    if os.path.exists(LOG_PATH):
        try:
            with open(LOG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                # لو اليوم جديد، امسح اللوج القديم
                if data.get("date") != today:
                    data = {"date": today, "posts": []}
        except Exception:
            data = {"date": today, "posts": []}
    else:
        data = {"date": today, "posts": []}

    return data


def save_log(data: dict):
    """Save log to file."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def pick_specialty(log_data: dict) -> str:
    """Pick a random specialty, avoid repeating same specialty in one day."""
    used_today = [p["specialty"] for p in log_data.get("posts", [])]
    available = [s for s in SPECIALTIES if s not in used_today]

    if not available:
        available = SPECIALTIES  # لو اتكررت كلها، ابدأ من أول

    return random.choice(available)


def format_post(specialty: str, content: str) -> str:
    """Format the post text."""
    return f"<b>{specialty}</b>\n\n{content}"


def main():
    print("=" * 50)
    print("[Publisher] بدء عملية النشر...")

    # تحقق من المتغيرات
    if not PUBLISHER_TOKEN:
        print("[Publisher] خطأ: PUBLISHER_TOKEN غير موجود!")
        sys.exit(1)
    if not TELEGRAM_CHANNEL:
        print("[Publisher] خطأ: TELEGRAM_CHANNEL غير موجود!")
        sys.exit(1)

    # حمّل اللوج
    log_data = load_log()

    # اختر التخصص
    specialty = pick_specialty(log_data)
    print(f"[Publisher] التخصص المختار: {specialty}")

    # ولّد المحتوى
    content = generate_content(specialty)
    print(f"[Publisher] المحتوى: {content[:80]}...")

    # نسّق البوست
    post_text = format_post(specialty, content)

    # انشر على القناة
    success = send_to_channel(post_text)

    # سجّل في اللوج
    now = datetime.now(EGYPT_TZ)
    log_entry = {
        "time": now.strftime("%H:%M:%S"),
        "specialty": specialty,
        "content": content,
        "status": "success" if success else "failed",
    }
    log_data["posts"].append(log_entry)
    save_log(log_data)

    if not success:
        sys.exit(1)

    print("[Publisher] انتهت العملية بنجاح ✅")


if __name__ == "__main__":
    main()
