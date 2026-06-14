"""
NAS100 Intelligence Dashboard
Dashboard Streamlit que integra el agente técnico y el agente de noticias.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="NAS100 Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS personalizado ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .metric-card {
        background: #1a1d2e;
        border: 1px solid #2d3250;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
    }
    .conclusion-box {
        border-radius: 12px;
        padding: 1.5rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        text-align: center;
        margin-top: 1rem;
    }
    .bull  { background:#0d2d1f; border:1.5px solid #1D9E75; color:#4ade80; }
    .bear  { background:#2d0f0f; border:1.5px solid #D85A30; color:#f87171; }
    .mixed { background:#2d2510; border:1.5px solid #EF9F27; color:#fbbf24; }
    .news-item {
        background: #1a1d2e;
        border-left: 3px solid #2d3250;
        border-radius: 0 8px 8px 0;
        padding: .6rem 1rem;
        margin-bottom: .5rem;
        font-size: .85rem;
    }
    .bull-news  { border-left-color: #1D9E75; }
    .bear-news  { border-left-color: #D85A30; }
    .neut-news  { border-left-color: #888780; }
    .stButton>button {
        background: #3266ad;
        color: white;
        border: none;
        border-radius: 8px;
        padding: .5rem 1.5rem;
        font-weight: 600;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


# ── Carga de datos con caché ──────────────────────────────────────────────────
@st.cache_data(ttl=300)
def cargar_tecnico():
    from technical_agent import get_technical_summary
    return get_technical_summary()


@st.cache_data(ttl=300)
def cargar_noticias():
    from news_agent import get_news_summary
    return get_news_summary()


def determinar_conclusion(tech: dict, news: dict) -> tuple[str, str, str]:
    """Devuelve (texto, clase_css, emoji) según las señales combinadas."""
    t = tech.get("tendencia", "")
    n = news.get("sentimiento", "")

    if t == "Alcista" and n == "Alcista":
        return ("✅ Momento favorable para operar al alza — técnicos y flujo de noticias alineados.",
                "bull", "✅")
    elif t == "Bajista" and n == "Bajista":
        return ("🔴 Precaución: presión vendedora en precio y noticias — evitar largos.",
                "bear", "🔴")
    elif t == "Alcista" and n == "Bajista":
        return ("⚠️ Señales mixtas: técnicos alcistas pero noticias negativas — esperar confirmación.",
                "mixed", "⚠️")
    elif t == "Bajista" and n == "Alcista":
        return ("⚠️ Señales mixtas: noticias positivas pero precio en tendencia bajista — cautela.",
                "mixed", "⚠️")
    else:
        return ("⚠️ Mercado en zona de indecisión — sin señal clara. Mejor esperar.",
                "mixed", "⚠️")


# ── Header ────────────────────────────────────────────────────────────────────
col_title, col_btn = st.columns([4, 1])
with col_title:
    st.markdown("## 📊 NAS100 Intelligence Dashboard")
    st.caption(f"Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Actualizar análisis"):
        st.cache_data.clear()
        st.rerun()

st.divider()

# ── Carga de datos ─────────────────────────────────────────────────────────────
with st.spinner("Cargando análisis técnico..."):
    tech = cargar_tecnico()

with st.spinner("Clasificando noticias con IA..."):
    news = cargar_noticias()

if "error" in tech:
    st.error(f"Error en agente técnico: {tech['error']}")
    st.stop()

# ── Métricas superiores ────────────────────────────────────────────────────────
m1, m2, m3, m4, m5 = st.columns(5)

cambio_color = "normal" if tech["cambio_dia"] >= 0 else "inverse"
m1.metric("💹 NAS100", f"{tech['precio_actual']:,.0f}",
          f"{tech['cambio_dia']:+,.0f} ({tech['cambio_pct']:+.2f}%)", delta_color=cambio_color)
m2.metric("📉 RSI (14)", f"{tech['rsi']}", tech["senal_rsi"])
m3.metric("📰 Sentimiento", news.get("sentimiento", "—"),
          f"{news.get('alcistas',0)}🟢 {news.get('bajistas',0)}🔴 {news.get('neutras',0)}⚪")
m4.metric("📈 Tendencia", tech["tendencia"])
m5.metric("🎯 MACD", f"{tech['macd']:+.0f}", f"Señal: {tech['macd_signal']:.0f}")

st.divider()

# ── Columnas principales ───────────────────────────────────────────────────────
col_left, col_right = st.columns([3, 2])

with col_left:
    # Gráfico de precio
    st.subheader("📈 Precio NAS100 — últimos 60 días")
    df_precio = pd.DataFrame({
        "Fecha": pd.to_datetime(tech["fechas_recientes"]),
        "Precio": tech["precios_recientes"],
    })
    df_precio["SMA20"] = df_precio["Precio"].rolling(20).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_precio["Fecha"], y=df_precio["Precio"],
                             name="NAS100", line=dict(color="#3266ad", width=2)))
    fig.add_trace(go.Scatter(x=df_precio["Fecha"], y=df_precio["SMA20"],
                             name="SMA 20", line=dict(color="#EF9F27", width=1.5, dash="dot")))
    fig.add_hline(y=tech["sma200"], line_dash="dash", line_color="#D85A30",
                  annotation_text=f"SMA 200: {tech['sma200']:,.0f}", annotation_position="left")
    fig.add_hline(y=tech["bb_superior"], line_dash="dot", line_color="#888780",
                  annotation_text="BB sup", annotation_position="right")
    fig.add_hline(y=tech["bb_inferior"], line_dash="dot", line_color="#888780",
                  annotation_text="BB inf", annotation_position="right")
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", height=320,
        legend=dict(orientation="h", y=1.1),
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Indicadores técnicos
    st.subheader("🔧 Indicadores técnicos")
    ic1, ic2, ic3 = st.columns(3)
    ic1.metric("SMA 20", f"{tech['sma20']:,.0f}",
               "↑ Precio sobre SMA" if tech["precio_actual"] > tech["sma20"] else "↓ Precio bajo SMA",
               delta_color="normal" if tech["precio_actual"] > tech["sma20"] else "inverse")
    ic2.metric("SMA 50", f"{tech['sma50']:,.0f}", tech["senal_corto"])
    ic3.metric("SMA 200", f"{tech['sma200']:,.0f}",
               "↑ Tendencia alcista" if tech["precio_actual"] > tech["sma200"] else "↓ Tendencia bajista",
               delta_color="normal" if tech["precio_actual"] > tech["sma200"] else "inverse")

    ic4, ic5, ic6 = st.columns(3)
    ic4.metric("RSI", tech["rsi"], tech["senal_rsi"])
    ic5.metric("BB Superior", f"{tech['bb_superior']:,.0f}")
    ic6.metric("BB Inferior", f"{tech['bb_inferior']:,.0f}")

    ic7, ic8 = st.columns(2)
    ic7.metric("Máximo 52s", f"{tech['maximo_52s']:,.0f}")
    ic8.metric("Mínimo 52s", f"{tech['minimo_52s']:,.0f}")

with col_right:
    # Análisis de noticias
    st.subheader("📰 Análisis de noticias")

    total = news.get("total", 1) or 1
    alc = news.get("alcistas", 0)
    baj = news.get("bajistas", 0)
    neu = news.get("neutras", 0)

    fig_pie = go.Figure(go.Pie(
        labels=["Alcistas", "Bajistas", "Neutras"],
        values=[alc, baj, neu],
        hole=.55,
        marker_colors=["#1D9E75", "#D85A30", "#888780"],
        textinfo="label+percent",
    ))
    fig_pie.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        height=220, showlegend=False,
        margin=dict(l=0, r=0, t=10, b=0),
        annotations=[dict(text=f"{news.get('sentimiento','—')}", x=0.5, y=0.5,
                          font_size=14, showarrow=False, font_color="white")]
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # Lista de noticias
    st.markdown("**Últimas noticias clasificadas**")
    for n in news.get("noticias", [])[:8]:
        cl = n.get("clasificacion", "Neutral")
        css = "bull-news" if cl == "Alcista" else "bear-news" if cl == "Bajista" else "neut-news"
        emoji = "🟢" if cl == "Alcista" else "🔴" if cl == "Bajista" else "⚪"
        title = n.get("title", "")[:65] + ("..." if len(n.get("title","")) > 65 else "")
        razon = n.get("razon", "")
        st.markdown(
            f'<div class="news-item {css}">{emoji} <strong>{title}</strong><br>'
            f'<span style="color:#aaa;font-size:.8rem">{razon}</span></div>',
            unsafe_allow_html=True
        )

# ── Conclusión final ──────────────────────────────────────────────────────────
st.divider()
st.subheader("🤖 Conclusión del Agente")
texto, css_clase, _ = determinar_conclusion(tech, news)
st.markdown(f'<div class="conclusion-box {css_clase}">{texto}</div>', unsafe_allow_html=True)

# Detalle expandible
with st.expander("Ver detalle completo del análisis"):
    dc1, dc2 = st.columns(2)
    with dc1:
        st.markdown("**Agente Técnico**")
        st.json({k: v for k, v in tech.items()
                 if k not in ("precios_recientes", "fechas_recientes")})
    with dc2:
        st.markdown("**Agente de Noticias**")
        st.json({k: v for k, v in news.items() if k != "noticias"})
