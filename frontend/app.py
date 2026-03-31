import streamlit as st
import streamlit_antd_components as sac
from dotenv import load_dotenv

from services.api_client import DEFAULT_API_BASE, create_media, get_profile, publish_media
from services.gemini_service import generate_caption_and_hashtags


load_dotenv()

st.set_page_config(
    page_title="Instagram Planner Dashboard",
    page_icon="📅",
    layout="wide",
)


def init_state() -> None:
    defaults = {
        "api_base": DEFAULT_API_BASE,
        "menu": "Planner",
        "ultimo_user_id": "",
        "ultimo_creation_id": "",
        "ultima_risposta": None,
        "ultima_azione": "Nessuna",
        "ultimo_errore": "",
        "topic": "",
        "audience": "",
        "tone": "Professionale",
        "cta": "",
        "url_risorsa": "",
        "caption": "",
        "hashtags": [],
        "first_comment": "",
        "gemini_model": "gemini-1.5-flash",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def save_response(action: str, data: dict) -> None:
    st.session_state.ultima_azione = action
    st.session_state.ultima_risposta = data
    st.session_state.ultimo_errore = ""


def save_error(exc: Exception) -> None:
    st.session_state.ultimo_errore = str(exc)


def run_profile_sync() -> None:
    profile = get_profile(st.session_state.api_base)
    user_id = profile.get("user_id") or profile.get("id")
    if user_id:
        st.session_state.ultimo_user_id = str(user_id)
    save_response("GET /api/profile", profile)


def run_create_media() -> None:
    result = create_media(
        st.session_state.api_base,
        st.session_state.url_risorsa.strip(),
        st.session_state.caption.strip(),
        st.session_state.ultimo_user_id,
    )
    creation_id = result.get("id") or result.get("creation_id")
    if creation_id:
        st.session_state.ultimo_creation_id = str(creation_id)
    save_response("POST /api/createPost", result)


def run_publish_media() -> None:
    result = publish_media(
        st.session_state.api_base,
        st.session_state.ultimo_user_id,
        st.session_state.ultimo_creation_id,
    )
    save_response("POST /api/PostMedia", result)


def run_gemini_generation() -> None:
    generated = generate_caption_and_hashtags(
        topic=st.session_state.topic.strip(),
        audience=st.session_state.audience.strip(),
        tone=st.session_state.tone,
        cta=st.session_state.cta.strip(),
    )
    st.session_state.caption = generated["caption"]
    st.session_state.hashtags = generated["hashtags"]
    st.session_state.first_comment = generated["first_comment"]
    st.session_state.gemini_model = generated["model"]


def render_topbar() -> str:
    st.title("Instagram Content Planner")
    st.caption("Workflow stile planner: idea, copy, preview, publish")

    selected = sac.menu(
        [
            sac.MenuItem("Planner", icon="kanban"),
            sac.MenuItem("API Log", icon="journal-text"),
        ],
        index=["Planner", "API Log"].index(st.session_state.menu),
        variant="filled",
        color="blue",
        return_index=False,
        key="main_menu",
    )
    st.session_state.menu = selected or st.session_state.menu
    return selected


def render_metrics() -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Backend", st.session_state.api_base)
    c2.metric("User ID", st.session_state.ultimo_user_id or "-")
    c3.metric("Creation ID", st.session_state.ultimo_creation_id or "-")
    c4.metric("Gemini", st.session_state.gemini_model)


def render_composer_controls() -> None:
    with st.container(border=True):
        st.subheader("Controlli")
        st.session_state.api_base = st.session_state.api_base.rstrip("/")
        st.text_input("Backend URL", key="api_base")

        tabs = st.tabs(["Brief", "AI Caption", "Create Media", "Publish"])

        with tabs[0]:
            st.text_input(
                "Topic del contenuto",
                key="topic",
                placeholder="Lancio nuovo servizio, promo evento, guida prodotto...",
            )
            st.text_input(
                "Audience",
                key="audience",
                placeholder="PMI, creator, studenti...",
            )
            st.session_state.tone = st.selectbox(
                "Tone of voice",
                options=["Professionale", "Friendly", "Bold", "Educativo"],
                index=["Professionale", "Friendly", "Bold", "Educativo"].index(st.session_state.tone),
                key="tone_select",
            )
            st.text_input(
                "Call to Action",
                key="cta",
                placeholder="Scrivici in DM, visita il link in bio...",
            )

        with tabs[1]:
            with st.expander("Gemini settings", expanded=True):
                st.write("Modello: gemini-1.5-flash")
                st.caption("Richiede variabile ambiente GEMINI_API_KEY nel file .env")

            if st.button("Genera caption e hashtag", type="primary", use_container_width=True):
                if not st.session_state.topic.strip():
                    st.warning("Inserisci almeno il topic prima di generare.")
                else:
                    try:
                        with st.spinner("Gemini sta creando la proposta..."):
                            run_gemini_generation()
                        st.success("Proposta AI aggiornata")
                    except Exception as exc:
                        save_error(exc)
                        st.error(f"Errore Gemini: {exc}")

            st.text_area(
                "Caption finale",
                key="caption",
                height=180,
                placeholder="La caption comparira qui...",
            )
            st.text_area("First comment (opzionale)", key="first_comment", height=80)

        with tabs[2]:
            st.text_input(
                "URL immagine",
                key="url_risorsa",
                placeholder="https://example.com/post.jpg",
            )

            profile_col, create_col = st.columns(2)
            if profile_col.button("Sync profilo", use_container_width=True):
                try:
                    run_profile_sync()
                    st.success("Profilo sincronizzato")
                except Exception as exc:
                    save_error(exc)
                    st.error(f"Errore profilo: {exc}")

            if create_col.button("Crea media", use_container_width=True):
                if not st.session_state.url_risorsa.strip():
                    st.warning("Inserisci URL immagine")
                elif not st.session_state.ultimo_user_id:
                    st.warning("User ID mancante. Premi prima Sync profilo.")
                elif not st.session_state.caption.strip():
                    st.warning("Caption vuota. Generala o scrivila manualmente.")
                else:
                    try:
                        run_create_media()
                        st.success("Media creata")
                    except Exception as exc:
                        save_error(exc)
                        st.error(f"Errore create media: {exc}")

        with tabs[3]:
            st.write("Pubblica la media usando User ID e Creation ID presenti nello stato.")
            st.text_input("User ID", key="ultimo_user_id")
            st.text_input("Creation ID", key="ultimo_creation_id")

            if st.button("Pubblica ora", type="primary", use_container_width=True):
                if not st.session_state.ultimo_user_id:
                    st.warning("User ID mancante")
                elif not st.session_state.ultimo_creation_id:
                    st.warning("Creation ID mancante")
                else:
                    try:
                        run_publish_media()
                        st.success("Post pubblicato")
                    except Exception as exc:
                        save_error(exc)
                        st.error(f"Errore publish: {exc}")


def render_api_log_controls() -> None:
    with st.container(border=True):
        st.subheader("API Log")
        if st.session_state.ultimo_errore:
            st.error(st.session_state.ultimo_errore)
        if st.session_state.ultima_risposta is None:
            st.info("Nessuna risposta API registrata")
        else:
            st.write(st.session_state.ultima_azione)
            st.json(st.session_state.ultima_risposta)


def render_preview() -> None:
    with st.container(border=True):
        st.subheader("Mockup Preview")

        st.write("Instagram Post")
        st.caption(f"@{st.session_state.ultimo_user_id or 'username'}")

        if st.session_state.url_risorsa.strip():
            st.image(st.session_state.url_risorsa.strip(), use_container_width=True)
        else:
            st.info("Inserisci un URL immagine per vedere la preview.")

        st.write(st.session_state.caption or "La caption apparira qui.")
        if st.session_state.hashtags:
            st.write(" ".join(st.session_state.hashtags))
        if st.session_state.first_comment:
            with st.expander("First comment"):
                st.write(st.session_state.first_comment)


init_state()
selected_menu = render_topbar()
render_metrics()

left_col, right_col = st.columns([1.2, 1])

with left_col:
    if selected_menu == "Planner":
        render_composer_controls()
    else:
        render_api_log_controls()

with right_col:
    render_preview()

st.caption("Endpoint usati: /api/profile, /api/createPost, /api/PostMedia")
