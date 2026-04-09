import streamlit as st
from database import get_users, add_user, delete_user


def show():
    st.title("⚙️ Správa používateľov")

    if st.session_state.user.get("role") != "admin":
        st.error("Prístup zamietnutý. Táto sekcia je len pre administrátora.")
        return

    users = get_users()
    st.subheader(f"Registrovaní používatelia ({len(users)})")

    for u in users:
        role_badge = "👑 Admin" if u["role"] == "admin" else "👤 Člen"
        with st.expander(f"{role_badge} — {u['full_name']} (@{u['username']})"):
            st.write(f"**Rola:** {u['role']}")
            st.write(f"**Vytvorený:** {u['created_at'][:10] if u['created_at'] else '—'}")
            is_self = u["id"] == st.session_state.user["id"]
            if is_self:
                st.info("Toto je váš vlastný účet — nemôžete ho vymazať.")
            else:
                if st.button("🗑️ Vymazať používateľa", key=f"del_u_{u['id']}"):
                    delete_user(u["id"])
                    st.success("Používateľ vymazaný.")
                    st.rerun()

    st.divider()
    st.subheader("➕ Pridať nového používateľa")
    with st.form("add_user_form"):
        c1, c2 = st.columns(2)
        full_name = c1.text_input("Celé meno *")
        username = c2.text_input("Používateľské meno *")
        c3, c4 = st.columns(2)
        password = c3.text_input("Heslo *", type="password")
        role = c4.selectbox("Rola", ["member", "admin"])
        submitted = st.form_submit_button("➕ Pridať", type="primary")

    if submitted:
        if not full_name.strip() or not username.strip() or not password.strip():
            st.error("Všetky polia sú povinné.")
        else:
            try:
                add_user(username.strip(), password, full_name.strip(), role)
                st.success(f"Používateľ **{full_name}** bol pridaný.")
                st.rerun()
            except Exception as e:
                st.error(f"Chyba: {e} — používateľské meno už existuje.")
