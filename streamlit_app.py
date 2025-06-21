import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Carrinhos Abandonados", layout="wide")

# 📥 Planilhas CSV
csv_abandono_url = "https://docs.google.com/spreadsheets/d/1OBKs2RpmRNqHDn6xE3uMOU-bwwnO_JY1ZhqctZGpA3E/export?format=csv"
csv_base_dados_url = "https://docs.google.com/spreadsheets/d/1JYHDnY8ykyklYELm2m5Wq7YaTs3CKPmecLjB3lDyBTI/export?format=csv&gid=1860131802"

@st.cache_data
def load_data():
    df_abandono = pd.read_csv(csv_abandono_url)
    df_abandono["DATA INICIAL"] = pd.to_datetime(df_abandono["DATA INICIAL"], errors="coerce")
    df_abandono["VALOR"] = df_abandono["VALOR"].astype(str).str.replace(",", ".").astype(float)
    df_abandono.dropna(subset=["DATA INICIAL", "VALOR", "ABANDONOU EM"], inplace=True)
    return df_abandono

@st.cache_data
def load_investimentos():
    df_ads = pd.read_csv(csv_base_dados_url, names=["Data", "Gasto"], header=None)
    df_ads["Data"] = pd.to_datetime(df_ads["Data"], format="%d/%m/%Y", errors="coerce")
    df_ads["Investimento"] = pd.to_numeric(
        df_ads["Gasto"].astype(str).str.replace(".", "", regex=False).str.replace(",", "."),
        errors="coerce"
    )
    df_ads = df_ads.dropna(subset=["Data", "Investimento"])
    return df_ads

# 📦 Dados
df = load_data()
df_ads = load_investimentos()

# 🎯 Filtro de datas
st.sidebar.header("📅 Filtro de Período")
data_min = df["DATA INICIAL"].min()
data_max = df["DATA INICIAL"].max()

datas = st.sidebar.date_input(
    "Selecionar intervalo:",
    [data_min, data_max],
    min_value=data_min,
    max_value=data_max
)

# ✅ Garante que o intervalo seja válido
if isinstance(datas, tuple) and len(datas) == 2:
    data_inicial, data_final = datas
else:
    st.error("Por favor, selecione um intervalo de datas válido.")
    st.stop()

# 🔍 Filtragem
df_filtrado = df[
    (df["DATA INICIAL"] >= pd.to_datetime(data_inicial)) &
    (df["DATA INICIAL"] <= pd.to_datetime(data_final))
].copy()

df_ads_filtrado = df_ads[
    (df_ads["Data"] >= pd.to_datetime(data_inicial)) &
    (df_ads["Data"] <= pd.to_datetime(data_final))
].copy()

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

# 📈 Gráfico: Abandonos por Dia
st.subheader("📅 Carrinhos Abandonados por Dia")

df_filtrado["DataFormatada"] = pd.to_datetime(df_filtrado["DATA INICIAL"].dt.date)

abandonos_dia = (
    df_filtrado.groupby("DataFormatada")
    .size()
    .reset_index(name="Abandonos")
    .sort_values("DataFormatada")
)

fig = px.bar(
    abandonos_dia,
    x=abandonos_dia["DataFormatada"].dt.strftime("%d/%m"),
    y="Abandonos",
    text="Abandonos",
    labels={"DataFormatada": "Data", "Abandonos": "Carrinhos Abandonados"},
    title="📊 Carrinhos Abandonados por Dia",
    color_discrete_sequence=["#1f77b4"]
)

fig.update_traces(textposition="outside")
fig.update_layout(
    xaxis_tickformat="%d/%m",
    yaxis_title="Abandonos",
    bargap=0.2,
    margin=dict(t=50, b=40, l=0, r=0),
    height=450,
    template="simple_white"
)

st.plotly_chart(fig, use_container_width=True)

# 💸 Investimento Diário
st.subheader("💸 Investimento Diário em Anúncios (Meta Ads)")

df_ads_filtrado["Data"] = pd.to_datetime(df_ads_filtrado["Data"]).dt.date
df_ads_filtrado["Data"] = pd.to_datetime(df_ads_filtrado["Data"])

investimento_por_dia = (
    df_ads_filtrado
    .groupby("Data")["Investimento"]
    .sum()
    .reset_index()
    .sort_values("Data")
)

fig_invest = px.line(
    investimento_por_dia,
    x=investimento_por_dia["Data"].dt.strftime("%d/%m"),
    y="Investimento",
    markers=True,
    title="📈 Investimento por Dia",
    labels={"Data": "Data", "Investimento": "Valor Investido (R$)"}
)

fig_invest.update_layout(
    template="simple_white",
    height=400,
    margin=dict(t=50, b=40, l=0, r=0)
)

st.plotly_chart(fig_invest, use_container_width=True)

# 🥧 Etapas de abandono
st.subheader("🥧 Distribuição das Etapas de Abandono")
etapas = df_filtrado["ABANDONOU EM"].value_counts().reset_index()
etapas.columns = ["Etapa", "Quantidade"]
fig_pie = px.pie(etapas, names="Etapa", values="Quantidade", hole=0.4)
fig_pie.update_traces(textinfo="percent+label")
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
3. **Há padrões de abandono ao longo da semana?**  
4. **Quais testes A/B podem melhorar o funil?**
""")

# 💾 Baixar dados filtrados
st.download_button(
    "⬇️ Baixar dados filtrados",
    df_filtrado.to_csv(index=False),
    file_name="dados_abandonos_filtrados.csv",
    mime="text/csv"
)
