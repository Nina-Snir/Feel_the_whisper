import streamlit as st
from database import get_supplier_orders, add_supplier_order, update_supplier_order_status, delete_supplier_order, get_suppliers
from datetime import date

STATUSES = ["Objednaná", "Vo výrobe", "Dokončená", "Doručená", "Zrušená"]
STATUS_ICONS = {"Objednaná": "🔵", "Vo výrobe": "🟣", "Dokončená": "🟡",
                "Doručená": "🟢", "Zrušená": "🔴"}


def show():
    st.title("🏭 Objednávky u dodávateľov")

    tab1, tab2, tab3 = st.tabs(["📋 Zoznam", "➕ Nová objednávka", "🏢 Dodávatelia"])

    # ── LIST ──────────────────────────────────────────────────────────────────
    with tab1:
        status_filter = st.selectbox("Filtrovať podľa stavu", ["Všetky"] + STATUSES)
        orders = get_supplier_orders(status_filter)
        st.caption(f"Nájdených: {len(orders)} objednávok")

        if not orders:
            st.info("Žiadne objednávky u dodávateľov.")
        else:
            for o in orders:
                icon = STATUS_ICONS.get(o["status"], "⚪")
                deadline_str = o.get("deadline") or "—"
                with st.expander(f"{icon} #{o['id']} · {o['supplier_name']} — {o['products']}"):
                    d1, d2, d3 = st.columns(3)
                    d1.write(f"📦 Množstvo: **{o.get('quantity') or '—'}**")
                    d2.write(f"💶 Suma: **{o['amount']:.2f} €**")
                    d3.write(f"📅 Termín: **{deadline_str}**")
                    d1.write(f"📌 Stav: **{o['status']}**")
                    d2.write(f"🗓️ Objednané: **{o['order_date'][:10] if o['order_date'] else '—'}**")
                    if o.get("notes"):
                        st.info(f"📝 {o['notes']}")

                    st.divider()
                    with st.form(f"upd_so_{o['id']}"):
                        nc1, nc2 = st.columns(2)
                        new_status = nc1.selectbox("Zmeniť stav", STATUSES,
                                                   index=STATUSES.index(o["status"]) if o["status"] in STATUSES else 0)
                        new_notes = nc2.text_input("Poznámka", value=o.get("notes") or "")
                        if st.form_submit_button("💾 Uložiť", type="primary"):
                            update_supplier_order_status(o["id"], new_status, new_notes)
                            st.success("Aktualizované.")
                            st.rerun()

                    if st.button("🗑️ Vymazať", key=f"del_so_{o['id']}"):
                        delete_supplier_order(o["id"])
                        st.rerun()

    # ── ADD ORDER ─────────────────────────────────────────────────────────────
    with tab2:
        st.subheader("Nová objednávka u dodávateľa")
        suppliers = get_suppliers()
        supp_names = ["— zadať manuálne —"] + [s["name"] for s in suppliers]

        with st.form("add_so_form"):
            sel = st.selectbox("Dodávateľ", supp_names)
            if sel == "— zadať manuálne —":
                supp_name = st.text_input("Názov dodávateľa *")
                supp_id = None
            else:
                supp_name = sel
                supp_id = next((s["id"] for s in suppliers if s["name"] == sel), None)

            r1, r2 = st.columns(2)
            products = r1.text_input("Produkty *", placeholder="Napr. Hoodie čierny — 50 ks")
            quantity = r2.number_input("Počet kusov", min_value=0, step=1)

            r3, r4, r5 = st.columns(3)
            amount = r3.number_input("Suma (€)", min_value=0.0, step=1.0, format="%.2f")
            status = r4.selectbox("Stav", STATUSES)
            order_date = r5.date_input("Dátum objednávky", value=date.today())

            deadline = st.date_input("Termín dodania", value=None)
            notes = st.text_area("Poznámky", height=80)
            submitted = st.form_submit_button("➕ Pridať objednávku", type="primary")

        if submitted:
            if not supp_name.strip() or not products.strip():
                st.error("Dodávateľ a produkty sú povinné.")
            else:
                add_supplier_order(supp_name.strip(), products.strip(), quantity, amount,
                                   status, str(deadline) if deadline else None,
                                   notes.strip(), str(order_date), supp_id)
                st.success("Objednávka u dodávateľa pridaná.")
                st.rerun()

    # ── SUPPLIERS ─────────────────────────────────────────────────────────────
    with tab3:
        st.subheader("Správa dodávateľov")
        suppliers = get_suppliers()
        if suppliers:
            for s in suppliers:
                with st.expander(f"🏢 {s['name']}"):
                    st.write(f"📞 Kontakt: {s.get('contact') or '—'}")
                    st.write(f"📧 Email: {s.get('email') or '—'}")
                    if s.get("notes"):
                        st.write(f"📝 {s['notes']}")
                    if st.button("🗑️ Vymazať", key=f"del_s_{s['id']}"):
                        from database import delete_supplier
                        delete_supplier(s["id"])
                        st.rerun()
        else:
            st.info("Žiadni dodávatelia.")

        st.divider()
        st.subheader("Pridať dodávateľa")
        with st.form("add_supp"):
            s1, s2 = st.columns(2)
            sname = s1.text_input("Názov *")
            scontact = s2.text_input("Kontaktná osoba")
            s3, s4 = st.columns(2)
            semail = s3.text_input("Email")
            snotes = s4.text_input("Poznámky")
            if st.form_submit_button("➕ Pridať dodávateľa", type="primary"):
                if sname.strip():
                    from database import add_supplier
                    add_supplier(sname.strip(), scontact.strip(), semail.strip(), snotes.strip())
                    st.success("Dodávateľ pridaný.")
                    st.rerun()
