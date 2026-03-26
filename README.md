# 🇨🇴 Colombia Municipios API

API REST para validar, normalizar y consultar municipios de Colombia con códigos DANE oficiales.

## ✨ Características

- **Búsqueda fuzzy** — maneja tildes, mayúsculas, variaciones de escritura
- **Validación** — confirma si un texto es un municipio oficial de Colombia
- **Códigos DANE** — datos oficiales con código, departamento y coordenadas
- **Sin base de datos** — datos embebidos, cero dependencias externas

## 🚀 Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/departamentos` | Lista todos los departamentos |
| GET | `/municipios` | Lista municipios (filtrable por departamento) |
| GET | `/municipios/buscar?q=cali` | Búsqueda fuzzy por nombre |
| GET | `/municipios/validar?municipio=bogota` | Valida si es municipio oficial |
| GET | `/municipios/11001` | Obtiene municipio por código DANE |

## 📦 Despliegue en Render (gratis)

1. Sube este proyecto a un repositorio de GitHub
2. Ve a [render.com](https://render.com) y crea una cuenta
3. Click en **New > Web Service**
4. Conecta tu repositorio
5. Render detectará el `render.yaml` automáticamente
6. ¡Listo! Tu API estará en `https://colombia-municipios-api.onrender.com`

## 🖥️ Correr localmente

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Abre http://localhost:8000/docs para ver la documentación interactiva.

## 📋 Ejemplos de uso

```bash
# Buscar municipio con tilde o sin tilde
GET /municipios/buscar?q=bogota
GET /municipios/buscar?q=medellín

# Validar municipio desde un formulario
GET /municipios/validar?municipio=cartagena+de+indias

# Filtrar por departamento
GET /municipios?departamento=VALLE+DEL+CAUCA

# Obtener por código DANE
GET /municipios/76001   # Cali
GET /municipios/05001   # Medellín
```

## 📊 Publicar en RapidAPI

1. Ve a [rapidapi.com/provider](https://rapidapi.com/provider)
2. Crea una nueva API
3. Ingresa la URL base de tu Render deployment
4. Define los endpoints y parámetros
5. Configura un plan Freemium (gratis hasta X llamadas/mes, pago después)
6. Publica 🎉

## 💰 Estrategia de monetización sugerida

- **Free**: 100 requests/mes
- **Basic** ($9.99/mes): 10,000 requests/mes
- **Pro** ($29.99/mes): 100,000 requests/mes + soporte prioritario
