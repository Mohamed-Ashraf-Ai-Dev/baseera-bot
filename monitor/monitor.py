import os
import sys
import json
import requests
from datetime import datetime
import pytz

MONITOR_TOKEN = os.environ.get("MONITOR_TOKEN")
OWNER_CHAT_ID = os.environ.get("OWNER_CHAT_ID")
LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "logs", "daily_log.json")

EGYPT_TZ = pytz.timezone("Africa/Cairo")

SPECIALTY_EMOJI = {
"حقيقة غريبة": "🔮",
"معلومة مفيدة للحياة": "💡",
"معلومة تاريخية قصيرة": "📜",
"معلومة مستحيل تعرفها": "🤯",
"معلومة تقنية": "⚙️",
}


def send_to_owner(text: str) -> bool:
"""Send message to owner."""
url = f"
https://api.telegram.org/bot{MONITOR_TOKEN}/sendMessage
"
payload = {
"chat_id": OWNER_CHAT_ID,
"text": text,
"parse_mode": "HTML",
}
try:
resp = requests.post(url, json=payload, timeout=30)
resp.raise_for_status()
print("[Monitor] تم إرسال التقرير بنجاح ✅")
return True
except Exception as e:
print(f"[Monitor] فشل الإرسال: {e}")
return False


def load_log() -> dict | None:
"""Load daily log."""
if not os.path.exists(LOG_PATH):
return None
try:
with open(LOG_PATH, "r", encoding="utf-8") as f:
return json.load(f)
except Exception:
return None


def build_report(log_data: dict) -> str:
"""Build the daily report message."""
now = datetime.now(EGYPT_TZ)
date_str = now.strftime("%Y/%m/%d")
posts = log_data.get("posts", [])

success_count = sum(1 for p in posts if p.get("status") == "success")
failed_count = sum(1 for p in posts if p.get("status") == "failed")

# رأس التقرير
report = (
f"🌙 يا محمد باشا أشرف، تقرير يومك {date_str}\n"
f"{'━' * 30}\n\n"
)

if not posts:
report += "⚠️ لم يُنشر أي بوست اليوم.\n"
return report

# ملخص سريع
report += (
f"📊 ملخص اليوم:\n"
f"✅ بوستات نُشرت: {success_count}\n"
f"❌ بوستات فشلت: {failed_count}\n\n"
f"{'━' * 30}\n\n"
f"📋 تفاصيل البوستات:\n\n"
)

# تفاصيل كل بوست
for i, post in enumerate(posts, 1):
specialty = post.get("specialty", "غير محدد")
emoji = SPECIALTY_EMOJI.get(specialty, "📌")
time_str = post.get("time", "")
content = post.get("content", "")
status = "✅" if post.get("status") == "success" else "❌"

# اقتصر على أول 100 حرف من المحتوى
short_content = content[:100] + "..." if len(content) > 100 else content

report += (
f"{status} البوست {i} — الساعة {time_str}\n"
f"{emoji} {specialty}\n"
f"{short_content}\n\n"
)

report += f"{'━' * 30}\n"

# حالة القناة
if failed_count == 0:
report += "🚀 القناة تعمل بشكل مثالي اليوم!\n"
elif success_count == 0:
report += "🚨 تحذير: لم يُنشر أي بوست بنجاح اليوم!\n"
else:
report += f"⚠️ بعض البوستات فشلت، راجع اللوج للتفاصيل.\n"

report += "\n— بصيرة | نظام المراقبة"

return report


def main():
print("=" * 50)
print("[Monitor] بدء إرسال التقرير اليومي...")

if not MONITOR_TOKEN:
print("[Monitor] خطأ: MONITOR_TOKEN غير موجود!")
sys.exit(1)
if not OWNER_CHAT_ID:
print("[Monitor] خطأ: OWNER_CHAT_ID غير موجود!")
sys.exit(1)

log_data = load_log()

if not log_data:
now = datetime.now(EGYPT_TZ)
msg = (
f"⚠️ يا محمد باشا أشرف\n\n"
f"لا يوجد لوج ليوم {now.strftime('%Y/%m/%d')}.\n"
f"ربما لم تشتغل الأكشن اليوم أو حدث خطأ.\n\n"
f"— بصيرة | نظام المراقبة"
)
send_to_owner(msg)
return

report = build_report(log_data)
success = send_to_owner(report)

if not success:
sys.exit(1)

print("[Monitor] انتهى التقرير بنجاح ✅")


if __name__ == "__main__":
main()
