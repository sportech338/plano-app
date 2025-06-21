import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Carrinhos Abandonados", layout="wide")

# 📥 URLs das planilhas como CSV
csv_abandono_url = "https://docs.google.com/spreadsheets/d/1OBKs2RpmRNqHDn6xE3uMOU-bwwnO_JY1ZhqctZGpA3E/export?format=csv"
csv_base_dados_url = "https://docs.google.com/spreadsheets/d/1JYHDnY8ykyklYELm2m5Wq7YaTs3CKPmecLjB3lDyBTI/export?format=csv&gid=0"

@st.cache_data
def load_data():
    df_abandono = pd.read_csv(csv_abandono_url)
    df_abandono["DATA INICIAL"] = pd.to_datetime(df_abandono["DATA INICIAL"], format="%d/%m/%Y %H:%M", errors="coerce")
    df_abandono["VALOR"] = df_abandono["VALOR"].astype(str).str.replace(",", ".").astype(float)
    df_abandono.dropna(subset=["DATA INICIAL", "VALOR", "ABANDONOU EM"], inplace=True)

    df_ads = pd.read_csv(csv_base_dados_url, names=["Data", "Gasto"], header=None)
    df_ads["Data"] = pd.to_datetime(df_ads["Data"], format="%d/%m/%Y", errors="coerce")
    df_ads["Investimento"] = pd.to_numeric(df_ads["Gasto"].astype(str).str.replace(",", "."), errors="coerce")
    df_ads = df_ads[["Data", "Investimento"]].dropna()

    return df_abandono, df_ads

df, df_ads = load_data()

# 🎯 Filtro de datas
st.sidebar.header("📅 Filtro de Período")
data_min = df["DATA INICIAL"].min().date()
data_max = df["DATA INICIAL"].max().date()

data_range = st.sidebar.date_input(
    "Selecionar intervalo:",
    value=(data_min, data_max),
    min_value=data_min,
    max_value=data_max
)

if isinstance(data_range, tuple) and len(data_range) == 2:
    data_inicial, data_final = data_range
else:
    st.error("Selecione um intervalo de datas válido.")
    st.stop()

# 🔍 Filtra por intervalo de datas
df_filtrado = df[
    (df["DATA INICIAL"].dt.date >= data_inicial) &
    (df["DATA INICIAL"].dt.date <= data_final)
].copy()
df_ads_filtrado = df_ads[
    (df_ads["Data"].dt.date >= data_inicial) &
    (df_ads["Data"].dt.date <= data_final)
].copy()

# Força datas como string para merge
df_filtrado.loc[:, "Data"] = df_filtrado["DATA INICIAL"].dt.strftime("%Y-%m-%d")
df_ads_filtrado.loc[:, "Data"] = df_ads_filtrado["Data"].dt.strftime("%Y-%m-%d")

# Agrupamento de abandonos por dia
abandonos_dia = df_filtrado.groupby("Data").size().reset_index(name="Abandonos")

# Merge e ajuste para datetime
dados_merged = pd.merge(df_ads_filtrado, abandonos_dia, on="Data", how="left").fillna({"Abandonos": 0})
dados_merged["Data"] = pd.to_datetime(dados_merged["Data"])

# 📊 KPIs
valor_total = df_filtrado["VALOR"].sum()
ticket_medio = df_filtrado["VALOR"].mean()
total_abandonos = df_filtrado.shape[0]

st.title("📦 Dashboard de Carrinhos Abandonados")

col1, col2, col3 = st.columns(3)
col1.metric("💰 Valor Total Abandonado", f"R$ {valor_total:,.2f}")
col2.metric("🧾 Ticket Médio", f"R$ {ticket_medio:,.2f}")
col3.metric("🛒 Total de Abandonos", total_abandonos)

st.divider()

# 📈 Gráfico: Abandonos vs Investimento
st.subheader("📅 Abandonos vs Investimento Meta Ads")

fig = px.bar(
    dados_merged, x="Data", y="Abandonos", text="Abandonos",
    labels={"Data": "Data", "Abandonos": "Carrinhos Abandonados"},
    title="📊 Carrinhos Abandonados por Dia com Investimento",
    color_discrete_sequence=["#1f77b4"]
)

fig.add_scatter(
    x=dados_merged["Data"],
    y=dados_merged["Investimento"],
    name="Investimento (Meta Ads)",
    mode="lines+markers+text",
    text=[f"R$ {v:,.2f}" for v in dados_merged["Investimento"]],
    textposition="top center",
    yaxis="y2"
)

for trace in fig.data:
    if trace.type == "bar":
        trace.textposition = "outside"

fig.update_layout(
    xaxis_tickformat="%d/%m",
    yaxis_title="Abandonos",
    yaxis2=dict(
        title="Investimento (R$)",
        overlaying="y",
        side="right",
        showgrid=False
    ),
    margin=dict(t=50, b=40, l=0, r=0),
    height=450,
    template="simple_white"
)

st.plotly_chart(fig, use_container_width=True)

# 🔎 Debug opcional
with st.expander("📋 Dados combinados (debug)"):
    st.dataframe(dados_merged)

# 🥧 Etapas de abandono
st.subheader("🥧 Distribuição das Etapas de Abandono")
etapas = df_filtrado["ABANDONOU EM"].value_counts().reset_index()
etapas.columns = ["Etapa", "Quantidade"]
fig_pie = px.pie(etapas, names="Etapa", values="Quantidade", hole=0.4)
st.plotly_chart(fig_pie, use_container_width=True)

# 💰 Simulador de recuperação
st.subheader("📊 Simulador de Receita Recuperável")
meta = st.slider("Taxa de recuperação esperada (%)", 0, 100, 25, step=5)
valor_recuperado = valor_total * (meta / 100)
st.success(f"🔄 Recuperando {meta}% → **R$ {valor_recuperado:,.2f}**")

# 🧠 Reflexão
st.subheader("🧠 Perguntas Estratégicas para o Time de Marketing")
st.markdown("""
1. **Qual etapa está gerando mais perda de receita?**  
2. **Estamos priorizando os carrinhos de maior valor?**  
3. **Há relação entre aumento de investimento e abandono?**  
4. **Quais testes A/B podem melhorar o funil?**
""")
