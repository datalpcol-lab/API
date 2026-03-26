from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import unicodedata
import re
import httpx
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Dataset en memoria ─────────────────────────────────────────────────────
MUNICIPIOS = []
_by_dane = {}
_by_norm = {}
_dptos = {}

# ── Fuentes de datos (DIVIPOLA oficial - datos.gov.co) ────────────────────
FUENTES = [
    # Municipios con coordenadas
    "https://www.datos.gov.co/resource/vafm-j2df.json?$limit=1200",
    # Backup: DIVIPOLA sin coordenadas
    "https://www.datos.gov.co/resource/gdxc-w37w.json?$limit=1200",
]

# Coordenadas de fallback por código DANE para los municipios más importantes
COORDENADAS_FALLBACK = {
    "11001": (4.710989, -74.072090), "05001": (6.246631, -75.581775),
    "76001": (3.451390, -76.531940), "08001": (10.963889, -74.796387),
    "13001": (10.391049, -75.479427), "68001": (7.119350, -73.122590),
    "52001": (1.213610, -77.281390), "23001": (8.757780, -75.881390),
    "18001": (1.614680, -75.606340), "19001": (2.441160, -76.606340),
    "20001": (10.463700, -73.253500), "27001": (5.693900, -76.658800),
    "41001": (2.929440, -75.281390), "44001": (11.544480, -72.907190),
    "47001": (11.242780, -74.205280), "50001": (4.142770, -73.626920),
    "54001": (7.893910, -72.507310), "63001": (4.533890, -75.681110),
    "66001": (4.813390, -75.696110), "70001": (9.304440, -75.397500),
    "73001": (4.438610, -75.232220), "15001": (5.535530, -73.368030),
    "17001": (5.070150, -75.513610), "25001": (4.376280, -74.669780),
    "81001": (7.090280, -70.761940), "85001": (5.338610, -72.395000),
    "86001": (1.151940, -76.648060), "88001": (12.534440, -81.722220),
    "91001": (-4.215280, -69.939720), "94001": (3.865280, -67.922220),
    "95001": (2.566940, -72.638060), "97001": (1.197500, -70.172500),
    "99001": (6.189440, -67.481390),
}


