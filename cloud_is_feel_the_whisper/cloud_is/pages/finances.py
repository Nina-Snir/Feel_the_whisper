import streamlit as st
import pandas as pd
from database import get_finances, add_finance, delete_finance, get_finance_summary
from datetime import date

INCOME_CATS = ["Predaj – zákazníci", "Sponzorstvo", "Iné príjmy"]
EXPENSE_CATS = ["Výroba", "Marketing", "Poštovné / balenie", "Materiál", "Iné výdavky"]


def show():
    st.title("💰 Finančná evidencia")

    # ── SUMMARY KPIs ─────────────────────────────────────────────────────────
    summary = get_finance_summary()
    k1, k2, k3 = st.columns(3)
    k1.metric("📈 Celkové príjmy", f"{summary['income']:,.2f} €")
    k2.metric("📉 Celkové výdavky", f"{summary['expenses']:,.2f} €")
    k3.metric(
        "💹 Zisk / Strata",
        f"{summary['profit']:,.2f} €",
        delta=f"{'▲' if summary['profit'] >= 0 else '▼'} {abs(summary['profit']):.2f} €",
        delta_color="normal" if summary['profit'] >= 0 else "inverse",
    )

    st.divider()

    tab1, tab2, tab3 = st.tabs(["📋 Záznamy", "➕ Pridať záznam", "📊 Prehľad"])

    # ── RECORDS LIST ──────────────────────────────────────────────────────────
    with tab1:
        col1, col2 = st.columns(2)
        year_sel = col1.number_input("Rok", min_value=2024, max_value=2030,
                                     value=date.today().year, step=1)
        type_filter = col2.selectbox("Typ", ["Všetky", "Príjem", "Výdavok"])

        records = get_finances(year=year_sel)
        if type_filter != "Všetky":
            records = [r for r in records if r["type"] == type_filter]

        if not records:
            st.info("Žiadne záznamy.")
        else:
            df = pd.DataFrame(records)[["date", "type", "category", "amount", "description"]]
            df.columns = ["Dátum", "Typ", "Kategória", "Suma (€)", "Popis"]
            df["Dátum"] = pd.to_datetime(df["Dátum"]).dt.strftime("%d.%m.%Y")
            df["Suma (€)"] = df["Suma (€)"].apply(lambda x: f"{x:,.2f}")
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.divider()
            st.subheader("Vymazať záznam")
            for r in records:
                col_l, col_r = st.columns([4, 1])
                col_l.write(f"{r['date'][:10]} · {r['type']} · {r['category']} · **{r['amount']:.2f} €** — {r.get('description') or ''}")
                if col_r.button("🗑️", key=f"del_f_{r['id']}"):
                    delete_finance(r["id"])
                    st.rerun()

    # ── ADD RECORD ────────────────────────────────────────────────────────────
    with tab2:
        st.subheader("Nový finančný záznam")
        with st.form("add_finance_form"):
            f1, f2 = st.columns(2)
            ftype = f1.radio("Typ *", ["Príjem", "Výdavok"], horizontal=True)
            fdate = f2.date_input("Dátum", value=date.today())

            f3, f4 = st.columns(2)
            cats = INCOME_CATS if ftype == "Príjem" else EXPENSE_CATS
            fcat = f3.selectbox("Kategória *", cats)
            famount = f4.number_input("Suma (€) *", min_value=0.0, step=0.5, format="%.2f")

            fdesc = st.text_input("Popis / poznámka", placeholder="Napr. Drop #2 – tržby")
            submitted = st.form_submit_button("➕ Pridať záznam", type="primary")

        if submitted:
            if famount <= 0:
                st.error("Suma musí byť väčšia ako 0.")
            else:
                add_finance(ftype, fcat, famount, fdesc.strip(), str(fdate))
                st.success("Finančný záznam pridaný.")
                st.rerun()

    # ── CHARTS ───────────────────────────────────────────────────────────────
    with tab3:
        st.subheader("📊 Analýza financií")
        all_records = get_finances()

        if not all_records:
            st.info("Žiadne dáta na zobrazenie.")
            return

        df = pd.DataFrame(all_records)
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M").astype(str)

        # Monthly income vs expenses
        monthly = df.groupby(["month", "type"])["amount"].sum().reset_index()
        if not monthly.empty:
            pivot = monthly.pivot(index="month", columns="type", values="amount").fillna(0)
            st.subheader("Príjmy vs. Výdavky (mesačne)")
            st.bar_chart(pivot)

        st.divider()

        # Breakdown by category
        by_cat = df.groupby(["category", "type"])["amount"].sum().reset_index()
        by_cat = by_cat.sort_values("amount", ascending=False)

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Príjmy podľa kategórie")
            inc_df = by_cat[by_cat["type"] == "Príjem"][["category", "amount"]]
            if not inc_df.empty:
                inc_df.columns = ["Kategória", "Suma (€)"]
                st.dataframe(inc_df, use_container_width=True, hide_index=True)
            else:
                st.info("Žiadne príjmy.")

        with c2:
            st.subheader("Výdavky podľa kategórie")
            exp_df = by_cat[by_cat["type"] == "Výdavok"][["category", "amount"]]
            if not exp_df.empty:
                exp_df.columns = ["Kategória", "Suma (€)"]
                st.dataframe(exp_df, use_container_width=True, hide_index=True)
            else:
                st.info("Žiadne výdavky.")

        # Cumulative profit
        st.divider()
        st.subheader("Kumulatívny zisk / strata")
        df_sorted = df.sort_values("date")
        df_sorted["signed"] = df_sorted.apply(
            lambda r: r["amount"] if r["type"] == "Príjem" else -r["amount"], axis=1
        )
        df_sorted["cumulative"] = df_sorted["signed"].cumsum()
        df_sorted = df_sorted.set_index("date")
        st.line_chart(df_sorted["cumulative"])
