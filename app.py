import streamlit as st
import pandas as pd

st.set_page_config(page_title="Horas Complementares", layout="wide")
st.title("Dashboard de Horas Complementares")

TOTAL_HORAS = 240


# Pontuação das atividades
pontuacao = {
    # Ensino
    "Disciplina": {"tipo": "carga", "max": 120},
    "Curso de Língua": {"tipo": "carga", "max": 60},

    # Pesquisa - cursos
    "Curso": {"tipo": "curso", "max": 20},

    # Pesquisa - eventos
    "Congresso": {"tipo": "multiplicador", "valor": 5, "max": 30},
    "Seminário": {"tipo": "multiplicador", "valor": 1, "max": 30},
    "Organização de Evento": {"tipo": "multiplicador", "valor": 10, "max": 30},

    # Pesquisa - pôster
    "Pôster Local": {"tipo": "multiplicador", "valor": 5, "max": 20},
    "Pôster Regional": {"tipo": "multiplicador", "valor": 10, "max": 20},
    "Pôster Nacional": {"tipo": "multiplicador", "valor": 15, "max": 30},
    "Pôster Internacional": {"tipo": "multiplicador", "valor": 20, "max": 40},

    # Pesquisa - Publicação
    "Artigo": {"tipo": "multiplicador", "valor": 60, "max": 120},
    "Livro": {"tipo": "multiplicador", "valor": 60, "max": 120},
    "Capítulo de Livro": {"tipo": "multiplicador", "valor": 30, "max": 60},

    # Pesquisa - Projeto
    "Projeto de Pesquisa": {"tipo": "multiplicador", "valor": 30, "max": 60},

    # Extensão
    "Monitoria": {"tipo": "multiplicador", "valor": 30, "max": 60},
    "Estágio": {"tipo": "multiplicador", "valor": 30, "max": 60},
    "Empresa Júnior": {"tipo": "multiplicador", "valor": 30, "max": 60},
    "Representante": {"tipo": "multiplicador", "valor": 5, "max": 20},
}


# Função de Cálculo de Horas
def calcular_horas(tipo, carga, quantidade):
    regra = pontuacao[tipo]

    if regra["tipo"] == "carga":
        return carga

    if regra["tipo"] == "multiplicador":
        return regra["valor"] * quantidade

    if regra["tipo"] == "curso":
        if carga <= 10:
            return 5
        elif carga <= 20:
            return 10
        elif carga <= 30:
            return 15
        else:
            return 20

    return 0


# Session State
if "dados" not in st.session_state:
    st.session_state["dados"] = pd.DataFrame(columns=[
        "Atividade", "Categoria", "Tipo", "Carga Certificado",
        "Quantidade", "Carga Aproveitada"
    ])


# Input de atividades
st.subheader("Adicionar atividade")

col1, col2, col3 = st.columns(3)

with col1:
    atividade = st.text_input("Nome da atividade")

with col2:
    categoria = st.selectbox("Categoria", ["Ensino", "Pesquisa", "Extensão"])

with col3:
    carga = st.number_input("Carga horária (certificado)", min_value=0)

# Tipos dinâmicos
if categoria == "Ensino":
    opcoes = ["Disciplina", "Curso de Língua"]

elif categoria == "Pesquisa":
    opcoes = [
        "Curso",
        "Congresso",
        "Seminário",
        "Organização de Evento",
        "Projeto de Pesquisa",
        "Pôster Local",
        "Pôster Regional",
        "Pôster Nacional",
        "Pôster Internacional",
        "Artigo",
        "Livro",
        "Capítulo de Livro"
    ]

elif categoria == "Extensão":
    opcoes = [
        "Monitoria",
        "Estágio",
        "Empresa Júnior",
        "Representante"
    ]

tipo = st.selectbox("Tipo", opcoes)

quantidade = st.number_input("Quantidade (ex: semestres/eventos)", min_value=1, value=1)


# ADICIONAR
if st.button("Adicionar"):
    carga_calc = calcular_horas(tipo, carga, quantidade)

    total_tipo = st.session_state["dados"][
        st.session_state["dados"]["Tipo"] == tipo
    ]["Carga Aproveitada"].sum()

    limite = pontuacao[tipo]["max"]

    if total_tipo + carga_calc > limite:
        carga_calc = max(limite - total_tipo, 0)
        st.warning(f"Limite atingido para {tipo}. Ajustado automaticamente.")

    novo = pd.DataFrame([{
        "Atividade": atividade,
        "Categoria": categoria,
        "Tipo": tipo,
        "Carga Certificado": carga,
        "Quantidade": quantidade,
        "Carga Aproveitada": carga_calc
    }])

    st.session_state["dados"] = pd.concat(
        [st.session_state["dados"], novo],
        ignore_index=True
    )


# TABELA
st.subheader("Suas atividades")
st.dataframe(st.session_state["dados"], width="stretch")


# MÉTRICAS
total = st.session_state["dados"]["Carga Aproveitada"].sum()
faltam = max(TOTAL_HORAS - total, 0)
progresso = total / TOTAL_HORAS

st.subheader("Progresso")

col1, col2, col3 = st.columns(3)

col1.metric("Horas acumuladas", f"{total}h")
col2.metric("Horas restantes", f"{faltam}h")
col3.metric("Progresso", f"{progresso*100:.1f}%")

st.progress(min(progresso, 1.0))

