import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Carrinhos Abandonados", layout="wide")

# 📥 Lê direto do Google Sheets publicado como CSV
csv_url = "https://docs.google.com/spreadsheets/d/1OBKs2RpmRNqHDn6xE3uMOU-bwwnO_JY1ZhqctZGpA3E/export?format=csv"

@st.cache_data
def load_data():
    df = pd.read_csv(csv_url)
    df["DATA INICIAL"] = pd.to_datetime(df["DATA INICIAL"], errors="coerce")
    df["VALOR"] = df["VALOR"].astype(str).str.replace(",", ".").astype(float)
    df.dropna(subset=["DATA INICIAL", "VALOR", "ABANDONOU EM"], inplace=True)
    return df

df = load_data()

# KPIs
valor_total = df["VALOR"].sum()
ticket_medio = df["VALOR"].mean()
total_abandonos = df.shape[0]

st.title("📦 Dashboard de Carrinhos Abandonados")

col1, col2, col3 = st.columns(3)
col1.metric("💰 Valor Total Abandonado", f"R$ {valor_total:,.2f}")
col2.metric("🧾 Ticket Médio", f"R$ {ticket_medio:,.2f}")
col3.metric("🛒 Total de Abandonos", total_abandonos)

st.divider()

# Gráfico de abandonos por dia
st.subheader("📅 Abandonos por Dia")
abandonos_dia = df.groupby(df["DATA INICIAL"].dt.date).size()
fig, ax = plt.subplots()
ax.bar(abandonos_dia.index, abandonos_dia.values, color='skyblue')
ax.set_title("Carrinhos Abandonados por Dia")
plt.xticks(rotation=45)
st.pyplot(fig)

# Etapas de abandono
st.subheader("🚧 Etapas de Abandono")
etapas = df["ABANDONOU EM"].value_counts()
fig2, ax2 = plt.subplots()
ax2.barh(etapas.index, etapas.values, color='salmon')
ax2.invert_yaxis()
ax2.set_title("Etapas mais críticas")
st.pyplot(fig2)

# Simulações de recuperação
st.subheader("💰 Simulação de Receita Recuperável")
col4, col5, col6 = st.columns(3)
col4.metric("Recuperando 10%", f"R$ {valor_total * 0.10:,.2f}")
col5.metric("Recuperando 25%", f"R$ {valor_total * 0.25:,.2f}")
col6.metric("Recuperando 40%", f"R$ {valor_total * 0.40:,.2f}")

# Estratégia
st.subheader("🎯 Perguntas Estratégicas")
st.markdown("""
1. **Qual etapa está gerando mais perda de receita?**  
2. **Estamos priorizando os carrinhos de maior valor?**  
3. **Quais testes A/B podem melhorar o funil?**
""")
