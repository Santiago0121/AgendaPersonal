import math
from datetime import datetime, date

# ─── Fechas ───────────────────────────────────────────
def dias_para_evento(fecha_str: str) -> int:
    """Cuántos días faltan para una fecha dada (YYYY-MM-DD)."""
    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    return (fecha - date.today()).days

def eventos_proximos(eventos: list, dias: int = 7) -> list:
    """Filtra eventos que ocurren en los próximos N días."""
    return [e for e in eventos if 0 <= dias_para_evento(e["fecha"]) <= dias]

def formatear_fecha(fecha_str: str) -> str:
    """Convierte '2025-05-01' a '1 de mayo de 2025'."""
    meses = ["enero","febrero","marzo","abril","mayo","junio",
             "julio","agosto","septiembre","octubre","noviembre","diciembre"]
    d = datetime.strptime(fecha_str, "%Y-%m-%d")
    return f"{d.day} de {meses[d.month - 1]} de {d.year}"

# ─── Finanzas (usa math) ───────────────────────────────
def calcular_balance(transacciones: list) -> dict:
    """Calcula ingresos, gastos y balance neto."""
    ingresos = sum(t["monto"] for t in transacciones if t["tipo"] == "ingreso")
    gastos   = sum(t["monto"] for t in transacciones if t["tipo"] == "gasto")
    return {
        "ingresos": round(ingresos, 2),
        "gastos":   round(gastos, 2),
        "balance":  round(ingresos - gastos, 2),
        "promedio_ingreso": round(math.fsum(
            t["monto"] for t in transacciones if t["tipo"] == "ingreso"
        ) / max(1, sum(1 for t in transacciones if t["tipo"] == "ingreso")), 2)
    }

def porcentaje_repertorio_listo(canciones: list) -> float:
    """% de canciones con estado 'lista'."""
    if not canciones:
        return 0.0
    listas = sum(1 for c in canciones if c["estado"] == "lista")
    return round((listas / len(canciones)) * 100, 1)

# ─── Validaciones ─────────────────────────────────────
def validar_fecha(fecha_str: str) -> bool:
    try:
        datetime.strptime(fecha_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def formatear_moneda(monto: float, simbolo: str = "$") -> str:
    return f"{simbolo}{monto:,.2f}"