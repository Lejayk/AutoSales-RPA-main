# Guía de Ejecución — AutoSales-RPA

## Requisitos del sistema

| Requisito       | Versión mínima |
|-----------------|----------------|
| Python          | 3.9+           |
| pip             | cualquiera     |
| Windows / macOS | ✓              |

---

## 1. Clonar el repositorio

```bash
git clone https://github.com/Lejayk/AutoSales-RPA.git
cd AutoSales-RPA
```

---

## 2. Crear y activar el entorno virtual

```bash
# Crear
python -m venv .venv
```

### Activar en Windows

**Opción A — PowerShell (requiere permiso de scripts, ver nota):**
```powershell
.venv\Scripts\Activate.ps1
```

> ⚠️ **Error frecuente en Windows**: PowerShell puede bloquear este script con `UnauthorizedAccess`.
> Soluciones disponibles:
>
> **1. Habilitar scripts para tu usuario (recomendado si vas a usar `.ps1` habitualmente):**
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
>
> **2. Usar CMD en lugar de PowerShell:**
> ```cmd
> .venv\Scripts\activate.bat
> ```
>
> **3. No activar el venv — usar Python directamente (más simple para este proyecto):**
> ```powershell
> .venv\Scripts\python.exe src\main.py
> ```

**Opción B — macOS / Linux:**
```bash
source .venv/bin/activate
```

---

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

Paquetes que se instalan: `pandas`, `openpyxl`, `matplotlib`, `twilio`, `python-dotenv`, `pytest`.

---

## 4. Configurar el archivo `.env`

Copiá la plantilla y editala:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Editá `.env` con los valores reales:

```dotenv
# Twilio — dejarlo vacío si no querés notificaciones por WhatsApp
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM=
TWILIO_TO=

# Ruta al archivo Excel (relativa desde la raíz del proyecto)
DATA_FILE_PATH=data/Ventas - Fundamentos.xlsx

# Nombres de hojas del workbook — verificar con Excel antes de correr
SHEET_VENTAS=VENTAS
SHEET_VEHICULOS=VEHICULOS
```

> ⚠️ **Importante**: los nombres de las hojas son sensibles a mayúsculas/minúsculas.
> Para verificar los nombres reales del workbook, ejecutá:
> ```bash
> .venv\Scripts\python.exe -c "import openpyxl; wb = openpyxl.load_workbook('data/Ventas - Fundamentos.xlsx', read_only=True); print(wb.sheetnames)"
> ```

---

## 5. Ejecutar la aplicación

```bash
# Con el entorno virtual activo
python src/main.py

# Sin activar el entorno (Windows)
.venv\Scripts\python.exe src\main.py
```

### Salida esperada

```
2026-04-09 14:59:16 | INFO  | __main__          | AutoSales-RPA - Starting run
2026-04-09 14:59:16 | INFO  | core.extraction   | Loading workbook from ...
2026-04-09 14:59:18 | INFO  | core.extraction   | Workbook loaded: 14202 ventas rows, 179 vehículos rows.
2026-04-09 14:59:18 | INFO  | core.analytics    | KPIs ready | total_sales=14202 | unique_clients=14140 | total_billed=412933546.00
2026-04-09 14:59:19 | INFO  | core.visualization| Dashboard saved: output/dashboard_resumen.png
2026-04-09 14:59:19 | INFO  | __main__          | AutoSales-RPA run complete.
```

### Artefactos generados

| Archivo                      | Descripción                        |
|------------------------------|------------------------------------|
| `output/dashboard_resumen.png` | Dashboard con 4 gráficos de KPIs |
| `output/rpa_sales.log`       | Log completo de la ejecución       |

---

## 6. Notificación por WhatsApp (opcional)

Para activar el envío del reporte vía Twilio, completá estas variables en `.env`:

```dotenv
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=tu_token_real
TWILIO_FROM=whatsapp:+14155238886
TWILIO_TO=whatsapp:+549XXXXXXXXXX
```

> Si las variables están vacías, el paso de notificación se **saltea automáticamente** sin error.

---

## 7. Correr los tests

```bash
# Todos los tests
pytest -q

# Por módulo
pytest tests/core/test_extraction.py -q
pytest tests/core/test_analytics.py -q
pytest tests/core/test_visualization.py -q
pytest tests/infrastructure/test_notifier.py -q
```

---

## Troubleshooting

| Síntoma | Causa probable | Solución |
|---------|---------------|----------|
| `No module named 'dotenv'` | Dependencias no instaladas o venv no activado | `pip install -r requirements.txt` |
| `Worksheet named 'Ventas' not found` | Nombres de hoja no coinciden | Verificar con el script de openpyxl (paso 4) y actualizar `.env` |
| `FileNotFoundError` en el Excel | Ruta incorrecta en `DATA_FILE_PATH` | Revisar que el archivo exista en `data/` y que el nombre sea exacto |
| Dashboard no se genera | Error en matplotlib | Revisar `output/rpa_sales.log` para el traceback completo |

---

## Flujo interno del sistema

```
Excel (.xlsx)
    │
    ▼
extraction.py  ──►  LEFT JOIN (Ventas ⊕ Vehículos)
    │
    ▼
analytics.py   ──►  KPIs (total, por sede, por modelo, por canal)
    │
    ▼
visualization.py ──►  Dashboard 2×2 → output/dashboard_resumen.png
    │
    ▼
notifier.py    ──►  WhatsApp vía Twilio (opcional)
```
