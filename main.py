# pandas
# streamlit
# openpyxl

# no computador de voces
# pip install streamlit pandas openpyxl

# streamlit run main.py

import pandas as pd
import streamlit as st

# import streamlit as st
# import pandas as pd

# IMPORTANTE!
# SISTEMA DE LOGIN ANTES DE ENTRAR NO DASH 


# SENHA PADARAO
SENHA_CORRETA = "TitanFinanceir0123"  

# LOGIN
if "logado" not in st.session_state:
    st.session_state.logado = False

# SE AINDA NAO ESTIVER LOGADO MOSTRA TELA DE LOGIN
if not st.session_state.logado:
    st.title("🔒 Acesso Restrito")
    senha = st.text_input("Digite a senha para acessar o Dashboard Titan:", type="password")
    if st.button("Entrar"):
        if senha == SENHA_CORRETA:
            st.session_state.logado = True
            st.success("Login realizado com sucesso! ✅")
            st.rerun()  # recarrega para mostrar o dashboard
        else:
            st.error("Senha incorreta ❌")
    st.stop()  # Interrompe


# LOGADO

st.success("🔓 Acesso liberado!")



# AGORA CODIGOS DENTRO DO DASH APOS LOGIN


# IMPORTACAO

# tabela = pd.read_excel("dados 3.xlsx") TABELA ANTIGA SETEMBRO

# TABELA COM NOVAS METRICAS SETEMBRO/OUTUBRO
tabela = pd.read_excel("Acompanhamento de Metas.xlsx")

st.title("DashBoard Financeiro Titan")
st.subheader("Acompanhamento de Metas")


# remove espacos extras nos nomes das colunas
tabela.columns = tabela.columns.str.strip()

# converte colunas de valores para número
for col in ["Faturamento", "Custo", "Profit"]:
    tabela[col] = (
        tabela[col]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
        .replace("", "0")
        .astype(float)
    )


# Filtrar para a selecao de campo de escolha 

semana = st.multiselect("Selecione Qual Semana Deseja", tabela["Minisquad"].unique())
datas = st.multiselect("Selecione Qual Data Deseja", tabela["Data"].unique())
responsavel = st.multiselect("Selecione Qual Responsavel Deseja", tabela["Responsavel"].unique())
fonte = st.multiselect("Selecione Qual Fonte Deseja", tabela["Fonte"].unique())

if semana:
    tabela = tabela[tabela["Minisquad"].isin(semana)]
if datas:
    tabela = tabela[tabela["Data"].isin(datas)]
if responsavel:
    tabela = tabela[tabela["Responsavel"].isin(responsavel)]
if fonte:
    tabela = tabela[tabela["Fonte"].isin(fonte)]

# COLOCAR POR MES JA QUE AGORA VAO TER TODOS OS MESES 

# converter a coluna de datas para datetime
tabela["Data"] = pd.to_datetime(tabela["Data"], format="%d/%m/%Y", errors="coerce")

# cria uma nova coluna com o nome do mes e ano
tabela["Mês"] = tabela["Data"].dt.strftime("%B/%Y")  # ex: Outubro/2025, Setembro/2026

# FILTRAR PARA SELECAO DE CAMPO DE ESCOLHA
mes = st.multiselect("Selecione Qual Mês Deseja", tabela["Mês"].unique())

if mes:
    tabela = tabela[tabela["Mês"].isin(mes)]

# METRICAS GERIAS, faturamento, custo, profit, ROI

faturamento_total = tabela["Faturamento"].sum()
custo_total = tabela["Custo"].sum()
profit_total = tabela["Profit"].sum()
roi_total = (profit_total / custo_total) * 100 if custo_total != 0 else 0

# ticket medio so para Profit e ROI
ticket_medio_profit = tabela["Profit"].mean()
ticket_medio_roi = ((tabela["Profit"] / tabela["Custo"]).replace([float("inf"), -float("inf")], 0)).mean() * 100

st.subheader("Métricas Gerais")

