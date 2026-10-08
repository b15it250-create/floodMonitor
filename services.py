import os
import requests
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """
You are FloodWatch AI, a flood early-warning and response assistant.
Give concise, safety-first flood guidance. For immediate danger, advise
moving to higher ground and contacting local emergency authorities.
Never encourage walking or driving through floodwater.
"""

def rule_based_answer(question):
    q=question.lower()

    if "evacuat" in q:
        return "Evacuate early when instructed. Move to higher ground, carry medicines, drinking water, phone, power bank, documents in waterproof packaging, and avoid flooded roads."
    if "vehicle" in q or "drive" in q:
        return "Do not drive through floodwater. Depth and current are difficult to judge, roads may be damaged, and vehicles can be swept away."
    if "electric" in q:
        return "Avoid contact with electrical equipment or wires in wet areas. If water enters the building, switch off electricity only if it is safe to reach the main switch."
    if "water" in q and "drink" in q:
        return "Use sealed or safely treated drinking water. Floodwater may contain sewage, chemicals, fuel, and disease-causing organisms."
    if "river" in q or "level" in q:
        return "Monitor official river-gauge alerts and local warnings. A rapid rising trend can be as important as the absolute water level."
    return "For immediate flood danger, move to higher ground, avoid floodwater, follow official evacuation instructions, and contact local emergency services."

def ask_ai(question, context=""):
    key=os.getenv("GROQ_API_KEY","").strip()
    model=os.getenv("GROQ_MODEL","llama-3.1-8b-instant").strip()

    if not key:
        return rule_based_answer(question), "Rule-based flood advisor"

    try:
        r=requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
            json={
                "model":model,
                "messages":[
                    {"role":"system","content":SYSTEM_PROMPT},
                    {"role":"user","content":f"Flood monitoring context:\n{context}\n\nQuestion:\n{question}"}
                ],
                "temperature":0.2,
                "max_tokens":500
            },
            timeout=25
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"], f"AI mode: {model}"
    except Exception:
        return rule_based_answer(question), "Fallback rule-based advisor"

def get_weather():
    key=os.getenv("OPENWEATHER_API_KEY","").strip()
    city=os.getenv("WEATHER_CITY","Guwahati").strip()

    if not key:
        return {"available":False,"city":city,"message":"Add OPENWEATHER_API_KEY to .env for live weather."}

    try:
        r=requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q":city,"appid":key,"units":"metric"},
            timeout=20
        )
        r.raise_for_status()
        d=r.json()
        return {
            "available":True,
            "city":city,
            "temperature":d["main"]["temp"],
            "humidity":d["main"]["humidity"],
            "wind_speed":d["wind"]["speed"],
            "rain_1h":d.get("rain",{}).get("1h",0),
            "condition":d["weather"][0]["description"].title()
        }
    except Exception:
        return {"available":False,"city":city,"message":"Weather service is currently unavailable."}
