# AutoSales-RPA

Sistema de RPA (Robotic Process Automation) para análisis de ventas automotrices. El sistema procesa archivos de Excel complejos, genera un dashboard de KPIs en formato imagen y automatiza la distribución de reportes ejecutivos mediante la API de Twilio para WhatsApp. Diseñado bajo principios de modularidad, manejo robusto de excepciones y escalabilidad.

---

## Estructura del Proyecto

```
AutoSales-RPA/
├── data/
│   └── Ventas Fundamentos.xlsx   # Archivo de datos fuente (no incluido en el repo)
├── output/
│   ├── dashboard_resumen.png     # Dashboard generado automáticamente
│   └── rpa_sales.log             # Archivo de logs de ejecución
├── src/
│   ├── extraction.py             # Carga de datos y merge de DataFrames
│   ├── analytics.py              # Cálculo de KPIs y métricas
│   ├── visualization.py          # Generación del dashboard con Matplotlib
│   ├── notifier.py               # Cliente de Twilio para WhatsApp
│   └── main.py                   # Punto de entrada / Orquestador
├── .env                          # Variables de entorno (credenciales) — NO subir al repo
├── .env.example                  # Plantilla de variables de entorno
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Esquema de Datos

### Hoja `Ventas`
| Campo                  | Tipo    | Descripción                         |
|------------------------|---------|-------------------------------------|
| ID                     | int     | Identificador único de la venta     |
| Fecha                  | date    | Fecha de la transacción             |
| Canal                  | str     | Canal de venta (Showroom, Online…)  |
| Cliente                | str     | Nombre del cliente                  |
| Segmento               | str     | Segmento de mercado                 |
| ID_Vehículo            | str/int | Clave foránea hacia la hoja Vehículos|
| Precio Venta sin IGV   | float   | Precio neto de venta                |
| Sede                   | str     | Sede donde se realizó la venta      |

### Hoja `Vehículos`
| Campo       | Tipo    | Descripción              |
|-------------|---------|--------------------------|
| ID_Vehículo | str/int | Identificador del vehículo|
| MARCA       | str     | Marca del vehículo        |
| MODELO      | str     | Modelo del vehículo       |

> El módulo `extraction.py` realiza un LEFT JOIN entre `Ventas` y `Vehículos` por la columna `ID_Vehículo`.

---

## KPIs Calculados

| KPI                          | Descripción                                  |
|------------------------------|----------------------------------------------|
| Ventas por Sede              | Suma de `Precio Venta sin IGV` agrupada por `Sede` |
| Top 5 Modelos más vendidos   | Modelos con mayor número de ventas           |
| Clientes Únicos              | Conteo de valores únicos en columna `Cliente`|
| Volumen Total de Ventas      | Suma total de `Precio Venta sin IGV`         |

---

## Dashboard (2×2 Subplots)

| Posición | Gráfico                            |
|----------|------------------------------------|
| [0,0]    | Barras — Ventas por Sede           |
| [0,1]    | Barras horizontales — Top 5 Modelos|
| [1,0]    | Pie chart — Distribución por Segmento |
| [1,1]    | Barras — Ventas por Canal          |

El dashboard se guarda en `output/dashboard_resumen.png` sin mostrar ventana emergente.

---

## Requisitos Previos

- Python 3.9+
- Cuenta Twilio con número habilitado para WhatsApp Sandbox
- Archivo Excel fuente con hojas `Ventas` y `Vehículos` (ruta configurable con `DATA_FILE_PATH`)

---

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/Lejayk/AutoSales-RPA.git
cd AutoSales-RPA

# Crear y activar entorno virtual
python -m venv .venv
source .venv/bin/activate       # Linux / macOS
# .venv\Scripts\activate        # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales reales
```

---

## Configuración (`.env`)

```dotenv
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM=whatsapp:+14155238886
TWILIO_TO=whatsapp:+51999999999
DATA_FILE_PATH=data/Ventas Fundamentos.xlsx
SHEET_VENTAS=Ventas
SHEET_VEHICULOS=Vehículos
```

> `DATA_FILE_PATH` puede ser relativo al root del proyecto o una ruta absoluta.
> Si tu Excel usa hojas con otros nombres, configurá `SHEET_VENTAS` y `SHEET_VEHICULOS`.

---

## Ejecución

```bash
python src/main.py
```

Los logs se escriben simultáneamente en la consola y en `output/rpa_sales.log`.

---

## Testing (Pytest)

### Instalar dependencias

```bash
pip install -r requirements.txt
```

### Ejecutar todos los tests

```bash
pytest -q
```

### Ejecutar tests por módulo

```bash
pytest tests/core/test_extraction.py -q
pytest tests/core/test_analytics.py -q
pytest tests/core/test_visualization.py -q
pytest tests/infrastructure/test_notifier.py -q
```

### ¿Qué valida la suite?

- **Extracción**: archivo inexistente, columnas faltantes, merge LEFT correcto.
- **Analytics**: KPIs obligatorios y métricas escalares.
- **Visualización**: creación de `dashboard_resumen.png`.
- **Notificador**: validación de env vars y envío Twilio mockeado (sin llamadas reales).

---

## Qué te falta para que quede 100% funcional

1. **Archivo fuente real** con hojas:
   - `Ventas` / `Vehículos` por defecto
   - o los nombres definidos en `SHEET_VENTAS` y `SHEET_VEHICULOS`
   - Por defecto se usa `data/Ventas Fundamentos.xlsx`
   - Si tu archivo tiene otro nombre/ruta, seteá `DATA_FILE_PATH` en `.env`
2. **Variables de entorno en `.env`**:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_FROM`
   - `TWILIO_TO`
3. (Opcional) `DASHBOARD_URL` si querés adjuntar la imagen en el mensaje de WhatsApp.

---

## Calidad de Código

- **Type Hinting** en todas las funciones públicas.
- **Docstrings** en formato Google.
- **Manejo de excepciones** (`try/except`) para archivos faltantes y errores de API.
- **`logging`** en lugar de `print` para toda la trazabilidad de ejecución.

---

## Dependencias Principales

| Paquete        | Uso                                      |
|----------------|------------------------------------------|
| `pandas`       | Carga y transformación de DataFrames     |
| `openpyxl`     | Motor para leer archivos `.xlsx`         |
| `matplotlib`   | Generación del dashboard PNG             |
| `twilio`       | Envío de mensajes y archivos por WhatsApp|
| `python-dotenv`| Carga de variables de entorno desde `.env`|

---

## Licencia

MIT
