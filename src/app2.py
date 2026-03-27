import json
import pandas as pd
import streamlit as st

# ========= CARREGAR DADOS ========= #
perfil = json.load(open("./data/perfil_investidor.json"))
transacoes = pd.read_csv('./data/transacoes.csv')
historico = pd.read_csv('./data/historico_atendimento.csv')
produtos = json.load(open('./data/produtos_financeiros.json'))

# ========= ANÁLISE FINANCEIRA ========= #

receitas = transacoes[transacoes['tipo'] == 'receita']['valor'].sum()
despesas = transacoes[transacoes['tipo'] == 'despesa']['valor'].sum()

saldo = receitas - despesas

# Taxa de poupança
taxa_poupanca = saldo / receitas if receitas > 0 else 0

# Reserva em meses
reserva_meses = perfil['reserva_emergencia_atual'] / despesas if despesas > 0 else 0

# Classificação de risco
if taxa_poupanca < 0:
    risco = "ALTO"
elif taxa_poupanca < 0.2:
    risco = "MÉDIO"
else:
    risco = "BAIXO"

# ========= SIMULAÇÃO DE CENÁRIOS ========= #

cenarios = {
    "Crise": {
        "receitas": receitas * 0.7,
        "despesas": despesas * 1.1
    },
    "Estável": {
        "receitas": receitas,
        "despesas": despesas
    },
    "Crescimento": {
        "receitas": receitas * 1.2,
        "despesas": despesas * 1.05
    },
    "Perda de Renda": {
        "receitas": receitas * 0.3,
        "despesas": despesas
    }
}

simulacoes = {}

for nome, c in cenarios.items():
    saldo_cenario = c["receitas"] - c["despesas"]
    meses_reserva = perfil['reserva_emergencia_atual'] / c["despesas"] if c["despesas"] > 0 else 0

    simulacoes[nome] = {
        "saldo": round(saldo_cenario, 2),
        "reserva_meses": round(meses_reserva, 2)
    }

# ========= CONTEXTO INTELIGENTE ========= #

contexto = f"""
CLIENTE: {perfil['nome']}, {perfil['idade']} anos
PERFIL: {perfil['perfil_investidor']}
OBJETIVO: {perfil['objetivo_principal']}

RESUMO FINANCEIRO:
- Receitas: R$ {receitas:.2f}
- Despesas: R$ {despesas:.2f}
- Saldo: R$ {saldo:.2f}
- Taxa de poupança: {taxa_poupanca:.2%}
- Reserva de emergência: {reserva_meses:.1f} meses
- Nível de risco: {risco}

SIMULAÇÕES:
{json.dumps(simulacoes, indent=2, ensure_ascii=False)}

TRANSAÇÕES RECENTES:
{transacoes.to_string(index=False)}

ATENDIMENTOS ANTERIORES:
{historico.to_string(index=False)}
"""

# ========= PROMPT ESTRATÉGICO ========= #

SYSTEM_PROMPT = """Você é o Kaio, um analista financeiro estratégico.

OBJETIVO:
Ajudar o cliente a entender sua situação financeira e tomar decisões baseadas em risco e cenários econômicos.

O QUE VOCÊ DEVE FAZER:
- Analisar receitas, despesas e saldo
- Explicar o nível de risco
- Comparar cenários (crise, estável, crescimento, perda de renda)
- Mostrar impactos reais (sobrevivência financeira, reserva, etc.)
- Sugerir ações estratégicas (sem recomendar produtos específicos)

REGRAS:
- Linguagem simples e direta
- Máximo 4 parágrafos
- Use números reais do contexto
- Foque em decisão prática
- Sempre finalize perguntando se o usuário quer simular outro cenário
"""

# ========= FUNÇÃO DE PERGUNTA ========= #

def perguntar(msg):
    prompt = f"""
    CONTEXTO DO CLIENTE:
    {contexto}

    PERGUNTA:
    {msg}

    INSTRUÇÃO:
    Faça uma análise financeira estratégica considerando os cenários simulados.
    """

    from openai import AzureOpenAI

    client = AzureOpenAI(
        api_key="SUA_CHAVE_AQUI",
        api_version="2024-10-01-preview",
        azure_endpoint="https://SEU-ENDPOINT.openai.azure.com/"
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

# ========= INTERFACE STREAMLIT ========= #

st.title("📊 Edu - Analista Financeiro Inteligente")

# Mostrar indicadores principais
st.subheader("Resumo Financeiro")

col1, col2, col3 = st.columns(3)
col1.metric("Saldo", f"R$ {saldo:.2f}")
col2.metric("Taxa de Poupança", f"{taxa_poupanca:.2%}")
col3.metric("Risco", risco)

# Mostrar cenários
st.subheader("Simulação de Cenários")

df_cenarios = pd.DataFrame(simulacoes).T
st.dataframe(df_cenarios)

# Chat
st.subheader("Assistente Financeiro")

pergunta = st.chat_input("Pergunte sobre sua situação financeira...")

if pergunta:
    st.chat_message("user").write(pergunta)

    with st.spinner("Analisando cenários..."):
        resposta = perguntar(pergunta)

    st.chat_message("assistant").write(resposta)