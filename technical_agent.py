"""
Agente Técnico — NAS100
Descarga precios con yfinance y calcula indicadores técnicos.
"""

import yfinance as yf
import pandas as pd


def calcular_rsi(series: pd.Series, periodo: int = 14) -> float:
    """Calcula el RSI manualmente usando pandas."""
    delta = series.diff()
    ganancias = delta.clip(lower=0)
    perdidas = -delta.clip(upper=0)
    avg_gan = ganancias.ewm(com=periodo - 1, min_periods=periodo).mean()
    avg_per = perdidas.ewm(com=periodo - 1, min_periods=periodo).mean()
    rs = avg_gan / avg_per
    rsi = 100 - (100 / (1 + rs))
    return round(float(rsi.iloc[-1]), 2)


def calcular_macd(series: pd.Series) -> dict:
    """Calcula MACD (12, 26, 9)."""
    ema12 = series.ewm(span=12, adjust=False).mean()
    ema26 = series.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line
    return {
        "macd": round(float(macd_line.iloc[-1]), 2),
        "signal": round(float(signal_line.iloc[-1]), 2),
        "histogram": round(float(histogram.iloc[-1]), 2),
    }


def get_technical_summary() -> dict:
    """Descarga datos del NAS100 y calcula el análisis técnico completo."""
    print("📈 Descargando datos de precio del NAS100...")
    ticker = yf.Ticker("^NDX")
    df = ticker.history(period="1y")

    if df.empty:
        return {"error": "No se pudieron obtener datos de precio."}

    cierre = df["Close"]
    precio_actual = round(float(cierre.iloc[-1]), 2)
    precio_ayer = round(float(cierre.iloc[-2]), 2)
    cambio_dia = round(precio_actual - precio_ayer, 2)
    cambio_pct = round((cambio_dia / precio_ayer) * 100, 2)

    sma20 = round(float(cierre.rolling(20).mean().iloc[-1]), 2)
    sma50 = round(float(cierre.rolling(50).mean().iloc[-1]), 2)
    sma200 = round(float(cierre.rolling(200).mean().iloc[-1]), 2)

    rsi = calcular_rsi(cierre)
    macd_data = calcular_macd(cierre)

    maximo_52s = round(float(cierre.rolling(252).max().iloc[-1]), 2)
    minimo_52s = round(float(cierre.rolling(252).min().iloc[-1]), 2)

    std20 = cierre.rolling(20).std().iloc[-1]
    bb_superior = round(sma20 + 2 * std20, 2)
    bb_inferior = round(sma20 - 2 * std20, 2)

    # Tendencia principal
    if precio_actual > sma20 and precio_actual > sma200:
        tendencia = "Alcista"
    elif precio_actual < sma20 and precio_actual < sma200:
        tendencia = "Bajista"
    else:
        tendencia = "Zona de Indecisión"

    # Señal de corto plazo (SMA20 vs SMA50)
    if sma20 > sma50:
        senal_corto = "Golden Cross ✅"
    else:
        senal_corto = "Death Cross ⚠️"

    # Nivel RSI
    if rsi > 70:
        senal_rsi = "Sobrecomprado"
    elif rsi < 30:
        senal_rsi = "Sobrevendido"
    else:
        senal_rsi = "Neutral"

    print(f"   ✅ Precio: {precio_actual:,.0f} | Tendencia: {tendencia} | RSI: {rsi}")

    return {
        "precio_actual": precio_actual,
        "cambio_dia": cambio_dia,
        "cambio_pct": cambio_pct,
        "sma20": sma20,
        "sma50": sma50,
        "sma200": sma200,
        "rsi": rsi,
        "senal_rsi": senal_rsi,
        "macd": macd_data["macd"],
        "macd_signal": macd_data["signal"],
        "macd_histogram": macd_data["histogram"],
        "bb_superior": bb_superior,
        "bb_inferior": bb_inferior,
        "maximo_52s": maximo_52s,
        "minimo_52s": minimo_52s,
        "tendencia": tendencia,
        "senal_corto": senal_corto,
        "precios_recientes": cierre.tail(60).round(2).tolist(),
        "fechas_recientes": [str(d.date()) for d in cierre.tail(60).index],
    }


# Para importar desde app.py
technical_summary = {}


def run():
    global technical_summary
    technical_summary = get_technical_summary()
    return technical_summary


if __name__ == "__main__":
    s = run()
    print("\n--- RESUMEN TÉCNICO ---")
    print(f"Precio actual : {s['precio_actual']:>10,.2f}")
    print(f"Cambio día    : {s['cambio_dia']:>+10,.2f} ({s['cambio_pct']:+.2f}%)")
    print(f"SMA 20        : {s['sma20']:>10,.2f}")
    print(f"SMA 50        : {s['sma50']:>10,.2f}")
    print(f"SMA 200       : {s['sma200']:>10,.2f}")
    print(f"RSI (14)      : {s['rsi']:>10} → {s['senal_rsi']}")
    print(f"MACD          : {s['macd']:>10} (señal: {s['macd_signal']})")
    print(f"Tendencia     : {s['tendencia']}")
    print(f"Señal corto   : {s['senal_corto']}")
    print(f"52s máx/mín   : {s['maximo_52s']:,.0f} / {s['minimo_52s']:,.0f}")
