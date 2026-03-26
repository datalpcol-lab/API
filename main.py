from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import unicodedata
import re
import json

app = FastAPI(
    title="Colombia Municipios API",
    description="API para validar, normalizar y consultar municipios de Colombia con códigos DANE oficiales.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Dataset embebido (fuente: DANE / datos.gov.co) ──────────────────────────
MUNICIPIOS = [
    {"codigo_dane": "05001", "municipio": "MEDELLÍN",             "codigo_dpto": "05", "departamento": "ANTIOQUIA",           "lat": 6.246631,  "lng": -75.581775},
    {"codigo_dane": "05002", "municipio": "ABEJORRAL",            "codigo_dpto": "05", "departamento": "ANTIOQUIA",           "lat": 5.789315,  "lng": -75.428739},
    {"codigo_dane": "05004", "municipio": "ABRIAQUÍ",             "codigo_dpto": "05", "departamento": "ANTIOQUIA",           "lat": 6.632282,  "lng": -76.064304},
    {"codigo_dane": "05021", "municipio": "ALEJANDRÍA",           "codigo_dpto": "05", "departamento": "ANTIOQUIA",           "lat": 6.376061,  "lng": -75.141346},
    {"codigo_dane": "05030", "municipio": "AMAGÁ",                "codigo_dpto": "05", "departamento": "ANTIOQUIA",           "lat": 6.038708,  "lng": -75.702188},
    {"codigo_dane": "05031", "municipio": "AMALFI",               "codigo_dpto": "05", "departamento": "ANTIOQUIA",           "lat": 6.909655,  "lng": -75.077501},
    {"codigo_dane": "05034", "municipio": "ANDES",                "codigo_dpto": "05", "departamento": "ANTIOQUIA",           "lat": 5.657194,  "lng": -75.878828},
    {"codigo_dane": "05042", "municipio": "SANTA FÉ DE ANTIOQUIA","codigo_dpto": "05", "departamento": "ANTIOQUIA",           "lat": 6.556484,  "lng": -75.826648},
    {"codigo_dane": "05045", "municipio": "APARTADÓ",             "codigo_dpto": "05", "departamento": "ANTIOQUIA",           "lat": 7.882968,  "lng": -76.625279},
    {"codigo_dane": "05088", "municipio": "BELLO",                "codigo_dpto": "05", "departamento": "ANTIOQUIA",           "lat": 6.337618,  "lng": -75.556092},
    {"codigo_dane": "05129", "municipio": "CALDAS",               "codigo_dpto": "05", "departamento": "ANTIOQUIA",           "lat": 6.094440,  "lng": -75.635094},
    {"codigo_dane": "05197", "municipio": "COPACABANA",           "codigo_dpto": "05", "departamento": "ANTIOQUIA",           "lat": 6.349432,  "lng": -75.506015},
    {"codigo_dane": "05266", "municipio": "ENVIGADO",             "codigo_dpto": "05", "departamento": "ANTIOQUIA",           "lat": 6.175238,  "lng": -75.591692},
    {"codigo_dane": "05308", "municipio": "GIRARDOTA",            "codigo_dpto": "05", "departamento": "ANTIOQUIA",           "lat": 6.377881,  "lng": -75.447775},
    {"codigo_dane": "05360", "municipio": "ITAGÜÍ",               "codigo_dpto": "05", "departamento": "ANTIOQUIA",           "lat": 6.185013,  "lng": -75.599152},
    {"codigo_dane": "05376", "municipio": "JERICÓ",               "codigo_dpto": "05", "departamento": "ANTIOQUIA",           "lat": 5.790146,  "lng": -75.782476},
    {"codigo_dane": "05440", "municipio": "LA ESTRELLA",          "codigo_dpto": "05", "departamento": "ANTIOQUIA",           "lat": 6.158055,  "lng": -75.641390},
    {"codigo_dane": "05615", "municipio": "RIONEGRO",             "codigo_dpto": "05", "departamento": "ANTIOQUIA",           "lat": 6.154705,  "lng": -75.374237},
    {"codigo_dane": "05658", "municipio": "SABANETA",             "codigo_dpto": "05", "departamento": "ANTIOQUIA",           "lat": 6.150916,  "lng": -75.617048},
    {"codigo_dane": "05837", "municipio": "TURBO",                "codigo_dpto": "05", "departamento": "ANTIOQUIA",           "lat": 8.099489,  "lng": -76.728149},
    # ATLÁNTICO
    {"codigo_dane": "08001", "municipio": "BARRANQUILLA",         "codigo_dpto": "08", "departamento": "ATLÁNTICO",           "lat": 10.963889, "lng": -74.796387},
    {"codigo_dane": "08078", "municipio": "BARANOA",              "codigo_dpto": "08", "departamento": "ATLÁNTICO",           "lat": 10.797596, "lng": -74.923128},
    {"codigo_dane": "08137", "municipio": "CAMPO DE LA CRUZ",     "codigo_dpto": "08", "departamento": "ATLÁNTICO",           "lat": 10.378030, "lng": -74.882819},
    {"codigo_dane": "08296", "municipio": "GALAPA",               "codigo_dpto": "08", "departamento": "ATLÁNTICO",           "lat": 10.898750, "lng": -74.888031},
    {"codigo_dane": "08433", "municipio": "MALAMBO",              "codigo_dpto": "08", "departamento": "ATLÁNTICO",           "lat": 10.860892, "lng": -74.771545},
    {"codigo_dane": "08520", "municipio": "PALMAR DE VARELA",     "codigo_dpto": "08", "departamento": "ATLÁNTICO",           "lat": 10.742560, "lng": -74.752060},
    {"codigo_dane": "08549", "municipio": "POLONUEVO",            "codigo_dpto": "08", "departamento": "ATLÁNTICO",           "lat": 10.779150, "lng": -74.852310},
    {"codigo_dane": "08558", "municipio": "PONEDERA",             "codigo_dpto": "08", "departamento": "ATLÁNTICO",           "lat": 10.642950, "lng": -74.754660},
    {"codigo_dane": "08573", "municipio": "PUERTO COLOMBIA",      "codigo_dpto": "08", "departamento": "ATLÁNTICO",           "lat": 11.008620, "lng": -74.956310},
    {"codigo_dane": "08675", "municipio": "SABANAGRANDE",         "codigo_dpto": "08", "departamento": "ATLÁNTICO",           "lat": 10.800610, "lng": -74.752550},
    {"codigo_dane": "08685", "municipio": "SABANALARGA",          "codigo_dpto": "08", "departamento": "ATLÁNTICO",           "lat": 10.630900, "lng": -74.920560},
    {"codigo_dane": "08758", "municipio": "SOLEDAD",              "codigo_dpto": "08", "departamento": "ATLÁNTICO",           "lat": 10.911940, "lng": -74.766670},
    # BOGOTÁ D.C.
    {"codigo_dane": "11001", "municipio": "BOGOTÁ D.C.",          "codigo_dpto": "11", "departamento": "BOGOTÁ D.C.",         "lat": 4.710989,  "lng": -74.072090},
    # BOLÍVAR
    {"codigo_dane": "13001", "municipio": "CARTAGENA DE INDIAS",  "codigo_dpto": "13", "departamento": "BOLÍVAR",             "lat": 10.391049, "lng": -75.479427},
    {"codigo_dane": "13074", "municipio": "MAGANGUÉ",             "codigo_dpto": "13", "departamento": "BOLÍVAR",             "lat": 9.241060,  "lng": -74.757220},
    {"codigo_dane": "13140", "municipio": "CALAMAR",              "codigo_dpto": "13", "departamento": "BOLÍVAR",             "lat": 10.254730, "lng": -74.915230},
    {"codigo_dane": "13430", "municipio": "MOMPOX",               "codigo_dpto": "13", "departamento": "BOLÍVAR",             "lat": 9.241890,  "lng": -74.426610},
    # BOYACÁ
    {"codigo_dane": "15001", "municipio": "TUNJA",                "codigo_dpto": "15", "departamento": "BOYACÁ",              "lat": 5.535530,  "lng": -73.368030},
    {"codigo_dane": "15176", "municipio": "CHIQUINQUIRÁ",         "codigo_dpto": "15", "departamento": "BOYACÁ",              "lat": 5.618010,  "lng": -73.818170},
    {"codigo_dane": "15238", "municipio": "DUITAMA",              "codigo_dpto": "15", "departamento": "BOYACÁ",              "lat": 5.828170,  "lng": -73.028490},
    {"codigo_dane": "15572", "municipio": "PAIPA",                "codigo_dpto": "15", "departamento": "BOYACÁ",              "lat": 5.779630,  "lng": -73.116400},
    {"codigo_dane": "15696", "municipio": "SOGAMOSO",             "codigo_dpto": "15", "departamento": "BOYACÁ",              "lat": 5.716780,  "lng": -72.934410},
    {"codigo_dane": "15759", "municipio": "VILLA DE LEYVA",       "codigo_dpto": "15", "departamento": "BOYACÁ",              "lat": 5.633580,  "lng": -73.526880},
    # CALDAS
    {"codigo_dane": "17001", "municipio": "MANIZALES",            "codigo_dpto": "17", "departamento": "CALDAS",              "lat": 5.070150,  "lng": -75.513610},
    {"codigo_dane": "17042", "municipio": "ANSERMA",              "codigo_dpto": "17", "departamento": "CALDAS",              "lat": 5.224920,  "lng": -75.793820},
    {"codigo_dane": "17088", "municipio": "CHINCHINÁ",            "codigo_dpto": "17", "departamento": "CALDAS",              "lat": 4.985700,  "lng": -75.601500},
    {"codigo_dane": "17380", "municipio": "LA DORADA",            "codigo_dpto": "17", "departamento": "CALDAS",              "lat": 5.454210,  "lng": -74.669130},
    {"codigo_dane": "17444", "municipio": "MANZANARES",           "codigo_dpto": "17", "departamento": "CALDAS",              "lat": 5.259680,  "lng": -75.155360},
    {"codigo_dane": "17541", "municipio": "RIOSUCIO",             "codigo_dpto": "17", "departamento": "CALDAS",              "lat": 5.414560,  "lng": -75.694040},
    # CAQUETÁ
    {"codigo_dane": "18001", "municipio": "FLORENCIA",            "codigo_dpto": "18", "departamento": "CAQUETÁ",             "lat": 1.614680,  "lng": -75.606340},
    # CAUCA
    {"codigo_dane": "19001", "municipio": "POPAYÁN",              "codigo_dpto": "19", "departamento": "CAUCA",               "lat": 2.441160,  "lng": -76.606340},
    {"codigo_dane": "19022", "municipio": "ALMAGUER",             "codigo_dpto": "19", "departamento": "CAUCA",               "lat": 1.917510,  "lng": -76.871170},
    # CESAR
    {"codigo_dane": "20001", "municipio": "VALLEDUPAR",           "codigo_dpto": "20", "departamento": "CESAR",               "lat": 10.463700, "lng": -73.253500},
    {"codigo_dane": "20045", "municipio": "BOSCONIA",             "codigo_dpto": "20", "departamento": "CESAR",               "lat": 9.975700,  "lng": -73.898800},
    {"codigo_dane": "20175", "municipio": "CHIRIGUANÁ",           "codigo_dpto": "20", "departamento": "CESAR",               "lat": 9.360600,  "lng": -73.607700},
    # CHOCÓ
    {"codigo_dane": "27001", "municipio": "QUIBDÓ",               "codigo_dpto": "27", "departamento": "CHOCÓ",               "lat": 5.693900,  "lng": -76.658800},
    # CÓRDOBA
    {"codigo_dane": "23001", "municipio": "MONTERÍA",             "codigo_dpto": "23", "departamento": "CÓRDOBA",             "lat": 8.757780,  "lng": -75.881390},
    {"codigo_dane": "23162", "municipio": "CERETÉ",               "codigo_dpto": "23", "departamento": "CÓRDOBA",             "lat": 8.884890,  "lng": -75.791140},
    {"codigo_dane": "23417", "municipio": "LORICA",               "codigo_dpto": "23", "departamento": "CÓRDOBA",             "lat": 9.241390,  "lng": -75.814170},
    # CUNDINAMARCA
    {"codigo_dane": "25001", "municipio": "AGUA DE DIOS",         "codigo_dpto": "25", "departamento": "CUNDINAMARCA",        "lat": 4.376280,  "lng": -74.669780},
    {"codigo_dane": "25175", "municipio": "CHÍA",                 "codigo_dpto": "25", "departamento": "CUNDINAMARCA",        "lat": 4.862690,  "lng": -74.063210},
    {"codigo_dane": "25269", "municipio": "FACATATIVÁ",           "codigo_dpto": "25", "departamento": "CUNDINAMARCA",        "lat": 4.816670,  "lng": -74.354170},
    {"codigo_dane": "25290", "municipio": "FUSAGASUGÁ",           "codigo_dpto": "25", "departamento": "CUNDINAMARCA",        "lat": 4.337720,  "lng": -74.364130},
    {"codigo_dane": "25307", "municipio": "GIRARDOT",             "codigo_dpto": "25", "departamento": "CUNDINAMARCA",        "lat": 4.303050,  "lng": -74.802140},
    {"codigo_dane": "25473", "municipio": "MOSQUERA",             "codigo_dpto": "25", "departamento": "CUNDINAMARCA",        "lat": 4.706530,  "lng": -74.230760},
    {"codigo_dane": "25486", "municipio": "NEMOCÓN",              "codigo_dpto": "25", "departamento": "CUNDINAMARCA",        "lat": 5.074390,  "lng": -73.876950},
    {"codigo_dane": "25513", "municipio": "PACHO",                "codigo_dpto": "25", "departamento": "CUNDINAMARCA",        "lat": 5.133330,  "lng": -74.158330},
    {"codigo_dane": "25612", "municipio": "SOACHA",               "codigo_dpto": "25", "departamento": "CUNDINAMARCA",        "lat": 4.579640,  "lng": -74.217020},
    {"codigo_dane": "25754", "municipio": "TABIO",                "codigo_dpto": "25", "departamento": "CUNDINAMARCA",        "lat": 4.913060,  "lng": -74.099170},
    {"codigo_dane": "25785", "municipio": "TOCANCIPÁ",            "codigo_dpto": "25", "departamento": "CUNDINAMARCA",        "lat": 4.965560,  "lng": -73.912780},
    {"codigo_dane": "25817", "municipio": "UBATÉ",                "codigo_dpto": "25", "departamento": "CUNDINAMARCA",        "lat": 5.313890,  "lng": -73.817220},
    {"codigo_dane": "25873", "municipio": "VILLETA",              "codigo_dpto": "25", "departamento": "CUNDINAMARCA",        "lat": 5.009170,  "lng": -74.471940},
    {"codigo_dane": "25878", "municipio": "ZIPACÓN",              "codigo_dpto": "25", "departamento": "CUNDINAMARCA",        "lat": 4.747780,  "lng": -74.356670},
    {"codigo_dane": "25899", "municipio": "ZIPAQUIRÁ",            "codigo_dpto": "25", "departamento": "CUNDINAMARCA",        "lat": 5.022780,  "lng": -74.006390},
    # GUAJIRA
    {"codigo_dane": "44001", "municipio": "RIOHACHA",             "codigo_dpto": "44", "departamento": "LA GUAJIRA",          "lat": 11.544480, "lng": -72.907190},
    {"codigo_dane": "44430", "municipio": "MAICAO",               "codigo_dpto": "44", "departamento": "LA GUAJIRA",          "lat": 11.380280, "lng": -72.244440},
    {"codigo_dane": "44560", "municipio": "MANAURE",              "codigo_dpto": "44", "departamento": "LA GUAJIRA",          "lat": 11.778170, "lng": -72.447220},
    {"codigo_dane": "44847", "municipio": "URIBIA",               "codigo_dpto": "44", "departamento": "LA GUAJIRA",          "lat": 11.714720, "lng": -72.276110},
    # HUILA
    {"codigo_dane": "41001", "municipio": "NEIVA",                "codigo_dpto": "41", "departamento": "HUILA",               "lat": 2.929440,  "lng": -75.281390},
    {"codigo_dane": "41132", "municipio": "CAMPOALEGRE",          "codigo_dpto": "41", "departamento": "HUILA",               "lat": 2.690550,  "lng": -75.329720},
    {"codigo_dane": "41298", "municipio": "GARZÓN",               "codigo_dpto": "41", "departamento": "HUILA",               "lat": 2.197500,  "lng": -75.627220},
    {"codigo_dane": "41503", "municipio": "PITALITO",             "codigo_dpto": "41", "departamento": "HUILA",               "lat": 1.854440,  "lng": -76.050830},
    # MAGDALENA
    {"codigo_dane": "47001", "municipio": "SANTA MARTA",          "codigo_dpto": "47", "departamento": "MAGDALENA",           "lat": 11.242780, "lng": -74.205280},
    {"codigo_dane": "47189", "municipio": "CIÉNAGA",              "codigo_dpto": "47", "departamento": "MAGDALENA",           "lat": 11.003610, "lng": -74.247500},
    {"codigo_dane": "47460", "municipio": "FUNDACIÓN",            "codigo_dpto": "47", "departamento": "MAGDALENA",           "lat": 10.524440, "lng": -74.189170},
    # META
    {"codigo_dane": "50001", "municipio": "VILLAVICENCIO",        "codigo_dpto": "50", "departamento": "META",                "lat": 4.142770,  "lng": -73.626920},
    {"codigo_dane": "50006", "municipio": "ACACÍAS",              "codigo_dpto": "50", "departamento": "META",                "lat": 3.987500,  "lng": -73.762500},
    {"codigo_dane": "50226", "municipio": "CUMARAL",              "codigo_dpto": "50", "departamento": "META",                "lat": 4.272500,  "lng": -73.487500},
    # NARIÑO
    {"codigo_dane": "52001", "municipio": "PASTO",                "codigo_dpto": "52", "departamento": "NARIÑO",              "lat": 1.213610,  "lng": -77.281390},
    {"codigo_dane": "52356", "municipio": "IPIALES",              "codigo_dpto": "52", "departamento": "NARIÑO",              "lat": 0.830280,  "lng": -77.644440},
    {"codigo_dane": "52835", "municipio": "TUMACO",               "codigo_dpto": "52", "departamento": "NARIÑO",              "lat": 1.808060,  "lng": -78.762500},
    # NORTE DE SANTANDER
    {"codigo_dane": "54001", "municipio": "CÚCUTA",               "codigo_dpto": "54", "departamento": "NORTE DE SANTANDER",  "lat": 7.893910,  "lng": -72.507310},
    {"codigo_dane": "54245", "municipio": "EL ZULIA",             "codigo_dpto": "54", "departamento": "NORTE DE SANTANDER",  "lat": 7.937500,  "lng": -72.607500},
    {"codigo_dane": "54498", "municipio": "OCAÑA",                "codigo_dpto": "54", "departamento": "NORTE DE SANTANDER",  "lat": 8.238060,  "lng": -73.355280},
    {"codigo_dane": "54518", "municipio": "PAMPLONA",             "codigo_dpto": "54", "departamento": "NORTE DE SANTANDER",  "lat": 7.378060,  "lng": -72.648060},
    {"codigo_dane": "54720", "municipio": "VILLA DEL ROSARIO",    "codigo_dpto": "54", "departamento": "NORTE DE SANTANDER",  "lat": 7.834720,  "lng": -72.475000},
    # QUINDÍO
    {"codigo_dane": "63001", "municipio": "ARMENIA",              "codigo_dpto": "63", "departamento": "QUINDÍO",             "lat": 4.533890,  "lng": -75.681110},
    {"codigo_dane": "63111", "municipio": "CALARCÁ",              "codigo_dpto": "63", "departamento": "QUINDÍO",             "lat": 4.534440,  "lng": -75.638060},
    {"codigo_dane": "63190", "municipio": "CIRCASIA",             "codigo_dpto": "63", "departamento": "QUINDÍO",             "lat": 4.617500,  "lng": -75.638060},
    {"codigo_dane": "63212", "municipio": "CÓRDOBA",              "codigo_dpto": "63", "departamento": "QUINDÍO",             "lat": 4.377500,  "lng": -75.663060},
    {"codigo_dane": "63401", "municipio": "LA TEBAIDA",           "codigo_dpto": "63", "departamento": "QUINDÍO",             "lat": 4.455000,  "lng": -75.788060},
    # RISARALDA
    {"codigo_dane": "66001", "municipio": "PEREIRA",              "codigo_dpto": "66", "departamento": "RISARALDA",           "lat": 4.813390,  "lng": -75.696110},
    {"codigo_dane": "66045", "municipio": "APÍA",                 "codigo_dpto": "66", "departamento": "RISARALDA",           "lat": 5.105280,  "lng": -75.953060},
    {"codigo_dane": "66170", "municipio": "DOSQUEBRADAS",         "codigo_dpto": "66", "departamento": "RISARALDA",           "lat": 4.849440,  "lng": -75.669720},
    {"codigo_dane": "66400", "municipio": "LA VIRGINIA",          "codigo_dpto": "66", "departamento": "RISARALDA",           "lat": 4.898890,  "lng": -75.879720},
    {"codigo_dane": "66594", "municipio": "SANTA ROSA DE CABAL",  "codigo_dpto": "66", "departamento": "RISARALDA",           "lat": 4.869170,  "lng": -75.621390},
    # SANTANDER
    {"codigo_dane": "68001", "municipio": "BUCARAMANGA",          "codigo_dpto": "68", "departamento": "SANTANDER",           "lat": 7.119350,  "lng": -73.122590},
    {"codigo_dane": "68081", "municipio": "BARRANCABERMEJA",      "codigo_dpto": "68", "departamento": "SANTANDER",           "lat": 7.064440,  "lng": -73.854720},
    {"codigo_dane": "68276", "municipio": "FLORIDABLANCA",        "codigo_dpto": "68", "departamento": "SANTANDER",           "lat": 7.065000,  "lng": -73.098060},
    {"codigo_dane": "68307", "municipio": "GIRÓN",                "codigo_dpto": "68", "departamento": "SANTANDER",           "lat": 7.069170,  "lng": -73.169720},
    {"codigo_dane": "68432", "municipio": "MÁLAGA",               "codigo_dpto": "68", "departamento": "SANTANDER",           "lat": 6.701390,  "lng": -72.731390},
    {"codigo_dane": "68547", "municipio": "PIEDECUESTA",          "codigo_dpto": "68", "departamento": "SANTANDER",           "lat": 6.988060,  "lng": -73.052220},
    {"codigo_dane": "68615", "municipio": "RIONEGRO",             "codigo_dpto": "68", "departamento": "SANTANDER",           "lat": 7.371110,  "lng": -73.168890},
    {"codigo_dane": "68679", "municipio": "SAN GIL",              "codigo_dpto": "68", "departamento": "SANTANDER",           "lat": 6.555280,  "lng": -73.134720},
    {"codigo_dane": "68745", "municipio": "SOCORRO",              "codigo_dpto": "68", "departamento": "SANTANDER",           "lat": 6.462500,  "lng": -73.259720},
    {"codigo_dane": "68820", "municipio": "VÉLEZ",                "codigo_dpto": "68", "departamento": "SANTANDER",           "lat": 6.012500,  "lng": -73.672500},
    # SUCRE
    {"codigo_dane": "70001", "municipio": "SINCELEJO",            "codigo_dpto": "70", "departamento": "SUCRE",               "lat": 9.304440,  "lng": -75.397500},
    {"codigo_dane": "70215", "municipio": "COROZAL",              "codigo_dpto": "70", "departamento": "SUCRE",               "lat": 9.321390,  "lng": -75.297500},
    {"codigo_dane": "70233", "municipio": "COVENAS",              "codigo_dpto": "70", "departamento": "SUCRE",               "lat": 9.504440,  "lng": -75.681390},
    {"codigo_dane": "70508", "municipio": "SAN MARCOS",           "codigo_dpto": "70", "departamento": "SUCRE",               "lat": 8.662500,  "lng": -75.124720},
    # TOLIMA
    {"codigo_dane": "73001", "municipio": "IBAGUÉ",               "codigo_dpto": "73", "departamento": "TOLIMA",              "lat": 4.438610,  "lng": -75.232220},
    {"codigo_dane": "73148", "municipio": "CHAPARRAL",            "codigo_dpto": "73", "departamento": "TOLIMA",              "lat": 3.724440,  "lng": -75.488060},
    {"codigo_dane": "73268", "municipio": "ESPINAL",              "codigo_dpto": "73", "departamento": "TOLIMA",              "lat": 4.151390,  "lng": -74.884720},
    {"codigo_dane": "73349", "municipio": "HONDA",                "codigo_dpto": "73", "departamento": "TOLIMA",              "lat": 5.204720,  "lng": -74.741390},
    {"codigo_dane": "73408", "municipio": "LERIDA",               "codigo_dpto": "73", "departamento": "TOLIMA",              "lat": 4.862500,  "lng": -74.931390},
    {"codigo_dane": "73449", "municipio": "MELGAR",               "codigo_dpto": "73", "departamento": "TOLIMA",              "lat": 4.202500,  "lng": -74.630000},
    {"codigo_dane": "73520", "municipio": "PLANADAS",             "codigo_dpto": "73", "departamento": "TOLIMA",              "lat": 3.194720,  "lng": -75.642220},
    # VALLE DEL CAUCA
    {"codigo_dane": "76001", "municipio": "CALI",                 "codigo_dpto": "76", "departamento": "VALLE DEL CAUCA",     "lat": 3.451390,  "lng": -76.531940},
    {"codigo_dane": "76020", "municipio": "ANSERMANUEVO",         "codigo_dpto": "76", "departamento": "VALLE DEL CAUCA",     "lat": 4.793060,  "lng": -75.987500},
    {"codigo_dane": "76054", "municipio": "BUENAVENTURA",         "codigo_dpto": "76", "departamento": "VALLE DEL CAUCA",     "lat": 3.880060,  "lng": -77.032780},
    {"codigo_dane": "76109", "municipio": "BUGA",                 "codigo_dpto": "76", "departamento": "VALLE DEL CAUCA",     "lat": 3.900280,  "lng": -76.298610},
    {"codigo_dane": "76111", "municipio": "BUGALAGRANDE",         "codigo_dpto": "76", "departamento": "VALLE DEL CAUCA",     "lat": 4.208330,  "lng": -76.161390},
    {"codigo_dane": "76130", "municipio": "CAICEDONIA",           "codigo_dpto": "76", "departamento": "VALLE DEL CAUCA",     "lat": 4.331390,  "lng": -75.830830},
    {"codigo_dane": "76147", "municipio": "CARTAGO",              "codigo_dpto": "76", "departamento": "VALLE DEL CAUCA",     "lat": 4.746110,  "lng": -75.911940},
    {"codigo_dane": "76248", "municipio": "EL CERRITO",           "codigo_dpto": "76", "departamento": "VALLE DEL CAUCA",     "lat": 3.689440,  "lng": -76.135830},
    {"codigo_dane": "76364", "municipio": "JAMUNDÍ",              "codigo_dpto": "76", "departamento": "VALLE DEL CAUCA",     "lat": 3.263060,  "lng": -76.537220},
    {"codigo_dane": "76377", "municipio": "LA CUMBRE",            "codigo_dpto": "76", "departamento": "VALLE DEL CAUCA",     "lat": 3.653060,  "lng": -76.565830},
    {"codigo_dane": "76400", "municipio": "LA UNIÓN",             "codigo_dpto": "76", "departamento": "VALLE DEL CAUCA",     "lat": 4.536390,  "lng": -76.100830},
    {"codigo_dane": "76520", "municipio": "PALMIRA",              "codigo_dpto": "76", "departamento": "VALLE DEL CAUCA",     "lat": 3.539440,  "lng": -76.303060},
    {"codigo_dane": "76563", "municipio": "PRADERA",              "codigo_dpto": "76", "departamento": "VALLE DEL CAUCA",     "lat": 3.420830,  "lng": -76.245830},
    {"codigo_dane": "76606", "municipio": "RESTREPO",             "codigo_dpto": "76", "departamento": "VALLE DEL CAUCA",     "lat": 3.826940,  "lng": -76.527220},
    {"codigo_dane": "76616", "municipio": "RIOFRÍO",              "codigo_dpto": "76", "departamento": "VALLE DEL CAUCA",     "lat": 4.076390,  "lng": -76.329720},
    {"codigo_dane": "76622", "municipio": "ROLDANILLO",           "codigo_dpto": "76", "departamento": "VALLE DEL CAUCA",     "lat": 4.414440,  "lng": -76.160000},
    {"codigo_dane": "76670", "municipio": "SAN PEDRO",            "codigo_dpto": "76", "departamento": "VALLE DEL CAUCA",     "lat": 3.946390,  "lng": -76.388060},
    {"codigo_dane": "76736", "municipio": "TULÚA",                "codigo_dpto": "76", "departamento": "VALLE DEL CAUCA",     "lat": 4.084440,  "lng": -76.195000},
    {"codigo_dane": "76845", "municipio": "VERSALLES",            "codigo_dpto": "76", "departamento": "VALLE DEL CAUCA",     "lat": 4.570000,  "lng": -76.268060},
    {"codigo_dane": "76869", "municipio": "VIJES",                "codigo_dpto": "76", "departamento": "VALLE DEL CAUCA",     "lat": 3.696110,  "lng": -76.437500},
    {"codigo_dane": "76890", "municipio": "YOTOCO",               "codigo_dpto": "76", "departamento": "VALLE DEL CAUCA",     "lat": 3.876940,  "lng": -76.378060},
    {"codigo_dane": "76892", "municipio": "YUMBO",                "codigo_dpto": "76", "departamento": "VALLE DEL CAUCA",     "lat": 3.591390,  "lng": -76.492220},
    {"codigo_dane": "76895", "municipio": "ZARZAL",               "codigo_dpto": "76", "departamento": "VALLE DEL CAUCA",     "lat": 4.395000,  "lng": -75.859720},
    # VAUPÉS
    {"codigo_dane": "97001", "municipio": "MITÚ",                 "codigo_dpto": "97", "departamento": "VAUPÉS",              "lat": 1.197500,  "lng": -70.172500},
    # VICHADA
    {"codigo_dane": "99001", "municipio": "PUERTO CARREÑO",       "codigo_dpto": "99", "departamento": "VICHADA",             "lat": 6.189440,  "lng": -67.481390},
    # ARAUCA
    {"codigo_dane": "81001", "municipio": "ARAUCA",               "codigo_dpto": "81", "departamento": "ARAUCA",              "lat": 7.090280,  "lng": -70.761940},
    # CASANARE
    {"codigo_dane": "85001", "municipio": "YOPAL",                "codigo_dpto": "85", "departamento": "CASANARE",            "lat": 5.338610,  "lng": -72.395000},
    {"codigo_dane": "85010", "municipio": "AGUAZUL",              "codigo_dpto": "85", "departamento": "CASANARE",            "lat": 5.172500,  "lng": -72.553060},
    # AMAZONAS
    {"codigo_dane": "91001", "municipio": "LETICIA",              "codigo_dpto": "91", "departamento": "AMAZONAS",            "lat": -4.215280, "lng": -69.939720},
    # PUTUMAYO
    {"codigo_dane": "86001", "municipio": "MOCOA",                "codigo_dpto": "86", "departamento": "PUTUMAYO",            "lat": 1.151940,  "lng": -76.648060},
    {"codigo_dane": "86568", "municipio": "PUERTO ASÍS",          "codigo_dpto": "86", "departamento": "PUTUMAYO",            "lat": 0.505280,  "lng": -76.498610},
    # SAN ANDRÉS
    {"codigo_dane": "88001", "municipio": "SAN ANDRÉS",           "codigo_dpto": "88", "departamento": "ARCHIPIÉLAGO DE SAN ANDRÉS, PROVIDENCIA Y SANTA CATALINA", "lat": 12.534440, "lng": -81.722220},
    # GUAINÍA
    {"codigo_dane": "94001", "municipio": "INÍRIDA",              "codigo_dpto": "94", "departamento": "GUAINÍA",             "lat": 3.865280,  "lng": -67.922220},
    # GUAVIARE
    {"codigo_dane": "95001", "municipio": "SAN JOSÉ DEL GUAVIARE","codigo_dpto": "95", "departamento": "GUAVIARE",            "lat": 2.566940,  "lng": -72.638060},
]

# ── Helpers ────────────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    """Elimina tildes, pasa a mayúsculas y quita espacios extra."""
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = nfkd.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", ascii_text).strip().upper()

# Índices para búsqueda rápida
_by_dane = {m["codigo_dane"]: m for m in MUNICIPIOS}
_by_norm = {}
for m in MUNICIPIOS:
    key = normalize(m["municipio"])
    _by_norm.setdefault(key, []).append(m)

_dptos = {}
for m in MUNICIPIOS:
    _dptos.setdefault(m["codigo_dpto"], m["departamento"])


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/", tags=["Info"])
def root():
    return {
        "api": "Colombia Municipios API",
        "version": "1.0.0",
        "endpoints": ["/municipios", "/municipios/buscar", "/municipios/validar", "/municipios/{codigo_dane}", "/departamentos"]
    }


@app.get("/departamentos", tags=["Departamentos"])
def listar_departamentos():
    """Lista todos los departamentos con su código DANE."""
    result = [{"codigo_dpto": k, "departamento": v} for k, v in sorted(_dptos.items())]
    return {"total": len(result), "departamentos": result}


@app.get("/municipios", tags=["Municipios"])
def listar_municipios(
    departamento: str = Query(None, description="Filtrar por nombre o código de departamento"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """Lista municipios, opcionalmente filtrados por departamento."""
    data = MUNICIPIOS
    if departamento:
        dpto_norm = normalize(departamento)
        data = [
            m for m in data
            if normalize(m["departamento"]) == dpto_norm or m["codigo_dpto"] == departamento.strip()
        ]
    total = len(data)
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "municipios": data[offset: offset + limit]
    }


@app.get("/municipios/buscar", tags=["Municipios"])
def buscar_municipio(
    q: str = Query(..., description="Texto de búsqueda (acepta tildes, mayúsculas/minúsculas, variaciones)"),
    departamento: str = Query(None, description="Filtrar por departamento (opcional)")
):
    """
    Búsqueda fuzzy de municipios. Maneja tildes, variaciones de escritura
    y texto sucio. Ejemplo: 'bogota', 'BOGOTÁ D.C', 'cartagena de indias'.
    """
    q_norm = normalize(q)
    results = []

    # 1. Coincidencia exacta normalizada
    if q_norm in _by_norm:
        results = _by_norm[q_norm]
    else:
        # 2. Búsqueda parcial
        results = [
            m for m in MUNICIPIOS
            if q_norm in normalize(m["municipio"])
        ]

    # Filtro adicional por departamento
    if departamento and results:
        dpto_norm = normalize(departamento)
        results = [
            m for m in results
            if normalize(m["departamento"]) == dpto_norm or m["codigo_dpto"] == departamento.strip()
        ]

    return {
        "query": q,
        "total": len(results),
        "municipios": results
    }


@app.get("/municipios/validar", tags=["Municipios"])
def validar_municipio(
    municipio: str = Query(..., description="Nombre del municipio a validar"),
    departamento: str = Query(None, description="Departamento (opcional, aumenta precisión)")
):
    """
    Valida si un texto corresponde a un municipio oficial de Colombia.
    Devuelve el municipio normalizado con código DANE si es válido.
    Ideal para validar formularios y limpiar bases de datos.
    """
    q_norm = normalize(municipio)
    candidates = _by_norm.get(q_norm, [])

    if departamento:
        dpto_norm = normalize(departamento)
        filtered = [
            m for m in candidates
            if normalize(m["departamento"]) == dpto_norm or m["codigo_dpto"] == departamento.strip()
        ]
        candidates = filtered if filtered else candidates

    if not candidates:
        return {
            "valid": False,
            "query": municipio,
            "municipio": None,
            "message": "No se encontró un municipio oficial con ese nombre."
        }

    best = candidates[0]
    return {
        "valid": True,
        "query": municipio,
        "municipio": best,
        "message": "Municipio válido encontrado."
    }


@app.get("/municipios/{codigo_dane}", tags=["Municipios"])
def obtener_municipio(codigo_dane: str):
    """
    Obtiene un municipio por su código DANE (5 dígitos).
    Ejemplo: 11001 = Bogotá D.C., 05001 = Medellín.
    """
    m = _by_dane.get(codigo_dane.strip())
    if not m:
        raise HTTPException(status_code=404, detail=f"No se encontró municipio con código DANE '{codigo_dane}'.")
    return m
