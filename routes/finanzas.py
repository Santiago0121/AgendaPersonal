from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.transaccion import Transaccion
from models.evento import Evento
from routes.admin import requiere_login
from guitarutils import calcular_balance, formatear_moneda, formatear_fecha
from datetime import date

finanzas_bp = Blueprint("finanzas", __name__)

def get_modelo():
    return Transaccion(session.get("tenant_id"))

def _enriquecer_eventos_para_form(tenant_id: str) -> list:
    """
    Devuelve solo los eventos NO pagados, enriquecidos con valor_fmt,
    para mostrar en el selector del formulario de transacción.
    """
    eventos = Evento(tenant_id).listar()
    resultado = []
    for e in eventos:
        # Excluir eventos ya marcados como pagados
        if e.get("pagado"):
            continue
        e["valor_fmt"] = formatear_moneda(e.get("valor") or 0) if e.get("valor") else None
        resultado.append(e)
    return resultado


@finanzas_bp.route("/")
@requiere_login
def index():
    tipo  = request.args.get("tipo", "")
    modelo = get_modelo()

    transacciones = modelo.listar(tipo if tipo else None)
    todas         = modelo.listar()
    balance       = calcular_balance(todas)

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

    eventos = _enriquecer_eventos_para_form(session.get("tenant_id"))
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
    eventos     = _enriquecer_eventos_para_form(session.get("tenant_id"))

    # Si la transacción ya está vinculada a un evento pagado,
    # lo incluimos igual para que aparezca seleccionado al editar
    if transaccion.get("evento_id"):
        ids_en_lista = {e["id"] for e in eventos}
        if transaccion["evento_id"] not in ids_en_lista:
            evento_vinculado = Evento(session.get("tenant_id")).obtener(transaccion["evento_id"])
            if evento_vinculado:
                evento_vinculado["valor_fmt"] = formatear_moneda(evento_vinculado.get("valor") or 0)
                evento_vinculado["_solo_lectura"] = True  # marcador para el template
                eventos.insert(0, evento_vinculado)

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