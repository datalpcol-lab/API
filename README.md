# 🇨🇴 Colombia Municipios API

> Validate, normalize and query all **1,121 Colombian municipalities** with official DANE codes, departments and coordinates. No database required.

**[🔗 Live API on RapidAPI](https://rapidapi.com/TU_LINK_AQUI)** · **[📖 Docs](https://api-zdqs.onrender.com/docs)**

---

## ✨ Features

- **Fuzzy search** — handles accents, uppercase, spelling variations (`bogota` = `Bogotá`)
- **Official validation** — confirms if a string is a real Colombian municipality
- **DANE codes** — official government codes (DIVIPOLA) for all municipalities
- **Departments** — full department name and code included
- **Coordinates** — latitude and longitude for every municipality
- **No database** — in-memory dataset, zero cold-start latency on queries
- **1,121 municipalities · 33 departments** — full national coverage

---

## 🚀 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/departamentos` | List all 33 departments |
| GET | `/municipios` | List municipalities (filterable by department) |
| GET | `/municipios/buscar?q=cali` | Fuzzy search by name |
| GET | `/municipios/validar?municipio=bogota` | Validate if official municipality |
| GET | `/municipios/{codigo_dane}` | Get municipality by DANE code |

---

## 📋 Response Example

```json
GET /municipios/11001

{
  "codigo_dane": "11001",
  "municipio": "BOGOTÁ, D.C.",
  "codigo_dpto": "11",
  "departamento": "BOGOTÁ, D.C.",
  "lat": 4.710989,
  "lng": -74.072090
}
```

---

## 💡 Use Cases

- 📦 **Logistics & e-commerce** — validate shipping destinations in Colombia
- 📝 **Registration forms** — autocomplete and validate city fields
- 🏦 **Fintech / KYC** — verify user location data against official records
- 🗺️ **Geo apps** — get coordinates for any Colombian municipality
- 🏛️ **Govtech** — integrate official DANE codes into public sector apps

---

## 📦 Quick Start

```bash
# Search — handles accents and case insensitive
GET /municipios/buscar?q=bogota
GET /municipios/buscar?q=medellín

# Validate a municipality from a form input
GET /municipios/validar?municipio=cartagena+de+indias

# Filter all municipalities by department
GET /municipios?departamento=VALLE+DEL+CAUCA

# Lookup by official DANE code
GET /municipios/76001   # Cali
GET /municipios/05001   # Medellín
GET /municipios/11001   # Bogotá
```

---

## 🖥️ Run Locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Open http://localhost:8000/docs for interactive Swagger documentation.

---

## 📊 Data Source

Data sourced from **DIVIPOLA** — the official Colombian municipality and territory registry maintained by DANE (Departamento Administrativo Nacional de Estadística). Updated automatically on startup.

- 🔗 [datos.gov.co](https://www.datos.gov.co)
- 🔗 [DANE DIVIPOLA](https://www.dane.gov.co/index.php/sistema-estadistico-nacional-sen/normas-y-estandares/nomenclaturas-y-clasificaciones/clasificaciones/divipola-codigos-municipios)

---

## 🛠️ Tech Stack

- **FastAPI** — Python REST framework
- **Uvicorn** — ASGI server
- **httpx** — async HTTP client for data fetching
- **Render** — cloud deployment

---

## 📄 License

MIT License — free to use in personal and commercial projects.
