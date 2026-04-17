from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.transaccion import Transaccion
from models.evento import Evento
from routes.admin import requiere_login
from guitarutils import calcular_balance, formatear_moneda, formatear_fecha
from datetime import date

finanzas_bp = Blueprint("finanzas", __name__)

def get_modelo():
    return Transaccion(session.get("tenant_id"))

@finanzas_bp.route("/")
@requiere_login
def index():
    tipo = request.args.get("tipo", "")
    modelo = get_modelo()

    transacciones = modelo.listar(tipo if tipo else None)
    todas         = modelo.listar()
    balance       = calcular_balance(todas)

    # Enriquecer con fecha formateada y monto formateado
    for t in transacciones:
        t["fecha_bonita"] = formatear_fecha(t["fecha"])
        t["monto_fmt"]    = formatear_moneda(t["monto"])

    return render_template("finanzas/index.html",
                           transacciones=transacciones,
                           balance=balance,
                           tipo_activo=tipo,
                           formatear_moneda=formatear_moneda)

@finanzas_bp.route("/crear", methods=["GET", "POST"])
@requiere_login
def crear():
    if request.method == "POST":
        datos = {
            "tipo":        request.form["tipo"],
            "monto":       float(request.form["monto"]),
            "descripcion": request.form.get("descripcion", ""),
            "fecha":       request.form["fecha"],
            "evento_id":   request.form.get("evento_id") or None,
        }
        try:
            get_modelo().crear(datos)
            flash("Transacción registrada correctamente.", "success")
            return redirect(url_for("finanzas.index"))
        except Exception as e:
            flash(f"Error al registrar: {str(e)}", "error")

    eventos = Evento(session.get("tenant_id")).listar()
    return render_template("finanzas/form.html",
                           transaccion=None,
                           accion="Registrar",
                           eventos=eventos,
                           hoy=date.today().isoformat())

@finanzas_bp.route("/editar/<transaccion_id>", methods=["GET", "POST"])
@requiere_login
def editar(transaccion_id):
    modelo = get_modelo()

    if request.method == "POST":
        datos = {
            "tipo":        request.form["tipo"],
            "monto":       float(request.form["monto"]),
            "descripcion": request.form.get("descripcion", ""),
            "fecha":       request.form["fecha"],
            "evento_id":   request.form.get("evento_id") or None,
        }
        try:
            modelo.actualizar(transaccion_id, datos)
            flash("Transacción actualizada correctamente.", "success")
            return redirect(url_for("finanzas.index"))
        except Exception as e:
            flash(f"Error al actualizar: {str(e)}", "error")

    transaccion = modelo.obtener(transaccion_id)
    eventos     = Evento(session.get("tenant_id")).listar()
    return render_template("finanzas/form.html",
                           transaccion=transaccion,
                           accion="Editar",
                           eventos=eventos,
                           hoy=date.today().isoformat())

@finanzas_bp.route("/eliminar/<transaccion_id>", methods=["POST"])
@requiere_login
def eliminar(transaccion_id):
    try:
        get_modelo().eliminar(transaccion_id)
        flash("Transacción eliminada correctamente.", "success")
    except Exception as e:
        flash(f"Error al eliminar: {str(e)}", "error")
    return redirect(url_for("finanzas.index"))