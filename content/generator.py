import os
import requests

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

SPECIALTIES = [
"حقيقة غريبة",
"معلومة مفيدة للحياة",
"معلومة تاريخية قصيرة",
"معلومة مستحيل تعرفها",
"معلومة تقنية",
]

PROMPTS = {
"حقيقة غريبة": (
"اكتب حقيقة غريبة ومدهشة وصحيحة علمياً. "
"اكتب فقط الحقيقة بدون أي مقدمة أو خاتمة أو تعليق. "
"جملة أو جملتين بالعربية الفصحى البسيطة."
),
"معلومة مفيدة للحياة": (
"اكتب معلومة مفيدة جداً للحياة اليومية. "
"اكتب فقط المعلومة بدون أي مقدمة أو خاتمة أو تعليق. "
"جملة أو جملتين بالعربية الفصحى البسيطة."
),
"معلومة تاريخية قصيرة": (
"اكتب معلومة تاريخية قصيرة ومثيرة للاهتمام. "
"اكتب فقط المعلومة بدون أي مقدمة أو خاتمة أو تعليق. "
"جملة أو جملتين بالعربية الفصحى البسيطة."
),
"معلومة مستحيل تعرفها": (
"اكتب معلومة نادرة جداً لا يعرفها معظم الناس وصحيحة. "
"اكتب فقط المعلومة بدون أي مقدمة أو خاتمة أو تعليق. "
"جملة أو جملتين بالعربية الفصحى البسيطة."
),
"معلومة تقنية": (
"اكتب معلومة تقنية مثيرة للاهتمام عن التكنولوجيا أو البرمجة أو الذكاء الاصطناعي. "
"اكتب فقط المعلومة بدون أي مقدمة أو خاتمة أو تعليق. "
"جملة أو جملتين بالعربية الفصحى البسيطة."
),
}


def generate_with_openrouter(specialty: str) -> str | None:
"""Try to generate content using OpenRouter."""
if not OPENROUTER_API_KEY:
return None

prompt = PROMPTS[specialty]
headers = {
"Authorization": f"Bearer {OPENROUTER_API_KEY}",
"Content-Type": "application/json",
"HTTP-Referer": "
https://github.com/baseera-bot
",
"X-Title": "Baseera Bot",
}
body = {
"model": "meta-llama/llama-4-maverick:free",
"messages": [{"role": "user", "content": prompt}],
"max_tokens": 200,
"temperature": 0.9,
}

try:
resp = requests.post(
"
https://openrouter.ai/api/v1/chat/completions
",
headers=headers,
json=body,
timeout=30,
)
resp.raise_for_status()
data = resp.json()
text = data["choices"][0]["message"]["content"].strip()
return text if text else None
except Exception as e:
print(f"[OpenRouter] فشل: {e}")
return None


def generate_with_groq(specialty: str) -> str | None:
"""Try to generate content using Groq as fallback."""
if not GROQ_API_KEY:
return None

prompt = PROMPTS[specialty]
headers = {
"Authorization": f"Bearer {GROQ_API_KEY}",
"Content-Type": "application/json",
}
body = {
"model": "llama-3.3-70b-versatile",
"messages": [{"role": "user", "content": prompt}],
"max_tokens": 200,
"temperature": 0.9,
}

try:
resp = requests.post(
"
https://api.groq.com/openai/v1/chat/completions
",
headers=headers,
json=body,
timeout=30,
)
resp.raise_for_status()
data = resp.json()
text = data["choices"][0]["message"]["content"].strip()
return text if text else None
except Exception as e:
print(f"[Groq] فشل: {e}")
return None


def generate_content(specialty: str) -> str:
"""Generate content using OpenRouter first, then Groq as fallback."""
print(f"[Generator] جاري توليد محتوى لـ: {specialty}")

text = generate_with_openrouter(specialty)
if text:
print("[Generator] تم التوليد بنجاح عبر OpenRouter ✅")
return text

print("[Generator] OpenRouter فشل، جاري المحاولة عبر Groq...")
text = generate_with_groq(specialty)
if text:
print("[Generator] تم التوليد بنجاح عبر Groq ✅")
return text

raise RuntimeError("فشل توليد المحتوى من جميع المصادر.")
