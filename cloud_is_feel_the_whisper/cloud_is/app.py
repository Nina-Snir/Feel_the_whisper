import streamlit as st
from database import init_db, login

st.set_page_config(
    page_title="Feel the Whisper IS",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

# ── SESSION DEFAULTS ──────────────────────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None

# ── LOGIN PAGE ────────────────────────────────────────────────────────────────
def show_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style='text-align:center; margin-bottom: 2rem;'>
                <h1 style='font-size:2.5rem; font-weight:700; color:#1a1a1a;'>🌿 Feel the Whisper</h1>
                <p style='color:#666; font-size:1rem;'>Interný informačný systém</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("login_form"):
            username = st.text_input("Používateľské meno", placeholder="admin")
            password = st.text_input("Heslo", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Prihlásiť sa", use_container_width=True, type="primary")

        if submitted:
            user = login(username, password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Nesprávne prihlasovacie údaje.")

        st.markdown(
            "<p style='text-align:center; color:#999; font-size:0.8rem; margin-top:1rem;'>"
            "Predvolené: admin / admin123</p>",
            unsafe_allow_html=True,
        )


# ── SIDEBAR NAV ───────────────────────────────────────────────────────────────
def show_sidebar():
    with st.sidebar:
        st.markdown(
            f"""
            <div style='padding: 0.5rem 0 1.5rem 0;'>
                <h2 style='margin:0; font-size:1.3rem;'>🌿 Feel the Whisper</h2>
                <p style='color:#888; font-size:0.8rem; margin:0.2rem 0 0 0;'>
                    {st.session_state.user['full_name']} · {st.session_state.user['role']}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        page = st.radio(
            "Navigácia",
            [
                "📊 Dashboard",
                "👥 Zákazníci",
                "📦 Objednávky zákazníkov",
                "🏭 Objednávky dodávateľov",
                "📅 Kalendár termínov",
                "💰 Financie",
                "📣 Marketing",
            ],
            label_visibility="collapsed",
        )

        if st.session_state.user["role"] == "admin":
            st.divider()
            if st.checkbox("⚙️ Správa používateľov"):
                page = "⚙️ Správa používateľov"

        st.divider()
        if st.button("🚪 Odhlásiť sa", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    return page


# ── MAIN ──────────────────────────────────────────────────────────────────────
if st.session_state.user is None:
    show_login()
else:
    page = show_sidebar()

    if page == "📊 Dashboard":
        from pages.dashboard import show
        show()
    elif page == "👥 Zákazníci":
        from pages.customers import show
        show()
    elif page == "📦 Objednávky zákazníkov":
        from pages.customer_orders import show
        show()
    elif page == "🏭 Objednávky dodávateľov":
        from pages.supplier_orders import show
        show()
    elif page == "📅 Kalendár termínov":
        from pages.calendar import show
        show()
    elif page == "💰 Financie":
        from pages.finances import show
        show()
    elif page == "📣 Marketing":
        from pages.marketing import show
        show()
    elif page == "⚙️ Správa používateľov":
        from pages.users import show
        show()
