# planner.py
import os
import requests
from dotenv import load_dotenv
from external_apis import get_weather, web_search

load_dotenv()
HF_KEY = os.getenv("HF_KEY")
HF_MODEL = os.getenv("HF_MODEL", "gpt2")
HF_MODE = os.getenv("HF_MODE", "api").lower()

# --- API mode setup ---
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HF_HEADERS = {"Authorization": f"Bearer {HF_KEY}"} if HF_KEY else {}

# --- Local mode setup (lazy import) ---
generator = None
if HF_MODE == "local":
    from transformers import pipeline
    generator = pipeline("text-generation", model=HF_MODEL)

def call_hf_api(prompt, max_new_tokens=200, temperature=0.7):
    """Call HuggingFace Inference API (hosted)"""
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "return_full_text": False
        }
    }
    try:
        r = requests.post(HF_API_URL, headers=HF_HEADERS, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"].strip()
        return str(data)
    except Exception as e:
        return f"[HF API error] {e}"

def call_hf_local(prompt, max_new_tokens=200, temperature=0.7):
    """Call HuggingFace model locally"""
    result = generator(
        prompt,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        do_sample=True
    )
    return result[0]["generated_text"]

def generate_plan(goal, max_new_tokens=250, temperature=0.7):
    prompt = (
        "You are a helpful assistant that creates a clear, step-by-step, day-by-day plan.\n"
        f"Goal: {goal}\n\nPlan:\n"
    )
    if HF_MODE == "api":
        return call_hf_api(prompt, max_new_tokens=max_new_tokens, temperature=temperature)
    elif HF_MODE == "local":
        return call_hf_local(prompt, max_new_tokens=max_new_tokens, temperature=temperature)
    else:
        return "[Error] Invalid HF_MODE. Set HF_MODE=api or HF_MODE=local in .env"

def enrich_plan(plan_text, city=None):
    enriched = plan_text + "\n\n[External Information]\n"
    if city:
        enriched += f"Weather for {city}: {get_weather(city)}\n"
    query = plan_text if len(plan_text) < 200 else plan_text[:200]
    results = web_search(query)
    if results:
        enriched += "\nRelated Links:\n"
        for r in results:
            enriched += "- " + r + "\n"
    return enriched
