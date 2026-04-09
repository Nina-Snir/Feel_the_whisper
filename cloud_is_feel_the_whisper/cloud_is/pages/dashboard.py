import streamlit as st
from database import get_dashboard_stats, get_upcoming_events, get_customer_orders, get_supplier_orders
from datetime import datetime


def show():
    st.title("📊 Dashboard")
    st.caption(f"Prehľad stavu — {datetime.now().strftime('%d.%m.%Y')}")

    stats = get_dashboard_stats()

    # ── KPI CARDS ──────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 Zákazníci", stats["customers"])
    c2.metric("📦 Objednávky", stats["cust_orders"], f"{stats['cust_orders_new']} nových")
    c3.metric("🏭 Dodávateľské obj.", stats["supp_orders"], f"{stats['supp_orders_pending']} aktívnych")
    c4.metric("📅 Nadchádzajúce udalosti", stats["upcoming_events"])

    st.divider()

    # ── FINANCIAL SUMMARY ──────────────────────────────────────────────────────
    st.subheader("💰 Finančný prehľad")
    f1, f2, f3 = st.columns(3)
    f1.metric("Celkové príjmy", f"{stats['income']:,.2f} €", delta_color="normal")
    f2.metric("Celkové výdavky", f"{stats['expenses']:,.2f} €", delta_color="inverse")
    profit_delta = "▲ zisk" if stats["profit"] >= 0 else "▼ strata"
    f3.metric("Zisk / Strata", f"{stats['profit']:,.2f} €")

    st.divider()

    col_left, col_right = st.columns(2)

    # ── UPCOMING EVENTS ────────────────────────────────────────────────────────
    with col_left:
        st.subheader("📅 Nadchádzajúce termíny")
        events = get_upcoming_events()
        if events:
            for e in events[:8]:
                type_icon = {
                    "Výroba": "🏭",
                    "Drop / Predaj": "🛍️",
                    "Marketing": "📣",
                    "Dodávka": "📦",
                    "Iné": "📌",
                }.get(e["event_type"], "📌")
                date_str = e["event_date"]
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d")
                    date_str = dt.strftime("%d.%m.%Y")
                except Exception:
                    pass
                st.markdown(
                    f"**{type_icon} {e['title']}**  \n"
                    f"<span style='color:#888;font-size:0.85rem;'>{date_str} · {e['event_type']}</span>",
                    unsafe_allow_html=True,
                )
                if e.get("description"):
                    st.caption(e["description"])
                st.markdown("---")
        else:
            st.info("Žiadne nadchádzajúce udalosti.")

    # ── RECENT CUSTOMER ORDERS ─────────────────────────────────────────────────
    with col_right:
        st.subheader("📦 Posledné objednávky zákazníkov")
        orders = get_customer_orders()[:8]
        if orders:
            status_colors = {
                "Nová": "🔵",
                "Vybavená": "🟢",
                "Odoslaná": "🟡",
                "Zrušená": "🔴",
                "Čaká na výrobu": "🟠",
            }
            for o in orders:
                icon = status_colors.get(o["status"], "⚪")
                date_str = o["order_date"]
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d")
                    date_str = dt.strftime("%d.%m.%Y")
                except Exception:
                    pass
                st.markdown(
                    f"**{icon} {o['customer_name']}** — {o['products']}  \n"
                    f"<span style='color:#888;font-size:0.85rem;'>{date_str} · {o['status']} · {o['amount']:.2f} €</span>",
                    unsafe_allow_html=True,
                )
                st.markdown("---")
        else:
            st.info("Žiadne objednávky.")
