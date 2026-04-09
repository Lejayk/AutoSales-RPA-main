<div align="center">

# 🚗 AutoSales RPA

**Sistema de Robotic Process Automation para análisis de ventas automotrices**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.7%2B-11557C?style=for-the-badge&logo=matplotlib&logoColor=white)](https://matplotlib.org/)
[![Twilio](https://img.shields.io/badge/Twilio-WhatsApp-F22F46?style=for-the-badge&logo=twilio&logoColor=white)](https://www.twilio.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

*Procesa archivos Excel complejos · Genera dashboards de KPIs · Distribuye reportes por WhatsApp*

</div>

---

## 📋 Tabla de Contenidos

- [¿Qué hace este proyecto?](#-qué-hace-este-proyecto)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Esquema de Datos](#-esquema-de-datos)
- [KPIs Calculados](#-kpis-calculados)
- [Dashboard](#-dashboard-2×2-subplots)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Configuración](#-configuración-env)
- [Ejecución](#-ejecución)
- [Testing](#-testing-pytest)
- [Para que quede 100% funcional](#-para-que-quede-100-funcional)
- [Calidad de Código](#-calidad-de-código)
- [Dependencias](#-dependencias-principales)
- [Licencia](#-licencia)

---

## 🤖 ¿Qué hace este proyecto?

AutoSales RPA es un pipeline de automatización que, con un solo comando:

1. 📥 **Extrae** datos de ventas desde un archivo Excel con múltiples hojas y hace un merge inteligente entre `Ventas` y `Vehículos`.
2. 📊 **Calcula** KPIs clave: volumen total, ventas por sede, top modelos y clientes únicos.
3. 🖼️ **Genera** un dashboard visual de 2×2 gráficos exportado como imagen PNG.
4. 📲 **Envía** el reporte automáticamente por WhatsApp usando la API de Twilio.

Diseñado bajo principios de **modularidad**, **manejo robusto de excepciones** y **escalabilidad**.

---

## 📁 Estructura del Proyecto

```
AutoSales-RPA/
├── 📂 data/
│   └── Ventas Fundamentos.xlsx   # Archivo de datos fuente (no incluido en el repo)
├── 📂 output/
│   ├── dashboard_resumen.png     # Dashboard generado automáticamente
│   └── rpa_sales.log             # Archivo de logs de ejecución
├── 📂 src/
│   ├── 📂 core/
│   │   ├── extraction.py         # Carga de datos y merge de DataFrames
│   │   ├── analytics.py          # Cálculo de KPIs y métricas
│   │   └── visualization.py      # Generación del dashboard con Matplotlib
│   ├── 📂 infrastructure/
│   │   └── notifier.py           # Cliente de Twilio para WhatsApp
│   └── main.py                   # Punto de entrada / Orquestador
├── 📂 tests/                     # Suite de tests con Pytest
├── .env                          # Variables de entorno — ⚠️ NO subir al repo
├── .env.example                  # Plantilla de variables de entorno
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🗃️ Esquema de Datos

### Hoja `Ventas`

| Campo                  | Tipo    | Descripción                          |
|------------------------|---------|--------------------------------------|
| `ID`                   | int     | Identificador único de la venta      |
| `Fecha`                | date    | Fecha de la transacción              |
| `Canal`                | str     | Canal de venta (Showroom, Online…)   |
| `Cliente`              | str     | Nombre del cliente                   |
| `Segmento`             | str     | Segmento de mercado                  |
| `ID_Vehículo`          | str/int | Clave foránea → hoja Vehículos       |
| `Precio Venta sin IGV` | float   | Precio neto de venta                 |
| `Sede`                 | str     | Sede donde se realizó la venta       |

### Hoja `Vehículos`

| Campo         | Tipo    | Descripción               |
|---------------|---------|---------------------------|
| `ID_Vehículo` | str/int | Identificador del vehículo|
| `MARCA`       | str     | Marca del vehículo        |
| `MODELO`      | str     | Modelo del vehículo       |

> 💡 `extraction.py` realiza un **LEFT JOIN** entre `Ventas` y `Vehículos` por la columna `ID_Vehículo`.

---

## 📈 KPIs Calculados

| KPI                          | Descripción                                         |
|------------------------------|-----------------------------------------------------|
| 🏢 Ventas por Sede           | Suma de `Precio Venta sin IGV` agrupada por `Sede`  |
| 🚘 Top 5 Modelos más vendidos| Modelos con mayor número de ventas                  |
| 👥 Clientes Únicos           | Conteo de valores únicos en columna `Cliente`       |
| 💰 Volumen Total de Ventas   | Suma total de `Precio Venta sin IGV`                |

---

## 🖼️ Dashboard (2×2 Subplots)

| Posición | Gráfico                               |
|----------|---------------------------------------|
| `[0,0]`  | 📊 Barras — Ventas por Sede           |
| `[0,1]`  | 📉 Barras horizontales — Top 5 Modelos|
| `[1,0]`  | 🥧 Pie chart — Distribución por Segmento |
| `[1,1]`  | 📊 Barras — Ventas por Canal          |

> El dashboard se guarda en `output/dashboard_resumen.png` sin mostrar ventana emergente.

---

## ✅ Requisitos Previos

- 🐍 **Python 3.9+**
- 📞 **Cuenta Twilio** con número habilitado para WhatsApp Sandbox
- 📄 **Archivo Excel** con hojas `Ventas` y `Vehículos` (ruta configurable via `DATA_FILE_PATH`)

---

## 🚀 Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/Lejayk/AutoSales-RPA.git
cd AutoSales-RPA

# 2. Crear y activar entorno virtual
python -m venv .venv
source .venv/bin/activate       # Linux / macOS
# .venv\Scripts\activate        # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales reales
```

---

## ⚙️ Configuración (`.env`)

```dotenv
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM=whatsapp:+14155238886
TWILIO_TO=whatsapp:+51999999999
DATA_FILE_PATH=data/Ventas Fundamentos.xlsx
SHEET_VENTAS=Ventas
SHEET_VEHICULOS=Vehículos
```

> 📌 `DATA_FILE_PATH` puede ser relativo al root del proyecto o una ruta absoluta.  
> 📌 Si tu Excel usa hojas con otros nombres, configurá `SHEET_VENTAS` y `SHEET_VEHICULOS`.

---

## ▶️ Ejecución

```bash
python src/main.py
```

> Los logs se escriben simultáneamente en la **consola** y en `output/rpa_sales.log`.

---

## 🧪 Testing (Pytest)

```bash
# Ejecutar toda la suite
pytest -q

# Ejecutar por módulo
pytest tests/core/test_extraction.py -q
pytest tests/core/test_analytics.py -q
pytest tests/core/test_visualization.py -q
pytest tests/infrastructure/test_notifier.py -q
```

### ¿Qué valida la suite?

| Módulo           | Cobertura                                                       |
|------------------|-----------------------------------------------------------------|
| 📥 Extracción    | Archivo inexistente, columnas faltantes, merge LEFT correcto    |
| 📈 Analytics     | KPIs obligatorios y métricas escalares                          |
| 🖼️ Visualización | Creación de `dashboard_resumen.png`                             |
| 📲 Notificador   | Validación de env vars y envío Twilio mockeado (sin llamadas reales) |

---

## 🔧 Para que quede 100% funcional

1. **Archivo fuente real** con hojas:
   - `Ventas` y `Vehículos` (nombres por defecto)
   - O los nombres definidos en `SHEET_VENTAS` / `SHEET_VEHICULOS`
   - Ruta por defecto: `data/Ventas Fundamentos.xlsx`
   - Si tu archivo tiene otra ruta, configurá `DATA_FILE_PATH` en `.env`

2. **Variables de entorno** en `.env`:

   | Variable              | Descripción                         |
   |-----------------------|-------------------------------------|
   | `TWILIO_ACCOUNT_SID`  | SID de tu cuenta Twilio             |
   | `TWILIO_AUTH_TOKEN`   | Token de autenticación de Twilio    |
   | `TWILIO_FROM`         | Número Twilio habilitado (WhatsApp) |
   | `TWILIO_TO`           | Número destinatario (WhatsApp)      |

3. *(Opcional)* `DASHBOARD_URL` si querés adjuntar la imagen en el mensaje de WhatsApp.

---

## 🏆 Calidad de Código

| Práctica              | Descripción                                                        |
|-----------------------|--------------------------------------------------------------------|
| 🔷 Type Hinting       | Todas las funciones públicas incluyen anotaciones de tipo          |
| 📝 Docstrings         | Formato Google en todas las funciones y módulos                    |
| 🛡️ Manejo de errores  | `try/except` para archivos faltantes y errores de API              |
| 📋 Logging            | `logging` en lugar de `print` para trazabilidad completa           |

---

## 📦 Dependencias Principales

| Paquete          | Versión  | Uso                                        |
|------------------|----------|--------------------------------------------|
| `pandas`         | ≥ 2.0.0  | Carga y transformación de DataFrames       |
| `openpyxl`       | ≥ 3.1.0  | Motor para leer archivos `.xlsx`           |
| `matplotlib`     | ≥ 3.7.0  | Generación del dashboard PNG               |
| `twilio`         | ≥ 8.0.0  | Envío de mensajes y archivos por WhatsApp  |
| `cloudinary`     | ≥ 1.36.0 | Hosting de imágenes para adjuntos          |
| `python-dotenv`  | ≥ 1.0.0  | Carga de variables de entorno desde `.env` |
| `pytest`         | ≥ 8.0.0  | Framework de testing                       |

---

## 📄 Licencia

Este proyecto está bajo la licencia **MIT**. Podés usarlo, modificarlo y distribuirlo libremente.

---

<div align="center">

Hecho con ❤️ por [Lejayk](https://github.com/Lejayk)

</div>
