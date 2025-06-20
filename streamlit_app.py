import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Carrinhos Abandonados", layout="wide")

# URL da planilha do Google Sheets exportada como CSV
csv_url = "https://docs.google.com/spreadsheets/d/1OBKs2RpmRNqHDn6xE3uMOU-bwwnO_JY1ZhqctZGpA3E/export?format=csv"

@st.cache_data
def load_data():
    df = pd.read_csv(csv_url)
    df["DATA INICIAL"] = pd.to_datetime(df["DATA INICIAL"], errors="coerce")
    df["VALOR"] = df["VALOR"].astype(str).str.replace(",", ".").astype(float)
    df.dropna(subset=["DATA INICIAL", "VALOR", "ABANDONOU EM"], inplace=True)
    return df

df = load_data()

# Filtro de datas
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

# KPIs com base no filtro
valor_total = df_filtrado["VALOR"].sum()
ticket_medio = df_filtrado["VALOR"].mean()
total_abandonos = df_filtrado.shape[0]

st.title("📦 Dashboard de Carrinhos Abandonados")

col1, col2, col3 = st.columns(3)
col1.metric("💰 Valor Total Abandonado", f"R$ {valor_total:,.2f}")
col2.metric("🧾 Ticket Médio", f"R$ {ticket_medio:,.2f}")
col3.metric("🛒 Total de Abandonos", total_abandonos)

st.divider()

# Gráfico de abandonos por dia
st.subheader("📅 Abandonos por Dia")
abandonos_dia = df_filtrado.groupby(df_filtrado["DATA INICIAL"].dt.date).size()
fig, ax = plt.subplots()
ax.bar(abandonos_dia.index, abandonos_dia.values, color='skyblue')
ax.set_title("Carrinhos Abandonados por Dia")
plt.xticks(rotation=45)
st.pyplot(fig)

# Etapas de abandono
st.subheader("🚧 Etapas de Abandono")
etapas = df_filtrado["ABANDONOU EM"].value_counts()
fig2, ax2 = plt.subplots()
ax2.pie(etapas.values, labels=etapas.index, autopct='%1.1f%%', startangle=90)
ax2.axis('equal')
ax2.set_title("Distribuição das Etapas de Abandono")
st.pyplot(fig2)

# Simulador de recuperação
st.subheader("💰 Simulação de Receita Recuperável")
meta = st.slider("Taxa de recuperação esperada (%)", 0, 100, 25, step=5)
valor_recuperado = valor_total * (meta / 100)

st.success(f"🔄 Recuperando {meta}% → **R$ {valor_recuperado:,.2f}**")

# Estratégia
st.subheader("🎯 Perguntas Estratégicas")
st.markdown("""
1. **Qual etapa está gerando mais perda de receita?**  
2. **Estamos priorizando os carrinhos de maior valor?**  
3. **Quais testes A/B podem melhorar o funil?**
""")
