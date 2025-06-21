import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Carrinhos Abandonados", layout="wide")

# URLs das planilhas
csv_abandono_url = "https://docs.google.com/spreadsheets/d/1OBKs2RpmRNqHDn6xE3uMOU-bwwnO_JY1ZhqctZGpA3E/export?format=csv"
csv_investimento_url = "https://docs.google.com/spreadsheets/d/1JYHDnY8ykyklYELm2m5Wq7YaTs3CKPmecLjB3lDyBTI/export?format=csv"

@st.cache_data
def load_data():
    df_abandono = pd.read_csv(csv_abandono_url)
    df_abandono["DATA INICIAL"] = pd.to_datetime(df_abandono["DATA INICIAL"], errors="coerce")
    df_abandono["VALOR"] = df_abandono["VALOR"].astype(str).str.replace(",", ".").astype(float)
    df_abandono.dropna(subset=["DATA INICIAL", "VALOR", "ABANDONOU EM"], inplace=True)

    df_ads = pd.read_csv(csv_investimento_url)
    df_ads["Data"] = pd.to_datetime(df_ads["Data"], dayfirst=True, errors="coerce")
    df_ads["Investimento"] = df_ads["Investimento"].astype(str).str.replace(",", ".").astype(float)

    return df_abandono, df_ads

df, df_ads = load_data()

# Filtro de período
st.sidebar.header("📅 Filtro de Período")
data_min = df["DATA INICIAL"].min()
data_max = df["DATA INICIAL"].max()

data_inicial, data_final = st.sidebar.date_input(
    "Selecionar intervalo:",
    [data_min, data_max],
    min_value=data_min,
    max_value=data_max
)

df_filtrado = df[(df["DATA INICIAL"] >= pd.to_datetime(data_inicial)) & (df["DATA INICIAL"] <= pd.to_datetime(data_final))]
df_ads_filtrado = df_ads[(df_ads["Data"] >= pd.to_datetime(data_inicial)) & (df_ads["Data"] <= pd.to_datetime(data_final))]

# KPIs
valor_total = df_filtrado["VALOR"].sum()
ticket_medio = df_filtrado["VALOR"].mean()
total_abandonos = df_filtrado.shape[0]
investimento_total = df_ads_filtrado["Investimento"].sum()

st.title("📦 Dashboard de Carrinhos Abandonados + Meta Ads")

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Valor Total Abandonado", f"R$ {valor_total:,.2f}")
col2.metric("🧾 Ticket Médio", f"R$ {ticket_medio:,.2f}")
col3.metric("🛒 Total de Abandonos", total_abandonos)
col4.metric("📣 Investimento no Período", f"R$ {investimento_total:,.2f}")

st.divider()

# Gráfico de abandonos por dia
st.subheader("📈 Abandonos por Dia")
abandono_diario = df_filtrado.groupby(df_filtrado["DATA INICIAL"].dt.date).size().reset_index(name="Abandonos")
invest_diario = df_ads_filtrado.groupby(df_ads_filtrado["Data"].dt.date).sum(numeric_only=True).reset_index()

df_merged = pd.merge(abandono_diario, invest_diario, left_on="DATA INICIAL", right_on="Data", how="left").fillna(0)

fig = px.bar(df_merged, x="DATA INICIAL", y="Abandonos", text="Abandonos", title="📅 Abandonos por Dia vs Investimento")
fig.add_scatter(x=df_merged["DATA INICIAL"], y=df_merged["Investimento"], mode="lines+markers", name="Investimento", yaxis="y2")

fig.update_layout(
    yaxis=dict(title="Abandonos"),
    yaxis2=dict(title="Investimento (R$)", overlaying="y", side="right"),
    xaxis_tickformat="%d/%m",
    margin=dict(t=50, b=40, l=0, r=0),
    height=450
)

st.plotly_chart(fig, use_container_width=True)

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
1. **Houve aumento de abandono em dias com maior investimento?**  
2. **Estamos obtendo ROI positivo nos dias com mais verba?**  
3. **Quais campanhas ativas nesses dias precisam de ajustes?**
""")
