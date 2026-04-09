import streamlit as st
from database import get_marketing, add_marketing, update_marketing, delete_marketing
from datetime import date

CHANNELS = ["Instagram", "TikTok", "Email", "Osobná komunikácia", "Iné"]
STATUSES = ["Plánovaná", "Aktívna", "Dokončená", "Zrušená"]
STATUS_ICONS = {"Plánovaná": "🔵", "Aktívna": "🟢", "Dokončená": "✅", "Zrušená": "🔴"}
CHANNEL_ICONS = {"Instagram": "📸", "TikTok": "🎵", "Email": "📧",
                 "Osobná komunikácia": "💬", "Iné": "📢"}


def show():
    st.title("📣 Marketing a kampane")

    tab1, tab2 = st.tabs(["📋 Kampane", "➕ Nová kampaň"])

    with tab1:
        col1, col2 = st.columns(2)
        status_filter = col1.selectbox("Stav", ["Všetky"] + STATUSES)
        channel_filter = col2.selectbox("Kanál", ["Všetky"] + CHANNELS)

        campaigns = get_marketing(status_filter)
        if channel_filter != "Všetky":
            campaigns = [c for c in campaigns if c["channel"] == channel_filter]

        st.caption(f"Nájdených kampaní: {len(campaigns)}")

        if not campaigns:
            st.info("Žiadne kampane.")
        else:
            for camp in campaigns:
                icon = STATUS_ICONS.get(camp["status"], "📢")
                ch_icon = CHANNEL_ICONS.get(camp["channel"], "📢")
                planned = camp.get("planned_date") or "—"
                with st.expander(f"{icon} {camp['title']}  —  {ch_icon} {camp['channel']}  —  {planned}"):
                    d1, d2, d3 = st.columns(3)
                    d1.write(f"📌 Stav: **{camp['status']}**")
                    d2.write(f"📅 Plánovaný dátum: **{planned}**")
                    d3.write(f"📤 Publikované: **{camp.get('published_date') or '—'}**")

                    if camp.get("notes"):
                        st.info(f"📝 Poznámky: {camp['notes']}")
                    if camp.get("result"):
                        st.success(f"📊 Výsledok: {camp['result']}")

                    st.divider()
                    with st.form(f"upd_mkt_{camp['id']}"):
                        uc1, uc2, uc3 = st.columns(3)
                        new_status = uc1.selectbox(
                            "Zmeniť stav", STATUSES,
                            index=STATUSES.index(camp["status"]) if camp["status"] in STATUSES else 0
                        )
                        new_result = uc2.text_input("Výsledok / dosah", value=camp.get("result") or "")
                        new_pub = uc3.date_input(
                            "Dátum publikácie",
                            value=date.fromisoformat(camp["published_date"]) if camp.get("published_date") else None
                        )
                        if st.form_submit_button("💾 Uložiť zmeny", type="primary"):
                            update_marketing(camp["id"], new_status, new_result, str(new_pub) if new_pub else None)
                            st.success("Kampaň aktualizovaná.")
                            st.rerun()

                    if st.button("🗑️ Vymazať", key=f"del_mkt_{camp['id']}"):
                        delete_marketing(camp["id"])
                        st.rerun()

    with tab2:
        st.subheader("Nová marketingová kampaň")
        with st.form("add_mkt_form"):
            title = st.text_input("Názov kampane *", placeholder="Napr. Drop #3 – Instagram story")
            m1, m2 = st.columns(2)
            channel = m1.selectbox("Kanál", CHANNELS)
            status = m2.selectbox("Stav", STATUSES)
            m3, _ = st.columns(2)
            planned_date = m3.date_input("Plánovaný dátum", value=date.today())
            notes = st.text_area("Poznámky / popis kampane", height=100,
                                 placeholder="Popis obsahu, cieľ, cieľová skupina...")
            submitted = st.form_submit_button("➕ Pridať kampaň", type="primary")

        if submitted:
            if not title.strip():
                st.error("Názov kampane je povinný.")
            else:
                add_marketing(title.strip(), channel, status, str(planned_date), notes.strip())
                st.success(f"Kampaň **{title}** pridaná.")
                st.rerun()