# empilhadas com valores sem virgula
st.metric("Faturamento Total", f"${faturamento_total:,.0f}")
st.metric("Custo Total", f"${custo_total:,.0f}")
st.metric("Profit Total", f"${profit_total:,.0f}")
st.metric("ROI Total", f"{roi_total:.2f}%")

st.metric("Ticket Médio (Profit)", f"${ticket_medio_profit:,.0f}")
st.metric("Ticket Médio (ROI)", f"{ticket_medio_roi:.2f}%")



# METRICAS DATAS

roi_datas = (
    tabela.groupby("Data")[["Profit", "Custo"]]
    .sum()
    .assign(ROI=lambda x: (x["Profit"] / x["Custo"]) * 100)
)

dados_datas = (
    tabela.groupby("Data")[["Faturamento", "Custo", "Profit"]]
    .sum()
    .join(roi_datas["ROI"])
)

st.subheader("Métricas por Data")
st.dataframe(dados_datas)  # mostra os totais por data
st.line_chart(dados_datas)


# METRICAS SEMANA

roi_semanas = (
    tabela.groupby("Minisquad")[["Profit", "Custo"]]
    .sum()
    .assign(ROI=lambda x: (x["Profit"] / x["Custo"]) * 100)
)

dados_semanas = (
    tabela.groupby("Minisquad")[["Faturamento", "Custo", "Profit"]]
    .sum()
    .join(roi_semanas["ROI"])
)

st.subheader("Métricas por Semana")
st.dataframe(dados_semanas)  # mostra os totais por semana
st.line_chart(dados_semanas)



# RESPONSAVEIS

dados_responsavel = (
    tabela.groupby("Responsavel")[["Faturamento", "Custo", "Profit"]]
    .sum()
)

roi_responsavel = (
    tabela.groupby("Responsavel")[["Profit", "Custo"]]
    .sum()
    .assign(ROI=lambda x: (x["Profit"] / x["Custo"]) * 100)
)


dados_responsavel = dados_responsavel.join(roi_responsavel["ROI"])


st.subheader("Comparação entre Responsáveis")
st.dataframe(dados_responsavel)


st.line_chart(dados_responsavel)



# LUCRO/PROFIT POR RESPONSÁVEL RANKEADO


st.subheader("Lucro/Profit por Responsável")

lucro_responsavel = (
    tabela.groupby("Responsavel")[["Profit"]]
    .sum()
    .sort_values(by="Profit", ascending=False)
)

st.dataframe(lucro_responsavel)  # tabela organizada
st.bar_chart(lucro_responsavel)  # ranking em grafico barras, podem trocar por linhas caso quiserem


# FONTE MAIS LUCRATIVA E MENOS LUCRATIVA

lucro_fonte = (
    tabela.groupby("Fonte")[["Profit"]]
    .sum()
    .sort_values(by="Profit", ascending=False)
)

st.subheader("Fontes Lucrativas e Prejuízos")
st.write("🔹 **Top 3 Fontes Mais Lucrativas:**")
st.dataframe(lucro_fonte.head(3))

st.write("🔻 **Top 3 Fontes Menos Lucrativas:**")
st.dataframe(lucro_fonte.tail(3))


# RANK DOS MELHORES E PIORES RESPONSAVEIS

st.subheader("Ranking de Responsáveis")

st.write("🏅 **Top 3 Responsáveis:**")
st.dataframe(lucro_responsavel.head(3))

st.write("💀 **Piores 3 Responsáveis:**")
st.dataframe(lucro_responsavel.tail(3))


# FONTES

st.subheader("Métricas por Fonte")

for f in tabela["Fonte"].unique():
    st.markdown(f"### Fonte: {f}")
    fonte_df = tabela[tabela["Fonte"] == f]

    dados_fonte = (
        fonte_df.groupby("Data")[["Faturamento", "Custo", "Profit"]]
        .sum()
    )
    roi_fonte = (
        fonte_df.groupby("Data")[["Profit", "Custo"]]
        .sum()
        .assign(ROI=lambda x: (x["Profit"] / x["Custo"]) * 100)
    )
    dados_fonte = dados_fonte.join(roi_fonte["ROI"])

    st.line_chart(dados_fonte)


















