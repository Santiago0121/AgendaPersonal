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

app = Flask(__name__)
app.secret_key = SECRET_KEY

app.register_blueprint(auth_bp,      url_prefix="/auth")
app.register_blueprint(admin_bp,     url_prefix="/admin")
app.register_blueprint(eventos_bp,   url_prefix="/eventos")
app.register_blueprint(canciones_bp, url_prefix="/canciones")
app.register_blueprint(contactos_bp, url_prefix="/contactos")
app.register_blueprint(finanzas_bp,  url_prefix="/finanzas")
app.register_blueprint(perfil_bp,    url_prefix="/perfil")

@app.route("/")
@requiere_login
def dashboard():
    tenant_id = session.get("tenant_id")
    todos_eventos    = Evento(tenant_id).listar()
    proximos         = [e for e in todos_eventos
                        if dias_para_evento(e["fecha"]) >= 0][:5]
    for e in proximos:
        e["dias_restantes"] = dias_para_evento(e["fecha"])
        e["fecha_bonita"]   = formatear_fecha(e["fecha"])
    canciones        = Cancion(tenant_id).listar()
    progreso         = porcentaje_repertorio_listo(canciones)
    c_listas         = sum(1 for c in canciones if c["estado"] == "lista")
    c_aprendiendo    = sum(1 for c in canciones if c["estado"] == "aprendiendo")
    c_pausadas       = sum(1 for c in canciones if c["estado"] == "pausada")
    contactos        = Contacto(tenant_id).listar()
    transacciones    = Transaccion(tenant_id).listar()
    balance_data     = calcular_balance(transacciones)
    return render_template("dashboard.html",
        nombre                = session.get("nombre"),
        rol                   = session.get("rol"),
        total_eventos         = len(todos_eventos),
        proximos_eventos      = proximos,
        total_canciones       = len(canciones),
        progreso              = progreso,
        canciones_listas      = c_listas,
        canciones_aprendiendo = c_aprendiendo,
        canciones_pausadas    = c_pausadas,
        total_contactos       = len(contactos),
        balance               = balance_data["balance"],
        balance_fmt           = formatear_moneda(balance_data["balance"]),
        ingresos_fmt          = formatear_moneda(balance_data["ingresos"]),
        gastos_fmt            = formatear_moneda(balance_data["gastos"]),
        promedio_fmt          = formatear_moneda(balance_data["promedio_ingreso"]),
    )

if __name__ == "__main__":
    app.run(debug=True, port=8000, host="0.0.0.0")