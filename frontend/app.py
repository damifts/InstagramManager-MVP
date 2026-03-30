import os
from typing import Any

import httpx
import streamlit as st


DEFAULT_API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")


st.set_page_config(
    page_title="Social Manager Client",
    page_icon="📣",
    layout="wide",
)


def inizializza_stato() -> None:
    valori_default = {
        "api_base": DEFAULT_API_BASE,
        "ultimo_user_id": "",
        "ultimo_creation_id": "",
        "ultima_risposta": None,
        "ultima_azione": "Nessuna",
    }
    for chiave, valore in valori_default.items():
        if chiave not in st.session_state:
            st.session_state[chiave] = valore


inizializza_stato()


def call_api(method: str, api_base: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    with httpx.Client(timeout=20.0) as client:
        response = client.request(method=method, url=f"{api_base}{path}", json=payload)
        response.raise_for_status()
        if response.headers.get("content-type", "").startswith("application/json"):
            return response.json()
        return {"raw": response.text}


def salva_risposta(nome_azione: str, dati: dict[str, Any]) -> None:
    st.session_state.ultima_azione = nome_azione
    st.session_state.ultima_risposta = dati


def azione_profilo() -> None:
    profilo = call_api("GET", st.session_state.api_base, "/api/profile")
    if isinstance(profilo, dict):
        user_id = profilo.get("user_id") or profilo.get("id")
        if user_id:
            st.session_state.ultimo_user_id = str(user_id)
    salva_risposta("GET /api/profile", profilo)


def azione_crea_media(url_risorsa: str, caption: str, user_id: str) -> None:
    payload = {
        "url_risorsa": url_risorsa,
        "caption": caption,
        "user_id": user_id,
    }
    risultato = call_api("POST", st.session_state.api_base, "/api/createPost", payload)
    if isinstance(risultato, dict):
        creation_id = risultato.get("id") or risultato.get("creation_id")
        if creation_id:
            st.session_state.ultimo_creation_id = str(creation_id)
    if user_id:
        st.session_state.ultimo_user_id = user_id
    salva_risposta("POST /api/createPost", risultato)


def azione_pubblica_media(user_id: str, creation_id: str) -> None:
    payload = {
        "user_id": user_id,
        "creation_id": creation_id,
    }
    risultato = call_api("POST", st.session_state.api_base, "/api/PostMedia", payload)
    if user_id:
        st.session_state.ultimo_user_id = user_id
    if creation_id:
        st.session_state.ultimo_creation_id = creation_id
    salva_risposta("POST /api/PostMedia", risultato)


def header_dashboard() -> None:
    st.title("Social Manager Client")
    st.caption("Pannello rapido per lavorare con il backend Instagram")

    col1, col2, col3 = st.columns(3)
    col1.metric("Backend", st.session_state.api_base)
    col2.metric("User ID", st.session_state.ultimo_user_id or "-")
    col3.metric("Creation ID", st.session_state.ultimo_creation_id or "-")


def pannello_sidebar() -> None:
    with st.sidebar:
        st.subheader("Workspace")
        api_base = st.text_input("Backend URL", value=st.session_state.api_base)
        st.session_state.api_base = api_base.rstrip("/")

        st.divider()
        azione = st.radio("Azione", ["Profilo", "Crea media", "Pubblica media"])

        if azione == "Profilo":
            if st.button("Recupera profilo", use_container_width=True):
                try:
                    azione_profilo()
                    st.success("Profilo recuperato")
                except Exception as exc:
                    st.error(f"Errore: {exc}")

        if azione == "Crea media":
            url_risorsa = st.text_input("URL risorsa")
            caption = st.text_area("Caption", height=120)
            user_id = st.text_input("User ID", value=st.session_state.ultimo_user_id)
            if st.button("Crea media", use_container_width=True):
                try:
                    azione_crea_media(url_risorsa, caption, user_id)
                    st.success("Media creata")
                except Exception as exc:
                    st.error(f"Errore: {exc}")

        if azione == "Pubblica media":
            user_id_pub = st.text_input("User ID", value=st.session_state.ultimo_user_id, key="user_id_pub")
            creation_id = st.text_input("Creation ID", value=st.session_state.ultimo_creation_id)
            if st.button("Pubblica media", use_container_width=True):
                try:
                    azione_pubblica_media(user_id_pub, creation_id)
                    st.success("Media pubblicata")
                except Exception as exc:
                    st.error(f"Errore: {exc}")


def pannello_contenuto() -> None:
    tab_operativo, tab_output = st.tabs(["Operativo", "Risposta API"])

    with tab_operativo:
        st.write("Usa la sidebar per eseguire le azioni principali del flusso social.")
        st.write("Flusso consigliato: Profilo -> Crea media -> Pubblica media.")

    with tab_output:
        if st.session_state.ultima_risposta is None:
            st.info("Nessuna chiamata eseguita.")
        else:
            st.write(st.session_state.ultima_azione)
            st.json(st.session_state.ultima_risposta)


header_dashboard()
pannello_sidebar()
pannello_contenuto()
st.caption("Endpoint: /api/profile, /api/createPost, /api/PostMedia")