def normalize(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = nfkd.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", ascii_text).strip().upper()


def build_indexes():
    global _by_dane, _by_norm, _dptos
    _by_dane = {m["codigo_dane"]: m for m in MUNICIPIOS}
    _by_norm = {}
    for m in MUNICIPIOS:
        key = normalize(m["municipio"])
        _by_norm.setdefault(key, []).append(m)
    _dptos = {}
    for m in MUNICIPIOS:
        _dptos.setdefault(m["codigo_dpto"], m["departamento"])
    logger.info(f"Índices construidos: {len(MUNICIPIOS)} municipios, {len(_dptos)} departamentos")


def parse_municipios(data: list, fuente_idx: int) -> list:
    result = []
    for row in data:
        try:
            if fuente_idx == 0:
                codigo = str(row.get("c_digo_dane_del_municipio", "") or "").strip().zfill(5)
                nombre = str(row.get("nombre_municipio", "") or "").strip().upper()
                codigo_dpto = str(row.get("c_digo_dane_departamento", "") or "").strip().zfill(2)
                departamento = str(row.get("nombre_departamento", "") or "").strip().upper()
                lat = float(row.get("latitud", 0) or 0)
                lng = float(row.get("longitud", 0) or 0)
            else:
                codigo = str(row.get("codigo_municipio", "") or row.get("c_digo_dane_del_municipio", "") or "").strip().zfill(5)
                nombre = str(row.get("nombre_municipio", "") or row.get("municipio", "") or "").strip().upper()
                codigo_dpto = str(row.get("codigo_departamento", "") or row.get("c_digo_dane_departamento", "") or "").strip().zfill(2)
                departamento = str(row.get("nombre_departamento", "") or row.get("departamento", "") or "").strip().upper()
                lat, lng = 0.0, 0.0

            # Aplicar coordenadas de fallback si no hay
            if (lat == 0.0 and lng == 0.0) and codigo in COORDENADAS_FALLBACK:
                lat, lng = COORDENADAS_FALLBACK[codigo]

            if codigo and nombre and len(codigo) >= 4:
                result.append({
                    "codigo_dane": codigo,
                    "municipio": nombre,
                    "codigo_dpto": codigo_dpto,
                    "departamento": departamento,
                    "lat": round(lat, 6),
                    "lng": round(lng, 6),
                })
        except Exception as e:
            logger.warning(f"Error parsing row: {e}")
    return result


async def cargar_municipios():
    global MUNICIPIOS
    async with httpx.AsyncClient(timeout=30) as client:
        for i, url in enumerate(FUENTES):
            try:
                logger.info(f"Descargando dataset desde fuente {i+1}...")
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                parsed = parse_municipios(data, i)
                if len(parsed) > 100:
                    MUNICIPIOS = sorted(parsed, key=lambda x: x["codigo_dane"])
                    build_indexes()
                    logger.info(f"✅ Dataset cargado: {len(MUNICIPIOS)} municipios desde fuente {i+1}")
                    return
                else:
                    logger.warning(f"Fuente {i+1} devolvió pocos registros ({len(parsed)}), intentando siguiente...")
            except Exception as e:
                logger.error(f"Error con fuente {i+1}: {e}")

    logger.error("❌ No se pudo cargar el dataset desde ninguna fuente externa.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await cargar_municipios()
    yield


# ── App ────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Colombia Municipios API",
    description="API para validar, normalizar y consultar municipios de Colombia con códigos DANE oficiales. Datos DIVIPOLA actualizados automáticamente.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/", tags=["Info"])
def root():
    return {
        "api": "Colombia Municipios API",
        "version": "2.0.0",
        "municipios_cargados": len(MUNICIPIOS),
        "departamentos": len(_dptos),
        "endpoints": ["/municipios", "/municipios/buscar", "/municipios/validar", "/municipios/{codigo_dane}", "/departamentos"]
    }


@app.get("/departamentos", tags=["Departamentos"])
def listar_departamentos():
    result = [{"codigo_dpto": k, "departamento": v} for k, v in sorted(_dptos.items())]
    return {"total": len(result), "departamentos": result}


@app.get("/municipios", tags=["Municipios"])
def listar_municipios(
    departamento: str = Query(None, description="Filtrar por nombre o código de departamento"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    data = MUNICIPIOS
    if departamento:
        dpto_norm = normalize(departamento)
        data = [
            m for m in data
            if normalize(m["departamento"]) == dpto_norm or m["codigo_dpto"] == departamento.strip()
        ]
    total = len(data)
    return {"total": total, "limit": limit, "offset": offset, "municipios": data[offset: offset + limit]}


@app.get("/municipios/buscar", tags=["Municipios"])
def buscar_municipio(
    q: str = Query(..., description="Texto de búsqueda. Acepta tildes, variaciones, mayúsculas/minúsculas."),
    departamento: str = Query(None, description="Filtrar por departamento (opcional)"),
):
    q_norm = normalize(q)
    if q_norm in _by_norm:
        results = list(_by_norm[q_norm])
    else:
        results = [m for m in MUNICIPIOS if q_norm in normalize(m["municipio"])]

    if departamento and results:
        dpto_norm = normalize(departamento)
        filtered = [m for m in results if normalize(m["departamento"]) == dpto_norm or m["codigo_dpto"] == departamento.strip()]
        if filtered:
            results = filtered

    return {"query": q, "total": len(results), "municipios": results}


@app.get("/municipios/validar", tags=["Municipios"])
def validar_municipio(
    municipio: str = Query(..., description="Nombre del municipio a validar"),
    departamento: str = Query(None, description="Departamento (opcional, aumenta precisión)"),
):
    q_norm = normalize(municipio)
    candidates = list(_by_norm.get(q_norm, []))

    if departamento:
        dpto_norm = normalize(departamento)
        filtered = [m for m in candidates if normalize(m["departamento"]) == dpto_norm or m["codigo_dpto"] == departamento.strip()]
        if filtered:
            candidates = filtered

    if not candidates:
        return {"valid": False, "query": municipio, "municipio": None, "message": "No se encontró un municipio oficial con ese nombre."}

    return {"valid": True, "query": municipio, "municipio": candidates[0], "message": "Municipio válido encontrado."}


@app.get("/municipios/{codigo_dane}", tags=["Municipios"])
def obtener_municipio(codigo_dane: str):
    m = _by_dane.get(codigo_dane.strip().zfill(5))
    if not m:
        raise HTTPException(status_code=404, detail=f"No se encontró municipio con código DANE '{codigo_dane}'.")
    return m
