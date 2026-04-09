# 🌿 Feel the Whisper – Informačný systém

Cloudový informačný systém pre malú značku oblečenia Feel the Whisper.
Vybudovaný v **Python + Streamlit + SQLite**, nasadený na **Streamlit Community Cloud**.

---

## 🚀 Nasadenie na Streamlit Community Cloud (krok za krokom)

### 1. Príprava GitHub repozitára

1. Vytvor si účet na [github.com](https://github.com) (ak ho nemáš)
2. Klikni na **New repository** → pomenuj ho napr. `feel-the-whisper-is`
3. Nahraj všetky súbory z tohto projektu do repozitára:
   - `app.py`
   - `database.py`
   - `requirements.txt`
   - `pages/` (celý priečinok so všetkými súbormi)

### 2. Nasadenie na Streamlit Cloud

1. Choď na [share.streamlit.io](https://share.streamlit.io)
2. Prihlás sa cez GitHub účet
3. Klikni na **New app**
4. Vyber:
   - **Repository:** `tvoj-username/feel-the-whisper-is`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Klikni **Deploy!**

✅ Aplikácia bude živá na adrese: `https://tvoj-username-feel-the-whisper-is.streamlit.app`

---

## 📁 Štruktúra projektu

```
feel-the-whisper-is/
├── app.py                  # Hlavný súbor – prihlásenie + navigácia
├── database.py             # Databázová vrstva (SQLite)
├── requirements.txt        # Python závislosti
└── pages/
    ├── dashboard.py        # Prehľad / KPI štatistiky
    ├── customers.py        # Evidencia zákazníkov + história
    ├── customer_orders.py  # Objednávky zákazníkov (CRUD)
    ├── supplier_orders.py  # Objednávky dodávateľov (CRUD)
    ├── calendar.py         # Kalendár termínov
    ├── finances.py         # Finančná evidencia + grafy
    ├── marketing.py        # Marketing a kampane
    └── users.py            # Správa používateľov (admin)
```

---

## 🔐 Predvolené prihlasovacie údaje

| Rola  | Používateľské meno | Heslo    |
|-------|--------------------|----------|
| Admin | `admin`            | `admin123` |

> ⚠️ **Po prvom prihlásení zmeň heslo** vytvorením nového admin účtu a vymazaním predvoleného.

---

## 🗄️ Databáza (SQLite)

SQLite databáza sa automaticky vytvorí pri prvom spustení ako súbor `feel_the_whisper.db`.

> **Poznámka:** Na Streamlit Community Cloud sa databáza resetuje pri každom redeploymente.
> Pre produkčné nasadenie odporúčame prejsť na **Supabase** (PostgreSQL zadarmo).

---

## 📋 Moduly systému

| Modul | Priorita (MoSCoW) | Popis |
|-------|-------------------|-------|
| Evidencia zákazníkov | MUST | CRUD, história objednávok, poznámky |
| Objednávky zákazníkov | MUST | Stav výroby, suma, filtrovanie |
| Objednávky dodávateľov | MUST | Termíny, stav, prepojenie s dodávateľmi |
| Kalendár termínov | MUST | Typy udalostí, upozornenia, prehľad |
| Finančná evidencia | MUST | Príjmy/výdavky, grafy, zisk/strata |
| Evidencia marketingu | SHOULD | Kampane, kanály, výsledky |
| Dashboard | — | KPI prehľad, nadchádzajúce termíny |
| Správa používateľov | — | Tímový prístup, roly |
