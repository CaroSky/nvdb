import streamlit as st
import pandas as pd
import requests
from itertools import chain
import plotly.express as px

# ---------- KONFIG ----------
BASE_URL = "https://nvdbapiles.atlas.vegvesen.no"
HEADERS = {"X-Client": "demo-dataquality"}

# ---------- HENT EGENSKAPER ----------
@st.cache_data(show_spinner=False)
def hent_egenskapstyper(vegobjekttype):
    url = f"{BASE_URL}/vegobjekttyper/{vegobjekttype}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 404:
        st.error(f"Objekttype {vegobjekttype} finnes ikke.")
        return pd.DataFrame()
    r.raise_for_status()
    data = r.json()
    egenskapstyper = data.get("egenskapstyper", [])
    return pd.DataFrame(egenskapstyper)

# ---------- HENT NAVN PÅ VEGOBJEKT ----------
def hent_vegobjekttype_navn(vegobjekttype):
    url = f"{BASE_URL}/vegobjekttyper/{vegobjekttype}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        return f"(Ukjent navn for {vegobjekttype})"
    data = r.json()
    return data.get("navn", f"(Ukjent navn for {vegobjekttype})")

# ---------- HENT DATA ----------
@st.cache_data(show_spinner=False)
def hent_vegobjekter(vegobjekttype, fylke=34, antall=800):
    endpoint = f"{BASE_URL}/vegobjekter/api/v4/vegobjekter/{vegobjekttype}"
    params = {"inkluder": "metadata,egenskaper,lokasjon", "antall": antall, "fylke": fylke}
    r = requests.get(endpoint, headers=HEADERS, params=params)
    if r.status_code == 404:
        st.error(f"Objekttype {vegobjekttype} finnes ikke i API-et.")
        return {}
    r.raise_for_status()
    return r.json()

# ---------- PARSE JSON ----------
def parse_vegobjekter_json(json_data):
    records = []
    for obj in json_data.get("objekter", []):
        rec = {"id": obj.get("id")}
        for eg in obj.get("egenskaper", []):
            navn = eg.get("navn")
            verdi = eg.get("verdi")
            rec[navn] = verdi
        lok = obj.get("lokasjon", {})
        if isinstance(lok, dict):
            geom = lok.get("geometri", {})
            if isinstance(geom, dict) and "wgs84" in geom:
                geo = geom["wgs84"]
                rec["lat"] = geo.get("lat")
                rec["lon"] = geo.get("lon")
            rec["fylke"] = (lok.get("fylker") or [None])[0]
            rec["kommune"] = (lok.get("kommuner") or [None])[0]
        records.append(rec)
    return pd.DataFrame(records)

# ---------- DASHBOARD ----------
st.title("🛣️ NVDB Datakvalitet – Interaktiv utforsker av manglende verdier")

st.markdown(
    "Oppgi **objekttypenummer** (for eksempel `79` for Stikkrenne/Kulvert). "
    "Full oversikt finnes her: [NVDB Datakatalog](https://datakatalogen.atlas.vegvesen.no/)"
)

# --- 1. Inputfelt for objekttype ---
objekt_id = st.text_input("Objekttypenummer", "79")

# --- 2. Velg viktighet ---
viktighet_valg = st.selectbox(
    "Velg hvilken viktighet som skal analyseres:",
    ["ALLE", "PÅKREVD_ABSOLUTT", "PÅKREVD_IKKE_ABSOLUTT", "BETINGET", "OPSJONELL", "MINDRE_VIKTIG"]
)

# --- 3. Antall objekter ---
antall = st.slider("Antall objekter å hente", 100, 800, 500, 100)

if st.button("🚀 Kjør analyse"):
    try:
        objekt_id = int(objekt_id)
    except ValueError:
        st.error("Vennligst oppgi et gyldig objekttypenummer (heltall).")
        st.stop()

    with st.spinner("Henter data fra NVDB..."):
        egenskaper_df = hent_egenskapstyper(objekt_id)
        if egenskaper_df.empty:
            st.stop()
        data_raw = hent_vegobjekter(objekt_id, antall=antall)
        if not data_raw:
            st.stop()
        df = parse_vegobjekter_json(data_raw)

    objektnavn = hent_vegobjekttype_navn(objekt_id)
    st.subheader(f"Objekttype {objekt_id} – {objektnavn} – {len(df)} objekter hentet")

    # --- Filtrer egenskaper etter viktighet ---
    if viktighet_valg != "ALLE":
        paakrevde = egenskaper_df.loc[
            egenskaper_df["viktighet"] == viktighet_valg, "navn"
        ].tolist()
    else:
        paakrevde = egenskaper_df["navn"].tolist()

    paakrevde_i_data = [c for c in paakrevde if c in df.columns]

    if not paakrevde_i_data:
        st.warning("Ingen av de valgte egenskapene finnes i datasettet.")
        st.stop()

    st.caption(f"Egenskaper inkludert i analysen: {', '.join(paakrevde_i_data[:10])}...")

    # --- Beregn datakvalitet ---
    df["kompletthet_score"] = df[paakrevde_i_data].notna().mean(axis=1)
    manglende = df[paakrevde_i_data].isna().sum().sort_values(ascending=False)

    # --- Visualisering: manglende verdier ---
    st.subheader("📉 Manglende verdier")
    if not manglende.empty and manglende.sum() > 0:
        fig = px.bar(
            manglende[manglende > 0],
            x=manglende[manglende > 0].index,
            y=manglende[manglende > 0].values,
            title="Manglende verdier per felt",
            labels={"x": "Egenskap", "y": "Antall manglende"}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Ingen manglende verdier funnet for de valgte egenskapene.")

    # --- Visualisering: fordeling av kompletthet ---
    st.subheader("✅ Fordeling av datakvalitet")
    if "kompletthet_score" in df.columns:
        fig2 = px.histogram(
            df, x="kompletthet_score", nbins=20,
            title="Fordeling av kompletthetsscore per objekt",
            labels={"kompletthet_score": "Kompletthet (andel utfylte felt)"}
        )
        st.plotly_chart(fig2, use_container_width=True)

    # --- Vis data ---
    st.subheader("📊 Data")
    st.dataframe(df.head())

    st.caption("Kilde: Nasjonal vegdatabank (NVDB API v4)")
