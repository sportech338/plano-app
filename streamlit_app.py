import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Carrinhos Abandonados", layout="wide")

# 📥 Planilhas Google Sheets como CSV
csv_abandono_url = "https://docs.google.com/spreadsheets/d/1OBKs2RpmRNqHDn6xE3uMOU-bwwnO_JY1ZhqctZGpA3E/export?format=csv"
csv_investimento_url = "https://docs.google.com/spreadsheets/d/1JYHDnY8ykyklYELm2m5Wq7YaTs3CKPmecLjB3lDyBTI/export?format=csv"

@st.cache_data
def load_data():
    df_abandono = pd.read_csv(csv_abandono_url)
    df_abandono["DATA INICIAL"] = pd.to_datetime(df_abandono["DATA INICIAL"], errors="coerce")
    df_abandono["VALOR"] = df_abandono["VALOR"].astype(str).str.replace(",", ".").astype(float)
    df_abandono.dropna(subset=["DATA INICIAL", "VALOR", "ABANDONOU EM"], inplace=True)

    df_invest = pd.read_csv(csv_investimento_url)
    df_invest["Data"] = pd.to_datetime(df_invest["Data"], errors="coerce")
    df_invest["Investimento"] = df_invest["Investimento"].astype(str).str.replace(",", ".").astype(float)
    df_invest = df_invest[["Data", "Investimento"]].dropna()

    return df_abandono, df_invest

df, df_ads = load_data()

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

# 🎯 Aplica filtro
df_filtrado = df[(df["DATA INICIAL"] >= pd.to_datetime(data_inicial)) & (df["DATA INICIAL"] <= pd.to_datetime(data_final))]
df_ads_filtrado = df_ads[(df_ads["Data"] >= pd.to_datetime(data_inicial)) & (df_ads["Data"] <= pd.to_datetime(data_final))]

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

# 📈 Abandonos por dia + Investimento
st.subheader("📅 Abandonos vs Investimento Meta Ads")

abandonos_dia = (
    df_filtrado.groupby(df_filtrado["DATA INICIAL"].dt.date)
    .size()
    .reset_index(name="Abandonos")
    .rename(columns={"DATA INICIAL": "Data"})
)

dados_merged = pd.merge(abandonos_dia, df_ads_filtrado, on="Data", how="left").fillna(0)

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
    mode="lines+markers",
    yaxis="y2"
)

fig.update_traces(textposition="outside")
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
