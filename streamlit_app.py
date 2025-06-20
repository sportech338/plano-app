import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Carrinhos Abandonados", layout="wide")

# 📥 Google Sheets CSV
csv_url = "https://docs.google.com/spreadsheets/d/1OBKs2RpmRNqHDn6xE3uMOU-bwwnO_JY1ZhqctZGpA3E/export?format=csv"

@st.cache_data
def load_data():
    df = pd.read_csv(csv_url)
    df["DATA INICIAL"] = pd.to_datetime(df["DATA INICIAL"], errors="coerce")
    df["VALOR"] = df["VALOR"].astype(str).str.replace(",", ".").astype(float)
    df.dropna(subset=["DATA INICIAL", "VALOR", "ABANDONOU EM"], inplace=True)
    return df

df = load_data()

# 🔍 Filtro de data
st.sidebar.header("📅 Filtro de Período")
data_min = df["DATA INICIAL"].min()
data_max = df["DATA INICIAL"].max()

data_inicial, data_final = st.sidebar.date_input(
    "Selecionar intervalo:",
    [data_min, data_max],
    min_value=data_min,
    max_value=data_max
)

# Aplica filtro
df_filtrado = df[(df["DATA INICIAL"] >= pd.to_datetime(data_inicial)) & (df["DATA INICIAL"] <= pd.to_datetime(data_final))]

# 🎯 KPIs
valor_total = df_filtrado["VALOR"].sum()
ticket_medio = df_filtrado["VALOR"].mean()
total_abandonos = df_filtrado.shape[0]

st.title("📦 Dashboard de Carrinhos Abandonados")

col1, col2, col3 = st.columns(3)
col1.metric("💰 Valor Total Abandonado", f"R$ {valor_total:,.2f}")
col2.metric("🧾 Ticket Médio", f"R$ {ticket_medio:,.2f}")
col3.metric("🛒 Total de Abandonos", total_abandonos)

st.divider()

# 📅 Abandonos por dia (bar dynamic)
st.subheader("📈 Abandonos por Dia")
abandonos_dia = (
    df_filtrado.groupby(df_filtrado["DATA INICIAL"].dt.date)
    .size()
    .reset_index(name="Quantidade")
    .sort_values("DATA INICIAL")
)

fig_bar = px.bar(
    abandonos_dia,
    x="DATA INICIAL",
    y="Quantidade",
    title="📅 Carrinhos Abandonados por Dia",
    labels={"DATA INICIAL": "Data", "Quantidade": "Total de Abandonos"},
    color_discrete_sequence=["#1f77b4"],
    template="simple_white"
)

fig_bar.update_layout(
    xaxis_tickformat="%d/%m",
    xaxis_title=None,
    yaxis_title="Abandonos",
    margin=dict(t=50, b=40, l=0, r=0),
    height=400
)

st.plotly_chart(fig_bar, use_container_width=True)


# 🚧 Etapas de abandono (pie dynamic)
st.subheader("🥧 Distribuição das Etapas de Abandono")
etapas = df_filtrado["ABANDONOU EM"].value_counts().reset_index()
etapas.columns = ["Etapa", "Quantidade"]
fig_pie = px.pie(etapas, names="Etapa", values="Quantidade", title="Etapas onde ocorrem os abandonos", hole=0.4)
st.plotly_chart(fig_pie, use_container_width=True)

# 💰 Simulador de recuperação
st.subheader("📊 Simulador de Receita Recuperável")
meta = st.slider("Taxa de recuperação esperada (%)", 0, 100, 25, step=5)
valor_recuperado = valor_total * (meta / 100)
st.success(f"🔄 Recuperando {meta}% → **R$ {valor_recuperado:,.2f}**")

# 🎯 Perguntas estratégicas
st.subheader("🧠 Perguntas Estratégicas para o Time de Marketing")
st.markdown("""
1. **Qual etapa está gerando mais perda de receita?**  
2. **Estamos priorizando os carrinhos de maior valor?**  
3. **Quais testes A/B podem melhorar o funil?**
""")
