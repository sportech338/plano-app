import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Carrinhos Abandonados", layout="wide")

# 📥 URLs dos dados
csv_abandonos_url = "https://docs.google.com/spreadsheets/d/1OBKs2RpmRNqHDn6xE3uMOU-bwwnO_JY1ZhqctZGpA3E/export?format=csv"
csv_investimento_url = "https://docs.google.com/spreadsheets/d/1XXXXX_EXPORT_CSV_URL_AQUI/export?format=csv"  # Substituir pelo link real

@st.cache_data
def load_data():
    abandonos = pd.read_csv(csv_abandonos_url)
    abandonos["DATA INICIAL"] = pd.to_datetime(abandonos["DATA INICIAL"], errors="coerce")
    abandonos["VALOR"] = abandonos["VALOR"].astype(str).str.replace(",", ".").astype(float)
    abandonos.dropna(subset=["DATA INICIAL", "VALOR", "ABANDONOU EM"], inplace=True)
    return abandonos

@st.cache_data
def load_ads():
    ads = pd.read_csv(csv_investimento_url)
    ads["Data"] = pd.to_datetime(ads["Data"], errors="coerce")
    ads.rename(columns={"Data": "DATA INICIAL", "Investimento": "INVESTIMENTO"}, inplace=True)
    return ads

# Carregamento
df = load_data()
df_ads = load_ads()

# 🔍 Filtro de data
st.sidebar.header("📅 Filtro de Período")
data_min = df["DATA INICIAL"].min()
data_max = df["DATA INICIAL"].max()

intervalo = st.sidebar.date_input(
    "Selecionar intervalo:", [data_min, data_max], min_value=data_min, max_value=data_max
)
data_inicial, data_final = pd.to_datetime(intervalo[0]), pd.to_datetime(intervalo[1])

# Aplica filtro
df_filtrado = df[(df["DATA INICIAL"] >= data_inicial) & (df["DATA INICIAL"] <= data_final)]
df_ads_filtrado = df_ads[(df_ads["DATA INICIAL"] >= data_inicial) & (df_ads["DATA INICIAL"] <= data_final)]

# Junta os dados por data
resumo = df_filtrado.groupby(df_filtrado["DATA INICIAL"].dt.date).agg({
    "VALOR": "sum",
    "DATA INICIAL": "count"
}).rename(columns={"DATA INICIAL": "ABANDONOS", "VALOR": "VALOR ABANDONADO"}).reset_index()

resumo["DATA INICIAL"] = pd.to_datetime(resumo["DATA INICIAL"])
resumo_final = pd.merge(resumo, df_ads_filtrado, how="left", on="DATA INICIAL")

# KPIs
valor_total = df_filtrado["VALOR"].sum()
ticket_medio = df_filtrado["VALOR"].mean()
total_abandonos = df_filtrado.shape[0]

st.title("📦 Dashboard de Carrinhos Abandonados")

col1, col2, col3 = st.columns(3)
col1.metric("💰 Valor Total Abandonado", f"R$ {valor_total:,.2f}")
col2.metric("🧾 Ticket Médio", f"R$ {ticket_medio:,.2f}")
col3.metric("🛒 Total de Abandonos", total_abandonos)

st.divider()

# 📅 Abandonos vs Investimento
st.subheader("📊 Abandonos x Investimento por Dia")
fig_mix = px.bar(
    resumo_final,
    x="DATA INICIAL",
    y="ABANDONOS",
    labels={"DATA INICIAL": "Data", "ABANDONOS": "Abandonos"},
    text="ABANDONOS",
    color_discrete_sequence=["#1f77b4"]
)
fig_mix.add_scatter(
    x=resumo_final["DATA INICIAL"],
    y=resumo_final["INVESTIMENTO"],
    mode="lines+markers",
    name="Investimento (Meta Ads)",
    yaxis="y2",
    line=dict(color="#ff7f0e")
)
fig_mix.update_layout(
    yaxis=dict(title="Abandonos"),
    yaxis2=dict(title="Investimento (R$)", overlaying="y", side="right"),
    xaxis_tickformat="%d/%m",
    height=450
)

st.plotly_chart(fig_mix, use_container_width=True)

# Etapas de abandono
st.subheader("🥧 Distribuição das Etapas de Abandono")
etapas = df_filtrado["ABANDONOU EM"].value_counts().reset_index()
etapas.columns = ["Etapa", "Quantidade"]
fig_pie = px.pie(etapas, names="Etapa", values="Quantidade", title="Etapas onde ocorrem os abandonos", hole=0.4)
st.plotly_chart(fig_pie, use_container_width=True)

# Simulador de recuperação
st.subheader("📊 Simulador de Receita Recuperável")
meta = st.slider("Taxa de recuperação esperada (%)", 0, 100, 25, step=5)
valor_recuperado = valor_total * (meta / 100)
st.success(f"🔄 Recuperando {meta}% → **R$ {valor_recuperado:,.2f}**")

# Estratégia
st.subheader("🧠 Perguntas Estratégicas para o Time de Marketing")
st.markdown("""
1. **Qual etapa está gerando mais perda de receita?**  
2. **Estamos priorizando os carrinhos de maior valor?**  
3. **Quais testes A/B podem melhorar o funil?**
""")
