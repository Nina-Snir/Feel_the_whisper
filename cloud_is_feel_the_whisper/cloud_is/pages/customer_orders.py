import streamlit as st
from database import get_customer_orders, add_customer_order, update_customer_order_status, delete_customer_order, get_customers
from datetime import date

STATUSES = ["Nová", "Čaká na výrobu", "Vo výrobe", "Odoslaná", "Vybavená", "Zrušená"]
STATUS_ICONS = {"Nová": "🔵", "Čaká na výrobu": "🟠", "Vo výrobe": "🟣",
                "Odoslaná": "🟡", "Vybavená": "🟢", "Zrušená": "🔴"}


def show():
    st.title("📦 Objednávky zákazníkov")

    tab1, tab2 = st.tabs(["📋 Zoznam objednávok", "➕ Nová objednávka"])

    with tab1:
        col_s, col_f = st.columns([2, 1])
        search = col_s.text_input("🔍 Hľadať", placeholder="Zákazník alebo produkt...")
        status_filter = col_f.selectbox("Stav", ["Všetky"] + STATUSES)

        orders = get_customer_orders(search, status_filter)
        st.caption(f"Nájdených: {len(orders)} objednávok")

        if not orders:
            st.info("Žiadne objednávky.")
        else:
            for o in orders:
                icon = STATUS_ICONS.get(o["status"], "⚪")
                date_fmt = o["order_date"][:10] if o["order_date"] else "—"
                with st.expander(f"{icon} #{o['id']} · {o['customer_name']} — {o['products']} · {o['amount']:.2f} €"):
                    d1, d2 = st.columns(2)
                    d1.write(f"📅 Dátum: **{date_fmt}**")
                    d1.write(f"📌 Stav: **{o['status']}**")
                    d2.write(f"💶 Suma: **{o['amount']:.2f} €**")
                    if o.get("notes"):
                        st.info(f"📝 Poznámka: {o['notes']}")

                    st.divider()
                    with st.form(f"upd_co_{o['id']}"):
                        nc1, nc2 = st.columns(2)
                        new_status = nc1.selectbox("Zmeniť stav", STATUSES,
                                                   index=STATUSES.index(o["status"]) if o["status"] in STATUSES else 0)
                        new_notes = nc2.text_input("Poznámka", value=o.get("notes") or "")
                        if st.form_submit_button("💾 Uložiť zmeny", type="primary"):
                            update_customer_order_status(o["id"], new_status, new_notes)
                            st.success("Objednávka aktualizovaná.")
                            st.rerun()

                    if st.button("🗑️ Vymazať", key=f"del_co_{o['id']}"):
                        delete_customer_order(o["id"])
                        st.rerun()

    with tab2:
        st.subheader("Nová objednávka zákazníka")
        customers = get_customers()
        customer_names = ["— zadať manuálne —"] + [c["name"] for c in customers]

        with st.form("add_co_form"):
            sel = st.selectbox("Zákazník zo zoznamu", customer_names)
            if sel == "— zadať manuálne —":
                cust_name = st.text_input("Meno zákazníka *")
                cust_id = None
            else:
                cust_name = sel
                cust_id = next((c["id"] for c in customers if c["name"] == sel), None)

            r1, r2 = st.columns(2)
            products = r1.text_input("Produkty *", placeholder="Napr. Hoodie čierny M, Tričko biele S")
            amount = r2.number_input("Suma (€)", min_value=0.0, step=0.5, format="%.2f")

            r3, r4 = st.columns(2)
            status = r3.selectbox("Stav", STATUSES)
            order_date = r4.date_input("Dátum objednávky", value=date.today())

            notes = st.text_area("Poznámky / špeciálne požiadavky", height=80)
            submitted = st.form_submit_button("➕ Pridať objednávku", type="primary")

        if submitted:
            if not cust_name.strip() or not products.strip():
                st.error("Zákazník a produkty sú povinné.")
            else:
                add_customer_order(cust_name.strip(), products.strip(), amount, status,
                                   notes.strip(), str(order_date), cust_id)
                st.success("Objednávka pridaná.")
                st.rerun()
