# 🛣️ NVDB Datakvalitet – Interaktiv utforsker av manglende verdier

Dette prosjektet er et interaktivt **Streamlit-dashboard** som lar brukeren utforske **datakvalitet i Nasjonal Vegdatabank (NVDB)**.  
Applikasjonen henter data direkte fra NVDB API v4 og beregner **kompletthetsscore** for valgte vegobjekttyper basert på utfylte egenskaper.

Prosjektet er utviklet som en demonstrasjon av hvordan moderne dataverktøy og Python kan brukes til å:
- analysere **datakvalitet** på tvers av objekttyper
- identifisere **manglende verdier**
- visualisere **fordelingen av kompletthet**
- gjøre komplekse NVDB-data tilgjengelige og forståelige gjennom **interaktiv visualisering**

---

## 🚀 Funksjonalitet

- **Valg av objekttype:**  
  Brukeren oppgir et objekttypenummer (f.eks. `79` for *Stikkrenne/Kulvert*).  
  Full oversikt finnes i [NVDB Datakatalogen](https://datakatalogen.atlas.vegvesen.no/).

- **Filtrering på viktighet:**  
  Egenskaper kan filtreres etter viktighetsnivå fra NVDB (f.eks. `PÅKREVD_ABSOLUTT`, `OPSJONELL`, etc.).

- **Datakvalitetsanalyse:**  
  Programmet beregner en **kompletthetsscore** for hvert objekt – hvor stor andel av påkrevde egenskaper som er utfylt.

- **Visualiseringer:**
  - Bar-diagram over manglende verdier per felt  
  - Histogram over kompletthetsscore per objekt  
  - Interaktiv datatabell for videre utforsking

- **Caching:**  
  API-responser caches automatisk med `st.cache_data` for raskere ytelse og redusert belastning på NVDB.

---

## 📊 Hva er kompletthetsscore?

Kompletthetsscoren er et enkelt, men effektivt mål på **hvor komplette dataene er**.  
Den beregnes slik:

```python
df["kompletthet_score"] = df[paakrevde_i_data].notna().mean(axis=1)
```

- `True` → feltet er utfylt  
- `False` → feltet mangler  
- gjennomsnittet av disse gir andelen utfylte felter per objekt

Eksempel:

| Lengde | Materialtype | Diameter | Kompletthet |
|---------|---------------|----------|-------------|
| 10.5 | Betong | *NaN* | 0.67 |
| *NaN* | Plast | 1.2 | 0.67 |

Dette gir en skalerbar måte å måle datakvalitet på tvers av ulike objekttyper og felter.

---

## ⚙️ Installasjon og kjøring

1. **Klon prosjektet**
   ```bash
   git clone https://github.com/CaroSky/nvdb.git
   cd nvdb
   ```

2. **Installer avhengigheter**
   ```bash
   pip install -r requirements.txt
   ```

3. **Kjør applikasjonen**
   ```bash
   streamlit run app.py
   ```

4. Åpne nettleseren og gå til adressen Streamlit gir deg, f.eks.  
   `http://localhost:8501`

---

## 🧠 Teknisk arkitektur

- **Frontend:** Streamlit  
- **Backend:** Direkte API-integrasjon mot NVDB API v4 (`https://nvdbapiles.atlas.vegvesen.no`)  
- **Databehandling:** Pandas  
- **Visualisering:** Plotly Express  
- **Caching:** Streamlit `st.cache_data`

---

## 🔍 Eksempel

Når brukeren oppgir objekttypenummer `79` (Stikkrenne/Kulvert) og velger `PÅKREVD_ABSOLUTT`, henter applikasjonen data fra NVDB og visualiserer:
- hvor mange felt som mangler data
- hvordan datakompletthet fordeler seg på tvers av objektene

---

## 💡 Videre forbedringer

Forslag til videre utvikling:
- Filtrering på **fylke og kommune**
- Kartvisning av objekter (via `folium` eller `plotly.mapbox`)
- Eksport til CSV eller Excel
- Beregning av flere kvalitetsmål (nøyaktighet, konsistens, tidsmessighet)
- Integrasjon mot andre NVDB-endepunkter

---

## 📚 Kilder og referanser

- [NVDB API v4 Dokumentasjon](https://nvdbapiles.atlas.vegvesen.no/)
- [NVDB Datakatalogen](https://datakatalogen.atlas.vegvesen.no/)
- [Statens vegvesen – Nasjonal vegdatabank](https://www.vegvesen.no/fag/fokusomrader/nasjonal-vegdatabank/)

---

## 👨‍💻 Om utvikleren

Dette prosjektet er utviklet som en del av en søknad til **Statens vegvesen**.  
Formålet er å demonstrere kompetanse innen:
- dataanalyse og datakvalitet
- API-integrasjon og datastrukturering
- interaktiv visualisering og brukertilpasning
- Python og moderne verktøy for datadrevet beslutningsstøtte
