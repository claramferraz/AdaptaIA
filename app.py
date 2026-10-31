import streamlit as st
from mediador_neuroinclusivo import MediadorNeuroInclusivo, Perfil, Preferencias

perfis = st.multiselect("Perfis", [p.value for p in Perfil], default=["geral"])
limite = st.number_input("Limite de palavras (0 = sem limite)", 0, 500, 0)
tom = st.selectbox("Tom", ["acolhedor", "neutro", "formal"])
pedido = st.text_area("O que você precisa pedir à IA?")

if st.button("Gerar prompt") and pedido.strip():
    prefs = Preferencias(
        perfis=[Perfil(p) for p in perfis] or [Perfil.GERAL],
        max_palavras=limite or None,
        tom=tom,
    )
    prompt = MediadorNeuroInclusivo(prefs).gerar_prompt(pedido)
    st.code(prompt, language=None)