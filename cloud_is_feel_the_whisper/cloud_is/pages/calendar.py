import streamlit as st
from database import get_events, get_upcoming_events, add_event, delete_event
from datetime import date, datetime

EVENT_TYPES = ["Výroba", "Drop / Predaj", "Marketing", "Dodávka", "Iné"]
TYPE_ICONS = {"Výroba": "🏭", "Drop / Predaj": "🛍️", "Marketing": "📣",
              "Dodávka": "📦", "Iné": "📌"}


def show():
    st.title("📅 Kalendár termínov")

    tab1, tab2 = st.tabs(["📅 Všetky udalosti", "➕ Pridať udalosť"])

    with tab1:
        col1, col2, col3 = st.columns(3)
        today = date.today()
        year_sel = col1.number_input("Rok", min_value=2024, max_value=2030, value=today.year, step=1)
        month_sel = col2.selectbox("Mesiac", list(range(1, 13)),
                                   index=today.month - 1,
                                   format_func=lambda m: [
                                       "Január", "Február", "Marec", "Apríl", "Máj", "Jún",
                                       "Júl", "August", "September", "Október", "November", "December"
                                   ][m - 1])
        type_filter = col3.selectbox("Typ", ["Všetky"] + EVENT_TYPES)

        events = get_events(month=month_sel, year=year_sel)
        if type_filter != "Všetky":
            events = [e for e in events if e["event_type"] == type_filter]

        month_name = ["Január", "Február", "Marec", "Apríl", "Máj", "Jún",
                      "Júl", "August", "September", "Október", "November", "December"][month_sel - 1]
        st.subheader(f"{month_name} {year_sel}")
        st.caption(f"Nájdených udalostí: {len(events)}")

        if not events:
            st.info("Žiadne udalosti v tomto mesiaci.")
        else:
            for e in events:
                icon = TYPE_ICONS.get(e["event_type"], "📌")
                try:
                    dt = datetime.strptime(e["event_date"], "%Y-%m-%d")
                    date_fmt = dt.strftime("%d.%m.%Y (%A)")
                    is_past = dt.date() < date.today()
                except Exception:
                    date_fmt = e["event_date"]
                    is_past = False

                with st.expander(f"{icon} {e['title']}  —  {date_fmt}{'  ✅' if is_past else ''}"):
                    st.write(f"**Typ:** {e['event_type']}")
                    st.write(f"**Dátum:** {date_fmt}")
                    if e.get("description"):
                        st.write(f"**Popis:** {e['description']}")
                    if is_past:
                        st.caption("Táto udalosť už prebehla.")
                    if st.button("🗑️ Vymazať", key=f"del_ev_{e['id']}"):
                        delete_event(e["id"])
                        st.rerun()

        # Upcoming events sidebar card
        st.divider()
        st.subheader("📌 Najbližšie termíny")
        upcoming = get_upcoming_events()
        if upcoming:
            for e in upcoming[:10]:
                icon = TYPE_ICONS.get(e["event_type"], "📌")
                try:
                    dt = datetime.strptime(e["event_date"], "%Y-%m-%d")
                    days_left = (dt.date() - date.today()).days
                    date_fmt = dt.strftime("%d.%m.%Y")
                    if days_left == 0:
                        badge = "🔴 **DNES**"
                    elif days_left <= 3:
                        badge = f"🟠 za **{days_left} dní**"
                    elif days_left <= 7:
                        badge = f"🟡 za {days_left} dní"
                    else:
                        badge = f"🟢 za {days_left} dní"
                except Exception:
                    date_fmt = e["event_date"]
                    badge = ""

                st.markdown(
                    f"{icon} **{e['title']}** — {date_fmt}  {badge}",
                    unsafe_allow_html=True,
                )
        else:
            st.info("Žiadne nadchádzajúce termíny.")

    with tab2:
        st.subheader("Nová udalosť / termín")
        with st.form("add_event_form"):
            title = st.text_input("Názov udalosti *", placeholder="Napr. Spustenie Dropu #3")
            c1, c2 = st.columns(2)
            event_type = c1.selectbox("Typ udalosti", EVENT_TYPES)
            event_date = c2.date_input("Dátum", value=date.today())
            description = st.text_area("Popis / poznámky", height=80)
            submitted = st.form_submit_button("➕ Pridať udalosť", type="primary")

        if submitted:
            if not title.strip():
                st.error("Názov je povinný.")
            else:
                user_id = st.session_state.user.get("id") if st.session_state.user else None
                add_event(title.strip(), event_type, str(event_date), description.strip(), user_id)
                st.success(f"Udalosť **{title}** bola pridaná.")
                st.rerun()
