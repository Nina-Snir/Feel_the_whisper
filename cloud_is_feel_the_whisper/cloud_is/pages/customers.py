import streamlit as st
from database import get_customers, add_customer, update_customer, delete_customer, get_customer_order_history


def show():
    st.title("👥 Evidencia zákazníkov")

    tab1, tab2 = st.tabs(["📋 Zoznam zákazníkov", "➕ Pridať zákazníka"])

    # ── LIST TAB ──────────────────────────────────────────────────────────────
    with tab1:
        search = st.text_input("🔍 Hľadať zákazníka", placeholder="Meno, email alebo Instagram...")
        customers = get_customers(search)

        if not customers:
            st.info("Žiadni zákazníci nenájdení.")
            return

        st.caption(f"Nájdených: {len(customers)} zákazníkov")

        for cust in customers:
            with st.expander(f"👤 {cust['name']}  —  {cust.get('email') or cust.get('instagram') or ''}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Kontaktné údaje**")
                    st.write(f"📧 Email: {cust.get('email') or '—'}")
                    st.write(f"📱 Telefón: {cust.get('phone') or '—'}")
                    st.write(f"📸 Instagram: {cust.get('instagram') or '—'}")
                    if cust.get("notes"):
                        st.write(f"📝 Poznámky: {cust['notes']}")

                with col2:
                    st.markdown("**História objednávok**")
                    history = get_customer_order_history(cust["name"])
                    if history:
                        for h in history[:5]:
                            st.markdown(
                                f"- {h['order_date'][:10] if h['order_date'] else '?'} · "
                                f"{h['products']} · **{h['amount']:.2f} €** · {h['status']}"
                            )
                        if len(history) > 5:
                            st.caption(f"... a ďalších {len(history) - 5} objednávok")
                    else:
                        st.caption("Žiadne objednávky.")

                st.divider()

                # Edit form
                with st.form(f"edit_cust_{cust['id']}"):
                    st.markdown("**Upraviť zákazníka**")
                    ec1, ec2 = st.columns(2)
                    new_name = ec1.text_input("Meno", value=cust["name"])
                    new_email = ec2.text_input("Email", value=cust.get("email") or "")
                    ec3, ec4 = st.columns(2)
                    new_phone = ec3.text_input("Telefón", value=cust.get("phone") or "")
                    new_ig = ec4.text_input("Instagram", value=cust.get("instagram") or "")
                    new_notes = st.text_area("Poznámky", value=cust.get("notes") or "", height=80)
                    bc1, bc2 = st.columns([1, 3])
                    save = bc1.form_submit_button("💾 Uložiť", type="primary")
                    if save:
                        update_customer(cust["id"], new_name, new_email, new_phone, new_ig, new_notes)
                        st.success("Zákazník bol upravený.")
                        st.rerun()

                if st.button(f"🗑️ Vymazať zákazníka", key=f"del_c_{cust['id']}"):
                    delete_customer(cust["id"])
                    st.warning("Zákazník vymazaný.")
                    st.rerun()

    # ── ADD TAB ───────────────────────────────────────────────────────────────
    with tab2:
        st.subheader("Nový zákazník")
        with st.form("add_customer_form"):
            a1, a2 = st.columns(2)
            name = a1.text_input("Meno *", placeholder="Ján Novák")
            email = a2.text_input("Email", placeholder="jan@email.sk")
            a3, a4 = st.columns(2)
            phone = a3.text_input("Telefón", placeholder="+421 900 000 000")
            instagram = a4.text_input("Instagram", placeholder="@username")
            notes = st.text_area("Poznámky / individuálne požiadavky", height=100)
            submitted = st.form_submit_button("➕ Pridať zákazníka", type="primary")

        if submitted:
            if not name.strip():
                st.error("Meno je povinné.")
            else:
                add_customer(name.strip(), email.strip(), phone.strip(), instagram.strip(), notes.strip())
                st.success(f"Zákazník **{name}** bol pridaný.")
                st.rerun()
