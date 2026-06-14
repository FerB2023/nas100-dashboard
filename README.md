# NAS100 Intelligence Dashboard

Dashboard de análisis del índice Nasdaq 100 con agentes de IA.

## Instalación

```bash
pip install -r requirements.txt
```

## Configuración

1. Copiá el archivo de ejemplo y completá tus API keys:
```bash
cp .env.example .env
```

2. Editá `.env` con tus claves:
- **ALPHA_VANTAGE_KEY** → gratis en https://www.alphavantage.co/support/#api-key
- **OPENAI_API_KEY** → https://platform.openai.com/api-keys

## Uso

### Probar agentes por separado
```bash
python technical_agent.py   # análisis técnico en consola
python news_agent.py        # clasificación de noticias en consola
```

### Lanzar el dashboard
```bash
streamlit run app.py
```

## Archivos

| Archivo | Descripción |
|---|---|
| `technical_agent.py` | Descarga precios del NAS100 con yfinance, calcula SMA20/50/200, RSI, MACD y Bollinger |
| `news_agent.py` | Descarga noticias de Alpha Vantage y las clasifica con GPT-4o-mini |
| `app.py` | Dashboard Streamlit que integra ambos agentes con gráficos y conclusión final |
| `requirements.txt` | Dependencias Python |
| `.env.example` | Template de variables de entorno |
