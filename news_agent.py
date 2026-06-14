"""
Agente de Noticias — NAS100
Descarga noticias de Alpha Vantage y las clasifica con OpenAI.
"""

import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

AV_KEY = os.getenv("ALPHA_VANTAGE_KEY")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def fetch_news(limit: int = 20) -> list[dict]:
    """Descarga las últimas noticias del NAS100/QQQ desde Alpha Vantage."""
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": "QQQ,NVDA,MSFT,AAPL,AMZN",
        "topics": "technology,earnings",
        "limit": limit,
        "apikey": AV_KEY,
    }
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    articles = []
    for item in data.get("feed", []):
        articles.append({
            "title": item.get("title", ""),
            "summary": item.get("summary", "")[:400],
            "source": item.get("source", ""),
            "published": item.get("time_published", ""),
        })
    return articles


def classify_news(articles: list[dict]) -> list[dict]:
    """Clasifica cada noticia como Alcista, Bajista o Neutral usando GPT."""
    results = []
    for art in articles:
        prompt = f"""Eres un analista de mercados experto en el índice Nasdaq 100 (NAS100).
Analiza la siguiente noticia y clasifícala SOLO como: Alcista, Bajista o Neutral para el NAS100.
Responde en formato JSON exacto: {{"clasificacion": "Alcista|Bajista|Neutral", "razon": "una sola oración"}}

Título: {art['title']}
Resumen: {art['summary']}"""

        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=120,
                temperature=0.2,
            )
            import json
            parsed = json.loads(resp.choices[0].message.content)
            results.append({
                **art,
                "clasificacion": parsed.get("clasificacion", "Neutral"),
                "razon": parsed.get("razon", ""),
            })
        except Exception as e:
            results.append({**art, "clasificacion": "Neutral", "razon": f"Error: {e}"})
    return results


def get_news_summary() -> dict:
    """Ejecuta el agente completo y devuelve el resumen de noticias."""
    print("📰 Descargando noticias...")
    articles = fetch_news(limit=20)

    if not articles:
        return {
            "total": 0, "alcistas": 0, "bajistas": 0, "neutras": 0,
            "sentimiento": "Sin datos", "noticias": [],
        }

    print(f"   {len(articles)} noticias encontradas. Clasificando con IA...")
    noticias = classify_news(articles)

    conteo = {"Alcista": 0, "Bajista": 0, "Neutral": 0}
    for n in noticias:
        conteo[n["clasificacion"]] = conteo.get(n["clasificacion"], 0) + 1

    total = len(noticias)
    if conteo["Alcista"] > conteo["Bajista"] and conteo["Alcista"] > conteo["Neutral"]:
        sentimiento = "Alcista"
    elif conteo["Bajista"] > conteo["Alcista"] and conteo["Bajista"] > conteo["Neutral"]:
        sentimiento = "Bajista"
    else:
        sentimiento = "Neutral"

    print(f"   ✅ Sentimiento: {sentimiento} ({conteo['Alcista']} 🟢 / {conteo['Bajista']} 🔴 / {conteo['Neutral']} ⚪)")

    return {
        "total": total,
        "alcistas": conteo["Alcista"],
        "bajistas": conteo["Bajista"],
        "neutras": conteo["Neutral"],
        "sentimiento": sentimiento,
        "noticias": noticias,
    }


# Para importar desde app.py
news_summary = {}


def run():
    global news_summary
    news_summary = get_news_summary()
    return news_summary


if __name__ == "__main__":
    summary = run()
    print("\n--- RESUMEN DE NOTICIAS ---")
    for n in summary["noticias"][:5]:
        emoji = "🟢" if n["clasificacion"] == "Alcista" else "🔴" if n["clasificacion"] == "Bajista" else "⚪"
        print(f"{emoji} [{n['clasificacion']}] {n['title'][:70]}...")
        print(f"   → {n['razon']}")
