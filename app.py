from flask import Flask, render_template, redirect, url_for, session
from config import SECRET_KEY
from routes.auth import auth_bp
from routes.admin import admin_bp, requiere_login
from routes.eventos import eventos_bp
from routes.canciones import canciones_bp
from routes.contactos import contactos_bp
from routes.finanzas import finanzas_bp
from routes.perfil import perfil_bp
from models.evento import Evento
from models.cancion import Cancion
from models.contacto import Contacto
from models.transaccion import Transaccion
from guitarutils import (dias_para_evento, formatear_fecha,
                         calcular_balance, formatear_moneda,
                         porcentaje_repertorio_listo)
from datetime import datetime, timezone

app = Flask(__name__)
app.secret_key = SECRET_KEY

app.register_blueprint(auth_bp,      url_prefix="/auth")
app.register_blueprint(admin_bp,     url_prefix="/admin")
app.register_blueprint(eventos_bp,   url_prefix="/eventos")
app.register_blueprint(canciones_bp, url_prefix="/canciones")
app.register_blueprint(contactos_bp, url_prefix="/contactos")
app.register_blueprint(finanzas_bp,  url_prefix="/finanzas")
app.register_blueprint(perfil_bp,    url_prefix="/perfil")


def _tiempo_relativo(fecha_iso: str) -> str:
    """
    Convierte una fecha ISO (YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS...)
    en texto relativo: 'Hoy', 'Ayer', 'Hace 3 días', etc.
    """
    try:
        fecha_str = fecha_iso[:10]  # tomar solo YYYY-MM-DD
        fecha     = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        hoy       = datetime.now(timezone.utc).date()
        diff      = (hoy - fecha).days
        if diff == 0:   return "Hoy"
        if diff == 1:   return "Ayer"
        if diff < 7:    return f"Hace {diff} días"
        if diff < 30:   return f"Hace {diff // 7} sem."
        return f"Hace {diff // 30} mes."
    except Exception:
        return ""


def _construir_actividad_reciente(eventos, canciones, transacciones, contactos) -> list:
    """
    Mezcla los registros más recientes de cada modelo y devuelve
    una lista de dicts con { tipo, texto, tiempo } ordenada por fecha desc.
    """
    items = []

    for e in eventos[-5:]:
        items.append({
            "tipo":   "evento",
            "texto":  f"Evento creado: <strong>{e['titulo']}</strong>",
            "fecha":  e.get("created_at", e.get("fecha", "")),
        })

    for c in canciones[-5:]:
        items.append({
            "tipo":   "cancion",
            "texto":  f"Canción agregada: <strong>{c['titulo']}</strong>",
            "fecha":  c.get("created_at", ""),
        })

    for t in transacciones[:5]:  # ya vienen desc por fecha
        tipo_txt = "Ingreso" if t["tipo"] == "ingreso" else "Gasto"
        items.append({
            "tipo":   "finanza",
            "texto":  f"{tipo_txt} registrado: <strong>{formatear_moneda(t['monto'])}</strong>",
            "fecha":  t.get("created_at", t.get("fecha", "")),
        })

    for ct in contactos[-5:]:
        items.append({
            "tipo":   "contacto",
            "texto":  f"Contacto agregado: <strong>{ct['nombre']}</strong>",
            "fecha":  ct.get("created_at", ""),
        })

    # Ordenar por fecha descendente y tomar los 5 más recientes
    items.sort(key=lambda x: x["fecha"], reverse=True)

    for item in items:
        item["tiempo"] = _tiempo_relativo(item["fecha"])

    return items[:5]


@app.route("/")
@requiere_login
def dashboard():
    tenant_id = session.get("tenant_id")

    # ── Eventos ────────────────────────────────────
    todos_eventos = Evento(tenant_id).listar()

    for e in todos_eventos:
        e["dias_restantes"] = dias_para_evento(e["fecha"])
        e["fecha_bonita"]   = formatear_fecha(e["fecha"])

    # Próximos: solo futuros o hoy, máx 5
    proximos = [e for e in todos_eventos if e["dias_restantes"] >= 0][:5]

    # Evento urgente: el más próximo en los próximos 2 días
    evento_urgente = next(
        (e for e in proximos if 0 <= e["dias_restantes"] <= 2),
        None
    )

    # ── Canciones ──────────────────────────────────
    canciones     = Cancion(tenant_id).listar()
    progreso      = porcentaje_repertorio_listo(canciones)
    c_listas      = sum(1 for c in canciones if c["estado"] == "lista")
    c_aprendiendo = sum(1 for c in canciones if c["estado"] == "aprendiendo")
    c_pausadas    = sum(1 for c in canciones if c["estado"] == "pausada")

    # ── Contactos ──────────────────────────────────
    contactos = Contacto(tenant_id).listar()

    # ── Finanzas ───────────────────────────────────
    transacciones = Transaccion(tenant_id).listar()
    balance_data  = calcular_balance(transacciones)

    # ── Actividad reciente ─────────────────────────
    actividad_reciente = _construir_actividad_reciente(
        todos_eventos, canciones, transacciones, contactos
    )

    return render_template("dashboard.html",
        nombre                = session.get("nombre"),
        rol                   = session.get("rol"),
        # Eventos
        total_eventos         = len(todos_eventos),
        proximos_eventos      = proximos,
        evento_urgente        = evento_urgente,
        # Canciones
        total_canciones       = len(canciones),
        progreso              = progreso,
        canciones_listas      = c_listas,
        canciones_aprendiendo = c_aprendiendo,
        canciones_pausadas    = c_pausadas,
        # Contactos
        total_contactos       = len(contactos),
        # Finanzas
        balance               = balance_data["balance"],
        balance_fmt           = formatear_moneda(balance_data["balance"]),
        ingresos_fmt          = formatear_moneda(balance_data["ingresos"]),
        gastos_fmt            = formatear_moneda(balance_data["gastos"]),
        promedio_fmt          = formatear_moneda(balance_data["promedio_ingreso"]),
        # Actividad
        actividad_reciente    = actividad_reciente,
    )


if __name__ == "__main__":
    app.run(debug=True, port=8000, host="0.0.0.0")